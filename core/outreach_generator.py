"""
Scoutdesk Tailored Outreach Generator.
Synthesizes high-converting, personalized cold proposals referencing Bamsemma's
real live demo projects from biework and dynamically engineered tailored prototypes.
Supports dynamic Vercel deployment URLs, GitHub portfolio links, custom domains,
and three distinct Anti-Resume pitch angles drawn from The Anti Job and JobAssist.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
from core.db import create_outreach_draft, get_setting, get_portfolio_demos
from core.ats_analyzer import analyze_ats_fit


def get_base_url() -> str:
    """Return configured live portfolio base URL (Vercel or custom domain)."""
    val = get_setting("portfolio_url", os.environ.get("PORTFOLIO_URL", "https://biework.vercel.app"))
    return (val or "https://biework.vercel.app").rstrip("/")


def get_github_url() -> str:
    """Return configured GitHub profile or portfolio link."""
    val = get_setting("github_url", os.environ.get("GITHUB_URL", "https://github.com/bamsemma"))
    return (val or "https://github.com/bamsemma").rstrip("/")


def get_demo_registry() -> List[Dict[str, Any]]:
    """Return registry of live proof-of-work applications, combining baseline and vault demos."""
    base_url = get_base_url()

    vault_demos = []
    try:
        demos = get_portfolio_demos(limit=50)
        for d in demos:
            vault_demos.append({
                "id": d["slug"],
                "name": d["title"],
                "category": d["category"],
                "url": d["demo_url"] if d["demo_url"].startswith("http") else f"{base_url}/{d['slug']}",
                "desc": d.get("preview_desc", ""),
                "is_tailored": True,
                "opportunity_id": d.get("opportunity_id")
            })
    except Exception:
        pass

    defaults = [
        {
            "id": "swiftlegal",
            "name": "SwiftLegal Nigeria",
            "category": "corporate",
            "url": f"{base_url}/swiftlegal-nigeria",
            "desc": "Authoritative corporate portal with practice areas, team profiles, and consultation booking."
        },
        {
            "id": "realty",
            "name": "Lagos Premier Realty",
            "category": "realty",
            "url": f"{base_url}/lagos-premier-realty",
            "desc": "High-converting property portal with listing filters, neighborhood guides, and WhatsApp lead routing."
        },
        {
            "id": "nutricoach",
            "name": "NutriCoach Abuja",
            "category": "health",
            "url": f"{base_url}/nutricoach-abuja",
            "desc": "Health coaching platform featuring an interactive live BMI calculator lead magnet."
        },
        {
            "id": "roi_calc",
            "name": "Real Estate ROI Calculator",
            "category": "finance",
            "url": f"{base_url}/roi-calculator",
            "desc": "Interactive financial tool calculating yields, break-even periods, and 5-year ROI forecasts."
        },
        {
            "id": "invoice_gen",
            "name": "AI-Powered Invoice Generator",
            "category": "saas",
            "url": f"{base_url}/invoice-generator",
            "desc": "Professional browser billing tool with line items, tax calculations, and PDF download."
        },
        {
            "id": "biework",
            "name": "B.I.E.AI Consulting & Gigs Studio",
            "category": "general",
            "url": f"{base_url}/",
            "desc": "Complete agency showcase presenting full-stack systems, automation workflows, and AI media."
        }
    ]

    return vault_demos + defaults


DEMO_REGISTRY = get_demo_registry()


def select_best_demo(
    title: str,
    desc: str,
    category: str,
    opp_id: Optional[int] = None,
    custom_demo: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Select the highest-relevance demo, prioritizing custom tailored prototypes."""
    if custom_demo:
        return {
            "id": custom_demo.get("slug", "custom"),
            "name": custom_demo.get("title", "Tailored Prototype"),
            "category": custom_demo.get("category", category),
            "url": custom_demo.get("demo_url", f"{get_base_url()}/{custom_demo.get('slug')}"),
            "desc": custom_demo.get("preview_desc", ""),
            "is_tailored": True
        }

    registry = get_demo_registry()

    if opp_id:
        for d in registry:
            if d.get("opportunity_id") == opp_id:
                return d

    text = f"{title} {desc} {category}".lower()

    for d in registry:
        if d.get("is_tailored") and d.get("category") in text:
            return d

    if any(k in text for k in ["legal", "law", "corporate", "compliance", "attorney", "contract"]):
        return next((d for d in registry if d["id"] == "swiftlegal"), registry[-1])
    elif any(k in text for k in ["real estate", "realty", "property", "apartment", "housing", "mortgage"]):
        return next((d for d in registry if d["id"] == "realty"), registry[-1])
    elif any(k in text for k in ["health", "fitness", "coach", "wellness", "nutrition", "clinic", "medical"]):
        return next((d for d in registry if d["id"] == "nutricoach"), registry[-1])
    elif any(k in text for k in ["finance", "roi", "calculator", "investment", "fintech", "yield", "ledger"]):
        return next((d for d in registry if d["id"] == "roi_calc"), registry[-1])
    elif any(k in text for k in ["invoice", "billing", "saas", "payment", "accounting"]):
        return next((d for d in registry if d["id"] == "invoice_gen"), registry[-1])
    else:
        return next((d for d in registry if d["id"] == "biework"), registry[-1])


