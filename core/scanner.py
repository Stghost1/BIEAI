"""
Scoutdesk Live Signal Scanner.
Fetches real remote engineering, web development, AI, and design opportunities
from public APIs without requiring external API keys.
"""

from __future__ import annotations

import html
import json
import re
import urllib.request
from typing import Any, Dict, List, Tuple
from core.db import insert_opportunity, log_scan


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


def clean_metadata(text: str) -> str:
    """Clean company names and job titles of HTML entities and encoding artifacts."""
    if not text:
        return ""
    s = html.unescape(text)
    s = s.replace("â€™", "'").replace("\x80\x99", "'")
    s = s.replace("â€“", ", ").replace("\x80\x93", ", ")
    s = re.sub(r'\s*\ufffd\s*', ', ', s)
    s = re.sub(r'\s*[—–]\s*', ', ', s)
    s = re.sub(r'\s+--\s+', ', ', s)
    s = re.sub(r'\s+-\s+', ', ', s)
    s = re.sub(r'[\u007f-\u009f]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def clean_job_text(text: str, max_chars: int = 1800) -> str:
    """
    Cleans and standardizes job descriptions:
    - Resolves mojibake, byte artifacts, and replacement characters
    - Unescapes all HTML entities (including numeric & named entities)
    - Strips HTML tags while inserting appropriate spacing and sentence structure
    - Enforces Law 2 (zero em-dash or en-dash sentence punctuation)
    - Truncates at natural sentence boundaries without slicing words in half
    - Ensures clean terminal punctuation
    """
    if not text:
        return ""

    s = text

    # 1. Unescape literal backslash escapes
    s = s.replace("\\n", " ").replace("\\r", " ").replace("\\t", " ")

    # 2. Fix mojibake / broken byte patterns before HTML parsing
    s = s.replace("â€™", "'").replace("â€˜", "'")
    s = s.replace("â€œ", '"').replace("â€\x9d", '"').replace("â€\x9c", '"')
    s = s.replace("â€“", ", ").replace("â€”", ", ")
    s = s.replace("Â", " ").replace("\xa0", " ")
    s = s.replace("\ufeff", "").replace("\u200b", "")

    # Common raw byte artifacts from poorly decoded cp1252 / iso-8859-1 into utf-8
    s = s.replace("\x80\x99", "'").replace("\x80\x98", "'")
    s = s.replace("\x80\x9c", '"').replace("\x80\x9d", '"')
    s = s.replace("\x80\x93", ", ").replace("\x80\x94", ", ")

    # Handle bullet sequences with corrupted byte headers
    s = re.sub(r'(?:\ufffd|[\u0080-\u00bf])+\xa2', ', ', s)

    # Replacement character \ufffd handling
    s = re.sub(r'([a-zA-Z])\ufffd([a-zA-Z])', r"\1'\2", s)
    s = re.sub(r'(\d+)\s*\ufffd\s*(\d+)', r'\1 to \2', s)
    s = re.sub(r'\ufffd(?=[\'"])', '', s)
    s = re.sub(r'(?<=[\'"])\ufffd', '', s)
    s = re.sub(r'\ufffd(?:\ufffd|[\u0080-\u00bf])*', ' ', s)
    s = s.replace("\ufffd", " ")

    # Remove stray C1 control characters (0x7F - 0x9F)
    s = re.sub(r'[\u007f-\u009f]', '', s)

    # Handle '???' artifact patterns
    s = re.sub(r'([a-zA-Z])\?{2,3}([a-zA-Z])', r"\1'\2", s)
    s = re.sub(r'(\d+)\s*\?{2,3}\s*(\d+)', r'\1 to \2', s)

    # 3. HTML entity unescape (first pass)
    s = html.unescape(s)

    # 4. Handle block elements and list items to preserve readability
    s = re.sub(r'</?(?:p|div|section|article|blockquote)[^>]*>', ' ', s, flags=re.I)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'</?li[^>]*>', ', ', s, flags=re.I)
    s = re.sub(r'</?h[1-6][^>]*>', '. ', s, flags=re.I)
    s = re.sub(r'</?tr[^>]*>', '. ', s, flags=re.I)

    # 5. Strip all remaining HTML tags
    s = re.sub(r'<[^>]+>', ' ', s)

    # 6. HTML entity unescape (second pass for entities revealed by tag stripping)
    s = html.unescape(s)

    # 7. Normalize typography and enforce Law 2
    s = re.sub(r'(\d+)\s*[–—]\s*(\d+)', r'\1 to \2', s)
    s = re.sub(r'\s*[—–]\s*', ', ', s)
    s = re.sub(r'\s+--\s+', ', ', s)
    s = re.sub(r'\s+-\s+', ', ', s)

    # Normalize quotes and bullets
    s = s.replace("‘", "'").replace("’", "'").replace("`", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("«", '"').replace("»", '"')
    s = s.replace("…", "...")
    s = s.replace("·", ", ")
    s = s.replace("•", ", ")

    # 8. Clean up whitespace and punctuation
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r':\s*,', ':', s)
    s = re.sub(r'\s+([,.:;?!])', r'\1', s)
    s = re.sub(r',\s*,+', ', ', s)
    s = re.sub(r'\.\s*\.+', '.', s)
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    s = s.strip()

    # 9. Natural boundary truncation if exceeding max_chars
    if len(s) > max_chars:
        window_start = max_chars - 300
        window = s[window_start:max_chars]
        last_punct = -1
        for m in re.finditer(r'[.!?]\s', window):
            last_punct = m.end() - 1

        if last_punct != -1:
            cut_idx = window_start + last_punct
            s = s[:cut_idx].strip()
        else:
            cut_s = s[:max_chars]
            last_space = cut_s.rfind(' ')
            if last_space > max_chars - 120:
                cut_s = cut_s[:last_space].strip()
            dangling = {'and', 'or', 'to', 'the', 'a', 'an', 'with', 'for', 'of', 'in', 'on', 'at', 'by', 'as', 'r', 'is', 'that', 'which'}
            words = cut_s.split()
            while words and words[-1].lower().rstrip('.,;:!?') in dangling:
                words.pop()
            cut_s = ' '.join(words).rstrip(' ,;:-')
            s = cut_s

    # Final cleanup of trailing punctuation
    s = re.sub(r'[,;:\s]+$', '', s).strip()
    if s and not s.endswith(('.', '!', '?', '"', "'")):
        s += '.'

    return s


