"""
The Anti-Job Strategy Engine & Decision-Maker Playbook.
Formulates the tactical principles drawn from The Anti Job (theantijob)
to bypass HR applicant tracking systems, identify technical leadership,
and pitch tailored proof-of-work prototypes directly to decision-makers.
"""

from __future__ import annotations

from typing import Any, Dict, List


def get_antijob_playbook() -> Dict[str, Any]:
    """
    Returns structured operational chapters of the Anti-Job cold outreach methodology.
    """
    return {
        "title": "The Anti-Job Field Operating Playbook",
        "subtitle": "Bypass ATS Black Holes & Win High-Value Contracts with Unsolicited Proof of Work",
        "version": "2.0",
        "principles": [
            "Never compete in a queue of 300+ generic resumes.",
            "Build working software before asking for a conversation.",
            "Address technical decision-makers directly: Founders, CTOs, and VPs of Engineering.",
            "Frame yourself as an agile contractor who eliminates hiring lag.",
            "Use multi-touch cadences: proof of work, quick verification, and value-add update."
        ],
        "chapters": [
            {
                "id": "ch1",
                "number": "01",
                "title": "The ATS Black Hole vs Direct Decision-Maker Outreach",
                "summary": "Why submitting resumes through job boards yields less than 2% conversion.",
                "content": (
                    "When a venture-backed startup or remote tech company posts a role on RemoteOK or Jobicy, "
                    "applicant tracking systems (ATS) receive hundreds of automated submissions. HR screeners lack "
                    "the technical discernment to recognize architecture quality and rely on simplistic keyword filters. "
                    "By contrast, reaching out directly to the CTO or Founder with a dedicated interactive prototype "
                    "skips the entire recruiter queue and positions you as a peer engineer solving their immediate backlog."
                )
            },
            {
                "id": "ch2",
                "number": "02",
                "title": "The Unsolicited Prototype Weapon",
                "summary": "How a bespoke Vercel demo converts cold outreach at 30% to 45%.",
                "content": (
                    "Talk is cheap and resumes are easily exaggerated. When a founder receives an email linking to a live, "
                    "fully responsive prototype built specifically for their company with their brand typography, color palette, "
                    "and business logic, the reaction changes from 'another applicant' to 'this person is already doing the work'. "
                    "Our autonomous engine synthesizes domain-adaptive prototypes within seconds, registering clean routes "
                    "on Vercel (e.g. biework.vercel.app/demo-company-slug) to provide irrefutable proof of execution speed."
                )
            },
            {
                "id": "ch3",
                "number": "03",
                "title": "Three Strategic Pitch Angles",
                "summary": "Tailor the pitch angle to match company maturity and pain point.",
                "content": (
                    "1. Interactive Proof of Work (The Anti-Resume): Ideal for product design and frontend roles where visual polish and UX state transitions speak for themselves.\n"
                    "2. Problem & Bottleneck Audit: Ideal for scaling companies where you identify latency, bundle bloat, or API waterfall bottlenecks and present the solution.\n"
                    "3. 14-Day Production Sprint: Ideal for founders needing fast roadmap delivery. Replaces 60 days of interviewing with an immediate, fixed-scope engineering sprint."
                )
            },
            {
                "id": "ch4",
                "number": "04",
                "title": "Finding the Technical Decision-Maker",
                "summary": "Bypass jobs@ and careers@ with precision search dorks.",
                "content": (
                    "Never email generic company inboxes. Use Google LinkedIn search formulas to pinpoint technical leadership:\n"
                    "Query: \"Company Name\" (\"CTO\" OR \"Founder\" OR \"Head of Engineering\" OR \"VP Engineering\") site:linkedin.com/in\n"
                    "Verify corporate email patterns using Hunter.io or Apollo (most common: first@company.com or first.last@company.com). "
                    "If email cannot be verified, send direct InMail or X message referencing the live demo URL."
                )
            },
            {
                "id": "ch5",
                "number": "05",
                "title": "Converting Job Posts into High-Value Contractor Retainers",
                "summary": "Turn a salaried vacancy into a $3k to $8k monthly agreement.",
                "content": (
                    "Full-time hiring costs companies months in sourcing, benefits, and equity overhead. When you present yourself "
                    "as an independent systems architect ready on day one, founders frequently pivot their hiring budget into a "
                    "monthly contractor retainer ($3,000 - $8,000/month) or sprint engagement. You maintain autonomy, work on "
                    "clear milestones, and expand your portfolio across multiple global clients."
                )
            }
        ]
    }
