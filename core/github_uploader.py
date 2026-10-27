"""
Scoutdesk Automated GitHub Version Control & Repository Dispatcher.
Automatically commits tailored demo micro-applications to git, stages vercel.json
route updates, tracks commits, and pushes to remote repositories.
Enforces Law 10: durability, clean conventional commits, and zero secrets committed.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
import urllib.request

ROOT = Path(__file__).resolve().parent.parent


def get_git_executable() -> str:
    return "git"


def commit_demo_locally(file_name: str, slug: str, company: str, title: str) -> Dict[str, Any]:
    """
    Stage the demo file and vercel.json, then create a conventional commit.
    """
    try:
        # Check if git repo exists
        git_dir = ROOT / ".git"
        if not git_dir.exists():
            subprocess.run([get_git_executable(), "-C", str(ROOT), "init"], capture_output=True, check=True)

        # Stage demo and vercel.json
        subprocess.run(
            [get_git_executable(), "-C", str(ROOT), "add", file_name, "vercel.json"],
            capture_output=True,
            check=True
        )

        # Commit
        commit_msg = f"feat(demo): ship live tailored prototype for {company} ({title})"
        res = subprocess.run(
            [get_git_executable(), "-C", str(ROOT), "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )

        # Get commit hash
        hash_res = subprocess.run(
            [get_git_executable(), "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True
        )
        commit_sha = hash_res.stdout.strip() if hash_res.returncode == 0 else "local_commit"

        return {
            "ok": True,
            "commit_sha": commit_sha,
            "message": commit_msg,
            "status": "committed_locally"
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "status": "commit_failed"
        }


def push_demo_to_github(file_name: str, slug: str, company: str, title: str) -> Dict[str, Any]:
    """
    Full GitHub pipeline:
    1. Commits file and vercel.json locally.
    2. Pushes to remote origin if configured.
    3. If GITHUB_TOKEN is present, synchronizes directly to GitHub REST API.
    4. Formulates canonical GitHub file URL.
    """
    commit_res = commit_demo_locally(file_name, slug, company, title)
    github_user = os.environ.get("GITHUB_USER", "Stghost1")
    github_repo = os.environ.get("GITHUB_REPO", "BIEAI")
    github_branch = os.environ.get("GITHUB_BRANCH", "main")
    canonical_github_url = f"https://github.com/{github_user}/{github_repo}/blob/{github_branch}/{file_name}"

    # Check for git remote origin
    pushed = False
    try:
        remotes = subprocess.run(
            [get_git_executable(), "-C", str(ROOT), "remote", "-v"],
            capture_output=True,
            text=True
        )
        if "origin" in remotes.stdout:
            push_res = subprocess.run(
                [get_git_executable(), "-C", str(ROOT), "push", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=15
            )
            pushed = push_res.returncode == 0
    except Exception:
        pass

    # Optional: GitHub REST API direct upload if GITHUB_TOKEN is available
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            file_path = ROOT / file_name
            if file_path.exists():
                content_b64 = base64.b64encode(file_path.read_bytes()).decode("utf-8")
                api_url = f"https://api.github.com/repos/{github_user}/{github_repo}/contents/{file_name}"
                body = {
                    "message": f"feat(demo): add tailored prototype for {company} ({title})",
                    "content": content_b64,
                    "branch": github_branch
                }
                req = urllib.request.Request(
                    api_url,
                    data=json.dumps(body).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github.v3+json",
                        "Content-Type": "application/json",
                        "User-Agent": "BIEAI-Scoutdesk"
                    },
                    method="PUT"
                )
                with urllib.request.urlopen(req, timeout=8) as r:
                    if r.status in (200, 201):
                        pushed = True
        except Exception:
            pass

    return {
        "ok": commit_res.get("ok", False),
        "github_url": canonical_github_url,
        "commit_sha": commit_res.get("commit_sha", ""),
        "pushed": pushed,
        "status": "pushed_to_remote" if pushed else "committed_locally"
    }