def clean_html(text: str) -> str:
    """Backwards-compatible wrapper calling clean_job_text."""
    return clean_job_text(text, max_chars=1800)


def calculate_fit(title: str, desc: str, tags: List[str]) -> Tuple[int, str, str, List[str]]:
    """
    Score the opportunity against Bamsemma's verified service capabilities:
    1. Full-Stack Web Development & Landing Pages (React/Next.js/Node/TypeScript/Tailwind)
    2. AI Video, Motion & UGC Production
    3. UI/UX & Brand Design (Figma, Design Systems)
    4. Python Automation & Data Workflows
    """
    full_text = f"{title} {desc} {' '.join(tags)}".lower()

    skills_matched = []
    category = "website"
    score = 65

    # Web & Full-stack keywords
    web_keywords = {
        "react": 12, "next.js": 15, "nextjs": 15, "node": 10, "typescript": 12,
        "javascript": 8, "tailwind": 12, "frontend": 10, "front-end": 10,
        "full stack": 14, "fullstack": 14, "landing page": 16, "web developer": 12,
        "express": 8, "html": 6, "css": 6, "api": 8, "postgres": 8, "mongodb": 8
    }

    # AI & Media production
    media_keywords = {
        "ai video": 18, "video": 12, "motion": 12, "animation": 14,
        "ugc": 16, "creator": 10, "shorts": 14, "tiktok": 10, "reels": 10,
        "after effects": 10, "content creator": 10
    }

    # UI/UX & Graphic design
    design_keywords = {
        "ui": 12, "ux": 12, "figma": 14, "product designer": 14,
        "design system": 15, "graphic": 10, "brand": 10, "visual": 8
    }

    # Automation & Scripting
    auto_keywords = {
        "python": 12, "automation": 15, "agent": 14, "bot": 12,
        "scraper": 14, "scraping": 14, "workflow": 10, "n8n": 15
    }

    # Evaluate Web matches
    for kw, weight in web_keywords.items():
        if kw in full_text:
            score += weight
            skills_matched.append(kw.title())

    # Evaluate Media matches
    media_score = 0
    for kw, weight in media_keywords.items():
        if kw in full_text:
            media_score += weight
            skills_matched.append(kw.title())

    # Evaluate Design matches
    design_score = 0
    for kw, weight in design_keywords.items():
        if kw in full_text:
            design_score += weight
            skills_matched.append(kw.title())

    # Evaluate Automation matches
    auto_score = 0
    for kw, weight in auto_keywords.items():
        if kw in full_text:
            auto_score += weight
            skills_matched.append(kw.title())

    # Determine dominant category
    scores = {
        "website": score,
        "video": 60 + media_score,
        "design": 60 + design_score,
        "automation": 60 + auto_score,
    }
    category = max(scores, key=scores.get)
    final_score = min(98, max(68, scores[category]))

    # Deduplicate matched skills
    unique_skills = list(dict.fromkeys(skills_matched))[:6]

    if final_score >= 88:
        tag = "High fit"
    elif final_score >= 78:
        tag = "Good fit"
    else:
        tag = "Explore"

    return final_score, tag, category, unique_skills


