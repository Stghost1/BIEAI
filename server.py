"""
B.I.E.AI Work & Opportunity Operating System.
Unified Server running on http://127.0.0.1:4173.
Combines:
1. Production Agency Showcase (index.html)
2. Live Opportunity Radar & Tailored Outreach Engine (radar.html / Scoutdesk)
3. Interactive Client Demo Applications & Custom Vault Prototypes
4. Autonomous Auto-Pilot Engine & Email Dispatcher
"""

from __future__ import annotations

import json
import mimetypes
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
from core.mailer import send_proposal_email, test_smtp_connection
from core.outreach_generator import generate_outreach, get_demo_registry, generate_followup
from core.scanner import run_full_scan
from core.autopilot import run_autopilot_pipeline, batch_autopilot
from core.ats_analyzer import analyze_ats_fit
from core.antijob import get_antijob_playbook
from core.email_scourer import scour_company_email

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 4173))
IS_SCANNING = False


def background_scan():
    global IS_SCANNING
    IS_SCANNING = True
    try:
        run_full_scan()
    finally:
        IS_SCANNING = False


class UnifiedAppHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def json_response(self, data: dict | list, status: int = 200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors()
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, file_path: Path):
        if not file_path.is_file():
            self.json_response({"error": "File not found"}, 404)
            return
        mime, _ = mimetypes.guess_type(str(file_path))
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{mime or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_cors()
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. Main Client Portfolio
        if path in ("/", "/index.html"):
            self.serve_file(ROOT / "index.html")
            return

        # 2. Scoutdesk Opportunity Radar & Surveys
        if path in ("/radar", "/radar.html", "/surveys"):
            self.serve_file(ROOT / "radar.html")
            return

        # 3. Clean Rewrites for Client Demos and Vault Prototypes
        clean_name = path.lstrip("/").replace(".html", "")
        demo_candidate = ROOT / f"{clean_name}.html"
        if demo_candidate.is_file():
            self.serve_file(demo_candidate)
            return

        # 4. Scoutdesk REST APIs
        if path == "/api/opportunities":
            category = query.get("category", ["all"])[0]
            search = query.get("search", [""])[0]
            limit = int(query.get("limit", [50])[0])
            status = query.get("status", [None])[0]
            items = get_opportunities(category=category, search=search, limit=limit, status=status)
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
            self.json_response({"settings": get_all_settings()})
            return

        if path == "/api/sources":
            stats = get_stats()
            sources_info = [
                {
                    "name": "RemoteOK",
                    "type": "Remote Tech & Design API",
                    "status": "Active",
                    "url": "https://remoteok.com/api",
                    "count": stats.get("sources", {}).get("RemoteOK", 0),
                },
                {
                    "name": "Jobicy",
                    "type": "Global Remote Jobs API",
                    "status": "Active",
                    "url": "https://jobicy.com/api/v2/remote-jobs",
                    "count": stats.get("sources", {}).get("Jobicy", 0),
                },
                {
                    "name": "Arbeitnow",
                    "type": "Curated Engineering API",
                    "status": "Active",
                    "url": "https://www.arbeitnow.com/api/job-board-api",
                    "count": stats.get("sources", {}).get("Arbeitnow", 0),
                },
                {
                    "name": "B.I.E.AI Signal Radar",
                    "type": "Capability Fit Engine",
                    "status": "Live",
                    "url": "Local SQLite Engine",
                    "count": stats.get("qualified", 0),
                }
            ]
            self.json_response({"sources": sources_info})
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

        # 5. Static Files from root
        file_candidate = ROOT / path.lstrip("/")
        if file_candidate.is_file() and ROOT in file_candidate.resolve().parents:
            self.serve_file(file_candidate)
            return

        self.json_response({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except Exception:
            payload = {}

        if parsed.path == "/api/scan":
            global IS_SCANNING
            if IS_SCANNING:
                self.json_response({"ok": False, "message": "Scan already in progress"}, 409)
                return
            t = threading.Thread(target=background_scan, daemon=True)
            t.start()
            self.json_response({"ok": True, "message": "Live signal scan initiated across RemoteOK, Jobicy, and Arbeitnow."})
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
            res = build_tailored_demo(target)
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
            password = payload.get("password", "")
            res = test_smtp_connection(host, port, user, password)
            self.json_response(res)
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
                if isinstance(v, (str, int, float, bool)):
                    set_setting(k, str(v).strip())
            self.json_response({"ok": True, "settings": get_all_settings()})
            return

        self.json_response({"error": "Not found"}, 404)


def main():
    init_db()
    print("=" * 70)
    print("B.I.E.AI WORK & OPPORTUNITY OPERATING SYSTEM")
    print(f"Client Portfolio: http://127.0.0.1:{PORT}/")
    print(f"Opportunity Radar: http://127.0.0.1:{PORT}/radar")
    print(f"Tailored Vault Prototypes: http://127.0.0.1:{PORT}/api/portfolio/demos")
    print(f"Autonomous Auto-Pilot: Ready")
    print("=" * 70)

    server = ThreadingHTTPServer(("127.0.0.1", PORT), UnifiedAppHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down B.I.E.AI Server.")
        server.server_close()


if __name__ == "__main__":
    main()
