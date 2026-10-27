"""
B.I.E.AI Tailored Demo Product Builder.
Analyzes job requirements and synthesizes an interactive, production-ready
micro-application demo tailored specifically for the target company and role.
Deploys clean route rewrites to vercel.json and logs the demo into the portfolio vault.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.db import get_setting, insert_portfolio_demo

ROOT = Path(__file__).resolve().parent.parent


def sanitize_slug(text: str, max_len: int = 40) -> str:
    """Create a clean URL slug from arbitrary text."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return slug[:max_len].strip("-") or "demo-prototype"


def get_base_portfolio_url() -> str:
    url = get_setting("portfolio_url", os.environ.get("PORTFOLIO_URL", "https://biework.vercel.app"))
    return (url or "https://biework.vercel.app").rstrip("/")


def get_github_url() -> str:
    url = get_setting("github_url", os.environ.get("GITHUB_URL", "https://github.com/bamsemma"))
    return (url or "https://github.com/bamsemma").rstrip("/")


def detect_archetype(title: str, desc: str, tags: List[str], company: str) -> Dict[str, Any]:
    """Classify the opportunity into a high-impact interactive prototype archetype."""
    text = f"{title} {desc} {' '.join(tags)} {company}".lower()

    if any(k in text for k in ["fintech", "payment", "stripe", "crypto", "wallet", "ledger", "billing", "bank"]):
        return {
            "key": "fintech",
            "name": "Interactive Payment & Settlement Hub",
            "category": "finance",
            "tech_stack": "Next.js, TypeScript, Tailwind, Stripe API, PostgreSQL",
            "feature": "Real-time fee calculator, transaction ledger simulator, and multi-currency settlement controls."
        }
    elif any(k in text for k in ["analytics", "metrics", "telemetry", "dashboard", "latency", "monitoring", "cloud", "saas"]):
        return {
            "key": "saas_analytics",
            "name": "Live Performance & Telemetry Dashboard",
            "category": "saas",
            "tech_stack": "React 19, TypeScript, Tailwind CSS, WebSockets, Redis",
            "feature": "Real-time query latency monitor, active request throughput simulator, and interactive alert filters."
        }
    elif any(k in text for k in ["ai", "llm", "prompt", "agent", "gpt", "rag", "langchain", "chatbot"]):
        return {
            "key": "ai_studio",
            "name": "AI Prompt & Workflow Orchestrator",
            "category": "ai",
            "tech_stack": "Next.js App Router, Python FastAPI, OpenAI/Gemini SDK, Vector DB",
            "feature": "Interactive prompt parameter tuner, token cost estimator, and simulated streaming completion workbench."
        }
    elif any(k in text for k in ["automation", "n8n", "scraper", "scraping", "crawler", "bot", "pipeline", "etl"]):
        return {
            "key": "automation_pipeline",
            "name": "Autonomous Data Pipeline & Webhook Inspector",
            "category": "automation",
            "tech_stack": "Python, Node.js, SQLite, Headless Chromium, Cron",
            "feature": "Visual multi-stage workflow pipeline with event triggers, data transforms, and live execution telemetry."
        }
    elif any(k in text for k in ["ecommerce", "shop", "shopify", "store", "dtc", "cart", "retail", "merch"]):
        return {
            "key": "ecommerce",
            "name": "High-Conversion E-Commerce & Checkout Portal",
            "category": "ecommerce",
            "tech_stack": "Next.js, Tailwind CSS, Stripe Checkout, Redis Cart Cache",
            "feature": "Interactive product configuration, dynamic bundle discount calculator, and instant checkout drawer."
        }
    elif any(k in text for k in ["health", "medical", "clinic", "wellness", "fitness", "patient", "doctor"]):
        return {
            "key": "healthtech",
            "name": "Clinical Triage & Patient Telemedicine Portal",
            "category": "health",
            "tech_stack": "React, TypeScript, Tailwind, HIPAA-Compliant Architecture, SQLite",
            "feature": "Interactive symptom severity triage calculator, intake form validation, and care appointment booking."
        }
    elif any(k in text for k in ["legal", "contract", "compliance", "law", "attorney", "audit", "gdpr"]):
        return {
            "key": "legaltech",
            "name": "Corporate Contract & Compliance Auditor",
            "category": "corporate",
            "tech_stack": "TypeScript, React, Node.js, Document Analysis Engine",
            "feature": "Interactive clause vulnerability checklist, risk scoring meter, and automated consultation intake."
        }
    elif any(k in text for k in ["video", "motion", "ugc", "animation", "youtube", "media", "editing"]):
        return {
            "key": "media_creative",
            "name": "AI Video & UGC Production Storyboard Hub",
            "category": "media",
            "tech_stack": "React, Tailwind CSS, Canvas API, FFMPEG Pipeline",
            "feature": "Interactive 8-second shot sequencer, aspect-ratio previewer, and automated creative render queue."
        }
    else:
        return {
            "key": "fullstack_web",
            "name": "High-Impact Conversion Platform & Client Portal",
            "category": "website",
            "tech_stack": "Next.js App Router, TypeScript, Tailwind CSS, Prisma, PostgreSQL",
            "feature": "Interactive capability demonstration, live metric calculator, and validated client booking pipeline."
        }


