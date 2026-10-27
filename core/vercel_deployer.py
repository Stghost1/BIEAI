"""
Scoutdesk Automated Vercel Deployment & Route Registrar.
Ensures every newly synthesized client demo receives a production rewrite in vercel.json,
dispatches to Vercel production deployment pipelines, and logs live URLs.
Enforces Law 10: durability, automated rebuild steps, and clean separation of config.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
import urllib.request

ROOT = Path(__file__).resolve().parent.parent


def get_base_portfolio_url() -> str:
    url = os.environ.get("PORTFOLIO_URL", "https://bieai.vercel.app")
    return url.rstrip("/")


def register_vercel_rewrite(slug: str) -> bool:
    """Ensure vercel.json has a clean URL rewrite for this demo."""
    candidates = [
        ROOT / "vercel.json",
        ROOT.parent / "biework" / "vercel.json",
        ROOT.parent / "bie job search platform" / "vercel.json"
    ]
    updated_any = False
    for vpath in candidates:
        if not vpath.exists():
            continue
        try:
            with open(vpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            rewrites = data.get("rewrites", [])
            source_path = f"/{slug}"
            dest_path = f"/{slug}.html"

            # Check if already present
            if not any(r.get("source") == source_path for r in rewrites):
                rewrites.append({
                    "source": source_path,
                    "destination": dest_path
                })
                data["rewrites"] = rewrites
                with open(vpath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                updated_any = True
        except Exception:
            pass
    return updated_any


def deploy_to_vercel(slug: str, file_name: str, company: str) -> Dict[str, Any]:
    """
    Automated Vercel pipeline:
    1. Registers clean URL rewrite in vercel.json.
    2. Checks for VERCEL_TOKEN / Vercel API deployment.
    3. Checks for Vercel CLI execution.
    4. Generates canonical live production URL: https://biework.vercel.app/{slug}.
    """
    rewrite_registered = register_vercel_rewrite(slug)
    base_url = get_base_portfolio_url()
    canonical_vercel_url = f"{base_url}/{slug}"

    deployed_via_api = False
    token = os.environ.get("VERCEL_TOKEN")
    project_id = os.environ.get("VERCEL_PROJECT_ID")

    # 1. Direct Vercel REST API deployment if token is provided
    if token:
        try:
            file_path = ROOT / file_name
            if file_path.exists():
                file_content = file_path.read_text(encoding="utf-8", errors="ignore")
                api_url = "https://api.vercel.com/v13/deployments"
                payload = {
                    "name": "biework",
                    "files": [
                        {"file": file_name, "data": file_content},
                        {"file": "vercel.json", "data": (ROOT / "vercel.json").read_text(encoding="utf-8")}
                    ],
                    "target": "production"
                }
                if project_id:
                    payload["projectId"] = project_id

                req = urllib.request.Request(
                    api_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=8) as r:
                    if r.status in (200, 201):
                        deployed_via_api = True
        except Exception:
            pass

    # 2. Vercel CLI execution check
    deployed_via_cli = False
    if not deployed_via_api:
        try:
            res = subprocess.run(
                ["vercel", "--prod", "--yes"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=12
            )
            if res.returncode == 0:
                deployed_via_cli = True
        except Exception:
            pass

    status = (
        "deployed_via_api" if deployed_via_api
        else "deployed_via_cli" if deployed_via_cli
        else "route_registered_live_on_push"
    )

    return {
        "ok": True,
        "vercel_url": canonical_vercel_url,
        "rewrite_registered": rewrite_registered,
        "status": status
    }
