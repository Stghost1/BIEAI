"""
B.I.E.AI Automated Email Dispatch Engine.
Handles direct TLS SMTP delivery (Gmail App Password, Sendgrid, Custom SMTP)
with zero-configuration fallback to 1-click webmail dispatch (Gmail Web & Outlook).
"""

from __future__ import annotations

import email.message
import os
import re
import smtplib
from typing import Any, Dict, Optional
from urllib.parse import quote

from core.db import get_setting, update_draft_status


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
    from_name = get_setting("smtp_from_name", os.environ.get("SMTP_FROM_NAME", "Emmanuel Pelumi Bamidele (Bamsemma)")).strip()

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
            "error": "Username and password/app-password are required."
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
        return {
            "ok": False,
            "error": f"SMTP connection failed: {str(e)}"
        }


def send_proposal_email(
    to_email: str,
    subject: str,
    body: str,
    draft_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Primary email dispatcher:
    1. If SMTP is configured, dispatches via smtplib with TLS.
    2. If SMTP is not yet configured, marks draft as queued and returns pre-formatted webmail links.
    """
    to_clean = (to_email or "").strip()
    webmail_links = build_webmail_links(to_clean, subject, body)

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
            "message": f"Proposal automatically delivered to {to_clean} via {cfg['host']}."
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
