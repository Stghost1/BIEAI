const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const oppId = (req.body && (req.body.opp_id || req.body.opportunity_id)) || (req.query && req.query.opp_id);
    const dataPath = path.join(process.cwd(), 'data', 'opportunities_fallback.json');
    let opp = null;

    if (fs.existsSync(dataPath)) {
      const raw = fs.readFileSync(dataPath, 'utf-8');
      const parsed = JSON.parse(raw);
      const list = parsed.opportunities || [];
      opp = list.find(o => String(o.id) === String(oppId)) || list[0];
    }

    if (!opp) {
      opp = {
        id: oppId || 1,
        company: 'Prospective Client',
        title: 'Full Stack & Automation Partner',
        url: 'https://bieai.vercel.app',
        matched_skills: ['Next.js', 'React', 'Node.js', 'Automation']
      };
    }

    const company = opp.company || 'Team';
    const title = opp.title || 'Technical Role';
    const skills = Array.isArray(opp.matched_skills) ? opp.matched_skills.join(', ') : 'Next.js, Node.js, AI workflows';
    const demoUrl = 'https://bieai.vercel.app';
    const demoName = 'B.I.E.AI Interactive Motion Studio & Radar';

    const subject = `Proof of concept for ${company}: Solving your ${title} roadmap bottlenecks`;
    const body = `Hi ${company} Team,\n\nI saw your listing for the ${title} position and rather than sending an ATS resume, I built an interactive solution to demonstrate exact capability.\n\nKey areas addressed:\n1. Zero-latency frontends & high-performance architecture (${skills})\n2. Resilient API integration & closed-loop automation\n3. 14-day production MVP sprint capability\n\nYou can inspect our live interactive proof-of-work systems here: ${demoUrl}\n\nWould you be open to a brief 10-minute exchange this week on how we can accelerate this roadmap?\n\nBest regards,\nEmmanuel Pelumi Bamidele (Bamsemma)\nFounder & Technical Lead, B.I.E.AI\nLagos & Akure · techwithbie@gmail.com · +234 905 404 5597`;

    return res.status(200).json({
      ok: true,
      draft: {
        id: `draft_${opp.id}`,
        opportunity_id: opp.id,
        opp_company: company,
        opp_title: title,
        opp_url: opp.url || '',
        subject: subject,
        hook: `Direct interactive proof-of-concept for ${company}`,
        body: body,
        recommended_demo: demoName,
        demo_url: demoUrl,
        recipient_email: opp.recipient_email || '',
        status: 'draft'
      }
    });
  } catch (err) {
    return res.status(500).json({ ok: false, error: err.message });
  }
};
