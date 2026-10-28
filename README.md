# B.I.E.AI Work & Opportunity Operating System

**Owner**: Emmanuel Bamidele (Bamsemma, B.I.E.AI)  
**Location**: `C:\Users\emman\Desktop\web projects\biework`  
**Server**: `http://127.0.0.1:4173`  

A unified operations headquarters combining client-facing consulting services with a live-running opportunity discovery radar and tailored cold outreach pipeline.

---

## Architecture Overview

```
biework/
├── index.html                   # Public agency & consulting portfolio (pricing, services, contact)
├── radar.html                   # Operator portal: Scoutdesk live opportunity radar & pipeline
├── scoutdesk.js                 # Asynchronous client for signal filtering and proposal drafting
├── scoutdesk.css                # Radar visual system styles
├── server.py                    # Unified HTTP REST API server on port 4173
├── start.bat                    # One-click desktop launcher
├── vercel.json                  # Clean deployment URL rewrites
│
├── core/
│   ├── db.py                    # SQLite engine (opportunities, outreach drafts, scan telemetry)
│   ├── scanner.py               # Live public feed scrapers (RemoteOK, Jobicy, Arbeitnow)
│   └── outreach_generator.py    # Cold proposal engine matching live biework demos
│
├── data/
│   └── scoutdesk.db             # Local SQLite database (124+ real live opportunities)
│
└── Live Client Demos:
    ├── swiftlegal-nigeria.html  # Law firm client site & practice areas
    ├── lagos-premier-realty.html# Real estate agency portal & property listings
    ├── nutricoach-abuja.html    # Health coach site with interactive live BMI calculator
    ├── roi-calculator.html      # Interactive Nigerian real estate ROI & yield calculator
    └── invoice-generator.html   # Client billing tool with line items & PDF download
```

---

## Unified URLs

| Interface | URL | Purpose |
|---|---|---|
| **Agency Portfolio** | `http://127.0.0.1:4173/` | Client-facing landing page with pricing, services, and booking |
| **Opportunity Radar** | `http://127.0.0.1:4173/radar` | Operator portal for remote tech signals, cold outreach, and 22 survey platforms |
| **Surveys & Fast Income** | `http://127.0.0.1:4173/surveys` | Direct Nigerian panels & Tier-1 VPN panels (USA, UK, France) with anti-ban guide |
| **SwiftLegal Demo** | `http://127.0.0.1:4173/swiftlegal-nigeria` | Corporate legal demo attached to proposals |
| **Lagos Realty Demo** | `http://127.0.0.1:4173/lagos-premier-realty` | Real estate demo attached to proposals |
| **NutriCoach Demo** | `http://127.0.0.1:4173/nutricoach-abuja` | Health coaching & BMI calculator demo |
| **ROI Calculator** | `http://127.0.0.1:4173/roi-calculator` | Interactive financial yield calculator |
| **Invoice Generator** | `http://127.0.0.1:4173/invoice-generator` | Invoicing application with PDF export |

---

## Quick Start

### 1. Launch Unified Server:
Double-click `start.bat` or run:
```powershell
python server.py
```
Open `http://127.0.0.1:4173/` in your browser.

### 2. Switch to Opportunity Radar:
Click the **◎ Opportunity Radar** button in the navigation header or open `http://127.0.0.1:4173/radar`.
Click **Run fresh scan** to query RemoteOK, Jobicy, and Arbeitnow for new live signals.
Click **Draft outreach** on any role to generate an immediate, personalized cold proposal referencing your live demos.
