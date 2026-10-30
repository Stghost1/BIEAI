"""
Abrahamic Opportunities Engine Local Server.
Runs on http://127.0.0.1:4174.
Combines:
1. Signal Radar & Surveys Interface (index.html)
2. Interactive Client Demo Applications & Custom Vault Prototypes
3. Autonomous Auto-Pilot Engine & Email Dispatcher
"""

from __future__ import annotations

import json
import mimetypes
import shutil
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from core.db import (
    init_db,
    get_opportunities,
    get_opportunity_by_id,
    update_opportunity_status,
    get_stats,
    get_pipeline,
    update_draft_status,
    get_surveys,
    get_survey_playbook,
    get_setting,
    set_setting,
    get_all_settings,
    get_portfolio_demos,
    get_autopilot_runs,
    update_opportunity_email,
)
from core.demo_builder import build_tailored_demo
from core.mailer import (
    send_proposal_email,
    test_smtp_connection,
    send_operator_notification,
    send_leads_digest_alert,
    get_operator_email,
)
from core.outreach_generator import generate_outreach, get_demo_registry, generate_followup
from core.scanner import run_full_scan, rescore_all, enabled_sources, SOURCE_INFO
from core.autopilot import run_autopilot_pipeline, batch_autopilot, autopilot_status, start_scheduler
from core.media_library import list_clips, save_uploaded_clip
from core.ats_analyzer import analyze_ats_fit
from core.antijob import get_antijob_playbook
from core.email_scourer import scour_company_email

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 4174))
IS_SCANNING = False
SCAN_LOCK = threading.Lock()
LAST_SCAN: dict = {}

