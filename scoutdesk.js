/**
 * Scoutdesk Live Frontend Engine.
 * Connects to local Python API for real-time opportunity discovery,
 * fit scoring, tailored prototype generation, and automated email dispatch.
 */

let currentFilter = 'all';
let currentSearch = '';
let currentView = 'opportunities';
let activeOpportunities = [];
let activeDraft = null;
let activeAutopilotData = null;

// Vault State
let allVaultDemos = [];
let currentVaultCategory = 'all';
let currentVaultSearch = '';

// DOM Elements
const toastEl = document.getElementById('toast');
const oppListEl = document.getElementById('opportunityList');
const searchInput = document.getElementById('searchInput');

function showToast(message) {
  if (!toastEl) return;
  toastEl.textContent = message;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), 3500);
}

function truncateSnippet(text, maxChars = 160) {
  if (!text) return '';
  if (text.length <= maxChars) return text;
  const cut = text.slice(0, maxChars);
  const lastSpace = cut.lastIndexOf(' ');
  const cleanCut = (lastSpace > maxChars - 40) ? cut.slice(0, lastSpace) : cut;
  return cleanCut.replace(/[,;:\s]+$/, '') + '...';
}

// Format today's date
const dateEl = document.getElementById('liveDate');
if (dateEl) {
  const now = new Date();
  dateEl.textContent = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
}

// Navigation Tab Switching
document.querySelectorAll('.main-nav .nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    const view = btn.dataset.view;
    switchView(view);
  });
});

function switchView(view) {
  currentView = view;
  document.querySelectorAll('.main-nav .nav-item').forEach(b => b.classList.toggle('active', b.dataset.view === view));

  document.querySelectorAll('.tab-view').forEach(v => v.style.display = 'none');
  const target = document.getElementById(`view-${view}`);
  if (target) target.style.display = 'block';

  const crumbPage = document.getElementById('crumbPage');
  if (view === 'opportunities') {
    crumbPage.textContent = 'Opportunity radar';
    loadOpportunities();
  } else if (view === 'surveys') {
    crumbPage.textContent = 'Surveys & fast income';
    loadSurveys();
  } else if (view === 'vault') {
    crumbPage.textContent = 'Tailored prototypes & vault';
    loadVault();
  } else if (view === 'pipeline') {
    crumbPage.textContent = 'Outreach pipeline';
    loadPipeline();
  } else if (view === 'demos') {
    crumbPage.textContent = 'Demo library';
    loadDemos();
  } else if (view === 'sources') {
    crumbPage.textContent = 'Configured sources';
    loadSources();
  }
}

// 1. Opportunities Feed
async function loadOpportunities() {
  if (!oppListEl) return;
  oppListEl.innerHTML = '<div style="padding:28px 0; text-align:center; color:var(--muted); font-size:12px;">Querying live SQLite database...</div>';
  try {
    const res = await fetch(`/api/opportunities?category=${currentFilter}&search=${encodeURIComponent(currentSearch)}&limit=40`);
    const data = await res.json();
    activeOpportunities = data.opportunities || [];
    renderOpportunityList(activeOpportunities);
  } catch (err) {
    oppListEl.innerHTML = '<div style="padding:24px 0; color:#ef4444; font-size:12px;">Error connecting to Scoutdesk server. Ensure server.py is running.</div>';
  }
}

function renderOpportunityList(items) {
  if (!oppListEl) return;
  if (!items.length) {
    oppListEl.innerHTML = '<div style="padding:32px 0; text-align:center; color:var(--muted); font-size:12px;">No opportunities match this filter. Click <strong>Run fresh scan</strong> to fetch new signals.</div>';
    return;
  }

  oppListEl.innerHTML = items.map(item => {
    const sourceClass = (item.source || 'board').toLowerCase();
    const skillsHtml = (item.matched_skills || []).map(s => `<span style="background:#edf7f2; color:#278b68; padding:2px 7px; border-radius:12px; font-size:9px; font-weight:600;">${escapeHtml(s)}</span>`).join(' ');
    const dorkUrl = `https://www.google.com/search?q=${encodeURIComponent('"' + item.company + '" ("CTO" OR "Founder" OR "Head of Engineering") site:linkedin.com/in')}`;

    return `
      <article class="opportunity" data-id="${item.id}">
        <div class="source-icon ${sourceClass}">${(item.source || 'W').charAt(0)}</div>
        <div>
          <div style="font-size:10px; color:var(--muted); font-family:'DM Mono',monospace; margin-bottom:2px; display:flex; align-items:center; gap:8px;">
            <span>${escapeHtml(item.company)} &bull; <strong style="color:#278b68;">${escapeHtml(item.budget || 'Competitive')}</strong></span>
            <span class="ats-badge-pill" title="JobAssist Match Analysis">${item.fit_score}% ATS Match</span>
          </div>
          <h3 style="cursor:pointer;" onclick="openOpportunityModal(${item.id})">${escapeHtml(item.title)}</h3>
          <p>${escapeHtml(truncateSnippet(item.description, 160))}</p>
          <div class="opportunity-meta" style="align-items:center;">
            <span>${escapeHtml(item.source)}</span>
            <span>${skillsHtml}</span>
          </div>
          <div class="row-actions" style="display:flex; gap:6px; margin-top:8px; flex-wrap:wrap;">
            <button class="row-action outline" onclick="openOpportunityModal(${item.id})">View details</button>
            <button class="row-action" style="font-weight:700;" onclick="draftOutreach(${item.id})">⚡ Draft outreach</button>
            <button class="row-action" style="background:#0f172a; color:#38bdf8; border:1px solid #0284c7; font-weight:700;" onclick="triggerAutopilot(${item.id})" title="Synthesize dedicated demo product, deploy route to Vercel, and auto-dispatch proposal">🚀 Auto-Pilot</button>
            <button class="row-action outline" style="background:#f0fdf4; color:#15803d; border-color:#86efac; font-weight:600;" onclick="triggerScourEmail(${item.id})" title="Scour company website, public contact points, and MX records for direct emails">🎯 Scour Email</button>
            <button class="row-action outline" style="background:#faf5ff; color:#7e22ce; border-color:#d8b4fe; font-weight:600;" onclick="triggerBuildDemo(${item.id})" title="Build real interactive prototype tailored to this job, commit to GitHub, and deploy to Vercel">🔨 Build Demo</button>
            <a href="${dorkUrl}" target="_blank" rel="noopener" class="row-action outline" style="text-decoration:none; font-size:10px; color:#0369a1; border-color:#bae6fd; background:#f0f9ff;" title="Search CTO/Founder on LinkedIn (The Anti Job)">🎯 Find CTO ↗</a>
          </div>
        </div>
        <div class="fit-score">
          <strong style="${item.fit_score >= 88 ? 'color:#278b68;' : 'color:#d97706;'}">${item.fit_score}</strong>
          <small>${escapeHtml(item.fit_tag || 'Good fit')}</small>
        </div>
      </article>
    `;
  }).join('');
}

function setFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll('#filterRow .filter-chip').forEach(c => c.classList.toggle('active', c.dataset.filter === filter));
  loadOpportunities();
}

let searchTimer;
function handleSearch(val) {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    currentSearch = val.trim();
    loadOpportunities();
  }, 300);
}

// 2. Opportunity Modal & Outreach
let selectedOpportunityId = null;

function openOpportunityModal(id) {
  const item = activeOpportunities.find(o => o.id === id);
  if (!item) return;
  selectedOpportunityId = id;

  document.getElementById('modalCompany').textContent = `${item.company} (${item.source})`;
  document.getElementById('modalTitle').textContent = item.title;
  document.getElementById('modalBody').textContent = item.description || 'No extended description provided.';
  document.getElementById('modalMeta').innerHTML = `
    <span>${item.fit_score}/100 Fit Score</span>
    <span>${item.category}</span>
    <span>Source: ${item.source}</span>
    <span>Status: ${item.status}</span>
  `;

  const extLink = document.getElementById('modalExtUrl');
  if (extLink) extLink.href = item.url || '#';

  const modal = document.getElementById('modalBackdrop');
  if (modal) modal.classList.add('open');
}

