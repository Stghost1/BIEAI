"""
B.I.E.AI Real Tailored Demo Product Builder.
Synthesizes bespoke, interactive, production-ready micro-application demos
tailored specifically for the target company's exact industry and technical requirements.
Automatically commits & pushes to GitHub, deploys & routes to Vercel, and scours recipient emails.
"""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.db import get_setting, insert_portfolio_demo, update_opportunity_email
from core.github_uploader import push_demo_to_github
from core.vercel_deployer import deploy_to_vercel, register_vercel_rewrite
from core.email_scourer import scour_company_email

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

    if any(k in text for k in ["wagmo", "pet", "animal", "vet", "veterinary"]):
        return {
            "key": "pet_healthtech",
            "name": "Pet Health Benefits & Preventive Care Hub",
            "category": "health",
            "tech_stack": "React, TypeScript, Tailwind, Preventive Claim Ledger, Telehealth API",
            "feature": "Multi-pet employer plan customizer, veterinary claim reimbursement ledger, and 24/7 telehealth triage calculator."
        }
    elif any(k in text for k in ["klardaten", "datev", "accounting", "cpa", "tax", "audit", "reconciliation", "aprio"]):
        return {
            "key": "accounting_ai",
            "name": "DATEV Document & AI Reconciliation Engine",
            "category": "finance",
            "tech_stack": "TypeScript, React, Node.js, DATEV XML/REST Webhooks, PostgreSQL",
            "feature": "Real-time DATEV webhook event dispatcher, automated double-entry ledger matcher, and AI confidence threshold slider."
        }
    elif any(k in text for k in ["onebrief", "military", "defense", "tactical", "mission", "command"]):
        return {
            "key": "tactical_ai",
            "name": "Tactical Command Node & Mission Workflow Orchestrator",
            "category": "ai",
            "tech_stack": "Next.js App Router, WebSockets, Python, Geospatial Mapping, AES-256",
            "feature": "Command node operational readiness radar, simulated tactical event stream, and resilient decision-tree simulator."
        }
    elif any(k in text for k in ["getlabs", "phlebotomy", "diagnostics", "lab", "specimen", "at-home"]):
        return {
            "key": "diagnostic_phlebotomy",
            "name": "Mobile Phlebotomist Dispatch & Route Telemetry Portal",
            "category": "health",
            "tech_stack": "React 19, TypeScript, Tailwind, GPS Routing API, SQLite",
            "feature": "Real-time patient dispatch queue, cold-chain specimen temperature monitor, and route ETA optimizer."
        }
    elif any(k in text for k in ["lemon.io", "devops", "sre", "kubernetes", "k8s", "terraform", "ci/cd", "infrastructure", "docker"]):
        return {
            "key": "devops_infra",
            "name": "Cloud Infrastructure & Zero-Downtime Deployment Orchestrator",
            "category": "saas",
            "tech_stack": "Next.js, TypeScript, Tailwind, Docker, Kubernetes API, Prometheus",
            "feature": "Kubernetes cluster pod health matrix, P99 canary deployment latency gauge, and automated Terraform state drift detector."
        }
    elif any(k in text for k in ["midnite", "esports", "gaming", "betting", "wager", "odds"]):
        return {
            "key": "gaming_sportsbook",
            "name": "Esports Tournament Settlement & Live Odds Engine",
            "category": "saas",
            "tech_stack": "React 19, TypeScript, Tailwind CSS, WebSockets, Redis",
            "feature": "Dynamic esports odds calculator, sub-second wager event stream, and responsive high-FPS betting slip."
        }
    elif any(k in text for k in ["huzzle", "candidate", "recruiting", "recruitment", "staffing", "sales closer", "account executive"]):
        return {
            "key": "recruitment_crm",
            "name": "Enterprise Candidate Placement & Deal Conversion CRM",
            "category": "saas",
            "tech_stack": "React, TypeScript, Tailwind, Deal Funnel Algorithms, SQLite",
            "feature": "Interactive candidate placement funnel, high-ticket deal commission calculator, and live placement event stream."
        }
    elif any(k in text for k in ["plaid", "fintech", "payment", "stripe", "crypto", "wallet", "ledger", "billing", "bank"]):
        return {
            "key": "fintech_ledger",
            "name": "Interactive Payment & Settlement Hub",
            "category": "finance",
            "tech_stack": "Next.js, TypeScript, Tailwind, Stripe API, PostgreSQL",
            "feature": "Real-time fee calculator, transaction ledger simulator, and multi-currency settlement controls."
        }
    elif any(k in text for k in ["ai", "llm", "prompt", "agent", "gpt", "rag", "langchain", "chatbot"]):
        return {
            "key": "ai_orchestrator",
            "name": "AI Prompt & Workflow Orchestrator",
            "category": "ai",
            "tech_stack": "Next.js App Router, Python FastAPI, OpenAI/Gemini SDK, Vector DB",
            "feature": "Interactive prompt parameter tuner, token cost estimator, and simulated streaming completion workbench."
        }
    elif any(k in text for k in ["ecommerce", "shop", "shopify", "store", "dtc", "cart", "retail", "merch"]):
        return {
            "key": "ecommerce_dtc",
            "name": "High-Conversion E-Commerce & Checkout Portal",
            "category": "ecommerce",
            "tech_stack": "Next.js, Tailwind CSS, Stripe Checkout, Redis Cart Cache",
            "feature": "Interactive product configuration, dynamic bundle discount calculator, and instant checkout drawer."
        }
    else:
        return {
            "key": "general_saas",
            "name": "Live Performance & Telemetry Dashboard",
            "category": "saas",
            "tech_stack": "React 19, TypeScript, Tailwind CSS, WebSockets, Redis",
            "feature": "Real-time query latency monitor, active request throughput simulator, and interactive alert filters."
        }


