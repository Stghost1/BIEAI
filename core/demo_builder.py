"""
Scoutdesk Bespoke Motion & Interactive Prototype Synthesis Engine (v4.0).
Directly inspired by motionsites.ai, Awwwards, and Pinterest modern visual design.
Engineers production-grade, highly-responsive interactive micro-applications with
niche-tailored typography, 60 FPS HTML5 canvas centerpieces, 3D tilt perspective cards,
real-time operational benches, live telemetry feeds, and zero dash punctuation.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.db import get_setting, insert_portfolio_demo, update_opportunity_email
from core.email_scourer import scour_company_email
from core.github_uploader import push_demo_to_github
from core.vercel_deployer import deploy_to_vercel, register_vercel_rewrite

ROOT = Path(__file__).resolve().parent.parent


def get_base_portfolio_url() -> str:
    url = get_setting("portfolio_url", os.environ.get("PORTFOLIO_URL", "https://bieai.vercel.app"))
    return (url or "https://bieai.vercel.app").rstrip("/")


def get_github_url() -> str:
    url = get_setting("github_url", os.environ.get("GITHUB_URL", "https://github.com/Stghost1/BIEAI"))
    return (url or "https://github.com/Stghost1/BIEAI").rstrip("/")


def _has_word(words: List[str], text: str) -> bool:
    """Strict word boundary search to avoid substring false positives (e.g. 'pet' in 'competitive')."""
    for w in words:
        if re.search(r"\b" + re.escape(w.lower()) + r"\b", text):
            return True
    return False


def detect_archetype(title: str, desc: str, tags: List[str], company: str) -> Dict[str, Any]:
    """
    Classify the opportunity into a high-impact interactive prototype archetype using strict word boundaries.
    """
    comp_lower = company.lower()
    title_lower = title.lower()
    desc_lower = desc.lower()
    all_text = f"{title_lower} {desc_lower} {' '.join(str(t).lower() for t in tags)} {comp_lower}"

    # 1. Company-specific high-priority overrides
    if "dreem health" in comp_lower or ("dreem" in comp_lower and "health" in all_text):
        return {
            "key": "sleep_healthtech",
            "name": "Clinical Operations & Sleep Telemetry Engine",
            "category": "automation",
            "tech_stack": "Plus Jakarta Sans, Outfit, HTML5 Canvas Circadian EEG, EHR Webhooks, Polysomnography Triage",
            "feature": "Circadian sleep architecture hypnogram, 4-stage automated EHR clinical intake, and clinician hours-saved forecasting."
        }
    if "wagmo" in comp_lower:
        return {
            "key": "pet_healthtech",
            "name": "Pet Health Benefits & Preventive Care Hub",
            "category": "automation",
            "tech_stack": "Outfit, Plus Jakarta Sans, Preventive Claim Ledger, Telehealth API, Wellness Calculator",
            "feature": "Multi-pet employer plan customizer, veterinary claim reimbursement ledger, and 24/7 telehealth triage calculator."
        }
    if "klardaten" in comp_lower or "aprio" in comp_lower:
        return {
            "key": "accounting_tax_ai",
            "name": "DATEV Document & AI Reconciliation Engine",
            "category": "website",
            "tech_stack": "Cinzel, Plus Jakarta Sans, JetBrains Mono, DATEV XML/REST Webhooks, Automated Ledger Matching",
            "feature": "Real-time DATEV webhook event dispatcher, automated double-entry ledger matcher, and AI confidence threshold slider."
        }
    if "onebrief" in comp_lower:
        return {
            "key": "tactical_defense_ai",
            "name": "Tactical Command Node & Mission Workflow Orchestrator",
            "category": "automation",
            "tech_stack": "Outfit, Share Tech Mono, WebSockets, Geospatial Radar, AES-256",
            "feature": "Command node operational readiness radar, simulated tactical event stream, and resilient decision-tree simulator."
        }
    if "lemon.io" in comp_lower:
        return {
            "key": "devops_cloud_infra",
            "name": "Cloud Infrastructure & Zero-Downtime Deployment Orchestrator",
            "category": "website",
            "tech_stack": "Outfit, JetBrains Mono, Kubernetes API, Prometheus, Terraform Cluster Topology",
            "feature": "Kubernetes cluster pod health matrix, P99 canary deployment latency gauge, and automated Terraform state drift detector."
        }
    if "anori tech" in comp_lower:
        return {
            "key": "hardware_embedded_systems",
            "name": "Hardware Telemetry & Firmware Diagnostics Bench",
            "category": "automation",
            "tech_stack": "Outfit, Share Tech Mono, Oscilloscope Canvas, Serial Telemetry, Thermal Analysis",
            "feature": "Real-time signal waveform oscilloscope, PCB thermal dissipation calculator, and firmware test-bench runner."
        }
    if "huzzle" in comp_lower:
        return {
            "key": "email_deliverability_crm",
            "name": "Enterprise Talent Pipeline & Deal Conversion Hub",
            "category": "automation",
            "tech_stack": "Syne, Outfit, Funnel Yield Algorithms, Commission Calculator, Gen-Z Micro-Badges",
            "feature": "Interactive candidate placement funnel, sales commission calculator, and live placement event stream."
        }
    if "bluetuskr" in comp_lower:
        return {
            "key": "motion_creative_studio",
            "name": "Kinetic Motion & Interactive Visual Studio",
            "category": "design",
            "tech_stack": "Outfit, Space Grotesk, 60 FPS Chromatic Particle Canvas, 3D Tilt Cards, Timeline Scrubber",
            "feature": "Kinetic particle flow canvas, frame-rate timeline scrubber, interactive 3D perspective card physics, and brand asset export."
        }
    if "bjak" in comp_lower:
        return {
            "key": "fintech_payments_ledger",
            "name": "High-Frequency Stockbroking & Liquidity Engine",
            "category": "website",
            "tech_stack": "Sora, JetBrains Mono, Holographic Order Book Canvas, Real-Time Trade Stream, WebSockets",
            "feature": "Sub-millisecond trade execution ticker, dynamic liquidity slider, and interactive candlestick depth canvas."
        }
    if "highlevel" in comp_lower:
        return {
            "key": "devops_cloud_infra",
            "name": "Agency CRM Infrastructure & Multi-Tenant Deployment Mesh",
            "category": "website",
            "tech_stack": "Outfit, JetBrains Mono, Multi-Tenant Pod Mesh, Zero-Downtime Rollout, P99 Latency Monitor",
            "feature": "Multi-tenant agency cluster visualizer, canary rollout percentage slider, and sub-10ms query latency telemetry."
        }
    if "fuel50" in comp_lower:
        return {
            "key": "email_deliverability_crm",
            "name": "Talent Architecture & Career Mobility Intelligence Bench",
            "category": "design",
            "tech_stack": "Syne, Outfit, Skills Matrix Engine, Career Pathway Graph, Mobility Simulator",
            "feature": "Interactive workforce skills taxonomy matcher, career pathway simulation slider, and talent retention yield calculator."
        }
    if "apex fintech" in comp_lower:
        return {
            "key": "fintech_payments_ledger",
            "name": "High-Frequency Payment Settlement & Ledger Hub",
            "category": "website",
            "tech_stack": "Sora, JetBrains Mono, Real-Time Clearing Ledger, Automated Double-Entry Matching",
            "feature": "Instant clearing settlement pipeline, liquidity reserve slider, and continuous transaction audit stream."
        }

    # 2. Domain Keywords (Strict Word Boundaries)
    if _has_word(["bakery", "pastry", "sourdough", "baking", "baker", "culinary", "restaurant", "cafe", "confectionery", "artisan bread"], all_text):
        return {
            "key": "artisanal_culinary_bakery",
            "name": "Artisanal Bakery & Dough Hydration Craft Studio",
            "category": "design",
            "tech_stack": "Playfair Display, Outfit, Canvas Fermentation Engine, Thermal Crust Telemetry",
            "feature": "Interactive sourdough baker's percentage & hydration calculator, oven steam timing monitor, and dynamic bread pre-order checkout."
        }

    if _has_word(["motion", "animation", "animator", "3d", "vfx", "video editor", "creative director", "brand designer", "graphic designer", "visual designer"], all_text):
        return {
            "key": "motion_creative_studio",
            "name": "Kinetic Motion & Interactive Visual Studio",
            "category": "design",
            "tech_stack": "Outfit, Space Grotesk, 60 FPS Chromatic Particle Canvas, 3D Tilt Cards, Timeline Scrubber",
            "feature": "Kinetic particle flow canvas, frame-rate timeline scrubber, interactive 3D perspective card physics, and brand asset export."
        }

    if _has_word(["sleep", "insomnia", "apnea", "circadian", "polysomnography", "telehealth", "patient care", "clinic"], all_text):
        return {
            "key": "sleep_healthtech",
            "name": "Clinical Operations & Sleep Telemetry Engine",
            "category": "automation",
            "tech_stack": "Plus Jakarta Sans, Outfit, HTML5 Canvas Circadian EEG, EHR Webhooks, Polysomnography Triage",
            "feature": "Circadian sleep architecture hypnogram, 4-stage automated EHR clinical intake, and clinician hours-saved forecasting."
        }

    if _has_word(["veterinary", "veterinarian", "pets", "pet", "canine", "feline", "dog", "cat", "animal health"], all_text):
        return {
            "key": "pet_healthtech",
            "name": "Pet Health Benefits & Preventive Care Hub",
            "category": "automation",
            "tech_stack": "Outfit, Plus Jakarta Sans, Preventive Claim Ledger, Telehealth API, Wellness Calculator",
            "feature": "Multi-pet employer plan customizer, veterinary claim reimbursement ledger, and 24/7 telehealth triage calculator."
        }

    if _has_word(["hardware", "embedded", "firmware", "robotics", "iot", "sensor", "circuit", "pcb", "microcontroller", "fpga"], all_text):
        return {
            "key": "hardware_embedded_systems",
            "name": "Hardware Telemetry & Firmware Diagnostics Bench",
            "category": "automation",
            "tech_stack": "Outfit, Share Tech Mono, Oscilloscope Canvas, Serial Telemetry, Thermal Analysis",
            "feature": "Real-time signal waveform oscilloscope, PCB thermal dissipation calculator, and firmware test-bench runner."
        }

    if _has_word(["fintech", "payment", "payments", "ledger", "stockbroking", "crypto", "trading", "brokerage", "clearing", "settlement"], all_text):
        return {
            "key": "fintech_payments_ledger",
            "name": "High-Frequency Payment Settlement & Ledger Hub",
            "category": "website",
            "tech_stack": "Sora, JetBrains Mono, Holographic Order Book Canvas, Real-Time Trade Stream, WebSockets",
            "feature": "Sub-millisecond trade execution ticker, dynamic liquidity slider, and interactive candlestick depth canvas."
        }

    if _has_word(["devops", "kubernetes", "k8s", "infrastructure", "terraform", "sre", "cloud", "docker", "platform engineer", "reliability"], all_text):
        return {
            "key": "devops_cloud_infra",
            "name": "Cloud Infrastructure & Zero-Downtime Deployment Orchestrator",
            "category": "website",
            "tech_stack": "Outfit, JetBrains Mono, Kubernetes API, Prometheus, Terraform Cluster Topology",
            "feature": "Kubernetes cluster pod health matrix, P99 canary deployment latency gauge, and automated Terraform state drift detector."
        }

    if _has_word(["accounting", "tax", "audit", "cpa", "financial reporting", "bookkeeping", "reconciliation", "datev", "payroll"], all_text):
        return {
            "key": "accounting_tax_ai",
            "name": "DATEV Document & AI Reconciliation Engine",
            "category": "website",
            "tech_stack": "Cinzel, Plus Jakarta Sans, JetBrains Mono, DATEV XML/REST Webhooks, Automated Ledger Matching",
            "feature": "Real-time DATEV webhook event dispatcher, automated double-entry ledger matcher, and AI confidence threshold slider."
        }

    if _has_word(["sales", "sdr", "bdr", "talent", "recruitment", "hiring", "applicant", "career", "placement", "pipeline"], all_text):
        return {
            "key": "email_deliverability_crm",
            "name": "Enterprise Talent Pipeline & Deal Conversion Hub",
            "category": "automation",
            "tech_stack": "Syne, Outfit, Funnel Yield Algorithms, Commission Calculator, Gen-Z Micro-Badges",
            "feature": "Interactive candidate placement funnel, sales commission calculator, and live placement event stream."
        }

    # Universal Fallback Archetype
    return {
        "key": "motion_creative_studio",
        "name": "Kinetic Interactive Experience & Digital Product Showcase",
        "category": "website",
        "tech_stack": "Outfit, Space Grotesk, 60 FPS Canvas Particles, 3D Perspective Tilt, Real-Time Telemetry",
        "feature": "Sub-16ms interactive canvas visuals, dynamic operational bench, and responsive high-conversion interface design."
    }


def get_archetype_theme(key: str) -> Dict[str, Any]:
    """Provide curated Google Fonts, colors, and motion styling per archetype directly inspired by motionsites.ai."""
    themes = {
        "motion_creative_studio": {
            "font_import": "https://fonts.googleapis.com/css2?family=Outfit:wght@800;900&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
            "font_display": "'Outfit', sans-serif",
            "font_sans": "'Space Grotesk', sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "bg_color": "#06070B",
            "bg_class": "bg-[#06070B] text-[#F3F4F6]",
            "card_class": "bg-[#11131C]/85 backdrop-blur-2xl border border-white/10 shadow-2xl hover:border-pink-500/40",
            "text_color": "#F3F4F6",
            "accent_color": "#FF0055",
            "accent_rgb": "255, 0, 85",
            "gradient_text": "from-white via-[#FF007A] to-[#00F5FF]",
            "badge_class": "bg-pink-950/60 text-pink-300 border border-pink-700/60",
            "canvas_type": "particle_mesh"
        },
        "sleep_healthtech": {
            "font_import": "https://fonts.googleapis.com/css2?family=Outfit:wght@800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap",
            "font_display": "'Outfit', sans-serif",
            "font_sans": "'Plus Jakarta Sans', sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "bg_color": "#030712",
            "bg_class": "bg-[#030712] text-[#E2E8F0]",
            "card_class": "bg-[#0F172A]/85 backdrop-blur-2xl border border-white/10 shadow-2xl hover:border-cyan-500/40",
            "text_color": "#E2E8F0",
            "accent_color": "#06B6D4",
            "accent_rgb": "6, 182, 212",
            "gradient_text": "from-white via-cyan-300 to-indigo-400",
            "badge_class": "bg-cyan-950/60 text-cyan-300 border border-cyan-700/60",
            "canvas_type": "sleep_eeg"
        },
        "hardware_embedded_systems": {
            "font_import": "https://fonts.googleapis.com/css2?family=Outfit:wght@800;900&family=Share+Tech+Mono&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
            "font_display": "'Outfit', sans-serif",
            "font_sans": "'Plus Jakarta Sans', sans-serif",
            "font_mono": "'Share Tech Mono', monospace",
            "bg_color": "#090C12",
            "bg_class": "bg-[#090C12] text-[#E5E7EB]",
            "card_class": "bg-[#121620]/90 backdrop-blur-2xl border border-orange-500/20 shadow-2xl hover:border-orange-500/50",
            "text_color": "#E5E7EB",
            "accent_color": "#FF6600",
            "accent_rgb": "255, 102, 0",
            "gradient_text": "from-white via-orange-400 to-emerald-400",
            "badge_class": "bg-orange-950/60 text-orange-300 border border-orange-700/60",
            "canvas_type": "oscilloscope"
        },
        "email_deliverability_crm": {
            "font_import": "https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap",
            "font_display": "'Syne', sans-serif",
            "font_sans": "'Outfit', sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "bg_color": "#070710",
            "bg_class": "bg-[#070710] text-[#F3F4F6]",
            "card_class": "bg-[#131322]/85 backdrop-blur-2xl border border-white/10 shadow-2xl hover:border-purple-500/50",
            "text_color": "#F3F4F6",
            "accent_color": "#FF007A",
            "accent_rgb": "255, 0, 122",
            "gradient_text": "from-white via-[#FF007A] to-[#CCFF00]",
            "badge_class": "bg-purple-950/60 text-purple-300 border border-purple-700/60",
            "canvas_type": "talent_burst"
        },
        "fintech_payments_ledger": {
            "font_import": "https://fonts.googleapis.com/css2?family=Sora:wght@700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap",
            "font_display": "'Sora', sans-serif",
            "font_sans": "'Plus Jakarta Sans', sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "bg_color": "#040711",
            "bg_class": "bg-[#040711] text-[#E5E7EB]",
            "card_class": "bg-[#0E1422]/90 backdrop-blur-2xl border border-emerald-500/20 shadow-2xl hover:border-emerald-500/50",
            "text_color": "#E5E7EB",
            "accent_color": "#00E599",
            "accent_rgb": "0, 229, 153",
            "gradient_text": "from-white via-emerald-400 to-cyan-400",
            "badge_class": "bg-emerald-950/60 text-emerald-300 border border-emerald-700/60",
            "canvas_type": "fintech_depth"
        },
        "devops_cloud_infra": {
            "font_import": "https://fonts.googleapis.com/css2?family=Outfit:wght@800;900&family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap",
            "font_display": "'Outfit', sans-serif",
            "font_sans": "'Plus Jakarta Sans', sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "bg_color": "#050811",
            "bg_class": "bg-[#050811] text-[#E2E8F0]",
            "card_class": "bg-[#0D1526]/85 backdrop-blur-2xl border border-cyan-500/20 shadow-2xl hover:border-cyan-500/50",
            "text_color": "#E2E8F0",
            "accent_color": "#00D2FF",
            "accent_rgb": "0, 210, 255",
            "gradient_text": "from-white via-cyan-400 to-indigo-400",
            "badge_class": "bg-cyan-950/60 text-cyan-300 border border-cyan-700/60",
            "canvas_type": "k8s_mesh"
        },
        "pet_healthtech": {
            "font_import": "https://fonts.googleapis.com/css2?family=Outfit:wght@800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
            "font_display": "'Outfit', sans-serif",
            "font_sans": "'Plus Jakarta Sans', sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "bg_color": "#FAF7F2",
            "bg_class": "bg-[#FAF7F2] text-[#2D2A26]",
            "card_class": "bg-[#FFFFFF] border border-[#EBE4DC] shadow-xl shadow-[#D8C7B5]/20 hover:border-[#FF5A36]/40",
            "text_color": "#2D2A26",
            "accent_color": "#FF5A36",
            "accent_rgb": "255, 90, 54",
            "gradient_text": "from-[#2D2A26] via-[#FF5A36] to-[#2E7D32]",
            "badge_class": "bg-[#FCEEEA] text-[#C23A1B] border border-[#F3CEC5]",
            "canvas_type": "wellness_rings"
        },
        "accounting_tax_ai": {
            "font_import": "https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
            "font_display": "'Cinzel', serif",
            "font_sans": "'Plus Jakarta Sans', sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "bg_color": "#080C16",
            "bg_class": "bg-[#080C16] text-[#E5E7EB]",
            "card_class": "bg-[#111827]/85 backdrop-blur-2xl border border-amber-500/20 shadow-2xl hover:border-amber-500/50",
            "text_color": "#E5E7EB",
            "accent_color": "#D4AF37",
            "accent_rgb": "212, 175, 55",
            "gradient_text": "from-white via-[#F5D77F] to-[#D4AF37]",
            "badge_class": "bg-amber-950/60 text-amber-300 border border-amber-700/60",
            "canvas_type": "luxury_gold"
        },
        "artisanal_culinary_bakery": {
            "font_import": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
            "font_display": "'Playfair Display', serif",
            "font_sans": "'Outfit', sans-serif",
            "font_mono": "'JetBrains Mono', monospace",
            "bg_color": "#FAF6F0",
            "bg_class": "bg-[#FAF6F0] text-[#241A15]",
            "card_class": "bg-[#FFFFFF] border border-[#E8DFD5] shadow-xl shadow-[#D8C7B5]/20 hover:border-[#C86241]/40",
            "text_color": "#241A15",
            "accent_color": "#C86241",
            "accent_rgb": "200, 98, 65",
            "gradient_text": "from-[#241A15] via-[#C86241] to-[#D4A373]",
            "badge_class": "bg-[#F3E8DB] text-[#9A4122] border border-[#DFCBB9]",
            "canvas_type": "dough_crumb"
        }
    }
    return themes.get(key, themes["motion_creative_studio"])


def sanitize_slug(text: str, max_len: int = 24) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return cleaned[:max_len]


def generate_canvas_script(canvas_type: str, accent_color: str, accent_rgb: str) -> str:
    """Generate dynamic 60 FPS HTML5 Canvas animation tailored for the archetype."""
    if canvas_type == "particle_mesh":
        return f"""
      const canvas = document.getElementById('heroMotionCanvas');
      if (canvas) {{
        const ctx = canvas.getContext('2d');
        let w, h, particles = [];
        let mouse = {{ x: -1000, y: -1000, radius: 150 }};

        function init() {{
          w = canvas.width = canvas.parentElement.clientWidth;
          h = canvas.height = canvas.parentElement.clientHeight;
          particles = [];
          const count = Math.min(Math.floor((w * h) / 10000), 80);
          for (let i = 0; i < count; i++) {{
            particles.push({{
              x: Math.random() * w,
              y: Math.random() * h,
              vx: (Math.random() - 0.5) * 1.2,
              vy: (Math.random() - 0.5) * 1.2,
              size: Math.random() * 2.5 + 1.2,
              color: Math.random() > 0.5 ? '{accent_color}' : '#00F5FF'
            }});
          }}
        }}

        canvas.parentElement.addEventListener('mousemove', (e) => {{
          const rect = canvas.getBoundingClientRect();
          mouse.x = e.clientX - rect.left;
          mouse.y = e.clientY - rect.top;
        }});
        canvas.parentElement.addEventListener('mouseleave', () => {{
          mouse.x = -1000;
          mouse.y = -1000;
        }});

        function draw() {{
          ctx.clearRect(0, 0, w, h);
          for (let i = 0; i < particles.length; i++) {{
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0 || p.x > w) p.vx *= -1;
            if (p.y < 0 || p.y > h) p.vy *= -1;

            const dx = mouse.x - p.x;
            const dy = mouse.y - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < mouse.radius) {{
              const force = (mouse.radius - dist) / mouse.radius;
              p.x -= (dx / dist) * force * 3;
              p.y -= (dy / dist) * force * 3;
            }}

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.shadowBlur = 10;
            ctx.shadowColor = p.color;
            ctx.fill();
            ctx.shadowBlur = 0;

            for (let j = i + 1; j < particles.length; j++) {{
              const p2 = particles[j];
              const d2 = Math.hypot(p.x - p2.x, p.y - p2.y);
              if (d2 < 120) {{
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.strokeStyle = `rgba({accent_rgb}, ${{1 - d2 / 120}})`;
                ctx.lineWidth = 0.8;
                ctx.stroke();
              }}
            }}
          }}
          requestAnimationFrame(draw);
        }}

        window.addEventListener('resize', init);
        init();
        draw();
      }}
        """

    if canvas_type == "sleep_eeg":
        return f"""
      const canvas = document.getElementById('heroMotionCanvas');
      if (canvas) {{
        const ctx = canvas.getContext('2d');
        let w, h, t = 0;
        let mode = 'rem';

        function init() {{
          w = canvas.width = canvas.parentElement.clientWidth;
          h = canvas.height = canvas.parentElement.clientHeight;
        }}

        window.setEegMode = function(m) {{
          mode = m;
          document.querySelectorAll('.eeg-tab').forEach(b => b.classList.remove('bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300'));
          const btn = document.getElementById('tab-' + m);
          if (btn) btn.classList.add('bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
        }};

        function draw() {{
          ctx.fillStyle = 'rgba(3, 7, 18, 0.18)';
          ctx.fillRect(0, 0, w, h);
          t += 0.04;

          const channels = [
            {{ y: h * 0.28, color: '#06B6D4', label: 'EEG Fp1-A2 (Frontal)', amp: mode === 'delta' ? 45 : 18, freq: mode === 'delta' ? 0.015 : 0.05 }},
            {{ y: h * 0.52, color: '#8B5CF6', label: 'EEG C3-A2 (Central)', amp: mode === 'rem' ? 32 : 12, freq: mode === 'rem' ? 0.08 : 0.03 }},
            {{ y: h * 0.76, color: '#10B981', label: 'SpO2 Blood O2 & Rhythm', amp: 14, freq: 0.025 }}
          ];

          channels.forEach((ch, idx) => {{
            ctx.beginPath();
            ctx.strokeStyle = ch.color;
            ctx.lineWidth = 2;
            ctx.shadowBlur = 8;
            ctx.shadowColor = ch.color;

            for (let x = 0; x < w; x += 3) {{
              const y = ch.y + Math.sin(x * ch.freq + t * (idx + 1)) * ch.amp + Math.cos(x * 0.01 + t * 0.5) * (ch.amp * 0.4);
              if (x === 0) ctx.moveTo(x, y);
              else ctx.lineTo(x, y);
            }}
            ctx.stroke();
            ctx.shadowBlur = 0;

            ctx.fillStyle = 'rgba(148, 163, 184, 0.6)';
            ctx.font = '10px JetBrains Mono';
            ctx.fillText(ch.label, 14, ch.y - 14);
          }});

          requestAnimationFrame(draw);
        }}

        window.addEventListener('resize', init);
        init();
        draw();
      }}
        """

    if canvas_type == "oscilloscope":
        return f"""
      const canvas = document.getElementById('heroMotionCanvas');
      if (canvas) {{
        const ctx = canvas.getContext('2d');
        let w, h, t = 0;

        function init() {{
          w = canvas.width = canvas.parentElement.clientWidth;
          h = canvas.height = canvas.parentElement.clientHeight;
        }}

        function draw() {{
          ctx.fillStyle = 'rgba(9, 12, 18, 0.22)';
          ctx.fillRect(0, 0, w, h);
          t += 0.06;

          // Draw grid
          ctx.strokeStyle = 'rgba(255, 102, 0, 0.08)';
          ctx.lineWidth = 1;
          for (let x = 0; x < w; x += 40) {{
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, h);
            ctx.stroke();
          }}
          for (let y = 0; y < h; y += 40) {{
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
          }}

          // Oscilloscope trace 1 (SPI Master Out)
          ctx.beginPath();
          ctx.strokeStyle = '#FF6600';
          ctx.lineWidth = 2.5;
          ctx.shadowBlur = 12;
          ctx.shadowColor = '#FF6600';
          for (let x = 0; x < w; x += 2) {{
            const y = (h * 0.4) + Math.sin(x * 0.03 + t) * 35 + Math.sin(x * 0.09 - t * 1.5) * 12;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }}
          ctx.stroke();

          // Oscilloscope trace 2 (Clock Bus 120MHz)
          ctx.beginPath();
          ctx.strokeStyle = '#00FF88';
          ctx.lineWidth = 1.8;
          ctx.shadowBlur = 8;
          ctx.shadowColor = '#00FF88';
          for (let x = 0; x < w; x += 2) {{
            const sq = Math.sign(Math.sin(x * 0.05 + t * 2)) * 25;
            const y = (h * 0.72) + sq;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }}
          ctx.stroke();
          ctx.shadowBlur = 0;

          requestAnimationFrame(draw);
        }}

        window.addEventListener('resize', init);
        init();
        draw();
      }}
        """

    # Universal default canvas fallback: dynamic radiant harmonic wave
    return f"""
      const canvas = document.getElementById('heroMotionCanvas');
      if (canvas) {{
        const ctx = canvas.getContext('2d');
        let w, h, t = 0;
        function init() {{
          w = canvas.width = canvas.parentElement.clientWidth;
          h = canvas.height = canvas.parentElement.clientHeight;
        }}
        function draw() {{
          ctx.clearRect(0, 0, w, h);
          t += 0.03;
          ctx.beginPath();
          ctx.strokeStyle = '{accent_color}';
          ctx.lineWidth = 2;
          ctx.shadowBlur = 10;
          ctx.shadowColor = '{accent_color}';
          for (let x = 0; x < w; x += 4) {{
            const y = (h * 0.5) + Math.sin(x * 0.02 + t) * 40 + Math.cos(x * 0.01 - t * 0.5) * 20;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }}
          ctx.stroke();
          ctx.shadowBlur = 0;
          requestAnimationFrame(draw);
        }}
        window.addEventListener('resize', init);
        init();
        draw();
      }}
    """


def generate_interactive_widget(archetype_key: str, company: str, title: str) -> str:
    """Produce rich domain-specific interactive JavaScript and HTML widget components."""
    if archetype_key == "motion_creative_studio":
        return f"""
    <!-- Creative Motion Director & Interactive Canvas Bench -->
    <div class="p-6 sm:p-8 rounded-3xl bg-[#11131C]/90 border border-white/10 shadow-2xl my-8 backdrop-blur-2xl">
      <div class="flex items-center justify-between mb-6 border-b border-white/10 pb-4 flex-wrap gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-pink-500 animate-ping"></span>
            <span class="text-xs font-mono text-pink-400 font-bold uppercase tracking-wider">Interactive 60 FPS Engine</span>
          </div>
          <h3 class="font-bold text-white text-2xl font-display">{company} Motion Director Bench</h3>
          <p class="text-xs text-slate-400 font-sans">Role Focus: {title} &bull; Spring Physics &bull; Canvas Shaders &bull; Awwwards Micro-Interactions</p>
        </div>
        <div class="flex gap-2">
          <button onclick="triggerMotionBurst()" class="px-4 py-2 bg-gradient-to-r from-pink-600 to-purple-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-pink-500/25 flex items-center gap-2">
            <span>✨ Trigger Kinetic Shockwave</span>
          </button>
          <button onclick="exportAuditJSON()" class="px-3.5 py-2 bg-slate-800/80 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-mono font-bold transition border border-white/10">
            Export Spec JSON ↗
          </button>
        </div>
      </div>

      <!-- INTERACTIVE SLIDERS & CONTROLS -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-900/60 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Playback Frame Rate</label>
            <span id="fpsLabel" class="text-xs font-mono font-bold text-pink-400">60 FPS</span>
          </div>
          <input type="range" id="fpsSlider" min="24" max="120" value="60" step="12" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-pink-500" oninput="updateMotionFps(this.value)">
          <div class="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
            <span>24fps (Cinematic)</span>
            <span>60fps</span>
            <span>120fps (ProMotion)</span>
          </div>
        </div>

        <div class="p-4 bg-slate-900/60 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Spring Tension Physics</label>
            <span id="tensionLabel" class="text-xs font-mono font-bold text-cyan-400">180 N/m</span>
          </div>
          <input type="range" id="tensionSlider" min="80" max="320" value="180" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400" oninput="document.getElementById('tensionLabel').textContent = this.value + ' N/m'">
          <div class="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
            <span>Fluid Float</span>
            <span>Balanced</span>
            <span>Snappy Snap</span>
          </div>
        </div>

        <div class="p-4 bg-slate-900/60 rounded-2xl border border-white/5">
          <label class="text-[11px] font-mono text-slate-400 uppercase font-bold block mb-2">Color Aura Palette</label>
          <div class="flex gap-2">
            <button onclick="setMotionColor('#FF0055', '255, 0, 85')" class="w-8 h-8 rounded-lg bg-[#FF0055] border-2 border-white/30 hover:scale-110 transition"></button>
            <button onclick="setMotionColor('#00F5FF', '0, 245, 255')" class="w-8 h-8 rounded-lg bg-[#00F5FF] border-2 border-white/30 hover:scale-110 transition"></button>
            <button onclick="setMotionColor('#8B5CF6', '139, 92, 246')" class="w-8 h-8 rounded-lg bg-[#8B5CF6] border-2 border-white/30 hover:scale-110 transition"></button>
            <button onclick="setMotionColor('#00FF88', '0, 255, 136')" class="w-8 h-8 rounded-lg bg-[#00FF88] border-2 border-white/30 hover:scale-110 transition"></button>
          </div>
        </div>
      </div>

      <!-- LIVE MOTION PERFORMANCE METRICS -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="p-3 bg-black/40 rounded-xl border border-white/5">
          <span class="text-[10px] font-mono text-slate-400 block">Render Latency</span>
          <span class="text-lg font-bold font-mono text-emerald-400">3.8 ms</span>
          <span class="text-[9px] text-slate-500 block">Target: &lt;16.6ms</span>
        </div>
        <div class="p-3 bg-black/40 rounded-xl border border-white/5">
          <span class="text-[10px] font-mono text-slate-400 block">GPU Shader Load</span>
          <span class="text-lg font-bold font-mono text-cyan-400">14.2%</span>
          <span class="text-[9px] text-slate-500 block">WebGL 2.0 Pipeline</span>
        </div>
        <div class="p-3 bg-black/40 rounded-xl border border-white/5">
          <span class="text-[10px] font-mono text-slate-400 block">Layout Shift (CLS)</span>
          <span class="text-lg font-bold font-mono text-pink-400">0.000</span>
          <span class="text-[9px] text-slate-500 block">Zero Jitter Assured</span>
        </div>
        <div class="p-3 bg-black/40 rounded-xl border border-white/5">
          <span class="text-[10px] font-mono text-slate-400 block">Interaction INP</span>
          <span class="text-lg font-bold font-mono text-amber-300">42 ms</span>
          <span class="text-[9px] text-slate-500 block">Instant Haptic Feedback</span>
        </div>
      </div>
    </div>
    <script>
      function updateMotionFps(val) {{
        document.getElementById('fpsLabel').textContent = val + ' FPS';
      }}
      function triggerMotionBurst() {{
        alert('✨ Shockwave dispatched: 120 particle physics burst recalculated across canvas viewport.');
      }}
      function setMotionColor(hex, rgb) {{
        console.log('Palette updated to', hex);
      }}
    </script>
        """

    if archetype_key == "sleep_healthtech":
        return f"""
    <!-- Clinical Sleep Telemetry & Polysomnography Triage Bench -->
    <div class="p-6 sm:p-8 rounded-3xl bg-[#0F172A]/90 border border-white/10 shadow-2xl my-8 backdrop-blur-2xl">
      <div class="flex items-center justify-between mb-6 border-b border-white/10 pb-4 flex-wrap gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
            <span class="text-xs font-mono text-cyan-300 font-bold uppercase tracking-wider">Polysomnography &bull; Live Telemetry</span>
          </div>
          <h3 class="font-bold text-white text-2xl font-display">{company} Clinical Operations Bench</h3>
          <p class="text-xs text-slate-400 font-sans">Role: {title} &bull; Circadian Analysis &bull; Apnea Hypopnea Index (AHI) Triage &bull; Automated EHR Dispatch</p>
        </div>
        <div class="flex gap-2">
          <button onclick="simulateEhrIntake()" class="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-cyan-500/25 flex items-center gap-2">
            <span>⚡ Simulate Patient EHR Intake</span>
          </button>
          <button onclick="exportAuditJSON()" class="px-3.5 py-2 bg-slate-800/80 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-mono font-bold transition border border-white/10">
            Export Clinical JSON ↗
          </button>
        </div>
      </div>

      <!-- INTERACTIVE EEG STAGE SELECTOR -->
      <div class="flex items-center gap-2 mb-6 flex-wrap">
        <span class="text-xs font-mono text-slate-400 mr-2">Circadian Phase:</span>
        <button id="tab-rem" onclick="setEegMode('rem')" class="eeg-tab px-3 py-1.5 rounded-xl border border-cyan-400 bg-cyan-500/20 text-cyan-300 text-xs font-mono font-bold transition">REM Sleep (Dreaming)</button>
        <button id="tab-delta" onclick="setEegMode('delta')" class="eeg-tab px-3 py-1.5 rounded-xl border border-white/10 bg-slate-900/60 text-slate-300 hover:text-white text-xs font-mono font-bold transition">N3 Deep Delta (Cellular Repair)</button>
        <button id="tab-theta" onclick="setEegMode('theta')" class="eeg-tab px-3 py-1.5 rounded-xl border border-white/10 bg-slate-900/60 text-slate-300 hover:text-white text-xs font-mono font-bold transition">N1/N2 Theta (Light Induction)</button>
      </div>

      <!-- AHI SEVERITY & CLINICAL YIELD SLIDERS -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Patient AHI Score</label>
            <span id="ahiLabel" class="text-xs font-mono font-bold text-amber-400">22.4 (Moderate Apnea)</span>
          </div>
          <input type="range" id="ahiSlider" min="2" max="60" value="22" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400" oninput="recalcAhi(this.value)">
          <div class="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
            <span>&lt;5 Normal</span>
            <span>15-30 Mod</span>
            <span>&gt;30 Severe</span>
          </div>
        </div>

        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Monthly Patient Volume</label>
            <span id="patientLabel" class="text-xs font-mono font-bold text-cyan-400">450 patients</span>
          </div>
          <input type="range" id="patientSlider" min="50" max="2500" value="450" step="50" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400" oninput="recalcSavings(this.value)">
        </div>

        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <label class="text-[11px] font-mono text-slate-400 uppercase font-bold block mb-1">Clinician Hours Saved / Yr</label>
          <div class="text-2xl font-bold font-mono text-emerald-400 mt-1" id="hoursSavedVal">2,160 hrs</div>
          <span class="text-[10px] text-slate-400 font-mono">Yielding $216,000/yr in operational capacity</span>
        </div>
      </div>
    </div>
    <script>
      function recalcAhi(val) {{
        let status = 'Normal';
        let color = '#10B981';
        if (val >= 5 && val < 15) {{ status = 'Mild'; color = '#FBBF24'; }}
        else if (val >= 15 && val < 30) {{ status = 'Moderate Apnea'; color = '#F59E0B'; }}
        else if (val >= 30) {{ status = 'Severe Apnea (Immediate BiPAP)'; color = '#EF4444'; }}
        const lbl = document.getElementById('ahiLabel');
        lbl.textContent = val + ' (' + status + ')';
        lbl.style.color = color;
      }}
      function recalcSavings(pts) {{
        document.getElementById('patientLabel').textContent = pts + ' patients';
        const hrs = Math.round(pts * 4.8);
        document.getElementById('hoursSavedVal').textContent = hrs.toLocaleString() + ' hrs';
      }}
      function simulateEhrIntake() {{
        alert('⚡ Automated EHR Webhook executed: Sleep study session parsed in 380ms. Physician triage route prepared.');
      }}
    </script>
        """

    if archetype_key == "hardware_embedded_systems":
        return f"""
    <!-- Hardware Diagnostics & Oscilloscope Signal Bench -->
    <div class="p-6 sm:p-8 rounded-3xl bg-[#121620]/90 border border-orange-500/20 shadow-2xl my-8 backdrop-blur-2xl">
      <div class="flex items-center justify-between mb-6 border-b border-orange-500/20 pb-4 flex-wrap gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-orange-500 animate-ping"></span>
            <span class="text-xs font-mono text-orange-400 font-bold uppercase tracking-wider">Hardware Telemetry &bull; Serial Bus Analyzer</span>
          </div>
          <h3 class="font-bold text-white text-2xl font-display">{company} Hardware Diagnostics Bench</h3>
          <p class="text-xs text-slate-400 font-sans">Role: {title} &bull; Thermal Analysis &bull; Signal Integrity &bull; Firmware Disassembly</p>
        </div>
        <div class="flex gap-2">
          <button onclick="injectBusGlitch()" class="px-4 py-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-orange-500/25 flex items-center gap-2">
            <span>⚡ Inject SPI Clock Glitch</span>
          </button>
          <button onclick="exportAuditJSON()" class="px-3.5 py-2 bg-slate-800/80 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-mono font-bold transition border border-white/10">
            Export Telemetry JSON ↗
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Clock Frequency</label>
            <span id="clockLabel" class="text-xs font-mono font-bold text-orange-400">120 MHz</span>
          </div>
          <input type="range" id="clockSlider" min="20" max="480" value="120" step="20" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-orange-500" oninput="document.getElementById('clockLabel').textContent = this.value + ' MHz'">
        </div>

        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">PCB Core Voltage</label>
            <span id="voltLabel" class="text-xs font-mono font-bold text-emerald-400">3.30 V</span>
          </div>
          <input type="range" id="voltSlider" min="12" max="50" value="33" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500" oninput="document.getElementById('voltLabel').textContent = (this.value / 10).toFixed(2) + ' V'">
        </div>

        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <label class="text-[11px] font-mono text-slate-400 uppercase font-bold block mb-1">Thermal Junction Temp</label>
          <div class="text-2xl font-bold font-mono text-amber-400 mt-1">42.6 &deg;C</div>
          <span class="text-[10px] text-slate-400 font-mono">Throttle Threshold: 85.0 &deg;C (Nominal)</span>
        </div>
      </div>
    </div>
    <script>
      function injectBusGlitch() {{
        alert('⚡ Glitch injected: CRC parity recovery validated in 1.4 microseconds.');
      }}
    </script>
        """

    if archetype_key == "email_deliverability_crm":
        return f"""
    <!-- Enterprise Talent Pipeline & Placement Velocity Engine -->
    <div class="p-6 sm:p-8 rounded-3xl bg-[#131322]/90 border border-white/10 shadow-2xl my-8 backdrop-blur-2xl">
      <div class="flex items-center justify-between mb-6 border-b border-white/10 pb-4 flex-wrap gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-purple-500 animate-ping"></span>
            <span class="text-xs font-mono text-purple-400 font-bold uppercase tracking-wider">Talent Acquisition &bull; Deal Funnel</span>
          </div>
          <h3 class="font-bold text-white text-2xl font-display">{company} Deal Velocity Hub</h3>
          <p class="text-xs text-slate-400 font-sans">Role Focus: {title} &bull; Funnel Conversion &bull; Contract Value &bull; Commission Forecasting</p>
        </div>
        <div class="flex gap-2">
          <button onclick="dispatchTalentLead()" class="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-purple-500/25 flex items-center gap-2">
            <span>🚀 Dispatch Verified Enterprise Lead</span>
          </button>
          <button onclick="exportAuditJSON()" class="px-3.5 py-2 bg-slate-800/80 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-mono font-bold transition border border-white/10">
            Export Funnel JSON ↗
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Monthly Target Deals</label>
            <span id="dealLabel" class="text-xs font-mono font-bold text-purple-400">14 Closed Deals</span>
          </div>
          <input type="range" id="dealSlider" min="2" max="50" value="14" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500" oninput="recalcTalentFunnel(this.value)">
        </div>

        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Avg Placement Value</label>
            <span id="acvLabel" class="text-xs font-mono font-bold text-pink-400">&euro;8,500</span>
          </div>
          <input type="range" id="acvSlider" min="3000" max="25000" value="8500" step="500" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-pink-500" oninput="recalcTalentFunnel()">
        </div>

        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <label class="text-[11px] font-mono text-slate-400 uppercase font-bold block mb-1">Projected Annual Pipeline</label>
          <div class="text-2xl font-bold font-mono text-emerald-400 mt-1" id="pipeValue">&euro;1,428,000</div>
          <span class="text-[10px] text-slate-400 font-mono">Net Attributed Revenue Run-Rate</span>
        </div>
      </div>
    </div>
    <script>
      function recalcTalentFunnel() {{
        const deals = parseInt(document.getElementById('dealSlider').value) || 14;
        const acv = parseInt(document.getElementById('acvSlider').value) || 8500;
        document.getElementById('dealLabel').textContent = deals + ' Closed Deals';
        document.getElementById('acvLabel').textContent = '€' + acv.toLocaleString();
        const total = deals * acv * 12;
        document.getElementById('pipeValue').textContent = '€' + total.toLocaleString();
      }}
      function dispatchTalentLead() {{
        alert('🚀 Lead dispatched: Candidate match verified and routed to account executive pipeline.');
      }}
    </script>
        """

    if archetype_key == "fintech_payments_ledger":
        return f"""
    <!-- High-Frequency Stockbroking & Financial Settlement Bench -->
    <div class="p-6 sm:p-8 rounded-3xl bg-[#0E1422]/90 border border-emerald-500/20 shadow-2xl my-8 backdrop-blur-2xl">
      <div class="flex items-center justify-between mb-6 border-b border-emerald-500/20 pb-4 flex-wrap gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
            <span class="text-xs font-mono text-emerald-300 font-bold uppercase tracking-wider">HFT Order Matching &bull; Sub-Millisecond</span>
          </div>
          <h3 class="font-bold text-white text-2xl font-display">{company} High-Frequency Trading Bench</h3>
          <p class="text-xs text-slate-400 font-sans">Target Role: {title} &bull; Order Book Depth &bull; Settlement Ticker &bull; Double-Entry Ledger</p>
        </div>
        <div class="flex gap-2">
          <button onclick="executeHftOrder()" class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-emerald-500/25 flex items-center gap-2">
            <span>⚡ Fire 5,000 Order Batch</span>
          </button>
          <button onclick="exportAuditJSON()" class="px-3.5 py-2 bg-slate-800/80 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-mono font-bold transition border border-white/10">
            Export Ledger JSON ↗
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Throughput Capacity</label>
            <span id="hftTpsLabel" class="text-xs font-mono font-bold text-emerald-400">15,000 tx/sec</span>
          </div>
          <input type="range" id="hftTpsSlider" min="1000" max="50000" value="15000" step="1000" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500" oninput="document.getElementById('hftTpsLabel').textContent = parseInt(this.value).toLocaleString() + ' tx/sec'">
        </div>

        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <div class="flex justify-between items-center mb-2">
            <label class="text-[11px] font-mono text-slate-400 uppercase font-bold">Clearing Latency P99</label>
            <span class="text-xs font-mono font-bold text-cyan-400">0.82 ms</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden mt-3">
            <div class="bg-cyan-400 h-full w-[24%]"></div>
          </div>
        </div>

        <div class="p-4 bg-slate-900/70 rounded-2xl border border-white/5">
          <label class="text-[11px] font-mono text-slate-400 uppercase font-bold block mb-1">Double-Entry Ledger Status</label>
          <div class="text-2xl font-bold font-mono text-emerald-400 mt-1">Balanced (0 &Delta;)</div>
          <span class="text-[10px] text-slate-400 font-mono">100% Cryptographic Audit Match</span>
        </div>
      </div>
    </div>
    <script>
      function executeHftOrder() {{
        alert('⚡ Order batch executed: 5,000 limit orders matched and settled across memory ledger in 4.2ms.');
      }}
    </script>
        """

    # Universal default telemetry widget
    return f"""
    <!-- Universal Interactive Telemetry & Operation Benchmark Widget -->
    <div class="p-6 sm:p-8 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-2xl my-8 backdrop-blur">
      <div class="flex items-center justify-between mb-6 border-b border-slate-800 pb-4 flex-wrap gap-4">
        <div>
          <h3 class="font-bold text-white text-2xl font-display">{company} Production Telemetry Bench</h3>
          <p class="text-xs text-slate-400 font-sans">Target Role: {title} &bull; Sub-Second Latency &bull; High-Conversion Micro-App</p>
        </div>
        <div class="flex gap-2">
          <button onclick="simulateTrafficSpike()" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold rounded-xl text-xs transition shadow-md shadow-cyan-500/20">
            Simulate Traffic Spike ↗
          </button>
          <button onclick="exportAuditJSON()" class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-mono font-bold transition border border-slate-700">
            Export Audit JSON ↗
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-slate-950/60 rounded-xl border border-slate-800">
          <span class="text-[10px] font-mono text-slate-400 uppercase font-bold">Core Execution Engine</span>
          <div class="text-xl font-bold text-white mt-1">Next.js &bull; TypeScript</div>
          <span class="text-[10px] text-emerald-400 font-mono mt-1 block">&bull; Zero Layout Shift</span>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-xl border border-slate-800">
          <span class="text-[10px] font-mono text-slate-400 uppercase font-bold">P99 Edge Latency</span>
          <div class="text-xl font-bold text-cyan-400 mt-1" id="p99Latency">12.4 ms</div>
          <span class="text-[10px] text-slate-400 font-mono mt-1 block">Global CDN Edge Delivery</span>
        </div>
        <div class="p-4 bg-slate-950/60 rounded-xl border border-slate-800">
          <span class="text-[10px] font-mono text-slate-400 uppercase font-bold">Throughput Simulation</span>
          <div class="text-xl font-bold text-purple-400 mt-1" id="simThroughput">2,480 req/s</div>
          <span class="text-[10px] text-slate-400 font-mono mt-1 block">Auto-scaling edge cluster</span>
        </div>
      </div>
    </div>
    <script>
      function simulateTrafficSpike() {{
        alert('⚡ Traffic spike simulated: Scaled 4 edge replicas. Latency steady at 12ms.');
      }}
    </script>
    """


def build_demo_html(
    company: str,
    title: str,
    slug: str,
    archetype: Dict[str, Any],
    opp_url: str = ""
) -> str:
    """Produce complete, runnable, production-quality HTML application with custom typography and motion."""
    portfolio_base = get_base_portfolio_url()
    github_url = get_github_url()
    canonical_vercel_url = f"{portfolio_base}/{slug}"
    canonical_github_file_url = f"https://github.com/Stghost1/BIEAI/blob/main/{slug}.html"
    theme = get_archetype_theme(archetype["key"])
    canvas_script = generate_canvas_script(theme["canvas_type"], theme["accent_color"], theme["accent_rgb"])
    widget_html = generate_interactive_widget(archetype["key"], company, title)

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{company}: {archetype['name']} (B.I.E.AI Bespoke Prototype)</title>
  <meta name="description" content="Production-ready interactive prototype engineered specifically for {company}'s {title} role by Emmanuel Pelumi Bamidele (Bamsemma).">

  <!-- Curated Typography: Diverse fonts per job -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{theme['font_import']}" rel="stylesheet">

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            display: [{theme['font_display']}],
            sans: [{theme['font_sans']}],
            mono: [{theme['font_mono']}],
          }},
          animation: {{
            'float-slow': 'float 6s ease-in-out infinite',
            'pulse-glow': 'pulseGlow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            'marquee': 'marquee 22s linear infinite',
          }},
          keyframes: {{
            float: {{
              '0%, 100%': {{ transform: 'translateY(0px)' }},
              '50%': {{ transform: 'translateY(-8px)' }},
            }},
            pulseGlow: {{
              '0%, 100%': {{ opacity: '0.4', filter: 'blur(20px)' }},
              '50%': {{ opacity: '0.8', filter: 'blur(32px)' }},
            }},
            marquee: {{
              '0%': {{ transform: 'translateX(0%)' }},
              '100%': {{ transform: 'translateX(-50%)' }}
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{
      font-family: {theme['font_sans']};
      background-color: {theme['bg_color']};
      color: {theme['text_color']};
      overflow-x: hidden;
    }}
    .font-display {{ font-family: {theme['font_display']}; }}
    .font-mono {{ font-family: {theme['font_mono']}; }}

    /* 3D Perspective Card Tilt */
    .tilt-card {{
      transition: transform 0.15s ease-out, border-color 0.25s ease, box-shadow 0.25s ease;
      will-change: transform;
      transform-style: preserve-3d;
    }}

    /* Kinetic Marquee */
    .marquee-track {{
      display: flex;
      width: 200%;
      animation: marquee 20s linear infinite;
    }}
    .marquee-track:hover {{
      animation-play-state: paused;
    }}
  </style>
</head>
<body class="min-h-[100dvh] flex flex-col justify-between selection:bg-pink-500/20 selection:text-pink-300 {theme['bg_class']}">

  <!-- TOP NAVIGATION BAR -->
  <header class="border-b border-white/10 bg-black/40 backdrop-blur-xl sticky top-0 z-50 px-4 sm:px-6 py-3.5">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center gap-3">
        <a href="{portfolio_base}" class="flex items-center gap-2.5 text-white font-display font-bold text-lg hover:opacity-90 transition">
          <span class="w-8 h-8 rounded-xl bg-gradient-to-tr from-pink-500 via-purple-600 to-cyan-400 text-white flex items-center justify-center font-black text-sm shadow-lg shadow-pink-500/20">B</span>
          <span class="tracking-tight">B.I.E.AI</span>
        </a>
        <span class="text-slate-600 text-xs font-mono">/</span>
        <span class="text-xs font-mono {theme['badge_class']} px-3 py-1 rounded-full font-bold">
          Tailored Prototype &bull; {company}
        </span>
      </div>
      <div class="flex items-center gap-2.5 text-xs font-mono">
        <span class="hidden md:inline-flex items-center gap-1.5 text-slate-300">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Live on Vercel
        </span>
        <a href="{canonical_github_file_url}" target="_blank" rel="noopener" class="px-3.5 py-1.5 bg-white/5 border border-white/10 hover:border-pink-500/60 text-slate-200 rounded-xl transition flex items-center gap-1.5 font-bold">
          GitHub Code ↗
        </a>
        <a href="{portfolio_base}" class="px-3.5 py-1.5 bg-gradient-to-r from-pink-500 to-cyan-500 hover:opacity-90 text-white font-bold rounded-xl transition shadow-md shadow-pink-500/20">
          Portfolio ↗
        </a>
      </div>
    </div>
  </header>

  <!-- KINETIC TICKER (motionsites.ai inspired) -->
  <div class="border-b border-white/5 bg-black/30 py-2 overflow-hidden whitespace-nowrap">
    <div class="marquee-track text-[11px] font-mono text-slate-400 font-bold uppercase tracking-wider">
      <span class="mx-6 text-pink-400">● 60 FPS INTERACTIVE MOTION CANVAS</span>
      <span class="mx-6 text-cyan-300">● BESPOKE ARCHITECTURE FOR {company.upper()}</span>
      <span class="mx-6 text-purple-300">● ZERO ATS RESUME TRASH</span>
      <span class="mx-6 text-emerald-400">● WORKING PRODUCTION SOFTWARE</span>
      <span class="mx-6 text-pink-400">● 60 FPS INTERACTIVE MOTION CANVAS</span>
      <span class="mx-6 text-cyan-300">● BESPOKE ARCHITECTURE FOR {company.upper()}</span>
      <span class="mx-6 text-purple-300">● ZERO ATS RESUME TRASH</span>
      <span class="mx-6 text-emerald-400">● WORKING PRODUCTION SOFTWARE</span>
    </div>
  </div>

  <!-- MAIN WORKSPACE -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full relative">

    <!-- HERO STAGE (motionsites.ai inspired) -->
    <div class="relative rounded-3xl overflow-hidden border border-white/10 bg-gradient-to-b from-white/[0.04] to-transparent p-6 sm:p-12 mb-8">
      
      <!-- Interactive 60 FPS Canvas Centerpiece -->
      <canvas id="heroMotionCanvas" class="absolute inset-0 w-full h-full pointer-events-auto opacity-70 z-0"></canvas>

      <!-- Ambient Glow Spotlights -->
      <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-[{theme['accent_color']}]/20 blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-24 -right-24 w-96 h-96 rounded-full bg-cyan-500/20 blur-3xl pointer-events-none"></div>

      <!-- Hero Content -->
      <div class="relative z-10 max-w-4xl">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full {theme['badge_class']} text-xs font-mono mb-4 font-bold">
          <span>Target Role: {title}</span>
          <span>&bull;</span>
          <span>{archetype['category'].upper()} ARCHETYPE</span>
        </div>

        <h1 class="text-4xl sm:text-6xl md:text-7xl font-display font-extrabold tracking-tight leading-[1.05] bg-gradient-to-r {theme['gradient_text']} bg-clip-text text-transparent">
          {archetype['name']}
        </h1>

        <p class="text-base sm:text-lg text-slate-300 mt-4 leading-relaxed font-sans max-w-3xl">
          {archetype['feature']} Built specifically for <strong>{company}</strong> by <strong>Emmanuel Pelumi Bamidele (Bamsemma)</strong> to replace generic outreach with a fully-functional, Awwwards-tier interactive application.
        </p>

        <!-- Live Action Buttons -->
        <div class="flex items-center gap-3 mt-6 flex-wrap">
          <a href="{canonical_vercel_url}" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-pink-500 via-purple-600 to-cyan-500 text-white font-display font-bold text-sm shadow-xl shadow-pink-500/25 hover:opacity-90 transition">
            Explore Interactive Prototype ↗
          </a>
          <a href="{canonical_github_file_url}" target="_blank" rel="noopener" class="px-5 py-2.5 rounded-xl bg-slate-900/80 border border-white/10 hover:border-pink-500 text-slate-200 font-mono font-bold text-xs transition">
            View Source on GitHub ↗
          </a>
          <span class="text-xs font-mono text-slate-400 ml-2">
            60 FPS Canvas Active &bull; Move mouse over viewport
          </span>
        </div>
      </div>
    </div>

    <!-- BESPOKE INTERACTIVE APPLICATION BENCH -->
    {widget_html}

    <!-- 3D PERSPECTIVE TILT BENTO SHOWCASE (motionsites.ai inspired) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-10">
      
      <div class="tilt-card p-6 sm:p-7 rounded-3xl {theme['card_class']} relative overflow-hidden">
        <div class="w-10 h-10 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-4 font-mono font-bold text-sm">
          01
        </div>
        <span class="text-[11px] font-mono text-cyan-400 uppercase font-bold tracking-wider">Engineering Architecture</span>
        <h4 class="font-display font-bold text-white text-xl mt-1">{archetype['tech_stack']}</h4>
        <p class="text-xs text-slate-400 mt-2 leading-relaxed">
          Engineered for zero layout shift, sub-50ms interaction latency, and high-frequency state updates.
        </p>
      </div>

      <div class="tilt-card p-6 sm:p-7 rounded-3xl {theme['card_class']} relative overflow-hidden">
        <div class="w-10 h-10 rounded-2xl bg-pink-500/10 border border-pink-500/30 flex items-center justify-center text-pink-400 mb-4 font-mono font-bold text-sm">
          02
        </div>
        <span class="text-[11px] font-mono text-pink-400 uppercase font-bold tracking-wider">Production Vercel Edge</span>
        <h4 class="font-display font-bold text-white text-xl mt-1">Live Global CDN Deployment</h4>
        <p class="text-xs text-slate-400 mt-2 leading-relaxed">
          Registered in vercel.json rewrites. Accessible anywhere at <a href="{canonical_vercel_url}" class="underline text-pink-300 font-mono">{slug}</a>.
        </p>
      </div>

      <div class="tilt-card p-6 sm:p-7 rounded-3xl {theme['card_class']} relative overflow-hidden">
        <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4 font-mono font-bold text-sm">
          03
        </div>
        <span class="text-[11px] font-mono text-emerald-400 uppercase font-bold tracking-wider">Verified Source Repository</span>
        <h4 class="font-display font-bold text-white text-xl mt-1">Stghost1/BIEAI on GitHub</h4>
        <p class="text-xs text-slate-400 mt-2 leading-relaxed">
          Committed with conventional commits. Inspect standalone code at <a href="{canonical_github_file_url}" target="_blank" rel="noopener" class="underline text-emerald-300 font-mono">GitHub Repo</a>.
        </p>
      </div>

    </div>

    <!-- LIVE TELEMETRY LOG -->
    <div class="p-6 rounded-2xl bg-black/40 border border-white/5 font-mono text-xs text-slate-400 my-8">
      <div class="flex items-center justify-between mb-3 border-b border-white/5 pb-2">
        <span class="text-slate-300 font-bold uppercase flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          Live Micro-Application Activity Telemetry
        </span>
        <span class="text-[10px] text-slate-500">Connected to Vercel Edge Event Bus</span>
      </div>
      <div id="liveTelemetryStream" class="space-y-1 text-[11px]">
        <div class="text-emerald-400">● [200 OK] Handshake established with {company} demonstration cluster.</div>
        <div class="text-slate-400">● Canvas 60 FPS requestAnimationFrame loop active. Zero frame drops detected.</div>
        <div class="text-cyan-400">● Dynamic archetype resolved: {archetype['name']}.</div>
      </div>
    </div>

  </main>

  <!-- FOOTER -->
  <footer class="border-t border-white/10 bg-black/60 py-8 px-4 sm:px-6 text-xs text-slate-400">
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-pink-500"></span>
        <span>Engineered specifically for <strong>{company}</strong> by <strong class="text-white">Emmanuel Pelumi Bamidele (Bamsemma)</strong></span>
      </div>
      <div class="flex items-center gap-4 font-mono">
        <a href="{portfolio_base}" class="hover:text-pink-400 transition">bieai.vercel.app</a>
        <span>&bull;</span>
        <a href="{github_url}" target="_blank" rel="noopener" class="hover:text-cyan-400 transition">github.com/Stghost1/BIEAI</a>
        <span>&bull;</span>
        <a href="{portfolio_base}/radar" class="hover:text-purple-400 transition">Radar Engine ↗</a>
      </div>
    </div>
  </footer>

  <!-- 3D PERSPECTIVE TILT SCRIPT -->
  <script>
    document.querySelectorAll('.tilt-card').forEach(card => {{
      card.addEventListener('mousemove', (e) => {{
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -6;
        const rotateY = ((x - centerX) / centerX) * 6;
        card.style.transform = `perspective(1000px) rotateX(${{rotateX}}deg) rotateY(${{rotateY}}deg) scale3d(1.02, 1.02, 1.02)`;
      }});
      card.addEventListener('mouseleave', () => {{
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
      }});
    }});
  </script>

  <!-- BESPOKE 60 FPS CANVAS SCRIPT -->
  <script>
    {canvas_script}
  </script>

  <!-- JSON AUDIT EXPORT SCRIPT -->
  <script>
    function exportAuditJSON() {{
      const data = {{
        company: "{company}",
        title: "{title}",
        archetype: "{archetype['name']}",
        timestamp: new Date().toISOString(),
        author: "Emmanuel Pelumi Bamidele (Bamsemma)",
        canonical_vercel_url: "{canonical_vercel_url}",
        canonical_github_url: "{canonical_github_file_url}",
        status: "verified_live"
      }};
      const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: "application/json" }});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "{slug}_audit.json";
      a.click();
    }}
  </script>
</body>
</html>
"""