function closeModal() {
  const modal = document.getElementById('modalBackdrop');
  if (modal) modal.classList.remove('open');
}

function draftFromModal() {
  if (selectedOpportunityId) {
    closeModal();
    draftOutreach(selectedOpportunityId);
  }
}

function autopilotFromModal() {
  if (selectedOpportunityId) {
    closeModal();
    triggerAutopilot(selectedOpportunityId);
  }
}

function buildDemoFromModal() {
  if (selectedOpportunityId) {
    closeModal();
    triggerBuildDemo(selectedOpportunityId);
  }
}

async function draftOutreach(id) {
  showToast('Generating tailored proposal referencing verified demos...');
  try {
    const res = await fetch('/api/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: id })
    });
    const data = await res.json();
    if (data.ok && data.draft) {
      activeDraft = data.draft;
      openDraftModal(activeDraft);
    } else {
      showToast(data.error || 'Failed to generate proposal');
    }
  } catch (err) {
    showToast('Error connecting to proposal API.');
  }
}

let currentDraftAngle = 'proof_of_work';

function openDraftModal(draft) {
  activeDraft = draft;
  document.getElementById('draftCompany').textContent = `${draft.opp_company || 'Client'} &bull; ${draft.opp_title || 'Opportunity'}`;
  document.getElementById('draftDemoName').textContent = draft.recommended_demo || draft.demo_name || 'B.I.E.AI Studio';

  const demoLink = document.getElementById('draftDemoUrl');
  if (demoLink) {
    demoLink.href = draft.demo_url || 'https://bieai.vercel.app';
    demoLink.textContent = draft.demo_url || 'preview link';
  }

  const recInput = document.getElementById('draftRecipientEmail');
  if (recInput) recInput.value = draft.recipient_email || '';

  const jobLink = document.getElementById('draftJobLink');
  if (jobLink) jobLink.href = draft.opp_url || '#';

  document.getElementById('draftSubject').value = draft.subject;
  document.getElementById('draftBody').value = draft.body;

  // Set Pitch Angle buttons
  const angle = draft.angle || currentDraftAngle || 'proof_of_work';
  currentDraftAngle = angle;
  document.querySelectorAll('#draftAngleBar .pitch-angle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.angle === angle);
  });

  // Set ATS Fit Badge
  const atsBadge = document.getElementById('draftAtsBadge');
  if (atsBadge) {
    atsBadge.textContent = `${draft.ats_score || 88}% ATS Match`;
  }

  // Populate Decision-Maker Links (The Anti-Job)
  const dorks = draft.decision_dorks || {};
  const comp = draft.opp_company || 'Company';
  const role = draft.opp_title || 'Engineer';

  const gLink = document.getElementById('dorkGoogleLink');
  if (gLink) {
    gLink.href = dorks.google_dork_url || `https://www.google.com/search?q=${encodeURIComponent('"' + comp + '" ("CTO" OR "Founder" OR "Head of Engineering") site:linkedin.com/in')}`;
  }
  const cLink = document.getElementById('dorkCompanyLink');
  if (cLink) {
    cLink.href = dorks.linkedin_search_url || `https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(comp + ' engineering')}`;
  }
  const xLink = document.getElementById('dorkXLink');
  if (xLink) {
    xLink.href = dorks.x_search_url || `https://twitter.com/search?q=${encodeURIComponent('"' + comp + '" hiring')}`;
  }

  const modal = document.getElementById('draftModalBackdrop');
  if (modal) modal.classList.add('open');
}

async function switchDraftAngle(angle) {
  currentDraftAngle = angle;
  document.querySelectorAll('#draftAngleBar .pitch-angle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.angle === angle);
  });
  if (!activeDraft) return;
  const oppId = activeDraft.opportunity_id || activeDraft.id;
  if (!oppId) return;

  showToast(`Synthesizing ${angle.replace('_', ' ')} pitch...`);
  try {
    const res = await fetch('/api/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: oppId, angle: angle })
    });
    const data = await res.json();
    if (data.ok && data.draft) {
      activeDraft = data.draft;
      document.getElementById('draftSubject').value = activeDraft.subject;
      document.getElementById('draftBody').value = activeDraft.body;
      showToast('Proposal re-synthesized with ' + angle.replace('_', ' ') + ' strategy.');
    }
  } catch (err) {
    showToast('Failed to switch pitch angle.');
  }
}

async function triggerScourEmail(oppId) {
  showToast('Scouring company web domain & MX records for decision-makers...');
  try {
    const res = await fetch('/api/scour/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: oppId })
    });
    const data = await res.json();
    if (data.ok && data.email) {
      showToast(`🎯 Found: ${data.email} (${data.confidence || 'Verified MX'})`);
      const item = activeOpportunities.find(o => o.id === oppId);
      if (item) {
        item.recipient_email = data.email;
      }
    } else {
      showToast('No direct email discovered. Use Find CTO ↗ for manual LinkedIn connection.');
    }
  } catch (err) {
    showToast('Email scour request failed: ' + err.message);
  }
}

async function triggerBuildDemo(oppId) {
  const item = activeOpportunities.find(o => o.id === oppId);
  const comp = item ? item.company : 'Client';
  showToast(`Building bespoke micro-app for ${comp}, committing to GitHub & deploying to Vercel...`);
  try {
    const res = await fetch('/api/demo/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: oppId })
    });
    const data = await res.json();
    if (data.ok && data.demo) {
      showToast(`🚀 Live prototype ready: ${data.demo.file_name} (Deployed & GitHub-synced)`);
      if (data.demo.recipient_email && item) {
        item.recipient_email = data.demo.recipient_email;
      }
      await loadVault();
      openSandboxModal(data.demo.title, data.demo.demo_url);
    } else {
      showToast('Error building prototype: ' + (data.error || 'Unknown error'));
    }
  } catch (err) {
    showToast('Failed to build demo: ' + err.message);
  }
}

async function scourEmailForCurrentDraft() {
  if (!activeDraft) return;
  const oppId = activeDraft.opportunity_id;
  const badge = document.getElementById('scourStatusBadge');
  if (badge) badge.textContent = 'Probing domain & MX mail exchangers...';
  try {
    const res = await fetch('/api/scour/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        opp_id: oppId,
        company: activeDraft.opp_company,
        url: activeDraft.opp_url
      })
    });
    const data = await res.json();
    if (data.ok && data.email) {
      document.getElementById('draftRecipientEmail').value = data.email;
      if (badge) badge.textContent = `✓ Discovered: ${data.email} (${data.confidence || 'Verified MX'})`;
      showToast(`Scoured: ${data.email}`);
    } else {
      if (badge) badge.textContent = 'No public inbox found. Try Find CTO on LinkedIn.';
    }
  } catch (err) {
    if (badge) badge.textContent = 'Scour request error.';
  }
}

async function applyCadenceFollowup(touch) {
  if (!activeDraft) return;
  const oppId = activeDraft.opportunity_id || activeDraft.id;
  if (!oppId) return;

  showToast(`Synthesizing Touch ${touch} follow-up cadence...`);
  try {
    const res = await fetch('/api/followup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: oppId, draft: activeDraft, touch: touch })
    });
    const data = await res.json();
    if (data.ok && data.followup) {
      document.getElementById('draftSubject').value = data.followup.subject;
      document.getElementById('draftBody').value = data.followup.body;
      showToast(`Loaded Touch ${touch} follow-up into composer.`);
    }
  } catch (err) {
    showToast('Failed to generate follow-up.');
  }
}

function closeDraftModal() {
  const modal = document.getElementById('draftModalBackdrop');
  if (modal) modal.classList.remove('open');
}

function insertPortfolioLink(type) {
  const bodyEl = document.getElementById('draftBody');
  if (!bodyEl) return;
  const portfolioUrl = appSettings.portfolio_url || 'https://bieai.vercel.app';
  const githubUrl = appSettings.github_url || 'https://github.com/Stghost1/BIEAI';
  const urlToInsert = type === 'vercel' ? portfolioUrl : githubUrl;

  const start = bodyEl.selectionStart;
  const end = bodyEl.selectionEnd;
  const text = bodyEl.value;
  bodyEl.value = text.substring(0, start) + urlToInsert + text.substring(end);
  bodyEl.selectionStart = bodyEl.selectionEnd = start + urlToInsert.length;
  bodyEl.focus();
  showToast(`Inserted ${type === 'vercel' ? 'Vercel' : 'GitHub'} link.`);
}