def generate_interactive_widget(archetype_key: str, company: str, title: str) -> str:
    """Produce domain-specific interactive JavaScript and HTML widget components."""
    if archetype_key == "fintech":
        return f"""
    <!-- Interactive Fintech Widget -->
    <div class="card p-6 border border-blue-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div>
          <h3 class="font-bold text-white text-lg">{company} Settlement Simulator</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Live Transaction & Fee Ledger</p>
        </div>
        <span class="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-mono rounded-full border border-emerald-500/20">Production-Ready Logic</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Gross Volume</label>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-slate-500 text-sm">$</span>
            <input type="number" id="volInput" value="25000" class="bg-transparent text-white font-mono font-bold text-xl w-full focus:outline-none" oninput="recalcFintech()">
          </div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Take Rate / Fee (%)</label>
          <div class="flex items-center gap-2 mt-1">
            <input type="number" id="feeInput" value="2.9" step="0.1" class="bg-transparent text-emerald-400 font-mono font-bold text-xl w-full focus:outline-none" oninput="recalcFintech()">
            <span class="text-slate-500 text-sm">%</span>
          </div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Net Settled Yield</label>
          <div class="text-blue-400 font-mono font-bold text-xl mt-1" id="netOutput">$24,275.00</div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
          <span>REAL-TIME TRANSACTION STREAM</span>
          <button onclick="injectTransaction()" class="px-2 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs transition">+ Simulate Payment Webhook</button>
        </div>
        <div id="txList" class="space-y-2 font-mono text-xs max-h-48 overflow-y-auto pr-1">
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">TX-8841 // Enterprise Subscription // Card (US)</span>
            <span class="text-emerald-400 font-bold">+$4,200.00</span>
          </div>
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">TX-8840 // API Usage Tier B // SEPA Direct</span>
            <span class="text-emerald-400 font-bold">+$850.00</span>
          </div>
        </div>
      </div>
    </div>
    <script>
      function recalcFintech() {{
        const vol = parseFloat(document.getElementById('volInput').value) || 0;
        const fee = parseFloat(document.getElementById('feeInput').value) || 0;
        const net = vol * (1 - (fee / 100));
        document.getElementById('netOutput').innerText = '$' + net.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
      }}
      function injectTransaction() {{
        const list = document.getElementById('txList');
        const randId = Math.floor(1000 + Math.random() * 9000);
        const amount = (Math.random() * 2500 + 100).toFixed(2);
        const div = document.createElement('div');
        div.className = 'flex items-center justify-between p-2.5 bg-blue-950/20 rounded border border-blue-500/30 animate-pulse';
        div.innerHTML = '<span class="text-blue-300">TX-' + randId + ' // Automated Settlement Event</span><span class="text-emerald-400 font-bold">+$' + parseFloat(amount).toLocaleString('en-US', {{minimumFractionDigits: 2}}) + '</span>';
        list.prepend(div);
        setTimeout(() => {{ div.classList.remove('animate-pulse'); }}, 600);
      }}
    </script>
        """

    elif archetype_key == "saas_analytics":
        return f"""
    <!-- Interactive SaaS Analytics Widget -->
    <div class="card p-6 border border-blue-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div>
          <h3 class="font-bold text-white text-lg">{company} Performance Telemetry</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Real-Time Edge Metrics</p>
        </div>
        <button onclick="refreshMetrics()" class="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono rounded transition">Ping Endpoints</button>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 font-mono">
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">P95 Latency</div>
          <div class="text-2xl font-bold text-emerald-400 mt-1" id="p95Val">38ms</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">RPS Throughput</div>
          <div class="text-2xl font-bold text-blue-400 mt-1" id="rpsVal">1,420</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Cache Hit Ratio</div>
          <div class="text-2xl font-bold text-purple-400 mt-1" id="cacheVal">98.4%</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Uptime SLA</div>
          <div class="text-2xl font-bold text-white mt-1">99.99%</div>
        </div>
      </div>

      <div class="p-4 bg-slate-950/60 rounded border border-slate-800 font-mono text-xs">
        <div class="flex justify-between text-slate-400 mb-2">
          <span>ENDPOINT LOAD DISTRIBUTION</span>
          <span class="text-emerald-400">All Clusters Healthy</span>
        </div>
        <div class="space-y-2">
          <div>
            <div class="flex justify-between text-[11px] text-slate-300 mb-1">
              <span>POST /api/v2/ingest</span>
              <span id="load1">78%</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-1.5"><div id="bar1" class="bg-blue-500 h-1.5 rounded-full" style="width: 78%"></div></div>
          </div>
          <div>
            <div class="flex justify-between text-[11px] text-slate-300 mb-1">
              <span>GET /api/v2/telemetry/query</span>
              <span id="load2">42%</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-1.5"><div id="bar2" class="bg-emerald-500 h-1.5 rounded-full" style="width: 42%"></div></div>
          </div>
        </div>
      </div>
    </div>
    <script>
      function refreshMetrics() {{
        const lat = Math.floor(Math.random() * 20 + 25);
        const rps = Math.floor(Math.random() * 500 + 1200);
        const l1 = Math.floor(Math.random() * 30 + 60);
        const l2 = Math.floor(Math.random() * 40 + 30);
        document.getElementById('p95Val').innerText = lat + 'ms';
        document.getElementById('rpsVal').innerText = rps.toLocaleString();
        document.getElementById('load1').innerText = l1 + '%';
        document.getElementById('bar1').style.width = l1 + '%';
        document.getElementById('load2').innerText = l2 + '%';
        document.getElementById('bar2').style.width = l2 + '%';
      }}
    </script>
        """

    elif archetype_key == "ai_studio":
        return f"""
    <!-- Interactive AI Studio Widget -->
    <div class="card p-6 border border-purple-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div>
          <h3 class="font-bold text-white text-lg">{company} AI Prompt Studio</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Parameter Tuning & Inference Lab</p>
        </div>
        <span class="px-3 py-1 bg-purple-500/10 text-purple-400 text-xs font-mono rounded-full border border-purple-500/20">Zero-Latency Mock</span>
      </div>

      <div class="space-y-4 font-mono text-xs">
        <div>
          <label class="block text-slate-400 mb-1">System Instruction / Context Prompt</label>
          <textarea id="promptArea" rows="2" class="w-full p-2.5 bg-slate-950/70 border border-slate-800 rounded text-slate-200 focus:outline-none focus:border-purple-500">You are the operational intelligence engine for {company}. Return structured, verified outputs.</textarea>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
            <label class="text-slate-400">Temperature: <span id="tempVal" class="text-purple-400">0.2</span></label>
            <input type="range" min="0" max="1" step="0.1" value="0.2" class="w-full mt-2 accent-purple-500" oninput="document.getElementById('tempVal').innerText=this.value">
          </div>
          <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
            <label class="text-slate-400">Max Tokens: <span class="text-purple-400">2048</span></label>
            <div class="text-slate-300 mt-2 font-bold">Strict Window</div>
          </div>
          <div class="p-3 bg-slate-950/60 rounded border border-slate-800 flex items-center justify-between">
            <label class="text-slate-400">Estimated Cost</label>
            <span class="text-emerald-400 font-bold">$0.0004 / run</span>
          </div>
        </div>

        <div>
          <button onclick="runInference()" class="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded font-bold transition">Test Model Response</button>
        </div>

        <div id="aiOutputBox" class="p-4 bg-slate-950 rounded border border-slate-800 text-slate-300 hidden">
          <div class="text-purple-400 font-bold mb-1">// SYNTHESIZED STREAM RESPONSE:</div>
          <p id="aiOutputText" class="text-xs leading-relaxed text-slate-200"></p>
        </div>
      </div>
    </div>
    <script>
      function runInference() {{
        const box = document.getElementById('aiOutputBox');
        const text = document.getElementById('aiOutputText');
        box.classList.remove('hidden');
        text.innerText = "Analyzing requirements for {company}... Verified clean contract schemas, parameterized queries, and defensive error boundaries initialized with zero regression.";
      }}
    </script>
        """

    elif archetype_key == "automation_pipeline":
        return f"""
    <!-- Interactive Automation Pipeline Widget -->
    <div class="card p-6 border border-emerald-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div>
          <h3 class="font-bold text-white text-lg">{company} Workflow Pipeline</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Automated Webhook & Data Sync</p>
        </div>
        <button onclick="triggerPipeline()" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono rounded transition">Execute Pipeline</button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-3 my-4 font-mono text-xs">
        <div id="step1" class="p-3 bg-slate-950/60 border border-slate-800 rounded transition">
          <div class="text-slate-400 text-[10px]">STAGE 1</div>
          <div class="text-white font-bold mt-1">Webhook Ingest</div>
          <div class="text-emerald-400 text-[11px] mt-1" id="st1">Ready</div>
        </div>
        <div id="step2" class="p-3 bg-slate-950/60 border border-slate-800 rounded transition">
          <div class="text-slate-400 text-[10px]">STAGE 2</div>
          <div class="text-white font-bold mt-1">Schema Validation</div>
          <div class="text-slate-500 text-[11px] mt-1" id="st2">Pending</div>
        </div>
        <div id="step3" class="p-3 bg-slate-950/60 border border-slate-800 rounded transition">
          <div class="text-slate-400 text-[10px]">STAGE 3</div>
          <div class="text-white font-bold mt-1">Data Enrichment</div>
          <div class="text-slate-500 text-[11px] mt-1" id="st3">Pending</div>
        </div>
        <div id="step4" class="p-3 bg-slate-950/60 border border-slate-800 rounded transition">
          <div class="text-slate-400 text-[10px]">STAGE 4</div>
          <div class="text-white font-bold mt-1">Dispatch & Alert</div>
          <div class="text-slate-500 text-[11px] mt-1" id="st4">Pending</div>
        </div>
      </div>

      <div class="p-3 bg-slate-950/80 rounded border border-slate-800 font-mono text-xs text-slate-400">
        <span class="text-emerald-400 font-bold">LOG STREAM: </span>
        <span id="pipelineLog">Waiting for execution trigger...</span>
      </div>
    </div>
    <script>
      function triggerPipeline() {{
        const log = document.getElementById('pipelineLog');
        document.getElementById('st1').innerText = "Processing...";
        document.getElementById('step1').classList.add('border-emerald-500');
        log.innerText = "[200 OK] Incoming payload received. Verifying Zod schema...";
        setTimeout(() => {{
          document.getElementById('st1').innerText = "Verified";
          document.getElementById('st2').innerText = "Validated";
          document.getElementById('step2').classList.add('border-emerald-500');
          log.innerText = "[VALID] Schema matched. Appending enriched metadata...";
        }}, 400);
        setTimeout(() => {{
          document.getElementById('st3').innerText = "Enriched";
          document.getElementById('step3').classList.add('border-emerald-500');
          log.innerText = "[SAVED] Record committed to PostgreSQL without N+1 overhead.";
        }}, 800);
        setTimeout(() => {{
          document.getElementById('st4').innerText = "Dispatched";
          document.getElementById('step4').classList.add('border-emerald-500');
          log.innerText = "[COMPLETE] Pipeline finished in 142ms. Zero failure.";
        }}, 1200);
      }}
    </script>
        """

    else:
        # Default Full-Stack / Interactive Web Showcase
        return f"""
    <!-- Interactive Web Platform Prototype Widget -->
    <div class="card p-6 border border-blue-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div>
          <h3 class="font-bold text-white text-lg">{company} Client Portal & Feature Showcase</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Interactive Capability Fit</p>
        </div>
        <span class="px-3 py-1 bg-blue-500/10 text-blue-400 text-xs font-mono rounded-full border border-blue-500/20">Production-Grade UI</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800 text-center">
          <div class="text-xs font-mono text-slate-400 uppercase">Architecture</div>
          <div class="font-bold text-white text-base mt-1">Next.js App Router</div>
          <div class="text-xs text-blue-400 mt-1">Zero Layout Shift</div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800 text-center">
          <div class="text-xs font-mono text-slate-400 uppercase">State Management</div>
          <div class="font-bold text-white text-base mt-1">TypeScript & Zod</div>
          <div class="text-xs text-emerald-400 mt-1">100% Typed Boundary</div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800 text-center">
          <div class="text-xs font-mono text-slate-400 uppercase">Execution Velocity</div>
          <div class="font-bold text-white text-base mt-1">Rapid Ship Sprint</div>
          <div class="text-xs text-purple-400 mt-1">Production Hand-off</div>
        </div>
      </div>

      <div class="p-4 bg-slate-950/80 rounded border border-slate-800 font-mono text-xs text-slate-300 flex items-center justify-between">
        <span>Verified for 4-8 GB RAM development environments & global mobile test targets.</span>
        <button onclick="alert('Interactive component verified.')" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded font-bold transition">Test Action</button>
      </div>
    </div>
        """