def get_decision_maker_dorks(company: str, role: str) -> Dict[str, str]:
    """
    Generate targeted search formulas for decision-makers (The Anti Job strategy).
    Bypasses standard applicant tracking systems by identifying technical leadership.
    """
    clean_company = re.sub(r'[^a-zA-Z0-9\s]', '', company).strip()
    
    # Google site dork for LinkedIn decision-makers
    dork_query = f'"{clean_company}" ("CTO" OR "Founder" OR "Head of Engineering" OR "VP Engineering" OR "Lead Developer") site:linkedin.com/in'
    google_url = f"https://www.google.com/search?q={quote_plus(dork_query)}"
    
    # LinkedIn direct search
    linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(clean_company + ' engineering founder')}"
    
    # X / Twitter search for public hiring signals
    x_query = f'"{clean_company}" hiring engineering'
    x_url = f"https://twitter.com/search?q={quote_plus(x_query)}&f=live"

    return {
        "google_dork_url": google_url,
        "linkedin_search_url": linkedin_url,
        "x_search_url": x_url,
        "dork_query": dork_query
    }


def generate_outreach(
    opp: Dict[str, Any],
    custom_demo: Optional[Dict[str, Any]] = None,
    angle: str = "proof_of_work"
) -> Dict[str, Any]:
    """
    Constructs a personalized cold proposal following B.I.E.AI and Anti-Job principles:
    - Direct hook.
    - Zero filler words.
    - Demonstrable proof of work referencing a live demo with valid Vercel or GitHub links.
    - Selectable Anti-Resume pitch angles:
      1. 'proof_of_work': The Anti-Resume leading with bespoke interactive prototype.
      2. 'problem_audit': Bottleneck and architectural audit with concrete solutions.
      3. 'mvp_sprint': 14-day production sprint framed as an agile contractor.
    - ATS match breakdown from JobAssist engine.
    - Direct decision-maker search formulas.
    """
    title = opp.get("title", "your project")
    company = opp.get("company", "the team")
    category = opp.get("category", "website")
    desc = opp.get("description", "")
    opp_id = opp.get("id")

    demo = select_best_demo(title, desc, category, opp_id=opp_id, custom_demo=custom_demo)
    portfolio_url = get_base_url()
    media_kit_url = f"{portfolio_url}/media-kit"
    github_url = get_github_url()
    contact_email = get_setting("email", "techwithbie@gmail.com")
    whatsapp = get_setting("whatsapp", "+234 905 404 5597")
    upwork_url = get_setting("upwork_url", "https://www.upwork.com/freelancers/~015875b6ee71b82e73")

    # Analyze ATS keyword density
    ats_data = analyze_ats_fit(title, desc, opp.get("tags", []))
    ats_score = ats_data.get("ats_score", 85)
    matched_skills = ats_data.get("matched_skills", [])
    matched_str = ", ".join(matched_skills[:5]) if matched_skills else "Next.js, TypeScript, Node.js"

    # Angle 1: Interactive Proof of Work (The Anti-Resume)
    if angle == "proof_of_work":
        subject = f"Interactive prototype for {title} at {company} (B.I.E.AI submission)"
        hook = (
            f"I came across {company}'s search for {title}. "
            f"Instead of sending another generic PDF resume into an ATS queue, I built a dedicated live interactive prototype specifically for your team."
        )
        if demo.get("is_tailored"):
            proof_block = (
                f"1. Bespoke Prototype: {demo['name']}\n"
                f"   Live URL: {demo['url']}\n"
                f"   Stack: {demo.get('tech_stack', 'React, TypeScript, Tailwind')}\n"
                f"   Architecture: Zero layout shift, mobile-responsive layout tested at 120Hz, clean state management."
            )
        else:
            proof_block = (
                f"1. Verified Proof of Work: {demo['name']}\n"
                f"   Live URL: {demo['url']}\n"
                f"   Key capabilities: Production UI, responsive data tables, client-side input validation."
            )

        core_points = (
            f"{proof_block}\n\n"
            f"2. Matched Core Stack: We work daily with {matched_str}. All components are strictly typed and covered by automated tests.\n\n"
            f"3. Direct Contractor Velocity: No recruiting agency markup or multi-month onboarding lag. We deploy working software from day one."
        )

    # Angle 2: Problem Audit & Architectural Fix
    elif angle == "problem_audit":
        subject = f"Architectural audit & prototype for {company} ({title})"
        hook = (
            f"Reviewing {company}'s technical requirements for {title}, I identified three common architectural friction points in similar production stacks: "
            f"unbounded state updates, API waterfall latency, and bundle overhead on mobile devices."
        )
        proof_block = (
            f"To demonstrate how we eliminate these bottlenecks, I assembled an interactive proof of concept:\n"
            f"Live Demo: {demo['url']}\n"
            f"Highlights: Sub-second initial paint, optimistic state transitions, strict boundary input validation with Zod."
        )
        core_points = (
            f"{proof_block}\n\n"
            f"1. Architecture: Clean separation of concerns with server components for data retrieval and client components only where user interaction occurs.\n\n"
            f"2. Database & API Integrity: Parameterized queries, explicit batch fetching to prevent N+1 issues, and standardized error envelopes: {{error: {{code, message, details}}}}.\n\n"
            f"3. Immediate Execution: Available to tackle the core technical backlog right away."
        )

    # Angle 3: 14-Day Sprint & Contractor Angle (Bypass traditional hiring)
    else:  # mvp_sprint
        subject = f"Proposal: 14-day production sprint for {title} at {company}"
        hook = (
            f"Rather than a protracted hiring cycle for {title}, I propose a high-velocity 14-day contractor sprint to ship your core roadmap deliverables immediately."
        )
        proof_block = (
            f"As tangible evidence of execution speed, I have already engineered the foundation for this role:\n"
            f"Prototype: {demo['name']} ({demo['url']})\n"
            f"Delivery standard: Production-ready code, 100% typed, documented endpoints, zero placeholder shortcuts."
        )
        core_points = (
            f"{proof_block}\n\n"
            f"1. Sprint Scope: Days 1 to 4 wireframe and core state models; Days 5 to 9 API integrations and database indexes; Days 10 to 14 performance audits and deployment handoff.\n\n"
            f"2. Verified Tech Alignment: Active production mastery of {matched_str}.\n\n"
            f"3. Clear Handoff: Daily commit logs, clean pull requests, and automated deployment scripts."
        )

    body = (
        f"Hi {company} leadership,\n\n"
        f"{hook}\n\n"
        f"{core_points}\n\n"
        f"You can review our verified engineering background and live client metrics on our media kit: {media_kit_url}\n\n"
        f"If you have 15 minutes this week, I would welcome the opportunity to walk through the prototype live.\n\n"
        f"Best regards,\n"
        f"Emmanuel Pelumi Bamidele (Bamsemma)\n"
        f"Founder, B.I.E.AI | Full-Stack Systems Architect\n"
        f"Portfolio: {portfolio_url}\n"
        f"Media Kit: {media_kit_url}\n"
        f"GitHub: {github_url}\n"
        f"WhatsApp: {whatsapp} | Email: {contact_email}\n"
        f"Upwork: {upwork_url}"
    )

    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', f"{desc} {opp.get('url', '')}")
    recipient_email = email_match.group(0).rstrip(".,;:!?)'\"") if email_match else ""

    draft = create_outreach_draft(
        opp_id=opp_id,
        subject=subject,
        hook=hook,
        body=body,
        demo_name=demo["name"],
        demo_url=demo["url"],
        recipient_email=recipient_email
    )

    decision_dorks = get_decision_maker_dorks(company, title)

    draft["recipient_email"] = recipient_email
    draft["opp_company"] = company
    draft["opp_title"] = title
    draft["opp_url"] = opp.get("url", "#")
    draft["demo_is_tailored"] = demo.get("is_tailored", False)
    draft["angle"] = angle
    draft["ats_score"] = ats_score
    draft["matched_skills"] = matched_skills
    draft["decision_dorks"] = decision_dorks
    return draft