async function saveDraftEdits() {
  if (!activeDraft) return;
  const newSubject = document.getElementById('draftSubject').value;
  const newBody = document.getElementById('draftBody').value;
  const newRecipient = document.getElementById('draftRecipientEmail').value.trim();

  try {
    const res = await fetch('/api/pipeline/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        draft_id: activeDraft.id,
        status: activeDraft.status || 'draft',
        subject: newSubject,
        body: newBody,
        recipient_email: newRecipient
      })
    });
    const data = await res.json();
    if (data.ok) {
      showToast('Proposal updates saved.');
      activeDraft.subject = newSubject;
      activeDraft.body = newBody;
      activeDraft.recipient_email = newRecipient;
    }
  } catch (err) {
    showToast('Failed to save edits.');
  }
}

function copyDraftToClipboard() {
  const body = document.getElementById('draftBody').value;
  const subject = document.getElementById('draftSubject').value;
  const recipient = document.getElementById('draftRecipientEmail').value;
  const fullText = `To: ${recipient}\nSubject: ${subject}\n\n${body}`;

  navigator.clipboard.writeText(fullText).then(() => {
    showToast('Proposal & headers copied to clipboard.');
  }).catch(() => {
    showToast('Could not access clipboard.');
  });
}

function sendViaGmail() {
  saveDraftEdits();
  const recipient = encodeURIComponent(document.getElementById('draftRecipientEmail').value.trim());
  const subject = encodeURIComponent(document.getElementById('draftSubject').value);
  const body = encodeURIComponent(document.getElementById('draftBody').value);
  const url = `https://mail.google.com/mail/?view=cm&fs=1&to=${recipient}&su=${subject}&body=${body}`;
  window.open(url, '_blank');
  showToast('Opening Gmail web compose...');
}

function sendViaOutlook() {
  saveDraftEdits();
  const recipient = encodeURIComponent(document.getElementById('draftRecipientEmail').value.trim());
  const subject = encodeURIComponent(document.getElementById('draftSubject').value);
  const body = encodeURIComponent(document.getElementById('draftBody').value);
  const url = `https://outlook.live.com/mail/0/deeplink/compose?to=${recipient}&subject=${subject}&body=${body}`;
  window.open(url, '_blank');
  showToast('Opening Outlook web compose...');
}

function sendViaDesktopMail() {
  saveDraftEdits();
  const recipient = encodeURIComponent(document.getElementById('draftRecipientEmail').value.trim());
  const subject = encodeURIComponent(document.getElementById('draftSubject').value);
  const body = encodeURIComponent(document.getElementById('draftBody').value);
  const mailtoUrl = `mailto:${recipient}?subject=${subject}&body=${body}`;

  const link = document.createElement('a');
  link.href = mailtoUrl;
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast('Invoking default mail client...');
}

// 3. Autonomous Auto-Pilot Execution
async function triggerAutopilot(oppId) {
  const modal = document.getElementById('autopilotModalBackdrop');
  if (!modal) return;
  modal.classList.add('open');

  document.getElementById('apStatusBadge').textContent = 'Running...';
  document.getElementById('apStatusBadge').style.background = '#f0f9ff';
  document.getElementById('apStatusBadge').style.color = '#0369a1';
  document.getElementById('apStatusBadge').style.borderColor = '#bae6fd';

  document.getElementById('apDemoCard').style.display = 'none';
  document.getElementById('apProposalCard').style.display = 'none';

  // Reset steps
  for (let i = 1; i <= 6; i++) {
    const el = document.getElementById(`apStep${i}`);
    if (el) {
      el.className = 'autopilot-step';
    }
  }

  // Progressive step runner through all 6 stages
  let currentStep = 1;
  const s1 = document.getElementById('apStep1');
  if (s1) s1.className = 'autopilot-step running';

  const stepTimer = setInterval(() => {
    if (currentStep < 6) {
      const prev = document.getElementById(`apStep${currentStep}`);
      if (prev) prev.className = 'autopilot-step done';
      currentStep++;
      const next = document.getElementById(`apStep${currentStep}`);
      if (next) next.className = 'autopilot-step running';
    }
  }, 2200);

  showToast('Executing full 6-stage Auto-Pilot pipeline...');

  try {
    const res = await fetch('/api/autopilot/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: oppId, auto_send: true })
    });
    const data = await res.json();
    clearInterval(stepTimer);
    activeAutopilotData = data;

    if (!data.ok) {
      showToast(data.error || 'Auto-pilot failed');
      document.getElementById('apStatusBadge').textContent = 'Failed';
      return;
    }

    // Mark all 6 stages complete
    for (let i = 1; i <= 6; i++) {
      const el = document.getElementById(`apStep${i}`);
      if (el) el.className = 'autopilot-step done';
    }

    // Populate Demo Product Banner
    const demoCard = document.getElementById('apDemoCard');
    demoCard.style.display = 'block';
    document.getElementById('apDemoTitle').innerHTML = data.demo.title || 'Tailored Prototype';
    document.getElementById('apDemoStack').textContent = data.demo.tech_stack || 'React / Next.js';
    document.getElementById('apDemoDesc').textContent = data.demo.preview_desc || '';
    const demoLink = document.getElementById('apDemoLink');
    if (demoLink) demoLink.href = data.demo.demo_url || '#';

    // Populate Proposal Card
    const propCard = document.getElementById('apProposalCard');
    propCard.style.display = 'block';
    document.getElementById('apRecipientEmail').value = data.recipient || '';
    document.getElementById('apSubject').value = data.draft.subject || '';
    document.getElementById('apBody').value = data.draft.body || '';

    // Status Badge
    const badge = document.getElementById('apStatusBadge');
    if (data.email_status === 'sent') {
      badge.textContent = 'Dispatched via SMTP';
      badge.style.background = '#edf7f2';
      badge.style.color = '#166534';
      badge.style.borderColor = '#bbf7d0';
    } else {
      badge.textContent = 'Prototype Live & Ready';
      badge.style.background = '#edf7f2';
      badge.style.color = '#166534';
      badge.style.borderColor = '#bbf7d0';
    }

    showToast('Tailored prototype synthesized & proposal drafted!');
    loadStats();
    loadVault();
  } catch (err) {
    showToast('Error communicating with Auto-Pilot API.');
  }
}

function closeAutopilotModal() {
  const modal = document.getElementById('autopilotModalBackdrop');
  if (modal) modal.classList.remove('open');
}

function copyApDemoUrl() {
  if (activeAutopilotData && activeAutopilotData.demo && activeAutopilotData.demo.demo_url) {
    navigator.clipboard.writeText(activeAutopilotData.demo.demo_url).then(() => {
      showToast('Live prototype URL copied to clipboard.');
    });
  }
}

function copyApProposal() {
  const recipient = document.getElementById('apRecipientEmail').value;
  const subject = document.getElementById('apSubject').value;
  const body = document.getElementById('apBody').value;
  const full = `To: ${recipient}\nSubject: ${subject}\n\n${body}`;
  navigator.clipboard.writeText(full).then(() => {
    showToast('Proposal and headers copied.');
  });
}

function sendApViaGmail() {
  const recipient = encodeURIComponent(document.getElementById('apRecipientEmail').value.trim());
  const subject = encodeURIComponent(document.getElementById('apSubject').value);
  const body = encodeURIComponent(document.getElementById('apBody').value);
  window.open(`https://mail.google.com/mail/?view=cm&fs=1&to=${recipient}&su=${subject}&body=${body}`, '_blank');
}

function sendApViaOutlook() {
  const recipient = encodeURIComponent(document.getElementById('apRecipientEmail').value.trim());
  const subject = encodeURIComponent(document.getElementById('apSubject').value);
  const body = encodeURIComponent(document.getElementById('apBody').value);
  window.open(`https://outlook.live.com/mail/0/deeplink/compose?to=${recipient}&subject=${subject}&body=${body}`, '_blank');
}