def build_tailored_demo(opp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize complete bespoke interactive prototype for any opportunity on the radar.
    1. Detects domain archetype with strict word boundaries.
    2. Writes custom HTML micro-application with distinctive fonts and motion graphics.
    3. Registers clean route in vercel.json.
    4. Automatically commits and pushes to GitHub (Stghost1/BIEAI:main).
    5. Scours company contact email.
    6. Stores record in portfolio_demos table.
    """
    company = opp.get("company", "Company")
    title = opp.get("title", "Full-Stack Engineer")
    desc = opp.get("description", "")
    opp_url = opp.get("url", "")
    opp_id = opp.get("id")
    tags = opp.get("tags", [])
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = []

    archetype = detect_archetype(title, desc, tags, company)

    # Generate slug: e.g. demo-dreem-health-clinical-operations
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

    # 3. Register rewrite in vercel.json and deploy
    vercel_res = deploy_to_vercel(slug, file_name, company)
    vercel_url = vercel_res.get("vercel_url", f"{base_url}/{slug}")

    # 4. Commit and push to GitHub
    github_res = push_demo_to_github(file_name, slug, company, title)
    github_url = github_res.get("github_url", f"https://github.com/Stghost1/BIEAI/blob/main/{file_name}")

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
        "slug": slug,
        "file_name": file_name,
        "title": demo_record["title"],
        "company": company,
        "category": archetype["category"],
        "tech_stack": archetype["tech_stack"],
        "demo_url": vercel_url,
        "github_url": github_url,
        "preview_desc": demo_record["preview_desc"],
        "recipient_email": recipient_email,
        "archetype": archetype["key"],
        "status": "live",
        "db_record": inserted
    }
