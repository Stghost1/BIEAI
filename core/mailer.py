"""
Abrahamic Opportunities Engine Automated Email Dispatch & Real-Time Telemetry Alert Engine.
Handles direct TLS SMTP delivery (Gmail App Password, Sendgrid, Custom SMTP)
with zero-configuration fallback to 1-click webmail dispatch (Gmail Web & Outlook),
plus automated real-time notifications and lead digests delivered directly to the operator's email.
Enforces Law 6: contact hygiene, verified records, and zero secrets committed.
"""

from __future__ import annotations

import email.message
import email.mime.multipart
import email.mime.text
import os
import re
import smtplib
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from core.db import get_setting, update_draft_status, get_opportunities, get_connection


EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def extract_email(text: str) -> Optional[str]:
    """Scan arbitrary text for an email address and strip trailing punctuation."""
    if not text:
        return None
    matches = EMAIL_REGEX.findall(text)
    clean_matches = []
    for m in matches:
        cleaned = m.rstrip(".,;:!?)'\"")
        if "@" in cleaned and not cleaned.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
            clean_matches.append(cleaned)
    return clean_matches[0] if clean_matches else None


def get_operator_email() -> str:
    """Return canonical operator notification email."""
    return get_setting("email", os.environ.get("OPERATOR_EMAIL", "techwithbie@gmail.com")).strip()


def get_smtp_config() -> Dict[str, Any]:
    """Load SMTP settings from SQLite database settings or environment variables."""
    host = get_setting("smtp_host", os.environ.get("SMTP_HOST", "smtp.gmail.com")).strip()
    port_str = get_setting("smtp_port", os.environ.get("SMTP_PORT", "587")).strip()
    try:
        port = int(port_str)
    except ValueError:
        port = 587
    user = get_setting("smtp_user", os.environ.get("SMTP_USER", "techwithbie@gmail.com")).strip()
    password = get_setting("smtp_pass", os.environ.get("SMTP_PASS", "")).strip()
    from_name = get_setting("smtp_from_name", os.environ.get("SMTP_FROM_NAME", "Emmanuel Bamidele (Bamsemma)")).strip()

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "from_name": from_name,
        "is_configured": bool(user and password)
    }


def build_webmail_links(to: str, subject: str, body: str) -> Dict[str, str]:
    """Generate instant 1-click webmail compose URLs."""
    enc_to = quote(to or "")
    enc_su = quote(subject or "")
    enc_body = quote(body or "")
    return {
        "gmail_url": f"https://mail.google.com/mail/?view=cm&fs=1&to={enc_to}&su={enc_su}&body={enc_body}",
        "outlook_url": f"https://outlook.live.com/mail/0/deeplink/compose?to={enc_to}&subject={enc_su}&body={enc_body}",
        "mailto_url": f"mailto:{enc_to}?subject={enc_su}&body={enc_body}"
    }


def test_smtp_connection(
    host: str,
    port: int,
    user: str,
    password: str
) -> Dict[str, Any]:
    """Verify SMTP credentials without sending a message."""
    if not user or not password:
        return {
            "ok": False,
            "error": "Email address and 16-character Gmail App Password are required."
        }
    try:
        server = smtplib.SMTP(host, port, timeout=10)
        server.ehlo()
        if port in (587, 25):
            server.starttls()
            server.ehlo()
        server.login(user, password)
        server.quit()
        return {
            "ok": True,
            "message": f"SMTP handshake and authentication succeeded for {user} on {host}:{port}."
        }
    except Exception as e:
        err_msg = str(e)
        hint = ""
        if "535" in err_msg or "Username and Password not accepted" in err_msg:
            hint = " (Google requires a 16-character App Password generated at: https://myaccount.google.com/apppasswords)"
        return {
            "ok": False,
            "error": f"SMTP connection failed: {err_msg}{hint}"
        }


