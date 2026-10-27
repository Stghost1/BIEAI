"""
Scoutdesk Local SQLite Database Engine.
Stores real opportunities, outreach pipeline drafts, scan telemetry,
tailored portfolio demos, and autopilot audit logs.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.surveys import init_surveys_table, get_survey_platforms, get_survey_playbook

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "scoutdesk.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            fit_score INTEGER DEFAULT 70,
            fit_tag TEXT DEFAULT 'Good fit',
            category TEXT DEFAULT 'website',
            matched_skills TEXT,
            budget TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outreach_drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id INTEGER NOT NULL,
            recipient_email TEXT DEFAULT '',
            subject TEXT NOT NULL,
            hook TEXT NOT NULL,
            body TEXT NOT NULL,
            recommended_demo TEXT,
            demo_url TEXT,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
        );
    """)

    try:
        cursor.execute("ALTER TABLE outreach_drafts ADD COLUMN recipient_email TEXT DEFAULT ''")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            items_found INTEGER DEFAULT 0,
            items_saved INTEGER DEFAULT 0,
            status TEXT DEFAULT 'success',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_demos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            tech_stack TEXT DEFAULT 'React, TypeScript, Tailwind',
            opportunity_id INTEGER,
            demo_url TEXT NOT NULL,
            file_name TEXT NOT NULL,
            preview_desc TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'live',
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autopilot_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            job_title TEXT NOT NULL,
            demo_slug TEXT,
            demo_url TEXT,
            recipient_email TEXT,
            email_status TEXT DEFAULT 'queued',
            proposal_subject TEXT,
            log_messages TEXT,
            status TEXT DEFAULT 'success',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
        );
    """)

    cursor.executescript("""
        CREATE INDEX IF NOT EXISTS idx_opp_score ON opportunities(fit_score DESC);
        CREATE INDEX IF NOT EXISTS idx_opp_category ON opportunities(category);
        CREATE INDEX IF NOT EXISTS idx_opp_status ON opportunities(status);
        CREATE INDEX IF NOT EXISTS idx_demos_slug ON portfolio_demos(slug);
        CREATE INDEX IF NOT EXISTS idx_autopilot_opp ON autopilot_runs(opportunity_id);
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    defaults = {
        "portfolio_url": "https://biework.vercel.app",
        "github_url": "https://github.com/bamsemma",
        "email": "techwithbie@gmail.com",
        "whatsapp": "+234 905 404 5597",
        "upwork_url": "https://www.upwork.com/freelancers/~015875b6ee71b82e73",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": "587",
        "smtp_user": "techwithbie@gmail.com",
        "smtp_pass": "",
        "smtp_from_name": "Emmanuel Pelumi Bamidele (Bamsemma)",
        "auto_send_enabled": "false",
    }
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    init_surveys_table(conn)
    seed_baseline_demos(conn)

    conn.commit()
    conn.close()


def seed_baseline_demos(conn: sqlite3.Connection) -> None:
    """Seed existing production demos into portfolio_demos table if not already present."""
    cursor = conn.cursor()
    baseline = [
        (
            "swiftlegal-nigeria",
            "SwiftLegal Nigeria",
            "SwiftLegal Partners",
            "corporate",
            "React, TypeScript, Tailwind, Node.js",
            "https://biework.vercel.app/swiftlegal-nigeria",
            "swiftlegal-nigeria.html",
            "Authoritative corporate portal with practice areas, team profiles, and consultation booking."
        ),
        (
            "lagos-premier-realty",
            "Lagos Premier Realty",
            "Lagos Premier Realty",
            "realty",
            "Next.js, Tailwind, Dynamic Filters, Leaflet Maps",
            "https://biework.vercel.app/lagos-premier-realty",
            "lagos-premier-realty.html",
            "High-converting property portal with listing filters, neighborhood guides, and WhatsApp lead routing."
        ),
        (
            "nutricoach-abuja",
            "NutriCoach Abuja",
            "NutriCoach Abuja",
            "health",
            "React, Tailwind, Interactive BMI Engine",
            "https://biework.vercel.app/nutricoach-abuja",
            "nutricoach-abuja.html",
            "Health coaching platform featuring an interactive live BMI calculator lead magnet."
        ),
        (
            "roi-calculator",
            "Real Estate ROI Calculator",
            "Apex Commercial",
            "finance",
            "TypeScript, React, Financial Yield Algorithms",
            "https://biework.vercel.app/roi-calculator",
            "roi-calculator.html",
            "Interactive financial tool calculating yields, break-even periods, and 5-year ROI forecasts."
        ),
        (
            "invoice-generator",
            "AI-Powered Invoice Generator",
            "B.I.E.AI Tools",
            "saas",
            "Vanilla JS, LocalStorage, Canvas/PDF Generation",
            "https://biework.vercel.app/invoice-generator",
            "invoice-generator.html",
            "Professional browser billing tool with line items, tax calculations, and PDF download."
        ),
    ]
    for slug, title, company, category, stack, url, filename, desc in baseline:
        cursor.execute("""
            INSERT OR IGNORE INTO portfolio_demos (
                slug, title, company, category, tech_stack, demo_url, file_name, preview_desc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (slug, title, company, category, stack, url, filename, desc))


def insert_opportunity(data: Dict[str, Any]) -> bool:
    """Insert opportunity if not already present. Returns True if inserted."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO opportunities (
                external_id, source, title, company, url, description, tags,
                fit_score, fit_tag, category, matched_skills, budget, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("external_id"),
            data.get("source", "Web"),
            data.get("title", "Untitled Opportunity"),
            data.get("company", "Direct Client"),
            data.get("url", "#"),
            data.get("description", ""),
            json.dumps(data.get("tags", [])),
            int(data.get("fit_score", 75)),
            data.get("fit_tag", "Good fit"),
            data.get("category", "website"),
            json.dumps(data.get("matched_skills", [])),
            data.get("budget", "$1k - $3k+"),
            data.get("status", "new")
        ))
        inserted = cursor.rowcount > 0
        conn.commit()
        return inserted
    finally:
        conn.close()