ALLOWED_ORIGINS = {f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"}

# Only these file types are ever served by the generic static fallback.
SERVABLE_EXT = {".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg",
                ".ico", ".mp4", ".webm", ".mov", ".woff", ".woff2"}
# Never served, whatever the extension: secrets, database, source, backups.
BLOCKED_TOP = {"data", "core", "tests", "temp_backup", "__pycache__", "node_modules", "docs"}


def safe_static_path(url_path: str):
    """Resolve a URL path to a file inside ROOT, refusing dotfiles, secrets and source dirs."""
    rel = url_path.lstrip("/")
    if not rel:
        return None
    parts = Path(rel).parts
    if any(p.startswith(".") for p in parts) or (parts and parts[0] in BLOCKED_TOP):
        return None
    candidate = (ROOT / rel).resolve()
    if ROOT not in candidate.parents or not candidate.is_file():
        return None
    if candidate.suffix.lower() not in SERVABLE_EXT:
        return None
    return candidate


def background_scan():
    global IS_SCANNING, LAST_SCAN
    if not SCAN_LOCK.acquire(blocking=False):
        return
    IS_SCANNING = True
    try:
        LAST_SCAN = run_full_scan()
    finally:
        IS_SCANNING = False
        SCAN_LOCK.release()


class AbrahamicEngineHandler(BaseHTTPRequestHandler):
    pass

class RobustThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_type and issubclass(exc_type, (ConnectionError, OSError)):
            return
        super().handle_error(request, client_address)


class ScoutDeskHandler(AbrahamicEngineHandler):
    def log_message(self, format, *args):
        pass

    def handle_media_upload(self, query):
        """POST /api/media/upload?filename=x.mp4&title=..&tags=ugc,product&tool=Kling
        Body: raw video bytes (fetch(url, {method:'POST', body:file})). Max 200 MB, streamed to disk."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        q = {k: v[0] for k, v in query.items()}
        try:
            clip = save_uploaded_clip(self.rfile, length, q.get("filename", "clip.mp4"),
                                      title=q.get("title", ""), tags=q.get("tags", ""), tool=q.get("tool", ""))
            self.json_response({"ok": True, "clip": clip})
        except ValueError as exc:
            self.json_response({"error": {"code": "invalid_upload", "message": str(exc), "details": None}}, 400)

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionError, OSError):
            pass

    def _origin_allowed(self) -> bool:
        """Requests without an Origin header (curl, same-origin GET) are allowed.
        Cross-origin browser requests are only allowed from the dashboard itself, so a random
        website you visit cannot read your settings or trigger autopilot sends."""
        origin = self.headers.get("Origin")
        return (not origin) or origin in ALLOWED_ORIGINS

    def send_cors(self):
        origin = self.headers.get("Origin")
        if origin and origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("X-Content-Type-Options", "nosniff")

    def json_response(self, data: dict | list, status: int = 200):
        try:
            body = json.dumps(data, default=str).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_cors()
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionError, OSError):
            pass

    def serve_file(self, file_path: Path):
        try:
            if not file_path.is_file():
                self.json_response({"error": "File not found"}, 404)
                return
            mime, _ = mimetypes.guess_type(str(file_path))
            mime = mime or "application/octet-stream"
            file_size = file_path.stat().st_size

            # Streaming and Range support for large media / video files
            range_header = self.headers.get("Range")
            if range_header and range_header.startswith("bytes="):
                try:
                    ranges = range_header.replace("bytes=", "").split("-")
                    start = int(ranges[0]) if ranges[0] else 0
                    end = int(ranges[1]) if len(ranges) > 1 and ranges[1] else file_size - 1
                    if start >= file_size or end >= file_size or start > end:
                        self.send_response(416)
                        self.send_header("Content-Range", f"bytes */{file_size}")
                        self.end_headers()
                        return
                    length = end - start + 1
                    self.send_response(206)
                    self.send_header("Content-Type", mime)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(length))
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_cors()
                    self.end_headers()
                    with open(file_path, "rb") as f:
                        f.seek(start)
                        remaining = length
                        chunk_size = 64 * 1024
                        while remaining > 0:
                            to_read = min(chunk_size, remaining)
                            buf = f.read(to_read)
                            if not buf:
                                break
                            self.wfile.write(buf)
                            remaining -= len(buf)
                    return
                except (ConnectionError, OSError):
                    return
                except Exception:
                    pass

            # Full file response
            self.send_response(200)
            if mime.startswith(("text/", "application/json", "application/javascript")):
                self.send_header("Content-Type", f"{mime}; charset=utf-8")
            else:
                self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_cors()
            self.end_headers()
            with open(file_path, "rb") as f:
                shutil.copyfileobj(f, self.wfile, length=64 * 1024)
        except (ConnectionError, OSError):
            pass

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_cors()
            self.end_headers()
        except (ConnectionError, OSError):
            pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in ("/radar", "/radar.html", "/surveys"):
            radar_candidate = ROOT / "radar.html"
            if radar_candidate.is_file():
                self.serve_file(radar_candidate)
                return
            self.serve_file(ROOT / "index.html")
            return

        if path in ("/", "/index.html"):
            self.serve_file(ROOT / "index.html")
            return

        if path in ("/media-kit", "/media-kit.html"):
            self.serve_file(ROOT / "media-kit.html")
            return

        if path in ("/styles.css", "/app.js") or path.startswith("/media/") or path.startswith("/assets/"):
            file_path = safe_static_path(path)
            if file_path:
                self.serve_file(file_path)
                return

        # Clean Rewrites for Client Demos and Vault Prototypes
        clean_name = path.lstrip("/").replace(".html", "")
        if clean_name and "/" not in clean_name and ".." not in clean_name and not clean_name.startswith("."):
            demo_candidate = ROOT / f"{clean_name}.html"
            if demo_candidate.is_file():
                self.serve_file(demo_candidate)
                return
            demos_sub_candidate = ROOT / "demos" / f"{clean_name}.html"
            if demos_sub_candidate.is_file():
                self.serve_file(demos_sub_candidate)
                return

        if path == "/api/opportunities":
            category = query.get("category", ["all"])[0]
            seniority = query.get("seniority", ["all"])[0]
            job_type = query.get("job_type", ["all"])[0]
            workplace_type = query.get("workplace", [query.get("remote", ["all"])[0]])[0]
            search = query.get("search", [""])[0]
            limit = int(query.get("limit", [50])[0])
            status = query.get("status", [None])[0]
            items = get_opportunities(
                category=category,
                seniority=seniority,
                job_type=job_type,
                workplace_type=workplace_type,
                search=search,
                limit=limit,
                status=status
            )
            self.json_response({"opportunities": items, "count": len(items)})
            return

        if path == "/api/stats":
            stats = get_stats()
            stats["is_scanning"] = IS_SCANNING
            self.json_response(stats)
            return

        if path == "/api/pipeline":
            pipeline = get_pipeline()
            self.json_response({"pipeline": pipeline, "count": len(pipeline)})
            return

        if path == "/api/demos":
            self.json_response({"demos": get_demo_registry()})
            return

        if path == "/api/portfolio/demos":
            cat = query.get("category", [None])[0]
            demos = get_portfolio_demos(category=cat)
            self.json_response({"demos": demos, "count": len(demos)})
            return

        if path == "/api/autopilot/runs":
            limit = int(query.get("limit", [50])[0])
            runs = get_autopilot_runs(limit=limit)
            self.json_response({"runs": runs, "count": len(runs)})
            return

        if path == "/api/settings":
            settings = get_all_settings()
            settings["smtp_pass_set"] = "true" if settings.get("smtp_pass") else "false"
            settings["smtp_pass"] = ""  # never sent back to the browser
            self.json_response({"settings": settings})
            return

        if path == "/api/sources":
            stats = get_stats()
            counts = stats.get("sources", {})
            last = {r["source"]: r for r in (LAST_SCAN.get("sources") or [])}
            enabled = set(enabled_sources())
            sources_info = []
            for key, (label, kind, url) in SOURCE_INFO.items():
                lr = last.get(label, {})
                sources_info.append({
                    "key": key, "name": label, "type": kind, "url": url,
                    "status": ("Error" if str(lr.get("status", "")).startswith("error") else "Active") if key in enabled else "Disabled",
                    "count": counts.get(label, 0),
                    "last_found": lr.get("found"), "last_new": lr.get("new"),
                    "last_status": lr.get("status", ""), "last_seconds": lr.get("seconds"),
                })
            sources_info.append({"name": "B.I.E.AI Signal Radar", "type": "Fit engine (eligible, score 58+)",
                                 "status": "Live", "url": "Local SQLite", "count": stats.get("qualified", 0)})
            self.json_response({"sources": sources_info, "scanning": IS_SCANNING, "last_scan": LAST_SCAN.get("finished_at")})
            return

        if path == "/api/scan/status":
            self.json_response({"scanning": IS_SCANNING, "last_scan": LAST_SCAN})
            return

        if path == "/api/autopilot/status":
            self.json_response(autopilot_status())
            return

        if path == "/api/media":
            self.json_response({"clips": list_clips()})
            return

        if path == "/api/surveys":
            category = query.get("category", ["all"])[0]
            country = query.get("country", ["all"])[0]
            search = query.get("search", [""])[0]
            vpn_param = query.get("vpn", [None])[0]
            vpn_required = None
            if vpn_param is not None:
                vpn_required = vpn_param.lower() in ("1", "true", "yes")
            items = get_surveys(category=category, country=country, search=search, vpn_required=vpn_required)
            self.json_response({"surveys": items, "count": len(items)})
            return

        if path == "/api/surveys/playbook":
            self.json_response({"playbook": get_survey_playbook()})
            return

        if path == "/api/antijob/playbook":
            self.json_response({"playbook": get_antijob_playbook()})
            return

        if path == "/api/ats/analyze":
            opp_id = query.get("opp_id", [None])[0]
            if opp_id:
                opp = get_opportunity_by_id(int(opp_id))
                if opp:
                    analysis = analyze_ats_fit(opp["title"], opp.get("description", ""), opp.get("tags", []))
                    self.json_response({"ok": True, "analysis": analysis, "opp_id": int(opp_id)})
                    return
                self.json_response({"error": "Opportunity not found"}, 404)
                return
            title = query.get("title", [""])[0]
            desc = query.get("desc", [""])[0]
            analysis = analyze_ats_fit(title, desc)
            self.json_response({"ok": True, "analysis": analysis})
            return

        file_candidate = safe_static_path(path)
        if file_candidate:
            self.serve_file(file_candidate)
            return

        self.json_response({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if not self._origin_allowed():
            self.json_response({"error": {"code": "forbidden_origin", "message": "Cross-origin request refused", "details": None}}, 403)
            return

        # Binary clip upload: body is the raw video, metadata in the query string.
        if parsed.path == "/api/media/upload":
            self.handle_media_upload(parse_qs(parsed.query))
            return

        length = int(self.headers.get("Content-Length", 0))
        if length > 2_000_000:
            self.json_response({"error": {"code": "payload_too_large", "message": "JSON body over 2 MB", "details": None}}, 413)
            return
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except Exception:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}

        if parsed.path == "/api/scan":
            global IS_SCANNING
            if IS_SCANNING:
                self.json_response({"ok": False, "message": "Scan already running in background"}, 409)
                return
            t = threading.Thread(target=background_scan, daemon=True)
            t.start()
            self.json_response({"ok": True, "message": "Live signal scan initiated across all sources."})
            return

        if parsed.path == "/api/rescore":
            self.json_response({"ok": True, **rescore_all()})
            return

        if parsed.path == "/api/draft":
            opp_id = payload.get("opp_id")
            angle = payload.get("angle", "proof_of_work")
            if not opp_id:
                self.json_response({"error": "opp_id is required"}, 400)
                return

            target = get_opportunity_by_id(int(opp_id))
            if not target:
                self.json_response({"error": "Opportunity not found"}, 404)
                return

            draft = generate_outreach(target, angle=angle)
            self.json_response({"ok": True, "draft": draft})
            return

        if parsed.path == "/api/followup":
            opp_id = payload.get("opp_id")
            touch = int(payload.get("touch", 2))
            if not opp_id:
                self.json_response({"error": "opp_id is required"}, 400)
                return
            target = get_opportunity_by_id(int(opp_id))
            if not target:
                self.json_response({"error": "Opportunity not found"}, 404)
                return
            draft_info = payload.get("draft") or {}
            followup = generate_followup(target, draft_info, touch=touch)
            self.json_response({"ok": True, "followup": followup})
            return

        if parsed.path == "/api/opportunity/status":
            opp_id = payload.get("opp_id")
            status = payload.get("status", "new")
            if not opp_id:
                self.json_response({"error": "opp_id is required"}, 400)
                return
            ok = update_opportunity_status(int(opp_id), status)
            self.json_response({"ok": ok, "opp_id": int(opp_id), "status": status})
            return

        if parsed.path == "/api/scour/email":
            opp_id = payload.get("opp_id")
            company = payload.get("company", "")
            opp_url = payload.get("url", "")
            title = payload.get("title", "")
            desc = payload.get("description", "")
            if opp_id:
                target = get_opportunity_by_id(int(opp_id))
                if target:
                    company = company or target.get("company", "")
                    opp_url = opp_url or target.get("url", "")
                    title = title or target.get("title", "")
                    desc = desc or target.get("description", "")
            res = scour_company_email(company, opp_url=opp_url, title=title, desc=desc)
            if res.get("ok") and res.get("email") and opp_id:
                update_opportunity_email(int(opp_id), res["email"], res.get("domain", ""))
            self.json_response(res)
            return

        if parsed.path == "/api/demo/build":
            opp_id = payload.get("opp_id")
            if not opp_id:
                self.json_response({"error": "opp_id is required"}, 400)
                return
            target = get_opportunity_by_id(int(opp_id))
            if not target:
                self.json_response({"error": "Opportunity not found"}, 404)
                return
            clips = [str(c) for c in (payload.get("clips") or []) if isinstance(c, str)][:6]
            res = build_tailored_demo(target, clips=clips or None)
            res.pop("html", None)  # the page is on disk; no need to ship 40 KB back to the UI
            self.json_response({"ok": True, "demo": res})
            return

        if parsed.path == "/api/autopilot/run":
            opp_id = payload.get("opp_id")
            if not opp_id:
                self.json_response({"error": "opp_id is required"}, 400)
                return
            auto_send = payload.get("auto_send")
            recipient = payload.get("recipient")
            res = run_autopilot_pipeline(int(opp_id), auto_send=auto_send, recipient_override=recipient)
            self.json_response(res)
            return

        if parsed.path == "/api/autopilot/batch":
            limit = int(payload.get("limit", 3))
            min_fit = int(payload.get("min_fit", 80))
            auto_send = payload.get("auto_send")
            res = batch_autopilot(limit=limit, min_fit=min_fit, auto_send=auto_send)
            self.json_response(res)
            return

        if parsed.path == "/api/mailer/send":
            recipient = payload.get("recipient", "")
            subject = payload.get("subject", "")
            body_text = payload.get("body", "")
            draft_id = payload.get("draft_id")
            res = send_proposal_email(recipient, subject, body_text, draft_id=draft_id)
            self.json_response(res)
            return

        if parsed.path == "/api/mailer/test":
            host = payload.get("host", "smtp.gmail.com")
            port = int(payload.get("port", 587))
            user = payload.get("user", "")
            password = payload.get("password", "") or get_setting("smtp_pass", "")
            res = test_smtp_connection(host, port, user, password)
            self.json_response(res)
            return

        if parsed.path == "/api/mailer/test-operator":
            op_email = get_operator_email()
            res = send_operator_notification(
                subject="[Synchronization Verified] Abrahamic Opportunities Engine Alert System",
                body_text=f"""ABRAHAMIC OPPORTUNITIES ENGINE EMAIL SYNCHRONIZATION TEST

Target Operator Email: {op_email}
Status: Verified Active
Architecture: Dual-Mode Autonomous SMTP + 1-Click Webmail Fallback

This confirms that your Abrahamic Opportunities Engine is actively configured to dispatch:
1. Real-time application dispatch alerts with bespoke prototype URLs.
2. Automated BCC copies of all cold outreach sent to prospective employers.
3. High-fit executive leads digests for top matching opportunities.
""",
                html_body=f"""<!DOCTYPE html>
<html>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; background:#0f172a; color:#f8fafc; padding:24px; margin:0;">
  <div style="max-width:580px; margin:0 auto; background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden;">
    <div style="background:#0284c7; padding:20px 24px;">
      <span style="font-size:11px; text-transform:uppercase; letter-spacing:0.08em; color:#e0f2fe; font-weight:700;">Abrahamic Opportunities Engine</span>
      <h2 style="margin:4px 0 0; color:#ffffff; font-size:20px;">Email Synchronization Verified</h2>
    </div>
    <div style="padding:24px;">
      <p style="margin:0 0 16px; color:#cbd5e1; font-size:14px; line-height:1.6;">
        This test notification confirms that your local engine is synchronized with <strong>{op_email}</strong>.
      </p>
      <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:16px; margin-bottom:20px;">
        <div style="font-size:12px; color:#38bdf8; font-weight:700; margin-bottom:8px;">ACTIVE SYNCHRONIZATION PIPELINES:</div>
        <ul style="margin:0; padding-left:18px; color:#cbd5e1; font-size:13px; line-height:1.7;">
          <li><strong>Autonomous Dispatches:</strong> Instant notification containing the live Vercel demo URL and recipient breakdown every time an application runs.</li>
          <li><strong>Automatic Application BCC:</strong> Exact delivery archive of every email sent to hiring leads.</li>
          <li><strong>Leads Digest:</strong> High-fit opportunity digests prioritized by match score.</li>
        </ul>
      </div>
      <div style="text-align:center;">
        <a href="http://127.0.0.1:4174" target="_blank" style="display:inline-block; background:#0284c7; color:#ffffff; text-decoration:none; padding:10px 20px; border-radius:6px; font-weight:700; font-size:14px;">Open Live Engine Dashboard &rarr;</a>
      </div>
    </div>
  </div>
</body>
</html>"""
            )
            self.json_response(res)
            return

        if parsed.path == "/api/mailer/digest":
            res = send_leads_digest_alert()
            self.json_response(res)
            return

        if parsed.path in ("/api/pipeline/mark-done", "/api/pipeline/mark-sent", "/api/outreach/mark-sent"):
            draft_id = payload.get("draft_id")
            opp_id = payload.get("opp_id")
            rec_email = payload.get("recipient_email")
            if draft_id:
                update_draft_status(int(draft_id), status="sent", recipient_email=rec_email)
            if opp_id:
                update_opportunity_status(int(opp_id), status="applied")
            self.json_response({"ok": True, "message": "Marked as sent and applied successfully."})
            return

        if parsed.path == "/api/pipeline/update":
            draft_id = payload.get("draft_id")
            status = payload.get("status", "draft")
            body_text = payload.get("body")
            subject_text = payload.get("subject")
            recipient_email = payload.get("recipient_email")
            if not draft_id:
                self.json_response({"error": "draft_id is required"}, 400)
                return
            success = update_draft_status(
                int(draft_id),
                status=status,
                body=body_text,
                subject=subject_text,
                recipient_email=recipient_email,
            )
            self.json_response({"ok": success})
            return

        if parsed.path == "/api/settings":
            for k, v in payload.items():
                if k == "smtp_pass_set":
                    continue
                if k == "smtp_pass" and not str(v).strip():
                    continue  # blank field in the UI means "keep the stored password"
                if isinstance(v, (str, int, float, bool)):
                    set_setting(k, str(v).strip())
            out = get_all_settings()
            out["smtp_pass_set"] = "true" if out.get("smtp_pass") else "false"
            out["smtp_pass"] = ""
            self.json_response({"ok": True, "settings": out})
            return

        self.json_response({"error": "Not found"}, 404)


def main():
    init_db()
    print("=" * 70)
    print("ABRAHAMIC OPPORTUNITIES ENGINE (B.I.E.AI)")
    print(f"Abrahamic Opportunities Engine Interface: http://127.0.0.1:{PORT}/")
    print(f"Opportunity Radar: http://127.0.0.1:{PORT}/radar")
    print(f"Tailored Vault Prototypes: http://127.0.0.1:{PORT}/api/portfolio/demos")
    print(f"Autonomous Auto-Pilot: Ready")
    print("=" * 70)

    start_scheduler()  # no-op unless autopilot_schedule_enabled = true in settings
    server = RobustThreadingHTTPServer(("127.0.0.1", PORT), ScoutDeskHandler)
    while True:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Abrahamic Opportunities Engine Server.")
            break
        except Exception as e:
            print(f"Server loop recovered from unexpected exception: {e}")
            import time
            time.sleep(0.5)
    server.server_close()


if __name__ == "__main__":
    main()
