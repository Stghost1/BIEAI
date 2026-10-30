module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { to, recipient, subject, body } = req.body || {};
  const targetEmail = to || recipient || '';

  // Generate webmail dispatch URL for Gmail and mailto
  const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(targetEmail)}&su=${encodeURIComponent(subject || '')}&body=${encodeURIComponent(body || '')}`;
  const mailtoUrl = `mailto:${encodeURIComponent(targetEmail)}?subject=${encodeURIComponent(subject || '')}&body=${encodeURIComponent(body || '')}`;

  return res.status(200).json({
    ok: true,
    mode: 'webmail_ready',
    message: 'Proposal prepared for instant 1-click dispatch.',
    gmail_url: gmailUrl,
    mailto_url: mailtoUrl,
    recipient: targetEmail,
    email_status: 'ready_to_send'
  });
};
