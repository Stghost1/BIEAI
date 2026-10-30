const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const dataPath = path.join(process.cwd(), 'data', 'opportunities_fallback.json');
    if (!fs.existsSync(dataPath)) {
      return res.status(200).json({ ok: true, opportunities: [], total: 0 });
    }

    const raw = fs.readFileSync(dataPath, 'utf-8');
    const parsed = JSON.parse(raw);
    let opps = parsed.opportunities || [];

    const { category, search, limit } = req.query || {};

    if (category && category !== 'all' && category !== 'All' && category !== 'High Fit (≥85)') {
      opps = opps.filter(o => 
        (o.category && o.category.toLowerCase().includes(category.toLowerCase())) ||
        (o.title && o.title.toLowerCase().includes(category.toLowerCase()))
      );
    } else if (category === 'High Fit (≥85)') {
      opps = opps.filter(o => (o.fit_score || 0) >= 85);
    }

    if (search) {
      const q = search.toLowerCase();
      opps = opps.filter(o => 
        (o.title && o.title.toLowerCase().includes(q)) ||
        (o.company && o.company.toLowerCase().includes(q)) ||
        (o.description && o.description.toLowerCase().includes(q))
      );
    }

    const maxLimit = limit ? parseInt(limit, 10) : 50;
    const sliced = opps.slice(0, maxLimit);

    return res.status(200).json({
      ok: true,
      opportunities: sliced,
      total: opps.length
    });
  } catch (err) {
    return res.status(500).json({ ok: false, error: err.message, opportunities: [] });
  }
};
