"""
JobAssist ATS & Tech-Stack Match Engine.
Analyzes job descriptions against B.I.E.AI / Bamsemma core capability matrix.
Extracts matched keywords, calculates ATS density fit score, identifies high-value
proposal focus areas, and detects missing stack elements.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set

# B.I.E.AI verified technical stack and capability ontology
CAPABILITY_MATRIX: Dict[str, List[str]] = {
    "frontend": [
        "react", "next.js", "nextjs", "typescript", "javascript", "tailwind",
        "tailwind css", "html5", "css3", "shadcn", "shadcn/ui", "redux",
        "zustand", "vue", "responsive design", "web performance", "frontend"
    ],
    "backend": [
        "node", "node.js", "express", "express.js", "python", "fastapi", "flask",
        "c#", ".net", "dotnet", "rest", "restful", "api", "apis", "graphql",
        "backend", "microservices", "webhooks"
    ],
    "database": [
        "postgresql", "postgres", "mongodb", "mongo", "sqlite", "redis",
        "prisma", "orm", "sql", "nosql", "supabase", "database", "indexing"
    ],
    "ai_automation": [
        "ai", "llm", "llms", "openai", "claude", "gemini", "agent", "agents",
        "automation", "workflow", "mcp", "langchain", "prompt engineering",
        "scraping", "nlp", "rag"
    ],
    "devops_cloud": [
        "vercel", "netlify", "docker", "git", "github", "ci/cd", "aws",
        "cloud", "linux", "deployment", "env"
    ],
    "production_quality": [
        "testing", "jest", "pytest", "unit tests", "integration tests", "tdd",
        "zod", "validation", "security", "jwt", "auth", "oauth", "performance"
    ]
}

# High-priority keywords that indicate direct engineering leadership fit
HIGH_VALUE_MARKERS: Set[str] = {
    "next.js", "react", "typescript", "node.js", "python", "postgresql",
    "tailwind", "api", "full stack", "ai", "automation", "mvp", "architecture"
}


def clean_text_tokens(text: str) -> Set[str]:
    """Tokenize and normalize text for keyword matching."""
    normalized = text.lower()
    # Replace punctuation with spaces while keeping tech terms like c#, .net, next.js
    normalized = normalized.replace("/", " ").replace("-", " ")
    tokens = set(re.findall(r'[a-z0-9.#+]+', normalized))
    return tokens


def analyze_ats_fit(title: str, description: str, tags: List[str] = None) -> Dict[str, Any]:
    """
    Evaluates how closely a job description aligns with Bamsemma's skill vector.
    Returns match percentage, matched skills, key proposal talking points,
    and missing keywords.
    """
    raw_text = f"{title} {description} {' '.join(tags or [])}".lower()
    
    matched_by_category: Dict[str, List[str]] = {}
    all_matched: List[str] = []
    high_value_hits: List[str] = []

    total_matrix_terms = 0
    matched_matrix_terms = 0

    for cat, terms in CAPABILITY_MATRIX.items():
        cat_matches = []
        for term in terms:
            total_matrix_terms += 1
            # Exact boundary matching for short terms like 'c#', 'ai', 'sql'
            pattern = r'(?:\b|[\s.,;/])' + re.escape(term) + r'(?:\b|[\s.,;/])'
            if re.search(pattern, raw_text):
                cat_matches.append(term)
                all_matched.append(term)
                matched_matrix_terms += 1
                if term in HIGH_VALUE_MARKERS:
                    high_value_hits.append(term)
        if cat_matches:
            matched_by_category[cat] = cat_matches

    # Calculate ATS density score (scaled 60 to 98)
    # Even single-stack roles start with a solid baseline
    hit_count = len(all_matched)
    if hit_count == 0:
        calculated_score = 65
    elif hit_count <= 2:
        calculated_score = 72
    elif hit_count <= 5:
        calculated_score = 80
    elif hit_count <= 8:
        calculated_score = 88
    elif hit_count <= 12:
        calculated_score = 94
    else:
        calculated_score = 98

    # Deduplicate high value hits
    unique_high_value = sorted(list(set(high_value_hits)))
    unique_matched = sorted(list(set(all_matched)))

    # Identify proposal focus recommendations based on matches
    proposal_focus: List[str] = []
    if any(k in unique_matched for k in ["react", "next.js", "typescript", "tailwind"]):
        proposal_focus.append("Modular React/Next.js component hierarchy with zero layout shift")
    if any(k in unique_matched for k in ["node", "node.js", "express", "python", "api"]):
        proposal_focus.append("Type-safe API endpoints with Zod/DTO validation and clean error envelopes")
    if any(k in unique_matched for k in ["postgresql", "mongodb", "database", "prisma"]):
        proposal_focus.append("Parameterized database queries, strict indexes, and N+1 prevention")
    if any(k in unique_matched for k in ["ai", "automation", "agent", "llm"]):
        proposal_focus.append("Autonomous tool calling, resilient retries, and structured JSON parsing")

    if not proposal_focus:
        proposal_focus.append("High-velocity prototyping with production-grade code structure")

    return {
        "ats_score": calculated_score,
        "matched_count": hit_count,
        "matched_skills": unique_matched[:12],
        "high_value_hits": unique_high_value,
        "category_matches": matched_by_category,
        "proposal_focus": proposal_focus,
        "fit_verdict": "Exceptional Match" if calculated_score >= 90 else "Strong Alignment" if calculated_score >= 80 else "Good General Fit"
    }