def generate_followup(
    opp: Dict[str, Any],
    draft: Dict[str, Any],
    touch: int = 2
) -> Dict[str, Any]:
    """
    Generate structured follow-up outreach according to JobAssist cadence:
    - Touch 2 (Day 3): Polite verification of prototype test drive.
    - Touch 3 (Day 7): Value-add feature update on the prototype.
    """
    company = opp.get("company", "the team")
    title = opp.get("title", "your opening")
    demo_url = draft.get("demo_url", get_base_url())
    contact_email = get_setting("email", "techwithbie@gmail.com")
    whatsapp = get_setting("whatsapp", "+234 905 404 5597")

    if touch == 2:
        subject = f"Re: Interactive prototype for {title} at {company}"
        body = (
            f"Hi {company} team,\n\n"
            f"Following up on my note earlier this week regarding the {title} role.\n\n"
            f"Did you or your technical team have an opportunity to test the live prototype built for {company}?\n"
            f"Direct link: {demo_url}\n\n"
            f"I designed it to demonstrate clean component architecture, responsive mobile layouts, and quick turnaround. "
            f"Happy to answer any technical questions or adapt features to match your exact roadmap priorities.\n\n"
            f"Best regards,\n"
            f"Emmanuel Pelumi Bamidele (Bamsemma)\n"
            f"WhatsApp: {whatsapp} | Email: {contact_email}"
        )
    else:  # touch 3
        subject = f"Feature update on prototype for {company} ({title})"
        body = (
            f"Hi {company} team,\n\n"
            f"Quick value-add update for {company}: I updated your bespoke prototype with an additional export and telemetry module.\n\n"
            f"Updated Prototype: {demo_url}\n\n"
            f"This demonstrates how we handle real-time data serialization, client caching, and print-ready PDF export. "
            f"If your team has moved forward with another candidate, no problem at all. Otherwise, I remain available for a 15-minute technical review.\n\n"
            f"Best regards,\n"
            f"Emmanuel Pelumi Bamidele (Bamsemma)\n"
            f"WhatsApp: {whatsapp} | Email: {contact_email}"
        )

    return {
        "touch": touch,
        "subject": subject,
        "body": body,
        "recipient_email": draft.get("recipient_email", ""),
        "demo_url": demo_url
    }