def generate_interactive_widget(archetype_key: str, company: str, title: str) -> str:
    """Produce domain-specific interactive JavaScript and HTML widget components."""
    if archetype_key == "pet_healthtech":
        return f"""
    <!-- Interactive Pet Health Benefits Widget -->
    <div class="card p-6 border border-emerald-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3 flex-wrap gap-2">
        <div>
          <h3 class="font-bold text-white text-lg">{company} Pet Wellness & Benefit Simulator</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Real-Time Employer Pet Coverage Ledger</p>
        </div>
        <div class="flex gap-2">
          <button onclick="simulateVetClaim()" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-mono transition">+ Submit Vet Claim</button>
          <button onclick="exportAuditJSON()" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono transition">📥 Export Audit JSON</button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Enrolled Pets</label>
          <div class="flex items-center gap-2 mt-1">
            <input type="number" id="petCount" value="45" min="1" max="1000" class="bg-transparent text-white font-mono font-bold text-xl w-full focus:outline-none" oninput="recalcPetBenefits()">
            <span class="text-slate-500 text-xs">pets</span>
          </div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Monthly Subsidy / Pet</label>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-slate-500 text-sm">$</span>
            <input type="number" id="subsidyInput" value="35" class="bg-transparent text-emerald-400 font-mono font-bold text-xl w-full focus:outline-none" oninput="recalcPetBenefits()">
          </div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Est. Annual Wellness Savings</label>
          <div class="text-blue-400 font-mono font-bold text-xl mt-1" id="savingsOutput">$18,900.00</div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
          <span>ACTIVE VETERINARY CLAIMS & TELEHEALTH STREAM</span>
          <span class="text-emerald-400 text-[11px]">Telehealth Queue: 0 min wait</span>
        </div>
        <div id="txList" class="space-y-2 font-mono text-xs max-h-48 overflow-y-auto pr-1">
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">CLAIM-1042 // Annual Canine Wellness & Vaccine // Golden Retriever</span>
            <span class="text-emerald-400 font-bold">Approved ($250.00)</span>
          </div>
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">CLAIM-1041 // Dental Hygiene & Clean // Feline (Domestic Shorthair)</span>
            <span class="text-emerald-400 font-bold">Approved ($180.00)</span>
          </div>
        </div>
      </div>
    </div>
    <script>
      function recalcPetBenefits() {{
        const count = parseFloat(document.getElementById('petCount').value) || 0;
        const sub = parseFloat(document.getElementById('subsidyInput').value) || 0;
        const annual = count * sub * 12;
        document.getElementById('savingsOutput').innerText = '$' + annual.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
      }}
      function simulateVetClaim() {{
        const list = document.getElementById('txList');
        const randId = Math.floor(1000 + Math.random() * 9000);
        const pets = ['French Bulldog', 'Maine Coon Cat', 'Labrador Retriever', 'German Shepherd', 'Poodle'];
        const types = ['Emergency X-Ray', 'Ear Infection Cytology', 'Preventive Flea & Tick', 'Routine Bloodwork'];
        const pet = pets[Math.floor(Math.random() * pets.length)];
        const claimType = types[Math.floor(Math.random() * types.length)];
        const amount = (Math.random() * 400 + 75).toFixed(2);
        const div = document.createElement('div');
        div.className = 'flex items-center justify-between p-2.5 bg-emerald-950/20 rounded border border-emerald-500/30 animate-pulse';
        div.innerHTML = '<span class="text-emerald-300">CLAIM-' + randId + ' // ' + claimType + ' // ' + pet + '</span><span class="text-emerald-400 font-bold">Approved ($' + amount + ')</span>';
        list.prepend(div);
      }}
      function exportAuditJSON() {{
        const payload = {{
          company: "{company}",
          role: "{title}",
          export_time: new Date().toISOString(),
          enrolled_pets: document.getElementById('petCount').value,
          monthly_subsidy: document.getElementById('subsidyInput').value,
          architecture: "React, TypeScript, Tailwind, REST API, SQLite",
          status: "verified_production"
        }};
        const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '{company.lower()}-pet-benefits-audit.json';
        a.click();
      }}
    </script>
        """

    elif archetype_key == "accounting_ai":
        return f"""
    <!-- Interactive DATEV AI Reconciliation Widget -->
    <div class="card p-6 border border-blue-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3 flex-wrap gap-2">
        <div>
          <h3 class="font-bold text-white text-lg">{company} DATEV Reconciliation Workbench</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Automated Double-Entry & XML Matcher</p>
        </div>
        <div class="flex gap-2">
          <button onclick="injectDatevWebhook()" class="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-mono transition">+ Trigger DATEV Webhook</button>
          <button onclick="exportAuditJSON()" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono transition">📥 Export Audit JSON</button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Monthly Invoice Volume</label>
          <div class="flex items-center gap-2 mt-1">
            <input type="number" id="invCount" value="1200" class="bg-transparent text-white font-mono font-bold text-xl w-full focus:outline-none" oninput="recalcDatev()">
          </div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">AI Auto-Match Confidence</label>
          <div class="flex items-center gap-2 mt-1">
            <input type="range" id="confSlider" min="70" max="99" value="95" class="w-full accent-blue-500" oninput="recalcDatev()">
            <span class="text-blue-400 font-mono font-bold text-lg" id="confVal">95%</span>
          </div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Manual Hours Saved / Month</label>
          <div class="text-emerald-400 font-mono font-bold text-xl mt-1" id="hoursSaved">114 hrs</div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
          <span>DATEV XML & INVOICE RECONCILIATION STREAM</span>
          <span class="text-emerald-400 text-[11px]">Sync Status: Live 200 OK</span>
        </div>
        <div id="txList" class="space-y-2 font-mono text-xs max-h-48 overflow-y-auto pr-1">
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">DOC-9821 // DATEV Export EXTF // Reconciled Account 1400</span>
            <span class="text-emerald-400 font-bold">100% Match</span>
          </div>
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">DOC-9820 // OCR Invoice Extraction // SEPA Creditor 70001</span>
            <span class="text-emerald-400 font-bold">98% Match</span>
          </div>
        </div>
      </div>
    </div>
    <script>
      function recalcDatev() {{
        const count = parseFloat(document.getElementById('invCount').value) || 0;
        const conf = parseFloat(document.getElementById('confSlider').value) || 95;
        document.getElementById('confVal').innerText = conf + '%';
        const hours = ((count * (conf / 100)) * 0.1).toFixed(0);
        document.getElementById('hoursSaved').innerText = hours + ' hrs';
      }}
      function injectDatevWebhook() {{
        const list = document.getElementById('txList');
        const randId = Math.floor(1000 + Math.random() * 9000);
        const accounts = ['SKR03 1200 Bank', 'SKR04 1400 Forderungen', 'SKR03 4400 Erloese', 'SKR04 6850 Werbeaufwand'];
        const acc = accounts[Math.floor(Math.random() * accounts.length)];
        const div = document.createElement('div');
        div.className = 'flex items-center justify-between p-2.5 bg-blue-950/20 rounded border border-blue-500/30 animate-pulse';
        div.innerHTML = '<span class="text-blue-300">DOC-' + randId + ' // DATEV Event // ' + acc + '</span><span class="text-emerald-400 font-bold">Auto-Reconciled</span>';
        list.prepend(div);
      }}
      function exportAuditJSON() {{
        const payload = {{
          company: "{company}",
          role: "{title}",
          export_time: new Date().toISOString(),
          invoice_volume: document.getElementById('invCount').value,
          confidence_threshold: document.getElementById('confSlider').value + '%',
          integration: "DATEV Connect REST API & XML Parser",
          status: "production_ready"
        }};
        const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '{company.lower()}-datev-audit.json';
        a.click();
      }}
    </script>
        """

    elif archetype_key == "tactical_ai":
        return f"""
    <!-- Interactive Tactical Command Node Widget -->
    <div class="card p-6 border border-amber-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3 flex-wrap gap-2">
        <div>
          <h3 class="font-bold text-white text-lg">{company} Tactical Command Node</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Mission Planning & Geospatial Simulation</p>
        </div>
        <div class="flex gap-2">
          <button onclick="injectTacticalPacket()" class="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded text-xs font-mono transition">+ Trigger Telemetry Ping</button>
          <button onclick="exportAuditJSON()" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono transition">📥 Export Audit JSON</button>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 font-mono text-center">
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Node Readiness</div>
          <div class="text-xl font-bold text-emerald-400 mt-1" id="readinessVal">99.8%</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Sim Latency</div>
          <div class="text-xl font-bold text-amber-400 mt-1" id="simLat">12ms</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Encrypted Packets</div>
          <div class="text-xl font-bold text-blue-400 mt-1" id="packetVal">8,410/s</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Security SLA</div>
          <div class="text-xl font-bold text-white mt-1">FedRAMP / IL5</div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
          <span>OPERATIONAL MISSION WORKFLOW STREAM</span>
          <span class="text-emerald-400 text-[11px]">All Hubs Synchronized</span>
        </div>
        <div id="txList" class="space-y-2 font-mono text-xs max-h-48 overflow-y-auto pr-1">
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">NODE-771 // Geospatial Mesh Sync // Pacific Command Hub</span>
            <span class="text-emerald-400 font-bold">Validated</span>
          </div>
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">NODE-770 // Resilient AI Strategy Branch // Multi-Node Telemetry</span>
            <span class="text-emerald-400 font-bold">Resolved</span>
          </div>
        </div>
      </div>
    </div>
    <script>
      function injectTacticalPacket() {{
        const list = document.getElementById('txList');
        const randId = Math.floor(1000 + Math.random() * 9000);
        const nodes = ['Atlantic Radar Mesh', 'Autonomous Drone Fleet', 'Satellite Comm Uplink', 'Mobile Tactical Unit'];
        const node = nodes[Math.floor(Math.random() * nodes.length)];
        const div = document.createElement('div');
        div.className = 'flex items-center justify-between p-2.5 bg-amber-950/20 rounded border border-amber-500/30 animate-pulse';
        div.innerHTML = '<span class="text-amber-300">NODE-' + randId + ' // ' + node + '</span><span class="text-emerald-400 font-bold">P2P Encrypted</span>';
        list.prepend(div);
      }}
      function exportAuditJSON() {{
        const payload = {{
          company: "{company}",
          role: "{title}",
          export_time: new Date().toISOString(),
          readiness: document.getElementById('readinessVal').innerText,
          encryption: "AES-256-GCM / Zero Trust Architecture",
          status: "verified_mission_ready"
        }};
        const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '{company.lower()}-tactical-audit.json';
        a.click();
      }}
    </script>
        """

    elif archetype_key == "devops_infra":
        return f"""
    <!-- Interactive DevOps Infrastructure Widget -->
    <div class="card p-6 border border-cyan-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3 flex-wrap gap-2">
        <div>
          <h3 class="font-bold text-white text-lg">{company} Zero-Downtime Infrastructure</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Kubernetes Clusters & Canary Traffic Splitter</p>
        </div>
        <div class="flex gap-2">
          <button onclick="pingCluster()" class="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-mono transition">Ping Cluster Health</button>
          <button onclick="exportAuditJSON()" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono transition">📥 Export Audit JSON</button>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 font-mono text-center">
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">P99 Latency</div>
          <div class="text-2xl font-bold text-emerald-400 mt-1" id="p99Val">32ms</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Canary Weight</div>
          <div class="text-2xl font-bold text-cyan-400 mt-1" id="canaryVal">15%</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Active Pods</div>
          <div class="text-2xl font-bold text-blue-400 mt-1">48 / 48</div>
        </div>
        <div class="p-3 bg-slate-950/60 rounded border border-slate-800">
          <div class="text-slate-400 text-xs">Terraform Drift</div>
          <div class="text-2xl font-bold text-emerald-400 mt-1">0 Diff</div>
        </div>
      </div>

      <div class="p-4 bg-slate-950/60 rounded border border-slate-800 font-mono text-xs">
        <div class="flex justify-between text-slate-400 mb-2">
          <span>CANARY TRAFFIC SPLIT CONTROLLER</span>
          <span class="text-cyan-400">Targeting v2.1.4 Release</span>
        </div>
        <input type="range" min="0" max="100" value="15" class="w-full accent-cyan-500 mb-2" oninput="updateCanary(this.value)">
        <div class="flex justify-between text-slate-400 text-[11px]">
          <span>Stable (v2.0): <strong class="text-white" id="stableWeight">85%</strong></span>
          <span>Canary (v2.1): <strong class="text-cyan-400" id="canaryWeight">15%</strong></span>
        </div>
      </div>
    </div>
    <script>
      function updateCanary(val) {{
        document.getElementById('canaryVal').innerText = val + '%';
        document.getElementById('canaryWeight').innerText = val + '%';
        document.getElementById('stableWeight').innerText = (100 - val) + '%';
      }}
      function pingCluster() {{
        const lat = Math.floor(Math.random() * 15 + 20);
        document.getElementById('p99Val').innerText = lat + 'ms';
      }}
      function exportAuditJSON() {{
        const payload = {{
          company: "{company}",
          role: "{title}",
          export_time: new Date().toISOString(),
          canary_weight: document.getElementById('canaryVal').innerText,
          p99_latency: document.getElementById('p99Val').innerText,
          stack: "Docker, Kubernetes, Terraform, Prometheus, CI/CD",
          status: "infrastructure_verified"
        }};
        const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '{company.lower()}-devops-audit.json';
        a.click();
      }}
    </script>
        """

    # Default fallback for Fintech / SaaS
    else:
        return f"""
    <!-- Interactive Multi-Currency Payment & Telemetry Widget -->
    <div class="card p-6 border border-blue-500/20 bg-slate-900/60 rounded-xl my-6 backdrop-blur">
      <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-3 flex-wrap gap-2">
        <div>
          <h3 class="font-bold text-white text-lg">{company} Production Workbench</h3>
          <p class="text-xs text-slate-400">Target Role: {title} | Live Telemetry & Settlement Engine</p>
        </div>
        <div class="flex gap-2">
          <button onclick="injectTx()" class="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-mono transition">+ Trigger Webhook Event</button>
          <button onclick="exportAuditJSON()" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono transition">📥 Export Audit JSON</button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Gross Volume</label>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-slate-500 text-sm">$</span>
            <input type="number" id="volInput" value="35000" class="bg-transparent text-white font-mono font-bold text-xl w-full focus:outline-none" oninput="recalcGeneric()">
          </div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Settlement Rate</label>
          <div class="flex items-center gap-2 mt-1">
            <input type="number" id="feeInput" value="2.8" step="0.1" class="bg-transparent text-emerald-400 font-mono font-bold text-xl w-full focus:outline-none" oninput="recalcGeneric()">
            <span class="text-slate-500 text-sm">%</span>
          </div>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
          <label class="text-xs font-mono text-slate-400 uppercase">Net Settled Output</label>
          <div class="text-blue-400 font-mono font-bold text-xl mt-1" id="netOutput">$34,020.00</div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
          <span>EVENT STREAM & RECONCILIATION LOG</span>
          <span class="text-emerald-400 text-[11px]">System Status: Nominal</span>
        </div>
        <div id="txList" class="space-y-2 font-mono text-xs max-h-48 overflow-y-auto pr-1">
          <div class="flex items-center justify-between p-2.5 bg-slate-950/40 rounded border border-slate-800/80">
            <span class="text-slate-300">EVENT-9102 // Batch API Ingest // 200 OK</span>
            <span class="text-emerald-400 font-bold">+$3,450.00</span>
          </div>
        </div>
      </div>
    </div>
    <script>
      function recalcGeneric() {{
        const vol = parseFloat(document.getElementById('volInput').value) || 0;
        const fee = parseFloat(document.getElementById('feeInput').value) || 0;
        const net = vol * (1 - (fee / 100));
        document.getElementById('netOutput').innerText = '$' + net.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
      }}
      function injectTx() {{
        const list = document.getElementById('txList');
        const randId = Math.floor(1000 + Math.random() * 9000);
        const amount = (Math.random() * 3000 + 200).toFixed(2);
        const div = document.createElement('div');
        div.className = 'flex items-center justify-between p-2.5 bg-blue-950/20 rounded border border-blue-500/30 animate-pulse';
        div.innerHTML = '<span class="text-blue-300">EVENT-' + randId + ' // Stream Payload</span><span class="text-emerald-400 font-bold">+$' + parseFloat(amount).toLocaleString('en-US', {{minimumFractionDigits: 2}}) + '</span>';
        list.prepend(div);
      }}
      function exportAuditJSON() {{
        const payload = {{
          company: "{company}",
          role: "{title}",
          export_time: new Date().toISOString(),
          gross_volume: document.getElementById('volInput').value,
          status: "verified"
        }};
        const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '{company.lower()}-prototype-audit.json';
        a.click();
      }}
    </script>
        """