def get_opportunities(
    category: Optional[str] = None,
    min_score: int = 0,
    search: Optional[str] = None,
    limit: int = 50,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM opportunities WHERE fit_score >= ?"
        params: List[Any] = [min_score]

        if category and category != "all":
            query += " AND category = ?"
            params.append(category)

        if status and status != "all":
            query += " AND status = ?"
            params.append(status)

        if search:
            query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        query += " ORDER BY fit_score DESC, created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "external_id": r["external_id"],
                "source": r["source"],
                "title": r["title"],
                "company": r["company"],
                "url": r["url"],
                "description": r["description"],
                "tags": json.loads(r["tags"] or "[]"),
                "fit_score": r["fit_score"],
                "fit_tag": r["fit_tag"],
                "category": r["category"],
                "matched_skills": json.loads(r["matched_skills"] or "[]"),
                "budget": r["budget"],
                "status": r["status"],
                "created_at": r["created_at"]
            })
        return results
    finally:
        conn.close()


def get_opportunity_by_id(opp_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        r = cursor.fetchone()
        if not r:
            return None
        return {
            "id": r["id"],
            "external_id": r["external_id"],
            "source": r["source"],
            "title": r["title"],
            "company": r["company"],
            "url": r["url"],
            "description": r["description"],
            "tags": json.loads(r["tags"] or "[]"),
            "fit_score": r["fit_score"],
            "fit_tag": r["fit_tag"],
            "category": r["category"],
            "matched_skills": json.loads(r["matched_skills"] or "[]"),
            "budget": r["budget"],
            "status": r["status"],
            "created_at": r["created_at"]
        }
    finally:
        conn.close()


def update_opportunity_status(opp_id: int, status: str) -> bool:
    """Update opportunity pipeline status (e.g. new, prototype_ready, applied, follow_up, interview, won, archived)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE opportunities SET status = ? WHERE id = ?", (status, opp_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM opportunities")
        total_signals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM opportunities WHERE fit_score >= 80")
        qualified = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM outreach_drafts")
        drafts_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM outreach_drafts WHERE status = 'sent'")
        sent_count = cursor.fetchone()[0]

        cursor.execute("SELECT source, COUNT(*) FROM opportunities GROUP BY source")
        sources_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) FROM survey_platforms WHERE status = 'active'")
        survey_total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM survey_platforms WHERE category = 'nigeria_direct' AND status = 'active'")
        survey_local = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM survey_platforms WHERE category = 'vpn_tier1' AND status = 'active'")
        survey_vpn = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM portfolio_demos WHERE status = 'live'")
        demos_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM autopilot_runs")
        autopilot_count = cursor.fetchone()[0]

        return {
            "total_signals": total_signals,
            "qualified": qualified,
            "pipeline_count": drafts_count,
            "sent_count": sent_count,
            "sources": sources_breakdown,
            "estimated_value": f"${max(10, qualified * 1.5):.1f}k",
            "survey_total": survey_total,
            "survey_local": survey_local,
            "survey_vpn": survey_vpn,
            "demos_count": demos_count,
            "autopilot_count": autopilot_count,
        }
    finally:
        conn.close()


def get_surveys(
    category: str = "all",
    country: str = "all",
    search: str = "",
    vpn_required: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        return get_survey_platforms(conn, category=category, country=country, search=search, vpn_required=vpn_required)
    finally:
        conn.close()


def create_outreach_draft(
    opp_id: int,
    subject: str,
    hook: str,
    body: str,
    demo_name: str,
    demo_url: str,
    recipient_email: str = ""
) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO outreach_drafts (
                opportunity_id, recipient_email, subject, hook, body, recommended_demo, demo_url, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'draft')
        """, (opp_id, recipient_email, subject, hook, body, demo_name, demo_url))
        draft_id = cursor.lastrowid
        cursor.execute("UPDATE opportunities SET status = 'outreach_drafted' WHERE id = ?", (opp_id,))
        conn.commit()
        return {
            "id": draft_id,
            "opportunity_id": opp_id,
            "recipient_email": recipient_email,
            "subject": subject,
            "hook": hook,
            "body": body,
            "recommended_demo": demo_name,
            "demo_url": demo_url,
            "status": "draft"
        }
    finally:
        conn.close()