def send_operator_notification(
    subject: str,
    body_text: str,
    html_body: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an automated alert or update directly to the operator's inbox (techwithbie@gmail.com).
    """
    operator_email = get_operator_email()
    cfg = get_smtp_config()

    if not cfg["is_configured"]:
        links = build_webmail_links(operator_email, subject, body_text)
        return {
            "ok": False,
            "mode": "webmail_ready",
            "status": "unconfigured_smtp",
            "recipient": operator_email,
            "message": "SMTP password not set in settings. Enter your Gmail App Password to enable automatic email dispatch.",
            **links
        }

    try:
        msg = email.mime.multipart.MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{cfg['from_name']} <{cfg['user']}>"
        msg["To"] = operator_email

        part1 = email.mime.text.MIMEText(body_text, "plain", "utf-8")
        msg.attach(part1)

        if html_body:
            part2 = email.mime.text.MIMEText(html_body, "html", "utf-8")
            msg.attach(part2)

        server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=15)
        server.ehlo()
        if cfg["port"] in (587, 25):
            server.starttls()
            server.ehlo()
        server.login(cfg["user"], cfg["password"])
        server.send_message(msg)
        server.quit()

        return {
            "ok": True,
            "mode": "smtp",
            "status": "delivered",
            "recipient": operator_email,
            "message": f"Update successfully delivered to {operator_email}."
        }
    except Exception as e:
        links = build_webmail_links(operator_email, subject, body_text)
        return {
            "ok": False,
            "error": f"Notification delivery failed: {str(e)}",
            **links
        }


def send_proposal_email(
    to_email: str,
    subject: str,
    body: str,
    draft_id: Optional[int] = None,
    bcc_operator: bool = True
) -> Dict[str, Any]:
    """
    Primary proposal/application email dispatcher:
    1. If SMTP is configured, dispatches via smtplib with TLS and BCCs operator.
    2. If SMTP is not yet configured, marks draft as queued and returns pre-formatted webmail links.
    """
    to_clean = (to_email or "").strip()
    webmail_links = build_webmail_links(to_clean, subject, body)
    operator_email = get_operator_email()

    cfg = get_smtp_config()

    if not cfg["is_configured"]:
        if draft_id:
            update_draft_status(
                draft_id,
                status="queued_webmail",
                body=body,
                subject=subject,
                recipient_email=to_clean
            )
        return {
            "ok": True,
            "mode": "webmail_ready",
            "status": "queued",
            "recipient": to_clean,
            "message": "SMTP password not set in settings. Proposal queued and ready for 1-click webmail dispatch.",
            **webmail_links
        }

    # Attempt direct SMTP dispatch
    if not to_clean or "@" not in to_clean:
        return {
            "ok": False,
            "error": "Valid recipient email address is required for automated SMTP send.",
            **webmail_links
        }

    try:
        msg = email.message.EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = f"{cfg['from_name']} <{cfg['user']}>"
        msg["To"] = to_clean
        if bcc_operator and operator_email:
            msg["Bcc"] = operator_email

        server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=15)
        server.ehlo()
        if cfg["port"] in (587, 25):
            server.starttls()
            server.ehlo()
        server.login(cfg["user"], cfg["password"])
        server.send_message(msg)
        server.quit()

        if draft_id:
            update_draft_status(
                draft_id,
                status="sent",
                body=body,
                subject=subject,
                recipient_email=to_clean
            )

        return {
            "ok": True,
            "mode": "smtp",
            "status": "sent",
            "recipient": to_clean,
            "message": f"Proposal automatically delivered to {to_clean} via {cfg['host']} with copy to {operator_email}."
        }
    except Exception as e:
        if draft_id:
            update_draft_status(
                draft_id,
                status="draft",
                body=body,
                subject=subject,
                recipient_email=to_clean
            )
        return {
            "ok": False,
            "error": f"SMTP dispatch failed: {str(e)}",
            **webmail_links
        }


def send_autopilot_dispatch_alert(
    opp: Dict[str, Any],
    demo: Dict[str, Any],
    draft: Dict[str, Any],
    send_res: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format and send an immediate email update to the operator whenever an autopilot run executes.
    """
    company = opp.get("company", "Client")
    title = opp.get("title", "Role")
    recipient = draft.get("recipient_email") or send_res.get("recipient") or "Not found publicly"
    demo_url = demo.get("demo_url", "https://bieai.vercel.app")
    mode = send_res.get("mode", "queued")
    status = send_res.get("status", "pending")

    status_tag = "DELIVERED via SMTP" if mode == "smtp" else "READY FOR 1-CLICK DISPATCH"
    subject = f"[{status_tag}] Application: {company} | {title} (Fit: {opp.get('fit_score', 85)}%)"

    text_body = f"""ABRAHAMIC OPPORTUNITIES ENGINE AUTONOMOUS APPLICATION UPDATE

Opportunity: {company} - {title}
Fit Score: {opp.get('fit_score', 85)}% ({opp.get('fit_tag', 'Good fit')})
Target Influx / Budget: {opp.get('budget', '$2k - $5k/mo')}
Job Posting URL: {opp.get('url', '#')}

=== BESPOKE PROTOTYPE ===
Title: {demo.get('title', 'Tailored Product')}
Live Vercel URL: {demo_url}
GitHub Repo: https://github.com/Stghost1/BIEAI/blob/main/{demo.get('file_name', '')}

=== RECIPIENT & STATUS ===
Hiring Contact: {recipient}
Dispatch Status: {status} ({mode})
System Telemetry: {send_res.get('message', 'Processed successfully')}

=== PROPOSAL SUMMARY ===
Subject: {draft.get('subject', '')}

{draft.get('body', '')}

=== 1-CLICK WEBMAIL DISPATCH (IF NEEDED) ===
Gmail: {send_res.get('gmail_url', 'N/A')}
Outlook: {send_res.get('outlook_url', 'N/A')}
"""

    html_body = f"""<!DOCTYPE html>
<html>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; background:#0f172a; color:#f8fafc; padding:24px; margin:0;">
  <div style="max-width:600px; margin:0 auto; background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden;">
    <div style="background:#0284c7; padding:20px 24px;">
      <span style="font-size:11px; text-transform:uppercase; letter-spacing:0.08em; color:#e0f2fe; font-weight:700;">Abrahamic Opportunities Engine</span>
      <h2 style="margin:4px 0 0; color:#ffffff; font-size:20px;">{status_tag}</h2>
    </div>
    <div style="padding:24px;">
      <h3 style="margin:0 0 8px; color:#ffffff; font-size:18px;">{company} &bull; {title}</h3>
      <div style="display:inline-block; background:#0369a1; color:#e0f2fe; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:700; margin-bottom:16px;">
        {opp.get('fit_score', 85)}% Match &bull; {opp.get('budget', '$2k - $5k/mo')}
      </div>

      <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:16px; margin-bottom:20px;">
        <div style="font-size:12px; color:#94a3b8; text-transform:uppercase; margin-bottom:6px; font-weight:700;">Live Prototype Engineered:</div>
        <div style="font-size:15px; font-weight:700; color:#38bdf8; margin-bottom:8px;">{demo.get('title', 'Tailored Product')}</div>
        <a href="{demo_url}" target="_blank" style="display:inline-block; background:#38bdf8; color:#0f172a; text-decoration:none; padding:8px 16px; border-radius:6px; font-weight:700; font-size:13px;">View Live Prototype &rarr;</a>
      </div>

      <div style="margin-bottom:20px;">
        <div style="font-size:12px; color:#94a3b8; text-transform:uppercase; margin-bottom:6px; font-weight:700;">Recipient:</div>
        <div style="font-size:14px; color:#f8fafc;">{recipient}</div>
      </div>

      <div style="margin-bottom:20px;">
        <div style="font-size:12px; color:#94a3b8; text-transform:uppercase; margin-bottom:6px; font-weight:700;">Proposal Subject:</div>
        <div style="font-size:14px; color:#38bdf8; font-weight:600;">{draft.get('subject', '')}</div>
      </div>

      <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:16px; font-size:13px; color:#cbd5e1; line-height:1.6; white-space:pre-wrap; margin-bottom:20px;">
{draft.get('body', '')}
      </div>

      <div style="border-top:1px solid #334155; padding-top:16px; display:flex; gap:12px;">
        <a href="{send_res.get('gmail_url', '#')}" target="_blank" style="background:#ef4444; color:#ffffff; text-decoration:none; padding:8px 14px; border-radius:6px; font-size:12px; font-weight:700;">Open in Gmail</a>
        <a href="{send_res.get('outlook_url', '#')}" target="_blank" style="background:#0284c7; color:#ffffff; text-decoration:none; padding:8px 14px; border-radius:6px; font-size:12px; font-weight:700;">Open in Outlook</a>
      </div>
    </div>
  </div>
</body>
</html>
"""

    return send_operator_notification(subject, text_body, html_body)


def send_leads_digest_alert(opportunities: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Send an executive digest of newly scanned high-fit leads to the operator's email.
    """
    if opportunities is None:
        opportunities = get_opportunities(min_score=80, limit=10)

    operator_email = get_operator_email()
    count = len(opportunities)
    subject = f"[Leads Digest] {count} High-Fit Opportunities Available (Abrahamic Opportunities Engine)"

    lines = [
        f"ABRAHAMIC OPPORTUNITIES ENGINE REAL-TIME LEADS DIGEST",
        f"Operator: {operator_email}",
        f"Qualified Leads Identified: {count}",
        "",
        "=== TOP OPPORTUNITIES ==="
    ]

    html_items = []
    for opp in opportunities[:10]:
        lines.append(f"• {opp.get('company')} | {opp.get('title')} | Fit: {opp.get('fit_score')}% | {opp.get('budget', '$2k - $5k/mo')}")
        lines.append(f"  URL: {opp.get('url', '#')}")
        lines.append("")

        html_items.append(f"""
        <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:14px; margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <div style="font-size:15px; font-weight:700; color:#ffffff;">{opp.get('title')}</div>
              <div style="font-size:13px; color:#38bdf8; font-weight:600;">{opp.get('company')} &bull; {opp.get('source', 'Web')}</div>
            </div>
            <div style="background:#0369a1; color:#e0f2fe; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
              {opp.get('fit_score')}% Fit
            </div>
          </div>
          <div style="font-size:12px; color:#94a3b8; margin:8px 0 10px;">{opp.get('budget', '$2k - $5k/mo')} &bull; {opp.get('seniority', 'Senior/Junior')} &bull; {opp.get('job_type', 'Full-time')}</div>
          <a href="{opp.get('url', '#')}" target="_blank" style="color:#38bdf8; font-size:12px; text-decoration:none; font-weight:600;">View Opportunity Posting &rarr;</a>
        </div>
        """)

    text_body = "\n".join(lines)
    html_body = f"""<!DOCTYPE html>
<html>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; background:#0f172a; color:#f8fafc; padding:24px; margin:0;">
  <div style="max-width:600px; margin:0 auto; background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden;">
    <div style="background:#0284c7; padding:20px 24px;">
      <span style="font-size:11px; text-transform:uppercase; letter-spacing:0.08em; color:#e0f2fe; font-weight:700;">Abrahamic Opportunities Engine</span>
      <h2 style="margin:4px 0 0; color:#ffffff; font-size:20px;">{count} High-Fit Opportunities Available</h2>
    </div>
    <div style="padding:24px;">
      <p style="margin:0 0 16px; color:#cbd5e1; font-size:14px;">Here are your top qualified job signals prioritized by ATS match and revenue potential:</p>
      {''.join(html_items)}
      <div style="text-align:center; padding-top:16px; border-top:1px solid #334155;">
        <a href="http://127.0.0.1:4174" target="_blank" style="display:inline-block; background:#0284c7; color:#ffffff; text-decoration:none; padding:10px 20px; border-radius:6px; font-weight:700; font-size:14px;">Open Live Dashboard &rarr;</a>
      </div>
    </div>
  </div>
</body>
</html>
"""

    return send_operator_notification(subject, text_body, html_body)