async function dispatchApViaSmtp() {
  const btn = document.getElementById('apSendSmtpBtn');
  const recipient = document.getElementById('apRecipientEmail').value.trim();
  const subject = document.getElementById('apSubject').value;
  const body = document.getElementById('apBody').value;
  const draftId = activeAutopilotData && activeAutopilotData.draft ? activeAutopilotData.draft.id : null;

  if (!recipient) {
    showToast('Please enter a recipient email address.');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Sending...';

  try {
    const res = await fetch('/api/mailer/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient, subject, body, draft_id: draftId })
    });
    const data = await res.json();
    btn.disabled = false;
    btn.textContent = '🚀 Send Email Now (SMTP)';

    if (data.ok && data.mode === 'smtp') {
      showToast(`Success: ${data.message}`);
      document.getElementById('apStatusBadge').textContent = 'Sent via SMTP';
      loadStats();
    } else if (data.ok && data.mode === 'webmail_ready') {
      showToast('SMTP password not set in settings. Opening Gmail...');
      sendApViaGmail();
    } else {
      showToast(data.error || 'Failed to dispatch email.');
    }
  } catch (err) {
    btn.disabled = false;
    btn.textContent = '🚀 Send Email Now (SMTP)';
    showToast('Error communicating with mailer API.');
  }
}

// 4. Batch Auto-Pilot Modal
function openBatchAutopilotModal() {
  const modal = document.getElementById('batchAutopilotModalBackdrop');
  if (modal) modal.classList.add('open');
}

function closeBatchAutopilotModal() {
  const modal = document.getElementById('batchAutopilotModalBackdrop');
  if (modal) modal.classList.remove('open');
}

async function executeBatchAutopilot() {
  const limit = parseInt(document.getElementById('batchLimitSelect').value) || 3;
  const minFit = parseInt(document.getElementById('batchScoreSelect').value) || 80;
  const autoSend = document.getElementById('batchAutoSendCheck').checked;

  const btn = document.getElementById('startBatchBtn');
  btn.disabled = true;
  btn.textContent = 'Running Batch...';

  const progressBox = document.getElementById('batchProgressBox');
  const statusText = document.getElementById('batchStatusText');
  const progressBar = document.getElementById('batchProgressBar');
  const logList = document.getElementById('batchLogList');

  progressBox.style.display = 'block';
  statusText.textContent = `Synthesizing prototypes for top ${limit} leads...`;
  progressBar.style.width = '30%';
  logList.innerHTML = '<div>Initiating batch execution...</div>';

  try {
    const res = await fetch('/api/autopilot/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ limit, min_fit: minFit, auto_send: autoSend })
    });
    const data = await res.json();
    btn.disabled = false;
    btn.textContent = '🚀 Run Auto-Pilot Batch';

    if (data.ok && data.results) {
      progressBar.style.width = '100%';
      statusText.textContent = `Completed! ${data.count} tailored prototypes created.`;

      logList.innerHTML = data.results.map(r => {
        if (r.ok) {
          return `<div style="color:#166534;">&bull; <strong>${escapeHtml(r.company)}:</strong> Prototype deployed at <a href="${r.demo.demo_url}" target="_blank" style="text-decoration:underline;">${r.demo.slug}</a> (${r.email_status})</div>`;
        } else {
          return `<div style="color:#b91c1c;">&bull; ${escapeHtml(r.company)}: ${escapeHtml(r.error || 'Failed')}</div>`;
        }
      }).join('');

      showToast(`Batch completed: ${data.count} prototypes created and deployed.`);
      loadStats();
      loadVault();
      setTimeout(() => {
        closeBatchAutopilotModal();
        switchView('vault');
      }, 2500);
    } else {
      showToast(data.error || 'Batch failed');
    }
  } catch (err) {
    btn.disabled = false;
    btn.textContent = '🚀 Run Auto-Pilot Batch';
    showToast('Error communicating with batch API.');
  }
}

// 5. Tailored Demos & Vault Library
async function loadVault() {
  const grid = document.getElementById('vaultGrid');
  if (!grid) return;
  grid.innerHTML = '<div style="padding:24px 0; text-align:center; color:var(--muted); font-size:12px;">Loading vault prototypes...</div>';

  try {
    const res = await fetch('/api/portfolio/demos');
    const data = await res.json();
    allVaultDemos = data.demos || [];
    renderVault(allVaultDemos);

    const countEl = document.getElementById('vaultCount');
    if (countEl) countEl.textContent = allVaultDemos.length;
    const navVault = document.getElementById('navVaultCount');
    if (navVault) navVault.textContent = allVaultDemos.length;
    const statVault = document.getElementById('statVaultDemos');
    if (statVault) statVault.textContent = allVaultDemos.length;
    return allVaultDemos;
  } catch (err) {
    grid.innerHTML = '<div style="padding:24px 0; color:#ef4444; font-size:12px;">Error loading vault prototypes.</div>';
    return [];
  }
}

// Universal aliases ensuring loadVaultDemos and loadVaultDemo are always defined globally
async function loadVaultDemos() {
  return await loadVault();
}
async function loadVaultDemo() {
  return await loadVault();
}

window.loadVault = loadVault;
window.loadVaultDemos = loadVaultDemos;
window.loadVaultDemo = loadVaultDemo;

function setVaultCategory(cat) {
  currentVaultCategory = cat;
  document.querySelectorAll('#vaultFilterChips .filter-chip').forEach(c => c.classList.toggle('active', c.dataset.vcat === cat));
  filterAndRenderVault();
}

function filterVaultDemos(query) {
  currentVaultSearch = (query || '').toLowerCase().trim();
  filterAndRenderVault();
}

function filterAndRenderVault() {
  let filtered = allVaultDemos;
  if (currentVaultCategory !== 'all') {
    filtered = filtered.filter(d => (d.category || '').toLowerCase() === currentVaultCategory.toLowerCase());
  }
  if (currentVaultSearch) {
    filtered = filtered.filter(d => {
      const hay = `${d.title} ${d.company} ${d.tech_stack} ${d.preview_desc} ${d.slug}`.toLowerCase();
      return hay.includes(currentVaultSearch);
    });
  }
  renderVault(filtered);
}

function renderVault(demos) {
  const grid = document.getElementById('vaultGrid');
  if (!grid) return;

  if (!demos.length) {
    grid.innerHTML = '<div style="padding:32px 0; text-align:center; color:var(--muted); font-size:12px; grid-column:span 3;">No prototypes found matching this filter. Run Auto-Pilot on opportunities to build dedicated prototypes.</div>';
    return;
  }

  grid.innerHTML = demos.map(d => {
    const liveUrl = d.demo_url.startsWith('http') ? d.demo_url : `https://bieai.vercel.app/${d.slug}`;
    return `
      <div class="vault-card" style="background:#fff; border:1px solid var(--line); border-radius:12px; padding:18px; display:flex; flex-direction:column; justify-content:space-between; transition:transform 0.15s ease, border-color 0.15s ease;">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:9px; font-family:'DM Mono',monospace; padding:2px 7px; border-radius:10px; background:#f0f9ff; color:#0369a1; border:1px solid #bae6fd; text-transform:uppercase; font-weight:700;">
              ${escapeHtml(d.category || 'General')}
            </span>
            <span style="font-size:9px; font-family:'DM Mono',monospace; color:#166534; background:#edf7f2; padding:2px 6px; border-radius:8px;">
              ● Vercel Live
            </span>
          </div>
          <h3 style="font-size:15px; font-weight:700; color:var(--ink); margin:0 0 4px; line-height:1.3;">
            ${d.title}
          </h3>
          <div style="font-size:10px; font-family:'DM Mono',monospace; color:var(--muted); margin-bottom:8px;">
            ${escapeHtml(d.company)} &bull; <span style="color:#0284c7;">${escapeHtml(d.tech_stack || 'React, TypeScript')}</span>
          </div>
          <p style="font-size:11px; color:var(--muted); line-height:1.5; margin:0 0 14px;">
            ${escapeHtml(d.preview_desc || 'Interactive proof-of-work application.')}
          </p>
        </div>
        <div style="display:flex; gap:6px; align-items:center; border-top:1px solid #f1f5f3; padding-top:12px; flex-wrap:wrap;">
          <a href="${liveUrl}" target="_blank" rel="noopener" style="text-decoration:none; background:#0f172a; color:#38bdf8; border:1px solid #0284c7; padding:6px 12px; font-size:10px; font-weight:700; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">
            <span>Open Demo</span> ↗
          </a>
          <button class="secondary-button" onclick="openSandboxModal('${escapeHtml(d.title)}', '${liveUrl}')" style="padding:6px 10px; font-size:10px; background:#f0f9ff; color:#0369a1; border:1px solid #bae6fd;">
            👁 Preview
          </button>
          <button class="secondary-button" onclick="navigator.clipboard.writeText('${liveUrl}'); showToast('Demo URL copied!');" style="padding:6px 10px; font-size:10px; background:#f8fafc; border:1px solid var(--line);">
            📋 Copy URL
          </button>
        </div>
      </div>
    `;
  }).join('');
}