def get_pipeline() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT d.*, o.title as opp_title, o.company as opp_company, o.url as opp_url, o.category
            FROM outreach_drafts d
            JOIN opportunities o ON d.opportunity_id = o.id
            ORDER BY d.id DESC
        """)
        rows = cursor.fetchall()
        results = []
        for r in rows:
            rec_email = ""
            try:
                rec_email = r["recipient_email"] or ""
            except Exception:
                pass
            results.append({
                "id": r["id"],
                "opportunity_id": r["opportunity_id"],
                "recipient_email": rec_email,
                "opp_title": r["opp_title"],
                "opp_company": r["opp_company"],
                "opp_url": r["opp_url"],
                "category": r["category"],
                "subject": r["subject"],
                "hook": r["hook"],
                "body": r["body"],
                "demo_name": r["recommended_demo"],
                "demo_url": r["demo_url"],
                "status": r["status"],
                "created_at": r["created_at"],
            })
        return results
    finally:
        conn.close()


def update_draft_status(
    draft_id: int,
    status: str,
    body: Optional[str] = None,
    subject: Optional[str] = None,
    recipient_email: Optional[str] = None
) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]
        if body is not None:
            updates.append("body = ?")
            params.append(body)
        if subject is not None:
            updates.append("subject = ?")
            params.append(subject)
        if recipient_email is not None:
            updates.append("recipient_email = ?")
            params.append(recipient_email)
        params.append(draft_id)
        query = f"UPDATE outreach_drafts SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def log_scan(source: str, found: int, saved: int, status: str = "success") -> None:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO scan_logs (source, items_found, items_saved, status)
            VALUES (?, ?, ?, ?)
        """, (source, found, saved, status))
        conn.commit()
    finally:
        conn.close()


def insert_portfolio_demo(demo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Store newly engineered tailored demo into portfolio_demos table."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO portfolio_demos (
                slug, title, company, category, tech_stack, opportunity_id,
                demo_url, file_name, preview_desc, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                category = excluded.category,
                tech_stack = excluded.tech_stack,
                demo_url = excluded.demo_url,
                file_name = excluded.file_name,
                preview_desc = excluded.preview_desc,
                status = excluded.status
        """, (
            demo_data.get("slug"),
            demo_data.get("title"),
            demo_data.get("company"),
            demo_data.get("category", "general"),
            demo_data.get("tech_stack", "React, TypeScript, Tailwind"),
            demo_data.get("opportunity_id"),
            demo_data.get("demo_url"),
            demo_data.get("file_name"),
            demo_data.get("preview_desc", ""),
            demo_data.get("status", "live")
        ))
        demo_id = cursor.lastrowid
        conn.commit()
        return {**demo_data, "id": demo_id}
    finally:
        conn.close()


def get_portfolio_demos(category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch all live portfolio demos."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if category and category != "all":
            cursor.execute("""
                SELECT * FROM portfolio_demos WHERE category = ? ORDER BY id DESC LIMIT ?
            """, (category, limit))
        else:
            cursor.execute("""
                SELECT * FROM portfolio_demos ORDER BY id DESC LIMIT ?
            """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_demo_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM portfolio_demos WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def log_autopilot_run(run_data: Dict[str, Any]) -> int:
    """Record an autopilot execution into the audit trail."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO autopilot_runs (
                opportunity_id, company, job_title, demo_slug, demo_url,
                recipient_email, email_status, proposal_subject, log_messages, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_data.get("opportunity_id"),
            run_data.get("company", ""),
            run_data.get("job_title", ""),
            run_data.get("demo_slug", ""),
            run_data.get("demo_url", ""),
            run_data.get("recipient_email", ""),
            run_data.get("email_status", "queued"),
            run_data.get("proposal_subject", ""),
            run_data.get("log_messages", ""),
            run_data.get("status", "success")
        ))
        run_id = cursor.lastrowid
        cursor.execute("UPDATE opportunities SET status = 'applied' WHERE id = ?", (run_data.get("opportunity_id"),))
        conn.commit()
        return run_id
    finally:
        conn.close()


def get_autopilot_runs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM autopilot_runs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default
    except sqlite3.OperationalError:
        return default
    finally:
        conn.close()


def set_setting(key: str, value: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()


def get_all_settings() -> Dict[str, str]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        return {r["key"]: r["value"] for r in rows}
    except sqlite3.OperationalError:
        return {}
    finally:
        conn.close()
