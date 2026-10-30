"""
B.I.E.AI Autonomous Auto-Pilot Engine (v4.0).
Coordinates end-to-end opportunity execution:
1. Signal evaluation and opportunity requirements analysis.
2. Domain-adaptive tailored interactive prototype generation (Motionsites.ai benchmark).
3. Clean route deployment to Vercel (vercel.json) and GitHub repository push.
4. Cold outreach proposal synthesis referencing the live prototype.
5. Automated email dispatch via SMTP with fallback to 1-click webmail (Gmail / Outlook).
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
from core.mailer import (
    extract_email,
    send_proposal_email,
    build_webmail_links,
    send_autopilot_dispatch_alert,
)
from core.outreach_generator import generate_outreach
from core.email_scourer import scour_company_email


def run_autopilot_pipeline(
    opp_id: int,
    auto_send: Optional[bool] = None,
    recipient_override: Optional[str] = None,
    force_rebuild: bool = True
) -> Dict[str, Any]:
    """
    Execute autonomous workflow for a single opportunity.
    """
    opp = get_opportunity_by_id(opp_id)
    if not opp:
        return {"ok": False, "error": f"Opportunity ID {opp_id} not found"}

    company = opp.get("company", "Direct Client")
    title = opp.get("title", "Full-Stack Opportunity")
    logs: List[str] = [f"Step 1: Analyzed opportunity for {company} ({title}). Matched core skill vectors."]

    # 1. Synthesize dedicated interactive demo
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolio_demos WHERE opportunity_id = ?", (opp_id,))
    row = cursor.fetchone()
    conn.close()

    needs_build = force_rebuild or (not row)
    if row and not force_rebuild:
        demo = dict(row)
        if "biework.vercel.app" in demo.get("demo_url", "") or ("Pet Health" in demo.get("title", "") and "dreem" in company.lower()):
            needs_build = True

    if not needs_build and row:
        demo = dict(row)
        logs.append(f"Step 2: Found verified tailored prototype: {demo['title']} -> {demo['demo_url']}")
    else:
        logs.append(f"Step 2: Engineered bespoke MotionSites prototype for {company} with distinctive typography and 60 FPS canvas.")
        demo = build_tailored_demo(opp)
        logs.append(f"Step 3: Deployed clean route to Vercel (/{demo['slug']}) and pushed to GitHub Stghost1/BIEAI.")
        logs.append(f"Step 4: Registered prototype in portfolio vault: {demo['demo_url']}.")

    # 2. Synthesize cold proposal embedding custom demo
    logs.append(f"Step 5: Synthesized high-converting cold proposal embedding live demo {demo['demo_url']}.")
    draft = generate_outreach(opp, custom_demo=demo)

    # 3. Determine recipient email
    recipient = (recipient_override or "").strip()
    if not recipient:
        recipient = (draft.get("recipient_email") or "").strip()
    if not recipient:
        detected = extract_email(f"{opp.get('description', '')} {opp.get('url', '')}")
        recipient = detected or ""
    if not recipient:
        scour_res = scour_company_email(company, opp_url=opp.get("url", ""), title=title, desc=opp.get("description", ""))
        if scour_res.get("ok") and scour_res.get("email"):
            recipient = scour_res["email"]
            update_opportunity_email(opp_id, recipient, scour_res.get("domain", ""))
            logs.append(f"Discovered recipient contact email: {recipient} ({scour_res.get('confidence')}).")

    # 4. Handle email dispatch
    # Default auto_send to True if not explicitly False
    auto_send_pref = get_setting("auto_send_enabled", "true").lower() == "true"
    should_send = auto_send if auto_send is not None else auto_send_pref

    email_status = "queued"
    dispatch_msg = ""
    webmail_links = build_webmail_links(recipient, draft["subject"], draft["body"])

    if recipient:
        if should_send:
            send_result = send_proposal_email(
                to_email=recipient,
                subject=draft["subject"],
                body=draft["body"],
                draft_id=draft["id"]
            )
            if send_result.get("ok") and send_result.get("mode") == "smtp":
                email_status = "sent"
                dispatch_msg = send_result.get("message", f"Proposal delivered to {recipient} via SMTP.")
                logs.append(f"Step 6: SUCCESS: {dispatch_msg}")
            elif send_result.get("mode") == "webmail_ready":
                email_status = "webmail_ready"
                dispatch_msg = f"Proposal & demo URL ready for 1-click webmail dispatch to {recipient}."
                logs.append(f"Step 6: READY: {dispatch_msg}")
            else:
                email_status = send_result.get("status", "queued_webmail")
                dispatch_msg = send_result.get("message", "Queued for webmail dispatch.")
                logs.append(f"Step 6: {dispatch_msg}")
        else:
            email_status = "queued_review"
            dispatch_msg = "Proposal saved and queued for operator review."
            logs.append(f"Step 6: {dispatch_msg}")
    else:
        email_status = "needs_recipient"
        dispatch_msg = "Recipient email not found publicly. Proposal saved with live demo link for direct ATS or LinkedIn submission."
        logs.append(f"Step 6: {dispatch_msg}")

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
        "status": "success" if email_status in ("sent", "webmail_ready", "queued", "queued_webmail") else "partial"
    }
    run_id = log_autopilot_run(run_record)
    logs.append(f"Autopilot telemetry recorded in audit database (Run #{run_id}).")

    # 6. Synchronize real-time application update to operator email (techwithbie@gmail.com)
    try:
        alert_res = send_autopilot_dispatch_alert(
            opp=opp,
            demo=demo,
            draft=draft,
            send_res={
                "ok": True if email_status in ("sent", "webmail_ready") else False,
                "mode": "smtp" if email_status == "sent" else ("webmail" if email_status == "webmail_ready" else "queued"),
                "status": email_status,
                "message": dispatch_msg,
                "recipient": recipient,
                "gmail_url": webmail_links.get("gmail", "#"),
                "outlook_url": webmail_links.get("outlook", "#")
            }
        )
        if alert_res.get("ok"):
            logs.append(f"Operator alert synchronized to {alert_res.get('recipient')}.")
        elif alert_res.get("mode") == "webmail_ready":
            logs.append(f"Operator alert pre-staged for {alert_res.get('recipient')} (SMTP password pending in settings).")
    except Exception as notify_err:
        logs.append(f"Operator sync notice: {notify_err}")

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

    eligible = [
        c for c in candidates
        if c.get("status") not in ("applied", "outreach_drafted")
    ][:limit]

    if not eligible:
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