// 6. Surveys & Fast Income
let allSurveys = [];
let currentSurveyCategory = 'all';
let currentSurveyCountry = 'all';
let currentSurveySearch = '';

async function loadSurveys() {
  const grid = document.getElementById('surveyGrid');
  if (!grid) return;
  grid.innerHTML = '<div style="padding:28px 0; text-align:center; color:var(--muted); font-size:12px;">Loading vetted survey platforms...</div>';

  try {
    const res = await fetch(`/api/surveys?category=${currentSurveyCategory}&country=${currentSurveyCountry}&search=${encodeURIComponent(currentSurveySearch)}`);
    const data = await res.json();
    allSurveys = data.surveys || [];
    renderSurveys(allSurveys);
  } catch (err) {
    grid.innerHTML = '<div style="padding:24px 0; color:#ef4444; font-size:12px;">Error connecting to surveys API.</div>';
  }
}

function setSurveyCategory(cat) {
  currentSurveyCategory = cat;
  currentSurveyCountry = 'all';
  document.querySelectorAll('#surveyFilterRow .filter-chip').forEach(c => c.classList.toggle('active', c.dataset.scat === cat));
  loadSurveys();
}

function setSurveyCountry(country) {
  currentSurveyCountry = country;
  currentSurveyCategory = 'all';
  document.querySelectorAll('#surveyFilterRow .filter-chip').forEach(c => c.classList.toggle('active', c.dataset.scat === country.toLowerCase()));
  loadSurveys();
}

let surveySearchTimer;
function handleSurveySearch(val) {
  clearTimeout(surveySearchTimer);
  surveySearchTimer = setTimeout(() => {
    currentSurveySearch = val.trim();
    loadSurveys();
  }, 300);
}

function renderSurveys(items) {
  const grid = document.getElementById('surveyGrid');
  if (!grid) return;

  if (!items.length) {
    grid.innerHTML = '<div style="padding:32px 0; text-align:center; color:var(--muted); font-size:12px; grid-column:span 2;">No survey platforms match your current filter.</div>';
    return;
  }

  grid.innerHTML = items.map(s => {
    const isVpn = s.vpn_required;
    const badgeClass = isVpn ? 'badge-vpn' : 'badge-local';
    const badgeText = isVpn ? 'VPN Required (Tier-1)' : 'Nigeria Direct (Zero VPN)';
    const countries = (s.countries || []).join(' &bull; ');
    const payoutMethods = (s.payout_methods || []).map(p => `<span class="badge-tag">${escapeHtml(p)}</span>`).join(' ');

    return `
      <div class="survey-card">
        <div>
          <div class="survey-card-header">
            <div>
              <span class="eyebrow" style="margin-bottom:2px;">${escapeHtml(countries)}</span>
              <h3 style="font-size:16px; margin:0 0 4px; font-weight:700;">${escapeHtml(s.name)}</h3>
            </div>
            <span class="badge-pill ${badgeClass}">${badgeText}</span>
          </div>

          <p style="font-size:11px; line-height:1.6; color:var(--muted); margin:0 0 12px;">${escapeHtml(s.description)}</p>

          <div class="survey-meta-grid">
            <div class="survey-meta-item">
              <span class="survey-meta-label">Est. Yield</span>
              <span class="survey-meta-val" style="color:#278b68;">${escapeHtml(s.earning_potential || 'Variable')}</span>
            </div>
            <div class="survey-meta-item">
              <span class="survey-meta-label">Min Cashout</span>
              <span class="survey-meta-val">${escapeHtml(s.min_cashout || 'None')}</span>
            </div>
          </div>

          <div style="margin-top:10px;">
            <span class="survey-meta-label">Payout Channels:</span>
            <div style="display:flex; flex-wrap:wrap; gap:4px; margin-top:4px;">
              ${payoutMethods}
            </div>
          </div>

          ${s.safety_tip ? `
            <div class="survey-safety-tip">
              <strong>Operational Tip:</strong> ${escapeHtml(s.safety_tip)}
            </div>
          ` : ''}
        </div>

        <div style="margin-top:16px; display:flex; justify-content:space-between; align-items:center; border-top:1px solid #f1f5f3; padding-top:12px;">
          <span style="font-size:10px; font-family:'DM Mono',monospace; color:var(--muted);">Category: ${escapeHtml(s.category)}</span>
          <a class="row-action" href="${s.url}" target="_blank" rel="noopener" style="text-decoration:none; display:inline-flex; align-items:center; gap:4px; font-weight:700;">
            <span>Open Platform</span> &rarr;
          </a>
        </div>
      </div>
    `;
  }).join('');
}

// Playbook Modal
async function openPlaybookModal() {
  const modal = document.getElementById('playbookModalBackdrop');
  if (!modal) return;
  modal.classList.add('open');

  const container = document.getElementById('playbookChaptersContainer');
  if (!container) return;

  try {
    const res = await fetch('/api/surveys/playbook');
    const data = await res.json();
    renderPlaybook(data.playbook);
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; font-size:12px;">Error loading anti-ban playbook.</div>';
  }
}

function renderPlaybook(playbook) {
  const container = document.getElementById('playbookChaptersContainer');
  if (!container || !playbook) return;

  const chapters = playbook.chapters || [];
  container.innerHTML = `
    ${chapters.map((ch, idx) => `
      <div class="playbook-chapter">
        <h4>${escapeHtml(ch.title)}</h4>
        <p>${escapeHtml(ch.content)}</p>
      </div>
    `).join('')}
    <div class="persona-card">
      <strong>📋 Recommended Survey Persona Cheat Sheet:</strong><br>
      &bull; <strong>Age:</strong> 34 (DOB: May 14, 1992)<br>
      &bull; <strong>Employment:</strong> Full-Time (IT Systems Engineer / Project Lead)<br>
      &bull; <strong>Household:</strong> Married, 1 child (age 7), homeowner with mortgage<br>
      &bull; <strong>Annual Income:</strong> $82,000 (US) / £52,000 (UK) / €58,000 (France)<br>
      &bull; <strong>Industry Disqualification Trap:</strong> NEVER check Advertising, Market Research, PR, or Media. Always select "None of the above".
    </div>
  `;
}

function closePlaybookModal() {
  const modal = document.getElementById('playbookModalBackdrop');
  if (modal) modal.classList.remove('open');
}

// 7. Outreach Pipeline & Kanban View (JobAssist Benchmark)
let pipelineViewMode = 'kanban';

function setPipelineViewMode(mode) {
  pipelineViewMode = mode;
  const btnK = document.getElementById('btnViewKanban');
  const btnL = document.getElementById('btnViewList');
  const kWrap = document.getElementById('pipelineKanbanContainer');
  const lWrap = document.getElementById('pipelineContainer');

  if (btnK) btnK.classList.toggle('active', mode === 'kanban');
  if (btnL) btnL.classList.toggle('active', mode === 'list');

  if (kWrap) kWrap.style.display = mode === 'kanban' ? 'block' : 'none';
  if (lWrap) lWrap.style.display = mode === 'list' ? 'block' : 'none';

  loadPipeline();
}