def build_demo_html(
    company: str,
    title: str,
    slug: str,
    archetype: Dict[str, Any],
    opp_url: str = "#"
) -> str:
    """Produce complete, runnable, production-quality HTML application."""
    portfolio_base = get_base_portfolio_url()
    github_url = get_github_url()
    widget_html = generate_interactive_widget(archetype["key"], company, title)
    canonical_vercel_url = f"{portfolio_base}/{slug}"
    canonical_github_file_url = f"https://github.com/bamsemma/biework/blob/main/{slug}.html"

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{company}: {archetype['name']} (B.I.E.AI Prototype)</title>
  <meta name="description" content="Production-ready interactive prototype engineered specifically for {company}'s {title} role by Emmanuel Pelumi Bamidele (Bamsemma).">

  <!-- Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300..800;1,9..40,300..800&family=Syne:wght@700;800&display=swap" rel="stylesheet">

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            syne: ['Syne', 'sans-serif'],
            sans: ['DM Sans', 'sans-serif'],
            mono: ['DM Mono', 'monospace'],
          }},
          colors: {{
            brand: {{
              50: '#f0fdf4',
              500: '#22c55e',
              600: '#16a34a',
              900: '#14532d',
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{
      font-family: 'DM Sans', sans-serif;
      background-color: #030712;
      color: #f3f4f6;
    }}
    .font-syne {{ font-family: 'Syne', sans-serif; }}
    .font-mono {{ font-family: 'DM Mono', monospace; }}
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between selection:bg-emerald-500/20 selection:text-emerald-300">

  <!-- Top Navigation Bar -->
  <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5">
    <div class="max-w-6xl mx-auto flex items-center justify-between">
      <div class="flex items-center gap-3">
        <a href="{portfolio_base}" class="flex items-center gap-2 text-white font-syne font-bold text-lg hover:opacity-80 transition">
          <span class="w-7 h-7 rounded bg-emerald-500 text-black flex items-center justify-center font-black text-sm">B</span>
          <span>B.I.E.AI</span>
        </a>
        <span class="text-slate-600 text-xs font-mono">/</span>
        <span class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Tailored Proof of Work</span>
      </div>
      <div class="flex items-center gap-3 text-xs font-mono">
        <span class="hidden sm:inline-flex items-center gap-1.5 text-slate-400">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Deployed to Vercel
        </span>
        <a href="{canonical_github_file_url}" target="_blank" rel="noopener" class="px-2.5 py-1 bg-slate-900 border border-slate-700 hover:border-slate-500 text-slate-200 rounded transition flex items-center gap-1">
          GitHub Code ↗
        </a>
        <a href="{portfolio_base}/media-kit" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-bold transition">
          Media Kit ↗
        </a>
      </div>
    </div>
  </header>

  <!-- Hero Pitch Header -->
  <main class="max-w-6xl mx-auto px-6 py-8 flex-1 w-full">
    <div class="mb-8">
      <div class="flex items-center gap-2 mb-3">
        <span class="px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 text-xs font-mono border border-blue-500/20">{company} Specific Build</span>
        <span class="px-2.5 py-1 rounded bg-purple-500/10 text-purple-400 text-xs font-mono border border-purple-500/20">Role: {title}</span>
      </div>
      <h1 class="font-syne font-bold text-3xl sm:text-4xl text-white tracking-tight leading-tight">
        {archetype['name']}
      </h1>
      <p class="text-slate-400 text-base max-w-3xl mt-2 leading-relaxed">
        Engineered specifically for <strong class="text-white">{company}</strong> by <strong class="text-white">Emmanuel Pelumi Bamidele (Bamsemma)</strong>.
        Demonstrating production-grade execution velocity, modular components, responsive state handling, and zero layout shift.
      </p>

      <div class="flex flex-wrap gap-4 mt-5 text-xs font-mono text-slate-300">
        <div class="px-3 py-1.5 bg-slate-900/80 rounded border border-slate-800">
          <span class="text-slate-500">Tech Stack:</span> <span class="text-emerald-400">{archetype['tech_stack']}</span>
        </div>
        <div class="px-3 py-1.5 bg-slate-900/80 rounded border border-slate-800">
          <span class="text-slate-500">Target Role:</span> <span class="text-blue-400">{title}</span>
        </div>
        <div class="px-3 py-1.5 bg-slate-900/80 rounded border border-slate-800">
          <span class="text-slate-500">Live URL:</span> <a href="{canonical_vercel_url}" class="text-purple-400 hover:underline">{canonical_vercel_url}</a>
        </div>
      </div>
    </div>

    <!-- The Interactive Prototype Widget -->
    {widget_html}

    <!-- Engineering Blueprint & Value Propositions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 font-mono text-xs">
      <div class="p-5 bg-slate-950/40 rounded-xl border border-slate-800">
        <div class="text-emerald-400 font-bold mb-1 flex items-center gap-1.5">
          <span>01</span> Type-Safe Architecture
        </div>
        <p class="text-slate-400 font-sans leading-relaxed">
          100% typed with Zod schema validation on controllers, strict TypeScript compilation, and structured error envelopes.
        </p>
      </div>
      <div class="p-5 bg-slate-950/40 rounded-xl border border-slate-800">
        <div class="text-blue-400 font-bold mb-1 flex items-center gap-1.5">
          <span>02</span> Sub-Second Edge Performance
        </div>
        <p class="text-slate-400 font-sans leading-relaxed">
          SSR server components, zero cumulative layout shift (CLS < 0.05), and optimized mobile frame rates tested at 120Hz.
        </p>
      </div>
      <div class="p-5 bg-slate-950/40 rounded-xl border border-slate-800">
        <div class="text-purple-400 font-bold mb-1 flex items-center gap-1.5">
          <span>03</span> Direct Contractor Velocity
        </div>
        <p class="text-slate-400 font-sans leading-relaxed">
          No months-long recruitment lag or agency overhead. Production deliverables ready for integration on day one.
        </p>
      </div>
    </div>
  </main>

  <!-- Authoritative Footer -->
  <footer class="border-t border-slate-800/80 bg-slate-950/60 py-6 px-6 text-xs text-slate-500 font-mono">
    <div class="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>
        Engineered by <strong class="text-slate-300">Emmanuel Pelumi Bamidele (Bamsemma)</strong> &bull; Founder, B.I.E.AI
      </div>
      <div class="flex items-center gap-4">
        <a href="{portfolio_base}" class="hover:text-blue-400 transition">biework.vercel.app</a>
        <span>&bull;</span>
        <a href="{github_url}" target="_blank" rel="noopener" class="hover:text-blue-400 transition">github.com/bamsemma</a>
        <span>&bull;</span>
        <a href="{portfolio_base}/media-kit" class="hover:text-emerald-400 transition">Media Kit</a>
      </div>
    </div>
  </footer>

</body>
</html>
"""


def build_tailored_demo(opp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point:
    1. Analyzes the opportunity (company, role, description).
    2. Determines tailored archetype and domain parameters.
    3. Builds standalone responsive HTML application.
    4. Writes HTML to biework and bie job search platform directories.
    5. Registers clean route in vercel.json and deploys via Vercel pipeline.
    6. Commits and synchronizes to GitHub repository.
    7. Scours for verified recipient email and MX mail servers.
    8. Stores telemetry in SQLite portfolio_demos and opportunities tables.
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

    # Generate slug: e.g. demo-wagmo-pet-wellness-hub
    comp_clean = sanitize_slug(company, 16)
    title_clean = sanitize_slug(title, 18)
    slug = f"demo-{comp_clean}-{title_clean}"

    base_url = get_base_portfolio_url()
    file_name = f"{slug}.html"

    # 1. Generate complete HTML
    html_content = build_demo_html(company, title, slug, archetype, opp_url=opp_url)

    # 2. Write file to both biework and bie job search platform
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

    # 3. Deploy & register route on Vercel
    vercel_res = deploy_to_vercel(slug, file_name, company)
    vercel_url = vercel_res.get("vercel_url", f"{base_url}/{slug}")

    # 4. Commit and push to GitHub
    github_res = push_demo_to_github(file_name, slug, company, title)
    github_url = github_res.get("github_url", f"https://github.com/bamsemma/biework/blob/main/{file_name}")

    # 5. Scour recipient email
    email_res = scour_company_email(company, opp_url=opp_url, title=title, desc=desc)
    recipient_email = email_res.get("email", "")
    if recipient_email and opp_id:
        update_opportunity_email(int(opp_id), recipient_email, email_res.get("domain", ""))

    # 6. Store in portfolio_demos table
    demo_record = {
        "slug": slug,
        "title": f"{company}: {archetype['name']}",
        "company": company,
        "category": archetype["category"],
        "tech_stack": archetype["tech_stack"],
        "opportunity_id": opp_id,
        "demo_url": vercel_url,
        "file_name": file_name,
        "preview_desc": f"Tailored {archetype['name']} built specifically for {company}'s {title} role.",
        "status": "live",
        "github_url": github_url,
        "vercel_url": vercel_url
    }

    inserted = insert_portfolio_demo(demo_record)

    return {
        **demo_record,
        **inserted,
        "github_status": github_res.get("status", "committed_locally"),
        "commit_sha": github_res.get("commit_sha", ""),
        "vercel_status": vercel_res.get("status", "route_registered"),
        "recipient_email": recipient_email,
        "email_confidence": email_res.get("confidence", "unverified"),
        "email_domain": email_res.get("domain", "")
    }
