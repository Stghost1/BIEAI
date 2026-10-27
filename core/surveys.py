"""
Surveys and Market Research Engine for Scoutdesk.
Provides curated, verified platforms for:
1. Local Direct Access (Nigeria and Global, zero VPN required, 100% ban-safe).
2. Tier-1 High-Yield Panels (USA, UK, France via Residential VPN/Proxy and Stealth Persona).
Includes complete VPN setup guidance, anti-ban protocols, and persona bibles.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

SURVEY_REGISTRY: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # 1. LOCAL DIRECT PLATFORMS (NIGERIA / GLOBAL DIRECT - NO VPN)
    # -------------------------------------------------------------
    {
        "slug": "ysense",
        "name": "ySense",
        "category": "local",
        "countries": ["NG", "Global"],
        "vpn_required": False,
        "pay_range": "$0.30 - $3.50 per survey",
        "payout_methods": ["PayPal", "Payoneer", "Skrill", "Steam Gift Cards"],
        "min_payout": "$5.05 (Skrill), $10 (PayPal), $25 (Payoneer)",
        "payout_speed": "2 to 4 business days",
        "safety_rating": "100% Ban-Safe (Direct Nigerian IP)",
        "recommended_ip": "Direct Local ISP (MTN, Airtel, Starlink, Fiber)",
        "url": "https://www.ysense.com",
        "best_for": "Top aggregator with daily CPX and BitLabs surveys for Nigeria",
        "description": "Premier global rewards and research platform. Aggregates live surveys from BitLabs, CPX Research, Wannads, and Peanut Labs specifically open to Nigerian profiles.",
        "stealth_notes": "Do not use a VPN on ySense; they maintain strict fraud heuristics. Fill out the profile surveys on day one to receive daily survey router invites. Cashout to Skrill or Payoneer for simple conversion to Nigerian bank accounts.",
        "tags": ["surveys", "offers", "cpx", "bitlabs", "skrill", "payoneer"],
    },
    {
        "slug": "triaba-ng",
        "name": "Triaba Nigeria",
        "category": "local",
        "countries": ["NG"],
        "vpn_required": False,
        "pay_range": "₦400 - ₦4,500 ($0.25 - $2.80) per survey",
        "payout_methods": ["PayPal", "GCodes Virtual Gift Codes"],
        "min_payout": "$10.00",
        "payout_speed": "1 to 3 business days",
        "safety_rating": "100% Ban-Safe (Dedicated Nigerian Panel)",
        "recommended_ip": "Direct Nigerian IP (No proxy)",
        "url": "https://www.triaba.com/ng",
        "best_for": "Official Cint-backed market research panel for Nigeria",
        "description": "Specialized Norwegian research panel operated in partnership with Cint and Syno International. Features a dedicated Nigerian member portal with surveys focused on domestic consumer brands and lifestyle.",
        "stealth_notes": "Register exclusively through the triaba.com/ng portal. Keep demographic details accurate to ensure high completion rates without survey disqualifications.",
        "tags": ["nigeria-direct", "cint", "paypal", "lifestyle", "brands"],
    },
    {
        "slug": "toluna-ng",
        "name": "Toluna Influencers Nigeria",
        "category": "local",
        "countries": ["NG"],
        "vpn_required": False,
        "pay_range": "1,000 - 5,000 points (₦500 - ₦3,000) per survey",
        "payout_methods": ["Mobile Airtime (MTN/Airtel/Glo)", "Jumia Vouchers", "PayPal"],
        "min_payout": "₦1,000 Airtime / $10 PayPal",
        "payout_speed": "Within 24 to 72 hours",
        "safety_rating": "100% Ban-Safe (Dedicated Nigerian Portal)",
        "recommended_ip": "Direct Nigerian Local IP",
        "url": "https://ng.toluna.com",
        "best_for": "Direct mobile airtime redemption and local FMCG surveys",
        "description": "Dedicated Nigerian community portal with direct point conversion to mobile recharge cards across all Nigerian networks and Jumia shopping vouchers.",
        "stealth_notes": "Complete all profile categories (technology, shopping, travel). Survey invitations are dispatched directly to your registered email address.",
        "tags": ["nigeria-direct", "airtime", "jumia", "paypal", "fmcg"],
    },
    {
        "slug": "mobrog-ng",
        "name": "Mobrog Nigeria",
        "category": "local",
        "countries": ["NG"],
        "vpn_required": False,
        "pay_range": "$0.50 - $2.50 per survey",
        "payout_methods": ["PayPal", "Skrill", "EcoMatcher"],
        "min_payout": "$6.25",
        "payout_speed": "Within 24 to 48 hours",
        "safety_rating": "100% Ban-Safe (Official Nigerian Mobile App)",
        "recommended_ip": "Direct Nigerian IP (Mobile App or Web)",
        "url": "https://www.mobrog.com/en-ng/",
        "best_for": "Mobile app push notifications and low $6.25 cashout",
        "description": "Operated by Splendid Research Germany with a dedicated presence in Nigeria. The mobile app delivers instant push alerts when new surveys matching your profile open up.",
        "stealth_notes": "Respond quickly to email and push alerts because survey participant quotas for Nigerian demographics fill up rapidly.",
        "tags": ["nigeria-direct", "mobile-app", "skrill", "paypal", "low-minimum"],
    },
    {
        "slug": "surveytime",
        "name": "Surveytime",
        "category": "local",
        "countries": ["NG", "Global"],
        "vpn_required": False,
        "pay_range": "Flat $1.00 USD per completed survey",
        "payout_methods": ["Instant PayPal", "Coinbase Crypto (BTC/LTC)", "Amazon GC"],
        "min_payout": "Zero Minimum ($1.00 Instant Cashout)",
        "payout_speed": "Instant (Under 5 minutes)",
        "safety_rating": "100% Ban-Safe",
        "recommended_ip": "Direct Nigerian IP",
        "url": "https://surveytime.io",
        "best_for": "Zero payout threshold with instant $1 crypto or PayPal transfer",
        "description": "One of the few global platforms with no minimum payout balance. Every survey completed pays a flat $1 sent directly to your linked Coinbase or PayPal account within minutes.",
        "stealth_notes": "Select Coinbase (Crypto) or PayPal at cashout. Complete the introductory qualification test accurately to establish an algorithmic trust baseline.",
        "tags": ["instant-payout", "crypto", "paypal", "no-minimum", "zero-threshold"],
    },
    {
        "slug": "paidviewpoint",
        "name": "PaidViewpoint",
        "category": "local",
        "countries": ["NG", "Global"],
        "vpn_required": False,
        "pay_range": "$0.10 - $1.80 per survey",
        "payout_methods": ["PayPal"],
        "min_payout": "$15.00 first cashout ($5 to $10 thereafter)",
        "payout_speed": "Under 24 hours",
        "safety_rating": "100% Ban-Safe",
        "recommended_ip": "Direct Local IP",
        "url": "https://paidviewpoint.com",
        "best_for": "Zero screen-outs with TraitScore progression system",
        "description": "Operated by Applied Analytic Solutions with a strict policy: you are never screened out or disqualified once a survey starts. As your TraitScore reaches 9,000+, pay per question increases.",
        "stealth_notes": "Maintain consistent answers over time. PaidViewpoint introduces subtle repeat verification questions to test honesty.",
        "tags": ["zero-disqualification", "trait-score", "paypal", "consistency"],
    },
    {
        "slug": "timebucks",
        "name": "Timebucks",
        "category": "local",
        "countries": ["NG", "Global"],
        "vpn_required": False,
        "pay_range": "$0.20 - $3.50 per survey",
        "payout_methods": ["Litecoin (LTC)", "AirTM", "Bitcoin", "Skrill"],
        "min_payout": "$5.00",
        "payout_speed": "Weekly automated transfer every Thursday",
        "safety_rating": "100% Ban-Safe",
        "recommended_ip": "Direct Nigerian IP",
        "url": "https://timebucks.com",
        "best_for": "Weekly automated crypto payouts (Litecoin) and multi-tasking",
        "description": "Widely used platform in West Africa combining survey routers (BitLabs, CPX, TheoremReach) with slide show viewings, clicks, and micro-tasks.",
        "stealth_notes": "Set your payout method to Litecoin (LTC). It incurs negligible network fees and transfers straight into your Binance, Bybit, or Roqqu wallet.",
        "tags": ["crypto", "litecoin", "airtm", "weekly-payout", "microtasks"],
    },
    {
        "slug": "premise-data",
        "name": "Premise Data",
        "category": "local",
        "countries": ["NG"],
        "vpn_required": False,
        "pay_range": "₦200 - ₦3,500 per task",
        "payout_methods": ["Nigerian Bank Account", "Paga", "Mobile Airtime"],
        "min_payout": "₦1,000",
        "payout_speed": "Within 24 hours",
        "safety_rating": "100% Ban-Safe",
        "recommended_ip": "Smartphone with Local Nigerian GPS (Lagos, Akure, Abuja, etc.)",
        "url": "https://www.premise.com/contributors/",
        "best_for": "Direct local bank deposits and city-based micro-audits",
        "description": "Smartphone application paying users to report market prices, audit supermarket inventory, photo-document local public amenities, and answer opinion polls in Nigerian cities.",
        "stealth_notes": "Requires GPS location services on Android or iOS. Excellent task availability in Lagos, Abuja, Ibadan, Port Harcourt, and state capitals.",
        "tags": ["mobile-app", "direct-bank", "paga", "gps-tasks", "local-audit"],
    },
    {
        "slug": "tgm-panel-ng",
        "name": "TGM Panel Nigeria",
        "category": "local",
        "countries": ["NG"],
        "vpn_required": False,
        "pay_range": "$0.50 - $3.00 per survey",
        "payout_methods": ["PayPal", "GCodes", "Virtual Visa"],
        "min_payout": "$10.00",
        "payout_speed": "1 to 3 business days",
        "safety_rating": "100% Ban-Safe",
        "recommended_ip": "Direct Local IP",
        "url": "https://tgmpanel.com/nigeria",
        "best_for": "High qualification rates for Nigerian tech and mobile studies",
        "description": "ESOMAR-accredited international market research firm operating an active Nigerian panel for banking, telecom, and consumer technology feedback.",
        "stealth_notes": "Fill in the extended profile surveys to unlock higher paying fintech and telecom research sessions.",
        "tags": ["nigeria-direct", "paypal", "virtual-visa", "esomar", "fintech"],
    },
    {
        "slug": "freecash-direct",
        "name": "Freecash (Direct Mode)",
        "category": "local",
        "countries": ["NG", "Global"],
        "vpn_required": False,
        "pay_range": "$0.30 - $4.50 per survey",
        "payout_methods": ["Crypto (Litecoin, USDT, BTC)", "PayPal", "AirTM"],
        "min_payout": "$0.50 for Crypto (Instant)",
        "payout_speed": "Instant (Under 5 minutes)",
        "safety_rating": "100% Ban-Safe (in direct mode)",
        "recommended_ip": "Direct Nigerian IP",
        "url": "https://freecash.com",
        "best_for": "Instant crypto withdrawals with zero US bank requirements",
        "description": "Top-tier rewards wall offering BitLabs, CPX Research, and InBrain surveys. Crypto payouts start at just $0.50 with instant processing straight to your external wallet.",
        "stealth_notes": "When using direct mode, keep your Nigerian IP consistent. Never toggle a datacenter VPN on the same account to prevent automated security locks.",
        "tags": ["instant-crypto", "litecoin", "usdt", "low-minimum", "bitlabs"],
    },
    {
        "slug": "outlier-ai",
        "name": "Outlier.ai (AI Training Tasks)",
        "category": "local",
        "countries": ["NG", "Global"],
        "vpn_required": False,
        "pay_range": "$7.50 - $25.00 / hour",
        "payout_methods": ["PayPal", "AirTM"],
        "min_payout": "Weekly automated deposit",
        "payout_speed": "Weekly on Tuesdays",
        "safety_rating": "100% Ban-Safe (Actively hires Nigerian talent)",
        "recommended_ip": "Direct Nigerian IP",
        "url": "https://outlier.ai",
        "best_for": "Substantial hourly income evaluating AI outputs and prompts",
        "description": "Scale AI platform hiring contributors to assess AI responses, edit model drafts, and rate reasoning accuracy. Delivers hourly rates significantly higher than traditional surveys.",
        "stealth_notes": "Register using your real Nigerian identity. Pass the initial screening assessment with careful grammar and reasoning to qualify for active client queues.",
        "tags": ["ai-training", "high-income", "hourly-rate", "airtm", "paypal"],
    },

    # -------------------------------------------------------------
    # 2. TIER-1 VPN PLATFORMS (USA, UK, FRANCE - RESIDENTIAL STEALTH)
    # -------------------------------------------------------------
    {
        "slug": "freecash-tier1",
        "name": "Freecash (Tier-1 US/UK/FR Mode)",
        "category": "vpn_tier1",
        "countries": ["US", "UK", "FR"],
        "vpn_required": True,
        "pay_range": "$1.50 - $15.00 per survey & offer",
        "payout_methods": ["Instant Crypto (Litecoin, USDT, BTC)", "Virtual Visa", "Gift Cards"],
        "min_payout": "$0.50 for Crypto (Instant)",
        "payout_speed": "Instant (Automated)",
        "safety_rating": "Moderate (Clean Residential IP Required)",
        "recommended_ip": "Clean Residential SOCKS5 / Static Residential VPN (US, UK, or France)",
        "url": "https://freecash.com",
        "best_for": "Top VPN platform: instant crypto cashouts without US bank or SSN",
        "description": "On a US, UK, or French residential IP, Freecash unlocks premium offerwalls (RevU, Torox, BitLabs, CPX) paying up to 10 times higher than local tiers. Instant crypto cashout eliminates US banking barriers.",
        "stealth_notes": "Run in an isolated browser profile with WebRTC disabled. Never rotate IP countries mid-session. Cash out in Litecoin (LTC) directly to your Binance or Bybit deposit address for instantaneous liquidation.",
        "tags": ["vpn-tier1", "usa", "uk", "france", "instant-crypto", "high-yield"],
    },
    {
        "slug": "prime-opinion-tier1",
        "name": "Prime Opinion",
        "category": "vpn_tier1",
        "countries": ["US", "UK", "FR"],
        "vpn_required": True,
        "pay_range": "$1.00 - $5.50 per survey",
        "payout_methods": ["PayPal", "Virtual Visa", "Amazon Gift Cards", "Apple/Google Play"],
        "min_payout": "$5.00 (500 points)",
        "payout_speed": "Under 30 minutes",
        "safety_rating": "Moderate (Monitors IP fraud scores)",
        "recommended_ip": "Residential IP with IPQualityScore fraud rating under 15",
        "url": "https://www.primeopinion.com",
        "best_for": "Massive daily survey inventory with rapid $5 cashouts",
        "description": "Fastest-growing consumer panel in the US, UK, and France. Hosts hundreds of daily surveys from Dynata, Toluna, and PureSpectrum with daily leaderboard bonus challenges.",
        "stealth_notes": "Avoid shared datacenter VPNs. Use a clean residential proxy. Synchronize your PC or browser timezone with your proxy city (for example America/New_York or Europe/London).",
        "tags": ["vpn-tier1", "usa", "uk", "france", "paypal", "virtual-visa"],
    },
    {
        "slug": "swagbucks-tier1",
        "name": "Swagbucks (US, UK, France)",
        "category": "vpn_tier1",
        "countries": ["US", "UK", "FR"],
        "vpn_required": True,
        "pay_range": "$1.00 - $4.50 per survey",
        "payout_methods": ["PayPal", "Virtual Visa / Mastercard", "Amazon Gift Cards"],
        "min_payout": "$5.00",
        "payout_speed": "1 to 3 business days",
        "safety_rating": "High Security (Strict anti-proxy filters)",
        "recommended_ip": "Clean Static Residential SOCKS5 Proxy or 4G Mobile Proxy",
        "url": "https://www.swagbucks.com",
        "best_for": "High-volume research inventory and recurring signup bonuses",
        "description": "The largest rewards platform in North America and Western Europe. Offers Gold Surveys, web search bonuses, and cashback offers. Dedicated French portal available at swagbucks.fr.",
        "stealth_notes": "Swagbucks enforces strict MaxMind checks. Verify zero WebRTC leaks on ipleak.net before signing in. Match your profile zip code with the proxy IP geo-location.",
        "tags": ["vpn-tier1", "usa", "uk", "france", "paypal", "amazon-gc"],
    },
    {
        "slug": "branded-surveys-tier1",
        "name": "Branded Surveys",
        "category": "vpn_tier1",
        "countries": ["US", "UK"],
        "vpn_required": True,
        "pay_range": "$1.00 - $4.00 per survey",
        "payout_methods": ["PayPal", "Bank Transfer via Wise", "Prepaid Visa"],
        "min_payout": "$5.00 (500 points)",
        "payout_speed": "1 to 2 business days",
        "safety_rating": "Medium Security",
        "recommended_ip": "US or UK Clean Residential IP",
        "url": "https://surveys.gobranded.com",
        "best_for": "Branded Elite loyalty tier granting up to 19% bonus on every survey",
        "description": "Focuses on Fortune 500 product testing and consumer insights across the US and UK. Completing daily streaks advances you through Bronze, Silver, and Gold tiers.",
        "stealth_notes": "Answer the daily 5-point poll every single day without fail. The streak multiplier compounds your total weekly earnings.",
        "tags": ["vpn-tier1", "usa", "uk", "paypal", "prepaid-visa", "streak-bonus"],
    },
    {
        "slug": "survey-junkie-tier1",
        "name": "Survey Junkie",
        "category": "vpn_tier1",
        "countries": ["US", "UK"],
        "vpn_required": True,
        "pay_range": "$1.00 - $3.50 per survey",
        "payout_methods": ["PayPal", "Bank Transfer (US/UK via Wise)", "Gift Cards"],
        "min_payout": "$5.00 (500 points)",
        "payout_speed": "Instant to 24 hours",
        "safety_rating": "High Security (Strict telephone verification)",
        "recommended_ip": "Static US or UK Residential IP",
        "url": "https://www.surveyjunkie.com",
        "best_for": "Clean dashboard with direct 100 points = $1 point conversion",
        "description": "Over 20 million members across the US and UK. Simple, distraction-free interface with guaranteed point payouts for completed studies.",
        "stealth_notes": "First cashout may prompt SMS verification. Use a non-VoIP US/UK number (via TextVerified or PVACodes) if prompted. Never change demographic variables.",
        "tags": ["vpn-tier1", "usa", "uk", "paypal", "bank-transfer"],
    },
    {
        "slug": "yougov-tier1",
        "name": "YouGov (US, UK, France)",
        "category": "vpn_tier1",
        "countries": ["US", "UK", "FR"],
        "vpn_required": True,
        "pay_range": "$1.50 - $5.00 per study",
        "payout_methods": ["Direct Bank / Wise", "PayPal", "Amazon Gift Cards"],
        "min_payout": "$15 to $25 depending on country portal",
        "payout_speed": "1 to 3 business days",
        "safety_rating": "Low-to-Moderate (Very stable, low ban rate on clean IPs)",
        "recommended_ip": "Residential IP matching portal language and region",
        "url": "https://today.yougov.com",
        "best_for": "Zero screen-outs on political, social, and brand surveys",
        "description": "Global public opinion leader. Dedicated portals for US (today.yougov.com), UK (yougov.co.uk), and France (fr.yougov.com). You are never screened out mid-survey.",
        "stealth_notes": "Select one regional portal and remain on it. Match your browser language header (for example fr-FR for France) and system timezone (Europe/Paris).",
        "tags": ["vpn-tier1", "usa", "uk", "france", "zero-disqualification", "polls"],
    },
    {
        "slug": "attapoll-tier1",
        "name": "AttaPoll",
        "category": "vpn_tier1",
        "countries": ["US", "UK", "FR"],
        "vpn_required": True,
        "pay_range": "$0.75 - $3.50 per survey",
        "payout_methods": ["PayPal", "Revolut", "Amazon Gift Cards"],
        "min_payout": "$3.00",
        "payout_speed": "Instant",
        "safety_rating": "Moderate Risk",
        "recommended_ip": "Device-level SOCKS5 proxy via Tun2Socks or WireGuard",
        "url": "https://attapoll.com",
        "best_for": "Low $3 cashout threshold and fast smartphone surveys",
        "description": "Mobile-first survey application with dense survey queues in the US, UK, and France. Displays estimated completion minutes and star ratings prior to starting.",
        "stealth_notes": "Run on an Android or iOS setup where the entire device traffic routes through a clean US/UK/FR residential socks5 proxy, with device location spoofed to match.",
        "tags": ["vpn-tier1", "usa", "uk", "france", "mobile-app", "low-minimum"],
    },
    {
        "slug": "qmee-tier1",
        "name": "Qmee",
        "category": "vpn_tier1",
        "countries": ["US", "UK", "FR"],
        "vpn_required": True,
        "pay_range": "$0.50 - $3.00 per survey",
        "payout_methods": ["Instant PayPal", "Venmo", "Gift Cards"],
        "min_payout": "Zero Minimum ($0.01 threshold)",
        "payout_speed": "Instant (Under 60 seconds)",
        "safety_rating": "High Security",
        "recommended_ip": "Clean Residential IP only",
        "url": "https://www.qmee.com",
        "best_for": "Zero minimum cashout and immediate automated PayPal credit",
        "description": "Allows immediate withdrawal to PayPal without any minimum balance required. Also provides a browser companion tool paying small rewards for search activity.",
        "stealth_notes": "Initial payout requires a PayPal account link with matching identity data. Use an established residential proxy connection.",
        "tags": ["vpn-tier1", "usa", "uk", "france", "no-minimum", "instant-paypal"],
    },
    {
        "slug": "toluna-tier1",
        "name": "Toluna Influencers (France, UK, US)",
        "category": "vpn_tier1",
        "countries": ["FR", "UK", "US"],
        "vpn_required": True,
        "pay_range": "€1.00 - €4.50 ($1.20 - $5.00) per survey",
        "payout_methods": ["PayPal", "Amazon.fr / Amazon.co.uk", "Virtual Mastercards"],
        "min_payout": "€10.00 / £10.00",
        "payout_speed": "1 to 3 business days",
        "safety_rating": "Moderate",
        "recommended_ip": "French Residential IP (Paris/Lyon) or UK IP",
        "url": "https://fr.toluna.com",
        "best_for": "French (Sondages Rémunérés) and UK consumer studies",
        "description": "Massive market share in France. French consumer goods, retail, and media brands spend heavily on Toluna panels with high reward points per study.",
        "stealth_notes": "For France: set browser language header to 'fr-FR,fr;q=0.9', timezone to Europe/Paris, and specify a French postal code (e.g. 75001 Paris or 69002 Lyon).",
        "tags": ["vpn-tier1", "france", "uk", "usa", "paypal", "sondages"],
    },
    {
        "slug": "mon-opinion-compte-fr",
        "name": "Mon Opinion Compte (France Dedicated)",
        "category": "vpn_tier1",
        "countries": ["FR"],
        "vpn_required": True,
        "pay_range": "€0.75 - €3.50 per survey",
        "payout_methods": ["PayPal (€2.50 threshold)", "Amazon.fr Gift Cards"],
        "min_payout": "€2.50 (Very low threshold)",
        "payout_speed": "Under 24 hours",
        "safety_rating": "Moderate Security",
        "recommended_ip": "France Residential IP (Paris or major French city)",
        "url": "https://www.monopinioncompte.fr",
        "best_for": "Leading French survey panel with low €2.50 cashout",
        "description": "The primary survey panel dedicated exclusively to French consumers, operated by Dynata. Features steady survey queues and fast Euro cashouts.",
        "stealth_notes": "All questionnaires are written in French. Ensure browser translation or conversational French is employed. Maintain a consistent French address and household profile.",
        "tags": ["vpn-tier1", "france", "dynata", "paypal", "low-minimum"],
    },
    {
        "slug": "usertesting-tier1",
        "name": "UserTesting & Respondent.io",
        "category": "vpn_tier1",
        "countries": ["US", "UK", "FR"],
        "vpn_required": True,
        "pay_range": "$10 for 20-min test / $40 - $120 for video interviews",
        "payout_methods": ["PayPal"],
        "min_payout": "$10.00",
        "payout_speed": "Exact 7 days automated PayPal deposit",
        "safety_rating": "Strict (Voice/screen recording and profile verification)",
        "recommended_ip": "High-speed Residential IP or direct if approved",
        "url": "https://www.usertesting.com",
        "best_for": "Highest income per hour: testing websites and prototype software",
        "description": "Top qualitative user experience platforms. Clients include Apple, Google, and Canva. You speak your thoughts out loud while navigating digital prototypes.",
        "stealth_notes": "Requires a quiet background and clear headset microphone. English fluency is mandatory for US/UK tests; French fluency is required for French client studies.",
        "tags": ["vpn-tier1", "usa", "uk", "france", "usability-testing", "high-income"],
    },
]

VPN_STEALTH_PLAYBOOK: Dict[str, Any] = {
    "title": "VPN & Stealth Anti-Ban Operating Playbook for Nigerian Operators",
    "updated": "2026-10-27",
    "core_principles": [
        "Datacenter VPNs get banned immediately; Residential IPs or 4G Mobile Proxies are mandatory.",
        "Disable WebRTC and verify 100% disguise score on whoer.net before signing in.",
        "Synchronize PC clock and browser timezone with the target city IP.",
        "Adopt a rock-solid Demographic Persona Bible and never alter your identity variables.",
        "Liquidate earnings via Crypto (LTC/USDT) where available, or trade verified gift cards.",
    ],
    "chapters": [
        {
            "id": "ip_hierarchy",
            "title": "1. IP Quality and Proxy Selection (Why Free VPNs Fail)",
            "summary": "Survey networks use fraud scoring databases (MaxMind minFraud, IPQualityScore, Fraudlogix). Standard datacenter VPN IPs (NordVPN, ExpressVPN server centers) have fraud scores above 85 and are instantly banned.",
            "steps": [
                "Avoid free VPNs and standard shared datacenter IPs.",
                "Use Residential SOCKS5 proxies or Static Residential VPN services (for example Mysterium Network residential nodes, Windscribe Static Residential IP, or Proxy-Cheap residential pools).",
                "Target countries: United States (East Coast, e.g. New York, New Jersey), United Kingdom (London, Manchester), or France (Paris, Lyon).",
                "Verify your IP reputation before opening any survey tab: check https://scamalytics.com and https://ipqualityscore.com. Ensure the Fraud Score is below 20.",
            ],
        },
        {
            "id": "browser_isolation",
            "title": "2. Browser Fingerprinting, WebRTC, and Leak Prevention",
            "summary": "Even if your VPN is active, WebRTC leaks your genuine Nigerian ISP IP address directly to Javascript screeners.",
            "steps": [
                "Install a dedicated anti-detect browser (such as AdsPower or Dolphin{anty}) or configure a clean Chrome/Brave profile dedicated exclusively to survey work.",
                "Disable WebRTC: In Chrome settings, install 'WebRTC Control' or disable WebRTC via chrome://flags to guarantee your real IP is never broadcast.",
                "Test your connection on https://whoer.net and https://ipleak.net. Your disguise score must read 90% to 100%.",
                "Never open personal Nigerian accounts (like Nigerian banking apps, local Gmails) in the same browser profile.",
            ],
        },
        {
            "id": "timezone_sync",
            "title": "3. Timezone and Locale Synchronization",
            "summary": "Javascript checks your device system clock against your IP timezone. If your IP says New York (EDT, UTC-4) but your system clock is West Africa Time (WAT, UTC+1), you trigger immediate automated fraud flags.",
            "steps": [
                "For USA surveys: Set Windows / Mac timezone to 'Eastern Time (US & Canada)' and browser accept-language to 'en-US,en;q=0.9'.",
                "For UK surveys: Set timezone to 'London / GMT' and language to 'en-GB,en;q=0.9'.",
                "For France surveys: Set timezone to 'Paris / CET' and language to 'fr-FR,fr;q=0.9'.",
                "Verify matching coordinates on whoer.net prior to launching.",
            ],
        },
        {
            "id": "demographic_bible",
            "title": "4. The Golden Demographic Persona Bible (Never Get Disqualified)",
            "summary": "Market research clients pay for decision-makers who purchase goods and services. Follow these demographic rules consistently across every single survey.",
            "steps": [
                "Age: 32 to 38 years old (the highest-income demographic targeted by commercial brands).",
                "Employment: Employed Full-Time (35+ hours/week).",
                "Industry: Information Technology, Computer Software, Healthcare, or Finance.",
                "CRITICAL TRAP QUESTION: When asked 'Do you or anyone in your household work in any of the following industries?', NEVER choose Advertising, Market Research, Media, Journalism, or Public Relations. Always select 'None of the above'. Choosing market research triggers an immediate disqualification.",
                "Job Role: Middle or Senior Manager with departmental purchasing authority for IT hardware, cloud software, or office supplies.",
                "Household: Married, homeowner (with mortgage), living with spouse and 1 or 2 children aged 6 to 12.",
                "Annual Household Income: $75,000 to $95,000 (USA), £48,000 to £65,000 (UK), or €52,000 to €70,000 (France).",
                "Consistency: Record your persona's name, birthdate, street address, postal code, and income in a private file. Always provide identical data.",
            ],
        },
        {
            "id": "cashout_liquidation",
            "title": "5. Cashout and Liquidation Channels for Nigerian Operators",
            "summary": "How to convert USD, GBP, and EUR balances into Naira (NGN) without a US Social Security Number or foreign bank account.",
            "steps": [
                "Channel 1 - Direct Crypto (Fastest & Zero KYC): Freecash, Timebucks, and Surveytime support direct Litecoin (LTC) and USDT withdrawals. Transfer straight to your Binance, Bybit, Roqqu, or Luno wallet.",
                "Channel 2 - Virtual Cards & International PayPal: Redeem Virtual Visa or Mastercard vouchers. Link to virtual accounts (Geegpay, Grey, Chipper) or spend directly on cloud servers, domains, and subscriptions.",
                "Channel 3 - Amazon & Retail Gift Cards: Redeem Amazon US/UK/FR, Apple, or Google Play gift cards. Trade them through verified P2P trading desks (e.g. NoOnes, Paxful, or verified local buyers) for direct Naira bank transfer.",
            ],
        },
    ],
}


def init_surveys_table(conn: sqlite3.Connection) -> None:
    """Create the survey_platforms table and seed it idempotently."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_platforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            countries TEXT NOT NULL,
            vpn_required INTEGER DEFAULT 0,
            pay_range TEXT NOT NULL,
            payout_methods TEXT NOT NULL,
            min_payout TEXT NOT NULL,
            payout_speed TEXT,
            safety_rating TEXT,
            recommended_ip TEXT,
            url TEXT NOT NULL,
            best_for TEXT,
            description TEXT,
            stealth_notes TEXT,
            tags TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_survey_category ON survey_platforms(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_survey_slug ON survey_platforms(slug);")

    # Seed or update entries
    for item in SURVEY_REGISTRY:
        cursor.execute("""
            INSERT INTO survey_platforms (
                slug, name, category, countries, vpn_required, pay_range,
                payout_methods, min_payout, payout_speed, safety_rating,
                recommended_ip, url, best_for, description, stealth_notes, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name=excluded.name,
                category=excluded.category,
                countries=excluded.countries,
                vpn_required=excluded.vpn_required,
                pay_range=excluded.pay_range,
                payout_methods=excluded.payout_methods,
                min_payout=excluded.min_payout,
                payout_speed=excluded.payout_speed,
                safety_rating=excluded.safety_rating,
                recommended_ip=excluded.recommended_ip,
                url=excluded.url,
                best_for=excluded.best_for,
                description=excluded.description,
                stealth_notes=excluded.stealth_notes,
                tags=excluded.tags;
        """, (
            item["slug"],
            item["name"],
            item["category"],
            json.dumps(item["countries"]),
            1 if item["vpn_required"] else 0,
            item["pay_range"],
            json.dumps(item["payout_methods"]),
            item["min_payout"],
            item.get("payout_speed", "Standard"),
            item.get("safety_rating", "Verified"),
            item.get("recommended_ip", "Residential IP"),
            item["url"],
            item.get("best_for", ""),
            item.get("description", ""),
            item.get("stealth_notes", ""),
            json.dumps(item.get("tags", [])),
        ))

    conn.commit()


def get_survey_platforms(
    conn: sqlite3.Connection,
    category: str = "all",
    country: str = "all",
    search: str = "",
    vpn_required: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Query surveys from SQLite with filtering."""
    cursor = conn.cursor()
    query = "SELECT * FROM survey_platforms WHERE status = 'active'"
    params: List[Any] = []

    if category and category != "all":
        query += " AND category = ?"
        params.append(category)

    if vpn_required is not None:
        query += " AND vpn_required = ?"
        params.append(1 if vpn_required else 0)

    if country and country != "all":
        query += " AND countries LIKE ?"
        params.append(f"%{country}%")

    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR best_for LIKE ? OR tags LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s])

    query += " ORDER BY vpn_required ASC, id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        row_dict = dict(r)
        try:
            row_dict["countries"] = json.loads(row_dict["countries"])
        except Exception:
            row_dict["countries"] = []
        try:
            row_dict["payout_methods"] = json.loads(row_dict["payout_methods"])
        except Exception:
            row_dict["payout_methods"] = []
        try:
            row_dict["tags"] = json.loads(row_dict["tags"])
        except Exception:
            row_dict["tags"] = []
        row_dict["vpn_required"] = bool(row_dict["vpn_required"])
        results.append(row_dict)
    return results


def get_survey_playbook() -> Dict[str, Any]:
    """Return the structured VPN and stealth operational playbook."""
    return VPN_STEALTH_PLAYBOOK