async function loadPipeline() {
  const kanbanContainer = document.getElementById('pipelineKanbanContainer');
  const listContainer = document.getElementById('pipelineContainer');

  try {
    const [pipeRes, oppRes, demosRes] = await Promise.all([
      fetch('/api/pipeline'),
      fetch('/api/opportunities?limit=100'),
      fetch('/api/portfolio/demos')
    ]);
    const pipeData = await pipeRes.json();
    const oppData = await oppRes.json();
    const demosData = await demosRes.json();

    const drafts = pipeData.pipeline || [];
    const opps = oppData.opportunities || [];
    const demos = demosData.demos || [];

    const demoByOppId = {};
    demos.forEach(d => {
      if (d.opportunity_id) demoByOppId[d.opportunity_id] = d;
    });

    const draftByOppId = {};
    drafts.forEach(d => {
      if (d.opportunity_id) draftByOppId[d.opportunity_id] = d;
    });

    if (pipelineViewMode === 'kanban') {
      renderKanbanBoard(opps, drafts, demoByOppId, draftByOppId);
    } else {
      renderPipelineList(drafts);
    }
  } catch (err) {
    if (kanbanContainer) kanbanContainer.innerHTML = '<div style="color:#ef4444; font-size:12px;">Error connecting to pipeline API.</div>';
  }
}

const KANBAN_STAGES = [
  { key: 'new', label: '📥 Discovered', next: 'prototype_ready', desc: 'Fresh market signals' },
  { key: 'prototype_ready', label: '🛠 Prototype Ready', next: 'applied', desc: 'Bespoke Vercel app built' },
  { key: 'applied', label: '📤 Pitched / Sent', next: 'follow_up', desc: 'Outreach dispatched' },
  { key: 'follow_up', label: '⏳ Follow-Up Active', next: 'interview', desc: 'Touch 2 / 3 cadence' },
  { key: 'interview', label: '🎯 Interviewing', next: 'won', desc: 'Direct dialogue with founder' },
  { key: 'won', label: '🏆 Won / Retainer', next: null, desc: 'Contract closed' }
];