def scan_remoteok() -> int:
    """Fetch opportunities from RemoteOK public API."""
    url = "https://remoteok.com/api"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    saved = 0
    found = 0
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            items = json.loads(res.read().decode("utf-8"))
            for item in items:
                if not isinstance(item, dict) or not item.get("id"):
                    continue
                found += 1
                title = clean_metadata(item.get("position", "Tech Role"))
                company = clean_metadata(item.get("company", "Remote Company"))
                desc = clean_job_text(item.get("description", ""), max_chars=1800)
                tags = item.get("tags", [])
                job_url = item.get("url") or f"https://remoteok.com/l/{item.get('id')}"

                fit_score, fit_tag, cat, matched_skills = calculate_fit(title, desc, tags)

                # Determine budget signal
                salary_min = item.get("salary_min")
                salary_max = item.get("salary_max")
                budget = f"${salary_min:,} - ${salary_max:,}" if salary_min and salary_max else "$2k - $5k/mo"

                inserted = insert_opportunity({
                    "external_id": f"remoteok_{item.get('id')}",
                    "source": "RemoteOK",
                    "title": title,
                    "company": company,
                    "url": job_url,
                    "description": desc,
                    "tags": tags[:5],
                    "fit_score": fit_score,
                    "fit_tag": fit_tag,
                    "category": cat,
                    "matched_skills": matched_skills,
                    "budget": budget,
                    "status": "new"
                })
                if inserted:
                    saved += 1
        log_scan("RemoteOK", found, saved, "success")
    except Exception as exc:
        log_scan("RemoteOK", found, saved, f"error: {str(exc)[:100]}")
    return saved


def scan_jobicy() -> int:
    """Fetch opportunities from Jobicy public API."""
    url = "https://jobicy.com/api/v2/remote-jobs?count=25"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    saved = 0
    found = 0
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            jobs = data.get("jobs", [])
            for j in jobs:
                found += 1
                job_id = j.get("id") or j.get("jobSlug")
                title = clean_metadata(j.get("jobTitle", "Remote Specialist"))
                company = clean_metadata(j.get("companyName", "Global Client"))
                desc = clean_job_text(j.get("jobDescription", ""), max_chars=1800)
                job_url = j.get("url", "https://jobicy.com")
                tags = [j.get("jobIndustry", "Tech")]

                fit_score, fit_tag, cat, matched_skills = calculate_fit(title, desc, tags)

                salary = j.get("annualSalaryMin")
                budget = f"${salary:,}/yr" if salary else "$1.5k - $4k/mo"

                inserted = insert_opportunity({
                    "external_id": f"jobicy_{job_id}",
                    "source": "Jobicy",
                    "title": title,
                    "company": company,
                    "url": job_url,
                    "description": desc,
                    "tags": tags,
                    "fit_score": fit_score,
                    "fit_tag": fit_tag,
                    "category": cat,
                    "matched_skills": matched_skills,
                    "budget": budget,
                    "status": "new"
                })
                if inserted:
                    saved += 1
        log_scan("Jobicy", found, saved, "success")
    except Exception as exc:
        log_scan("Jobicy", found, saved, f"error: {str(exc)[:100]}")
    return saved


def scan_arbeitnow() -> int:
    """Fetch opportunities from Arbeitnow public API."""
    url = "https://www.arbeitnow.com/api/job-board-api"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    saved = 0
    found = 0
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            jobs = data.get("data", [])
            for j in jobs[:25]:
                found += 1
                slug = j.get("slug")
                title = clean_metadata(j.get("title", "Software Specialist"))
                company = clean_metadata(j.get("company_name", "Global Agency"))
                desc = clean_job_text(j.get("description", ""), max_chars=1800)
                job_url = j.get("url", f"https://www.arbeitnow.com/view/{slug}")
                tags = j.get("tags", [])

                fit_score, fit_tag, cat, matched_skills = calculate_fit(title, desc, tags)

                inserted = insert_opportunity({
                    "external_id": f"arbeitnow_{slug}",
                    "source": "Arbeitnow",
                    "title": title,
                    "company": company,
                    "url": job_url,
                    "description": desc,
                    "tags": tags[:5],
                    "fit_score": fit_score,
                    "fit_tag": fit_tag,
                    "category": cat,
                    "matched_skills": matched_skills,
                    "budget": "Competitive",
                    "status": "new"
                })
                if inserted:
                    saved += 1
        log_scan("Arbeitnow", found, saved, "success")
    except Exception as exc:
        log_scan("Arbeitnow", found, saved, f"error: {str(exc)[:100]}")
    return saved


def run_full_scan() -> Dict[str, int]:
    """Execute all public feeds and return stats."""
    s1 = scan_remoteok()
    s2 = scan_jobicy()
    s3 = scan_arbeitnow()
    total_saved = s1 + s2 + s3
    return {
        "remoteok": s1,
        "jobicy": s2,
        "arbeitnow": s3,
        "total_new": total_saved
    }