def build_demo_html(
    company: str,
    title: str,
    slug: str,
    archetype: Dict[str, Any],
    opp_url: str = "#"
) -> str:
    """Generate the complete, responsive HTML micro-application with B.I.E.AI branding."""
    portfolio_base = get_base_portfolio_url()
    github_url = get_github_url()
    interactive_widget = generate_interactive_widget(archetype["key"], company, title)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{company} &mdash; Tailored Interactive Proof of Work | B.I.E.AI</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Syne:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'DM Sans', sans-serif; background: #05111F; color: #FAFAF8; }}
    .font-syne {{ font-family: 'Syne', sans-serif; }}
    .font-mono {{ font-family: 'Space Mono', monospace; }}
    .bg-grid {{
      background-image: linear-gradient(rgba(21, 88, 214, 0.08) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(21, 88, 214, 0.08) 1px, transparent 1px);
      background-size: 40px 40px;
    }}
  </style>
</head>
<body class="bg-[#05111F] text-slate-100 min-h-screen flex flex-col bg-grid">

  <!-- Top Navigation Bar -->
  <header class="border-b border-blue-500/20 bg-[#05111F]/90 backdrop-blur sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <a href="{portfolio_base}" class="font-syne font-extrabold text-xl text-white tracking-wide">
          B.I.E<span class="text-blue-500">.AI</span>
        </a>
        <span class="text-slate-600">/</span>
        <span class="font-mono text-xs text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded border border-blue-500/20">
          Tailored Prototype
        </span>
      </div>
      <div class="flex items-center gap-3">
        <a href="{opp_url}" target="_blank" rel="noopener" class="text-xs font-mono text-slate-400 hover:text-white transition hidden sm:inline">
          View Opportunity Posting ↗
        </a>
        <a href="https://wa.me/2349054045597?text=Hi%20Bamsemma,%20reviewing%20your%20demo%20for%20{company}" target="_blank" rel="noopener" class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-mono text-xs font-bold transition flex items-center gap-1.5">
          <span>WhatsApp Chat</span> ↗
        </a>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <main class="max-w-6xl mx-auto px-4 py-10 flex-1 w-full">
    <div class="p-6 md:p-10 rounded-2xl bg-gradient-to-b from-[#0A1E35]/80 to-[#071628]/90 border border-blue-500/30 shadow-2xl relative overflow-hidden">
      <div class="absolute -right-20 -top-20 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full text-blue-400 font-mono text-xs mb-4">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>VERIFIED PROOF OF WORK &mdash; PRE-BUILT FOR {company.upper()}</span>
      </div>

      <h1 class="font-syne text-3xl md:text-5xl font-extrabold text-white tracking-tight mb-4">
        {company} <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">&times; B.I.E.AI</span>
      </h1>

      <p class="text-slate-300 text-sm md:text-base max-w-2xl leading-relaxed mb-6">
        Rather than applying with a generic resume, I built an interactive prototype specifically addressing the requirements for <strong class="text-white">{title}</strong>. This demo showcases production engineering, clean state handling, and performant user interface design.
      </p>

      <div class="flex flex-wrap gap-2 text-xs font-mono">
        <span class="px-2.5 py-1 bg-slate-900/80 border border-slate-700 rounded text-slate-300">Target Role: {title}</span>
        <span class="px-2.5 py-1 bg-slate-900/80 border border-slate-700 rounded text-blue-300">Stack: {archetype['tech_stack']}</span>
        <span class="px-2.5 py-1 bg-slate-900/80 border border-slate-700 rounded text-emerald-300">Category: {archetype['category'].upper()}</span>
      </div>
    </div>

    <!-- Interactive Proof of Concept -->
    {interactive_widget}

    <!-- Production Architecture Blueprint -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-8">
      <div class="p-6 bg-slate-900/40 border border-slate-800 rounded-xl">
        <div class="font-mono text-xs text-blue-400 uppercase mb-2">01 / Architecture</div>
        <h4 class="font-syne font-bold text-white text-lg mb-2">Clean, Typed Boundaries</h4>
        <p class="text-xs text-slate-400 leading-relaxed">
          Every endpoint and component uses strict Zod/TypeScript schema contracts. No N+1 queries, parameterized SQL, and defensive error envelopes.
        </p>
      </div>

      <div class="p-6 bg-slate-900/40 border border-slate-800 rounded-xl">
        <div class="font-mono text-xs text-emerald-400 uppercase mb-2">02 / Performance</div>
        <h4 class="font-syne font-bold text-white text-lg mb-2">Sub-100ms Responses</h4>
        <p class="text-xs text-slate-400 leading-relaxed">
          Optimized Next.js App Router streaming, zero CLS layout shifts, lightweight bundles tested to run efficiently across low-memory environments.
        </p>
      </div>

      <div class="p-6 bg-slate-900/40 border border-slate-800 rounded-xl">
        <div class="font-mono text-xs text-purple-400 uppercase mb-2">03 / Reliability</div>
        <h4 class="font-syne font-bold text-white text-lg mb-2">Test-Driven Execution</h4>
        <p class="text-xs text-slate-400 leading-relaxed">
          Automated regression coverage, failure-mode safeguards, and daily milestone logs directly verifiable on GitHub or live staging.
        </p>
      </div>
    </div>

    <!-- Direct Call to Action -->
    <div class="p-8 rounded-xl bg-gradient-to-r from-blue-900/30 via-slate-900/60 to-blue-900/30 border border-blue-500/20 text-center my-8">
      <h3 class="font-syne text-2xl font-bold text-white mb-2">Ready to ship this for {company}?</h3>
      <p class="text-xs md:text-sm text-slate-300 max-w-xl mx-auto mb-6">
        I am available for contract and full-time engineering. Let's schedule a 15-minute technical walkthrough to review how we can deliver this without overhead.
      </p>
      <div class="flex flex-wrap items-center justify-center gap-4">
        <a href="mailto:techwithbie@gmail.com?subject=Technical%20Interview%20-%20{company}%20({title})" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded text-sm transition">
          Email Emmanuel (Bamsemma)
        </a>
        <a href="{portfolio_base}" class="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded text-sm transition font-mono">
          Explore Main Portfolio ↗
        </a>
        <a href="{github_url}" target="_blank" rel="noopener" class="px-6 py-2.5 border border-slate-700 hover:border-slate-500 text-slate-300 rounded text-sm transition font-mono">
          GitHub Profile ↗
        </a>
      </div>
    </div>
  </main>

  <!-- Technical Footer -->
  <footer class="border-t border-slate-800/80 bg-[#030A14] py-8 text-center text-xs font-mono text-slate-500">
    <div class="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
      <div>
        Engineered by <strong class="text-slate-300">Emmanuel Pelumi Bamidele (Bamsemma)</strong> &bull; Founder, B.I.E.AI
      </div>
      <div class="flex items-center gap-4">
        <a href="{portfolio_base}" class="hover:text-blue-400 transition">biework.vercel.app</a>
        <span>&bull;</span>
        <a href="{github_url}" target="_blank" rel="noopener" class="hover:text-blue-400 transition">github.com/bamsemma</a>
        <span>&bull;</span>
        <a href="https://www.upwork.com/freelancers/~015875b6ee71b82e73" target="_blank" rel="noopener" class="hover:text-blue-400 transition">Upwork Profile</a>
      </div>
    </div>
  </footer>