function renderKanbanBoard(opps, drafts, demoByOppId, draftByOppId) {
  const kanbanContainer = document.getElementById('pipelineKanbanContainer');
  if (!kanbanContainer) return;

  // Group items by stage
  const stageGroups = {
    new: [],
    prototype_ready: [],
    applied: [],
    follow_up: [],
    interview: [],
    won: []
  };

  opps.forEach(opp => {
    let st = opp.status || 'new';
    if (st === 'outreach_drafted') st = 'applied';
    if (st === 'new' && demoByOppId[opp.id]) {
      st = 'prototype_ready';
    }
    if (!stageGroups[st]) {
      st = 'new';
    }
    stageGroups[st].push(opp);
  });

  kanbanContainer.innerHTML = `
    <div class="kanban-board">
      ${KANBAN_STAGES.map(stage => {
        const cards = stageGroups[stage.key] || [];
        return `
          <div class="kanban-col" data-stage="${stage.key}">
            <div class="kanban-col-header">
              <span>${stage.label}</span>
              <span class="kanban-col-count">${cards.length}</span>
            </div>
            <div class="kanban-card-list">
              ${cards.length === 0 ? `
                <div style="font-size:11px; color:var(--muted); text-align:center; padding:20px 8px; border:1px dashed var(--line); border-radius:6px;">
                  No opportunities in ${stage.label}
                </div>
              ` : cards.map(opp => {
                const demo = demoByOppId[opp.id];
                const draft = draftByOppId[opp.id];
                const demoUrl = demo ? (demo.demo_url.startsWith('http') ? demo.demo_url : `https://bieai.vercel.app/${demo.slug}`) : null;
                const nextStageObj = KANBAN_STAGES.find(s => s.key === stage.next);

                return `
                  <div class="kanban-card" data-opp-id="${opp.id}">
                    <div class="kanban-card-meta">
                      <span class="kanban-card-company">${escapeHtml(opp.company)}</span>
                      <span class="ats-badge-pill">${opp.fit_score}% Fit</span>
                    </div>
                    <h4 class="kanban-card-title">${escapeHtml(opp.title)}</h4>
                    
                    <div class="kanban-card-badges">
                      <span style="font-size:9px; font-family:'DM Mono',monospace; background:#f1f5f3; padding:1px 5px; border-radius:4px; color:var(--muted);">${escapeHtml(opp.category || 'tech')}</span>
                      ${demo ? `
                        <span style="font-size:9px; font-family:'DM Mono',monospace; background:#edf7f2; color:#166534; padding:1px 6px; border-radius:4px; font-weight:700;">● Prototype Built</span>
                      ` : `
                        <span style="font-size:9px; font-family:'DM Mono',monospace; background:#f8fafc; color:#94a3b8; padding:1px 6px; border-radius:4px;">No Prototype</span>
                      `}
                    </div>

                    ${demo ? `
                      <div style="margin-bottom:8px; display:flex; gap:4px; align-items:center;">
                        <button class="stage-advance-btn" style="background:#f0f9ff; color:#0369a1; border-color:#bae6fd;" onclick="openSandboxModal('${escapeHtml(demo.title)}', '${demoUrl}')">
                          👁 Preview Live Demo
                        </button>
                      </div>
                    ` : ''}

                    <div class="kanban-card-actions">
                      <div style="display:flex; gap:4px;">
                        <button class="stage-advance-btn" onclick="draftOutreach(${opp.id})" title="Draft tailored proposal with Anti-Job pitch angles">
                          ⚡ Pitch
                        </button>
                        ${!demo ? `
                          <button class="stage-advance-btn" style="background:#0f172a; color:#38bdf8; border-color:#0284c7;" onclick="triggerAutopilot(${opp.id})" title="Auto-build prototype and draft proposal">
                            🚀 Auto-Pilot
                          </button>
                        ` : ''}
                      </div>

                      ${nextStageObj ? `
                        <button class="stage-advance-btn" onclick="advanceOpportunityStage(${opp.id}, '${nextStageObj.key}')" title="Advance to ${nextStageObj.label}">
                          Move &rarr;
                        </button>
                      ` : `
                        <span style="font-size:9px; color:#166534; font-weight:700;">Closed ✓</span>
                      `}
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
}

async function advanceOpportunityStage(oppId, newStatus) {
  showToast(`Advancing opportunity to ${newStatus.replace('_', ' ')}...`);
  try {
    const res = await fetch('/api/opportunity/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: oppId, status: newStatus })
    });
    const data = await res.json();
    if (data.ok) {
      showToast(`Opportunity stage updated to: ${newStatus.replace('_', ' ')}.`);
      loadPipeline();
      loadStats();
    } else {
      showToast('Failed to update opportunity stage.');
    }
  } catch (err) {
    showToast('Error contacting opportunity status API.');
  }
}

function renderPipelineList(items) {
  const container = document.getElementById('pipelineContainer');
  if (!container) return;

  if (!items.length) {
    container.innerHTML = '<div style="padding:24px 0; text-align:center; color:var(--muted); font-size:12px;">No outreach drafts created yet. Select an opportunity from the radar to draft a proposal.</div>';
    return;
  }

  container.innerHTML = items.map(d => {
    const rec = d.recipient_email || 'Not detected';
    return `
      <div style="background:#fff; border:1px solid var(--line); border-radius:10px; padding:16px; margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
          <div>
            <span class="eyebrow">${escapeHtml(d.opp_company || 'Client')} &bull; ${escapeHtml(d.opp_title || 'Opportunity')}</span>
            <h3 style="font-size:15px; margin:2px 0 4px;">${escapeHtml(d.subject)}</h3>
            <div style="font-size:10px; font-family:'DM Mono',monospace; color:var(--muted);">
              Recipient: <strong style="color:var(--ink);">${escapeHtml(rec)}</strong> &bull; Attached: <span style="color:#278b68;">${escapeHtml(d.demo_name || 'Demo')}</span>
            </div>
          </div>
          <span style="font-size:10px; font-family:'DM Mono',monospace; padding:3px 8px; border-radius:10px; background:${d.status === 'sent' ? '#edf7f2; color:#166534;' : '#fef3c7; color:#b45309;'}">
            ${escapeHtml(d.status || 'draft')}
          </span>
        </div>
        <div style="display:flex; gap:6px; margin-top:10px;">
          <button class="row-action outline" onclick='openDraftModal(${JSON.stringify(d).replace(/'/g, "&#39;")})'>Review &amp; Edit</button>
          <button class="row-action" style="background:#ea4335; color:#fff;" onclick="quickSendGmail('${escapeHtml(rec)}', '${escapeHtml(d.subject)}', '${encodeURIComponent(d.body)}')">Send Gmail ↗</button>
          <button class="row-action" style="background:#0078d4; color:#fff;" onclick="quickSendOutlook('${escapeHtml(rec)}', '${escapeHtml(d.subject)}', '${encodeURIComponent(d.body)}')">Outlook ↗</button>
        </div>
      </div>
    `;
  }).join('');
}

// 7b. Anti-Job Playbook Modal Handlers
async function openAntiJobPlaybookModal() {
  const modal = document.getElementById('antijobPlaybookModalBackdrop');
  if (!modal) return;
  modal.classList.add('open');
  const container = document.getElementById('antijobChaptersContainer');
  if (!container) return;
  container.innerHTML = '<div style="color:var(--muted); font-size:12px; padding:20px 0; text-align:center;">Loading Anti-Job strategy playbook...</div>';

  try {
    const res = await fetch('/api/antijob/playbook');
    const data = await res.json();
    const pb = data.playbook || {};
    const chapters = pb.chapters || [];
    container.innerHTML = `
      <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:8px; padding:14px; margin-bottom:18px;">
        <strong style="color:#0369a1; font-size:11px; text-transform:uppercase; display:block; margin-bottom:6px;">The Anti-Job Core Operating Principles:</strong>
        <ul style="margin:0 0 0 18px; font-size:11px; color:#334155; line-height:1.7;">
          ${(pb.principles || []).map(p => `<li>${escapeHtml(p)}</li>`).join('')}
        </ul>
      </div>
      ${chapters.map(ch => `
        <div class="playbook-chapter">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <h4 style="margin:0; font-size:14px;">${escapeHtml(ch.number)}. ${escapeHtml(ch.title)}</h4>
            <span style="font-size:10px; font-family:'DM Mono',monospace; color:var(--muted);">${escapeHtml(ch.summary)}</span>
          </div>
          <p style="white-space:pre-line; margin-top:6px; font-size:11px; line-height:1.6; color:#475569;">${escapeHtml(ch.content)}</p>
        </div>
      `).join('')}
      <div class="persona-card" style="margin-top:16px;">
        <strong>⚡ Decision-Maker Outreach Checklist:</strong><br>
        &bull; <strong>1. Research:</strong> Use Google LinkedIn dork to find CTO / VP Engineering name.<br>
        &bull; <strong>2. Deploy Prototype:</strong> Run Auto-Pilot to synthesize dedicated Vercel URL.<br>
        &bull; <strong>3. Pitch:</strong> Lead with live URL, not resume credentials. Select Proof-of-Work or Problem Audit.<br>
        &bull; <strong>4. Cadence:</strong> If no response in 72 hours, send Touch 2 verification nudge.<br>
        &bull; <strong>5. Close:</strong> Propose a 14-day fixed-scope production sprint or monthly retainer.
      </div>
    `;
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; font-size:12px;">Error loading Anti-Job playbook.</div>';
  }
}

function closeAntiJobPlaybookModal() {
  const modal = document.getElementById('antijobPlaybookModalBackdrop');
  if (modal) modal.classList.remove('open');
}

// 7c. Interactive Device Sandbox Modal (CreatorKit HQ Benchmark)
function openSandboxModal(titleOrUrl, urlOrTitle) {
  const modal = document.getElementById('sandboxModalBackdrop');
  if (!modal) return;

  let title = 'Interactive Prototype Sandbox';
  let url = '';

  const isFirstArgUrl = typeof titleOrUrl === 'string' && (titleOrUrl.startsWith('http') || titleOrUrl.startsWith('/') || titleOrUrl.includes('.html'));
  if (isFirstArgUrl) {
    url = titleOrUrl;
    title = urlOrTitle || 'Interactive Prototype Sandbox';
  } else {
    title = titleOrUrl || 'Interactive Prototype Sandbox';
    url = urlOrTitle || '';
  }

  const titleEl = document.getElementById('sandboxTitle');
  if (titleEl) titleEl.textContent = title;
  const iframe = document.getElementById('sandboxIframe');
  if (iframe) iframe.src = url;
  const ext = document.getElementById('sandboxExtLink');
  if (ext) ext.href = url;
  setSandboxDevice('desktop');
  modal.classList.add('open');
}

window.openSandboxModal = openSandboxModal;

function closeSandboxModal() {
  const modal = document.getElementById('sandboxModalBackdrop');
  if (modal) modal.classList.remove('open');
  const iframe = document.getElementById('sandboxIframe');
  if (iframe) iframe.src = 'about:blank';
}

function setSandboxDevice(dev) {
  const iframe = document.getElementById('sandboxIframe');
  if (!iframe) return;
  ['desktop', 'tablet', 'mobile'].forEach(d => {
    const btn = document.getElementById(`sbBtn${d.charAt(0).toUpperCase() + d.slice(1)}`);
    if (btn) btn.classList.toggle('active', d === dev);
  });
  if (dev === 'mobile') {
    iframe.style.width = '375px';
    iframe.style.maxWidth = '100%';
  } else if (dev === 'tablet') {
    iframe.style.width = '768px';
    iframe.style.maxWidth = '100%';
  } else {
    iframe.style.width = '100%';
  }
}

function quickSendGmail(to, subject, bodyEnc) {
  const body = decodeURIComponent(bodyEnc);
  window.open(`https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(to)}&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`, '_blank');
}

function quickSendOutlook(to, subject, bodyEnc) {
  const body = decodeURIComponent(bodyEnc);
  window.open(`https://outlook.live.com/mail/0/deeplink/compose?to=${encodeURIComponent(to)}&subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`, '_blank');
}

