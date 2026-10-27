"""
B.I.E.AI Autonomous Auto-Pilot Engine.
Coordinates end-to-end opportunity execution:
1. Signal evaluation and opportunity requirements analysis.
2. Domain-adaptive tailored interactive prototype generation.
3. Clean route deployment to Vercel (vercel.json) and portfolio vault registration.
4. Cold outreach proposal synthesis referencing the live prototype.
5. Automated email dispatch via SMTP with fallback to 1-click webmail.
6. Execution auditing and telemetry tracking.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from core.db import (
    get_connection,
    get_opportunity_by_id,
    get_opportunities,
    get_setting,
    log_autopilot_run,
    get_portfolio_demos,
    update_opportunity_email,
)
from core.demo_builder import build_tailored_demo
from core.mailer import extract_email, send_proposal_email, build_webmail_links
from core.outreach_generator import generate_outreach
from core.email_scourer import scour_company_email


def run_autopilot_pipeline(
    opp_id: int,
    auto_send: Optional[bool] = None,
    recipient_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute autonomous workflow for a single opportunity.
    """
    opp = get_opportunity_by_id(opp_id)
    if not opp:
        return {"ok": False, "error": f"Opportunity ID {opp_id} not found"}

    company = opp.get("company", "Direct Client")
    title = opp.get("title", "Full-Stack Opportunity")
    logs: List[str] = [f"Initiating B.I.E.AI Auto-Pilot for {company} ({title})."]

    # 1. Check or build tailored interactive demo
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolio_demos WHERE opportunity_id = ?", (opp_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        demo = dict(row)
        logs.append(f"Found existing tailored prototype in vault: {demo['title']} -> {demo['demo_url']}")
    else:
        logs.append(f"Synthesizing dedicated interactive prototype for {company}...")
        demo = build_tailored_demo(opp)
        logs.append(f"Tailored prototype created: {demo['title']}")
        logs.append(f"Live route registered in vercel.json: /{demo['slug']}")
        logs.append(f"Appended to permanent portfolio vault: {demo['demo_url']}")

    # 2. Synthesize cold proposal embedding custom demo
    logs.append("Synthesizing high-converting cold proposal referencing custom prototype...")
    draft = generate_outreach(opp, custom_demo=demo)
    logs.append(f"Proposal draft ready: '{draft['subject']}'")

    # 3. Determine recipient email
    recipient = (recipient_override or "").strip()
    if not recipient:
        recipient = (draft.get("recipient_email") or "").strip()
    if not recipient:
        detected = extract_email(f"{opp.get('description', '')} {opp.get('url', '')}")
        recipient = detected or ""
    if not recipient:
        logs.append(f"Scouring public contact endpoints and DNS MX servers for {company}...")
        scour_res = scour_company_email(company, opp_url=opp.get("url", ""), title=title, desc=opp.get("description", ""))
        if scour_res.get("ok") and scour_res.get("email"):
            recipient = scour_res["email"]
            update_opportunity_email(opp_id, recipient, scour_res.get("domain", ""))
            logs.append(f"Discovered recipient email: {recipient} ({scour_res.get('confidence')})")

    # 4. Handle email dispatch
    auto_send_pref = get_setting("auto_send_enabled", "false").lower() == "true"
    should_send = auto_send if auto_send is not None else auto_send_pref

    email_status = "queued"
    dispatch_msg = ""
    webmail_links = build_webmail_links(recipient, draft["subject"], draft["body"])

    if should_send and recipient:
        logs.append(f"Attempting automated SMTP dispatch to {recipient}...")
        send_result = send_proposal_email(
            to_email=recipient,
            subject=draft["subject"],
            body=draft["body"],
            draft_id=draft["id"]
        )
        if send_result.get("ok") and send_result.get("mode") == "smtp":
            email_status = "sent"
            dispatch_msg = send_result.get("message", "Dispatched via SMTP")
            logs.append(f"SUCCESS: {dispatch_msg}")
        else:
            email_status = send_result.get("status", "queued_webmail")
            dispatch_msg = send_result.get("message", "Queued for webmail")
            logs.append(f"NOTE: {dispatch_msg}")
    elif not recipient:
        email_status = "needs_recipient"
        dispatch_msg = "No destination email detected in job post. Draft saved for manual send."
        logs.append(dispatch_msg)
    else:
        email_status = "queued"
        dispatch_msg = "Proposal saved and queued for review (Auto-send disabled in settings)."
        logs.append(dispatch_msg)

    # 5. Record run in autopilot audit log
    run_record = {
        "opportunity_id": opp_id,
        "company": company,
        "job_title": title,
        "demo_slug": demo.get("slug", ""),
        "demo_url": demo.get("demo_url", ""),
        "recipient_email": recipient,
        "email_status": email_status,
        "proposal_subject": draft["subject"],
        "log_messages": "\n".join(logs),
        "status": "success" if email_status in ("sent", "queued", "queued_webmail") else "partial"
    }
    run_id = log_autopilot_run(run_record)
    logs.append(f"Autopilot run recorded in audit database (Run #{run_id}).")

    return {
        "ok": True,
        "run_id": run_id,
        "company": company,
        "title": title,
        "demo": demo,
        "draft": draft,
        "recipient": recipient,
        "email_status": email_status,
        "dispatch_message": dispatch_msg,
        "webmail_links": webmail_links,
        "logs": logs
    }


def batch_autopilot(
    limit: int = 3,
    min_fit: int = 80,
    auto_send: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Execute autonomous workflow for the top qualifying opportunities.
    """
    candidates = get_opportunities(min_score=min_fit, limit=limit * 3)

    # Filter for new or unapplied opportunities
    eligible = [
        c for c in candidates
        if c.get("status") not in ("applied", "outreach_drafted")
    ][:limit]

    if not eligible:
        # If none unapplied, take top candidates by score
        eligible = candidates[:limit]

    results = []
    for item in eligible:
        try:
            res = run_autopilot_pipeline(item["id"], auto_send=auto_send)
            results.append(res)
        except Exception as e:
            results.append({
                "ok": False,
                "opportunity_id": item["id"],
                "company": item.get("company", "Unknown"),
                "error": str(e)
            })

    return {
        "ok": True,
        "count": len(results),
        "results": results
    }