</body>
</html>
"""


def register_vercel_rewrite(slug: str) -> bool:
    """Ensure biework/vercel.json has a clean URL rewrite for this demo."""
    candidates = [
        ROOT / "vercel.json",
        ROOT.parent / "biework" / "vercel.json"
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


def build_tailored_demo(opp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point:
    1. Analyzes the opportunity.
    2. Determines archetype and tech stack.
    3. Builds standalone responsive HTML.
    4. Writes HTML to biework and bie job search platform directories.
    5. Registers clean route in vercel.json.
    6. Stores in portfolio_demos table.
    """
    company = opp.get("company") or "Direct Client"
    title = opp.get("title") or "Full-Stack Opportunity"
    opp_id = opp.get("id")
    opp_url = opp.get("url") or "#"
    desc = opp.get("description") or ""
    tags = opp.get("tags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = []

    archetype = detect_archetype(title, desc, tags, company)

    # Generate slug: e.g. demo-apex-fintech-senior-react
    comp_clean = sanitize_slug(company, 18)
    title_clean = sanitize_slug(title, 20)
    slug = f"demo-{comp_clean}-{title_clean}"

    base_url = get_base_portfolio_url()
    demo_url = f"{base_url}/{slug}"
    file_name = f"{slug}.html"

    # Generate complete HTML
    html_content = build_demo_html(company, title, slug, archetype, opp_url=opp_url)

    # Write file to both biework and bie job search platform
    target_dirs = [
        ROOT,
        ROOT.parent / "biework",
        ROOT.parent / "bie job search platform"
    ]
    for d in target_dirs:
        if d.exists() and d.is_dir():
            file_path = d / file_name
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
            except Exception:
                pass

    # Register rewrite in vercel.json
    register_vercel_rewrite(slug)

    # Store in database
    demo_record = {
        "slug": slug,
        "title": f"{company} &mdash; {archetype['name']}",
        "company": company,
        "category": archetype["category"],
        "tech_stack": archetype["tech_stack"],
        "opportunity_id": opp_id,
        "demo_url": demo_url,
        "file_name": file_name,
        "preview_desc": f"Tailored {archetype['name']} built specifically for {company}'s {title} role.",
        "status": "live"
    }

    inserted = insert_portfolio_demo(demo_record)
    return {**demo_record, **inserted}