// 8. Demo Library View
async function loadDemos() {
  const container = document.getElementById('demosContainer');
  if (!container) return;
  container.innerHTML = '<div style="color:var(--muted); font-size:12px;">Loading demos...</div>';

  try {
    const res = await fetch('/api/demos');
    const data = await res.json();
    const demos = data.demos || [];

    container.innerHTML = demos.map(d => `
      <div style="background:#fff; border:1px solid var(--line); border-radius:10px; padding:18px;">
        <span class="eyebrow" style="color:#278b68;">${escapeHtml(d.category)}</span>
        <h3 style="font-size:16px; margin:4px 0 6px;">${escapeHtml(d.name)}</h3>
        <p style="font-size:11px; color:var(--muted); line-height:1.6; margin:0 0 12px;">${escapeHtml(d.desc)}</p>
        <a href="${d.url}" target="_blank" rel="noopener" class="row-action" style="text-decoration:none; display:inline-flex; align-items:center; gap:4px; font-weight:700;">
          <span>Open Live Application</span> &rarr;
        </a>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; font-size:12px;">Error loading demos.</div>';
  }
}

// 9. Sources View
async function loadSources() {
  const container = document.getElementById('sourcesContainer');
  if (!container) return;
  container.innerHTML = '<div style="color:var(--muted); font-size:12px;">Loading sources...</div>';

  try {
    const res = await fetch('/api/sources');
    const data = await res.json();
    const sources = data.sources || [];

    container.innerHTML = sources.map(s => `
      <div style="background:#fff; border:1px solid var(--line); border-radius:10px; padding:18px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h3 style="font-size:15px; margin:0 0 4px;">${escapeHtml(s.name)}</h3>
          <div style="font-size:11px; color:var(--muted);">${escapeHtml(s.type)} &bull; ${escapeHtml(s.url)}</div>
        </div>
        <div style="text-align:right;">
          <strong style="font-size:18px; color:#278b68;">${s.count}</strong>
          <div style="font-size:10px; color:var(--muted);">Stored Signals</div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; font-size:12px;">Error loading sources.</div>';
  }
}

// 10. Stats & Live Scan Trigger
async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();

    const sq = document.getElementById('statQualified');
    if (sq) sq.textContent = data.qualified || 0;
    const sv = document.getElementById('statValue');
    if (sv) sv.textContent = data.estimated_value || '$0k';
    const sd = document.getElementById('statDrafts');
    if (sd) sd.textContent = data.pipeline_count || 0;
    const ss = document.getElementById('statSent');
    if (ss) ss.textContent = `${data.sent_count || 0} sent`;
    const st = document.getElementById('statTotal');
    if (st) st.textContent = data.total_signals || 0;

    const vd = document.getElementById('statVaultDemos');
    if (vd) vd.textContent = data.demos_count || 0;

    const no = document.getElementById('navOppCount');
    if (no) no.textContent = data.total_signals || 0;
    const nd = document.getElementById('navDraftCount');
    if (nd) nd.textContent = data.pipeline_count || 0;
    const nv = document.getElementById('navVaultCount');
    if (nv) nv.textContent = data.demos_count || 0;

    const navSurvey = document.getElementById('navSurveyCount');
    if (navSurvey) navSurvey.textContent = data.survey_total || 22;
    const statLocal = document.getElementById('statSurveyLocal');
    if (statLocal) statLocal.textContent = data.survey_local || 11;
    const statVpn = document.getElementById('statSurveyVPN');
    if (statVpn) statVpn.textContent = data.survey_vpn || 11;

    const badge = document.getElementById('scanStatusBadge');
    if (badge) {
      badge.style.display = data.is_scanning ? 'inline' : 'none';
    }
  } catch (err) {
    // offline or booting
  }
}

async function triggerScan() {
  const btn = document.getElementById('scanButton');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span>⏳</span> Scanning public APIs...';
  }
  const badge = document.getElementById('scanStatusBadge');
  if (badge) badge.style.display = 'inline';
  showToast('Live scan initiated across RemoteOK, Jobicy, and Arbeitnow...');

  try {
    const res = await fetch('/api/scan', { method: 'POST' });
    const data = await res.json();
    showToast(data.message || 'Scan underway.');

    let attempts = 0;
    const pollInterval = setInterval(async () => {
      attempts++;
      const sRes = await fetch('/api/stats');
      const stats = await sRes.json();
      if (!stats.is_scanning || attempts > 15) {
        clearInterval(pollInterval);
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span>＋</span> Run fresh scan';
        }
        if (badge) badge.style.display = 'none';
        showToast('Fresh scan completed! New opportunities qualified.');
        loadStats();
        loadOpportunities();
      }
    }, 2000);
  } catch (err) {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<span>＋</span> Run fresh scan';
    }
    showToast('Scan request error');
  }
}

function escapeHtml(str) {
  return String(str || '').replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[c]);
}

// 11. Settings & SMTP Configuration
let appSettings = {
  portfolio_url: 'https://bieai.vercel.app',
  github_url: 'https://github.com/Stghost1/BIEAI',
  email: 'techwithbie@gmail.com',
  whatsapp: '+234 905 404 5597',
  upwork_url: 'https://www.upwork.com/freelancers/~015875b6ee71b82e73',
  smtp_host: 'smtp.gmail.com',
  smtp_port: '587',
  smtp_user: 'techwithbie@gmail.com',
  smtp_pass: '',
  smtp_from_name: 'Emmanuel Bamidele (Bamsemma)',
  auto_send_enabled: 'false'
};

async function loadSettings() {
  try {
    const res = await fetch('/api/settings');
    const data = await res.json();
    if (data.settings) {
      appSettings = { ...appSettings, ...data.settings };
    }
  } catch (err) {
    // fallback
  }
}

function openSettingsModal() {
  const modal = document.getElementById('settingsModalBackdrop');
  if (!modal) return;
  document.getElementById('settingPortfolioUrl').value = appSettings.portfolio_url || 'https://bieai.vercel.app';
  document.getElementById('settingGithubUrl').value = appSettings.github_url || 'https://github.com/Stghost1/BIEAI';
  document.getElementById('settingEmail').value = appSettings.email || 'techwithbie@gmail.com';
  document.getElementById('settingWhatsapp').value = appSettings.whatsapp || '+234 905 404 5597';
  document.getElementById('settingUpwork').value = appSettings.upwork_url || 'https://www.upwork.com/freelancers/~015875b6ee71b82e73';

  document.getElementById('settingSmtpHost').value = appSettings.smtp_host || 'smtp.gmail.com';
  document.getElementById('settingSmtpPort').value = appSettings.smtp_port || '587';
  document.getElementById('settingSmtpUser').value = appSettings.smtp_user || 'techwithbie@gmail.com';
  document.getElementById('settingSmtpPass').value = appSettings.smtp_pass || '';
  document.getElementById('settingSmtpFromName').value = appSettings.smtp_from_name || 'Emmanuel Bamidele (Bamsemma)';
  document.getElementById('settingAutoSend').checked = appSettings.auto_send_enabled === 'true';

  const fb = document.getElementById('smtpTestFeedback');
  if (fb) fb.style.display = 'none';

  modal.classList.add('open');
}

function closeSettingsModal() {
  const modal = document.getElementById('settingsModalBackdrop');
  if (modal) modal.classList.remove('open');
}

async function testSmtpConnection() {
  const host = (document.getElementById('settingSmtpHost').value || '').trim();
  const port = parseInt(document.getElementById('settingSmtpPort').value) || 587;
  const user = (document.getElementById('settingSmtpUser').value || '').trim();
  const password = (document.getElementById('settingSmtpPass').value || '').trim();

  const fb = document.getElementById('smtpTestFeedback');
  if (!fb) return;
  fb.style.display = 'block';
  fb.style.background = '#f0f9ff';
  fb.style.color = '#0369a1';
  fb.textContent = 'Connecting and verifying credentials with SMTP server...';

  try {
    const res = await fetch('/api/mailer/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ host, port, user, password })
    });
    const data = await res.json();
    if (data.ok) {
      fb.style.background = '#edf7f2';
      fb.style.color = '#166534';
      fb.textContent = `✓ ${data.message}`;
    } else {
      fb.style.background = '#fef2f2';
      fb.style.color = '#991b1b';
      fb.textContent = `✗ ${data.error}`;
    }
  } catch (err) {
    fb.style.background = '#fef2f2';
    fb.style.color = '#991b1b';
    fb.textContent = '✗ Network error testing SMTP server.';
  }
}

async function saveSettings() {
  const payload = {
    portfolio_url: (document.getElementById('settingPortfolioUrl').value || '').trim(),
    github_url: (document.getElementById('settingGithubUrl').value || '').trim(),
    email: (document.getElementById('settingEmail').value || '').trim(),
    whatsapp: (document.getElementById('settingWhatsapp').value || '').trim(),
    upwork_url: (document.getElementById('settingUpwork').value || '').trim(),
    smtp_host: (document.getElementById('settingSmtpHost').value || '').trim(),
    smtp_port: (document.getElementById('settingSmtpPort').value || '').trim(),
    smtp_user: (document.getElementById('settingSmtpUser').value || '').trim(),
    smtp_pass: (document.getElementById('settingSmtpPass').value || '').trim(),
    smtp_from_name: (document.getElementById('settingSmtpFromName').value || '').trim(),
    auto_send_enabled: document.getElementById('settingAutoSend').checked ? 'true' : 'false'
  };

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.ok && data.settings) {
      appSettings = { ...appSettings, ...data.settings };
      showToast('Configuration and SMTP settings saved.');
      closeSettingsModal();
      loadDemos();
      loadVault();
    } else {
      showToast('Failed to save settings.');
    }
  } catch (err) {
    showToast('Error contacting settings API.');
  }
}

// Initial Boot
loadSettings();
loadStats();
loadOpportunities();
