const state = {
  contacts: [],
  selectedRecipients: new Set(),
  logs: [],
  automation: { auto_replies: [], blacklisted_emails: [] }
};

const URL_PARAMS = new URLSearchParams(window.location.search);
const DEMO_MODE = URL_PARAMS.get('demo') === '1';
const DEMO_STORAGE_KEY = 'email-automation-system-demo-state';
const DEFAULT_DEMO_STATE = {
  contacts: [
    { name: 'Ava Johnson', email: 'ava@example.com' },
    { name: 'Noah Patel', email: 'noah@example.com' },
    { name: 'Mia Chen', email: 'mia@example.com' }
  ],
  logs: [
    {
      timestamp: '2026-07-01 09:15:00',
      recipient: 'ava@example.com',
      status: 'SUCCESS',
      subject: 'Welcome update',
      message: 'Sent from the demo dashboard'
    },
    {
      timestamp: '2026-07-01 09:40:00',
      recipient: 'noah@example.com',
      status: 'FAILED',
      subject: 'Project update',
      message: 'SMTP connection not available in demo mode'
    }
  ],
  auto_replies: [
    { subject: 'Support', reply_message: 'Thanks for contacting support. We will get back to you shortly.' },
    { subject: 'Hello', reply_message: 'Thanks for reaching out. Nice to hear from you.' }
  ],
  blacklisted_emails: ['spam@example.com']
};

function cloneDemoState(source = DEFAULT_DEMO_STATE) {
  return JSON.parse(JSON.stringify(source));
}

function loadDemoState() {
  try {
    const stored = localStorage.getItem(DEMO_STORAGE_KEY);
    if (stored) {
      return { ...cloneDemoState(), ...JSON.parse(stored) };
    }
  } catch (error) {
    // Ignore storage issues and fall back to bundled sample data.
  }

  return cloneDemoState();
}

let demoState = DEMO_MODE ? loadDemoState() : null;

function persistDemoState() {
  if (!DEMO_MODE) {
    return;
  }

  try {
    localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(demoState));
  } catch (error) {
    // Ignore browser storage write failures.
  }
}

function demoCounts() {
  return {
    contacts: demoState.contacts.length,
    logs: demoState.logs.length,
    success: demoState.logs.filter((entry) => entry.status === 'SUCCESS').length,
    failed: demoState.logs.filter((entry) => entry.status === 'FAILED').length,
    autoReplies: demoState.auto_replies.length,
    blacklist: demoState.blacklisted_emails.length
  };
}

function demoConfig() {
  return {
    mode: 'demo',
    emailConfigured: true,
    passwordConfigured: true,
    smtpServer: 'Demo browser mode',
    port: 'local',
    files: {
      contacts: true,
      logs: true,
      autoReplies: true,
      blacklist: true
    }
  };
}

function demoLogs() {
  return {
    total: demoState.logs.length,
    success: demoState.logs.filter((entry) => entry.status === 'SUCCESS').length,
    failed: demoState.logs.filter((entry) => entry.status === 'FAILED').length,
    entries: demoState.logs.slice(-30).reverse()
  };
}

function readDemoBody(options = {}) {
  return options.body ? JSON.parse(options.body) : {};
}

function pushDemoLog(entry) {
  demoState.logs.push(entry);
  demoState.logs = demoState.logs.slice(-100);
  persistDemoState();
}

const templates = {
  followup: {
    subject: 'Follow-up on our conversation',
    message: 'Hi there,\n\nI wanted to follow up on our previous conversation and check whether anything else is needed from my side.\n\nBest regards,'
  },
  update: {
    subject: 'Project update',
    message: 'Hi team,\n\nHere is the latest project update. The current milestone is moving forward, and I will share the next checkpoint soon.\n\nThanks,'
  },
  support: {
    subject: 'Support reply',
    message: 'Hello,\n\nThanks for reaching out. I reviewed your request and I am looking into it now. I will get back to you with the next steps shortly.\n\nBest,'
  },
  intro: {
    subject: 'Introduction',
    message: 'Hello,\n\nI hope you are doing well. I wanted to introduce myself and share a quick note about how we can work together.\n\nRegards,'
  }
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const elements = {
  sendForm: $('#sendForm'),
  bulkForm: $('#bulkForm'),
  contactForm: $('#contactForm'),
  replyForm: $('#replyForm'),
  blacklistForm: $('#blacklistForm'),
  toast: $('#toast'),
  configBadge: $('#configBadge'),
  statusList: $('#statusList'),
  recentActivity: $('#recentActivity'),
  bulkRecipients: $('#bulkRecipients'),
  contactsList: $('#contactsList'),
  replyList: $('#replyList'),
  blacklistList: $('#blacklistList'),
  logsList: $('#logsList'),
  composeMeta: $('#composeMeta'),
  settingsForm: $('#settingsForm'),
  settingsEmail: $('#settingsEmail'),
  settingsPassword: $('#settingsPassword'),
  settingsSmtp: $('#settingsSmtp'),
  settingsPort: $('#settingsPort'),
  settingsMeta: $('#settingsMeta'),
  setupAlert: $('#setupAlert'),
  jumpToSettingsBtn: $('#jumpToSettingsBtn')
};

function escapeHtml(value = '') {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function showToast(message, type = 'info') {
  elements.toast.textContent = message;
  elements.toast.className = `toast is-visible ${type}`;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    elements.toast.className = 'toast';
  }, 4200);
}

function getApiBaseUrl() {
  if (window.location.protocol === 'file:') {
    return 'http://localhost:8001';
  }
  return '';
}

async function api(path, options = {}) {
  if (DEMO_MODE) {
    const body = readDemoBody(options);

    if (path === '/api/status') {
      return { config: demoConfig(), counts: demoCounts() };
    }

    if (path === '/api/settings' && (!options.method || options.method === 'GET')) {
      return {
        email: 'demo@example.com',
        smtpServer: 'Demo browser mode',
        port: 'local',
        configured: true
      };
    }

    if (path === '/api/contacts' && (!options.method || options.method === 'GET')) {
      return { contacts: demoState.contacts };
    }

    if (path === '/api/logs' && (!options.method || options.method === 'GET')) {
      return demoLogs();
    }

    if (path === '/api/automation' && (!options.method || options.method === 'GET')) {
      return {
        auto_replies: demoState.auto_replies,
        blacklisted_emails: demoState.blacklisted_emails
      };
    }

    if (path === '/api/send_email' && options.method === 'POST') {
      const receiver = (body.receiver || '').trim();
      const subject = (body.subject || '').trim();
      const message = (body.message || '').trim();

      if (!receiver || !subject || !message) {
        throw new Error('receiver, subject, and message are required');
      }

      const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
      pushDemoLog({
        timestamp,
        recipient: receiver,
        status: 'SUCCESS',
        subject,
        message: 'Sent in demo mode'
      });

      return {
        status: 'success',
        recipient: receiver,
        timestamp
      };
    }

    if (path === '/api/bulk_send' && options.method === 'POST') {
      const subject = (body.subject || '').trim();
      const message = (body.message || '').trim();
      const requestedRecipients = Array.isArray(body.recipients) ? body.recipients.map((email) => email.toLowerCase()) : [];

      if (!subject || !message) {
        throw new Error('Subject and message are required');
      }

      const contacts = requestedRecipients.length
        ? demoState.contacts.filter((contact) => requestedRecipients.includes(contact.email.toLowerCase()))
        : demoState.contacts;

      const results = contacts.map((contact) => {
        const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
        pushDemoLog({
          timestamp,
          recipient: contact.email,
          status: 'SUCCESS',
          subject,
          message: 'Sent in demo mode'
        });

        return {
          name: contact.name,
          email: contact.email,
          success: true,
          message: 'Sent in demo mode',
          timestamp
        };
      });

      return {
        status: 'complete',
        sent: results.length,
        failed: 0,
        total: results.length,
        results
      };
    }

    if (path === '/api/contacts' && options.method === 'POST') {
      const name = (body.name || '').trim();
      const email = (body.email || '').trim();

      if (!email) {
        throw new Error('Enter a valid email address');
      }

      if (demoState.contacts.some((contact) => contact.email.toLowerCase() === email.toLowerCase())) {
        throw new Error('This contact already exists');
      }

      const contact = { name: name || email.split('@')[0], email };
      demoState.contacts.push(contact);
      persistDemoState();
      return { contact, contacts: demoState.contacts };
    }

    if (path === '/api/automation' && options.method === 'POST') {
      if (body.action === 'add_reply') {
        const subject = (body.subject || '').trim();
        const replyMessage = (body.reply_message || '').trim();

        if (!subject || !replyMessage) {
          throw new Error('Subject and reply message are required');
        }

        demoState.auto_replies.push({ subject, reply_message: replyMessage });
        persistDemoState();
      } else if (body.action === 'add_blacklist') {
        const email = (body.email || '').trim();

        if (!email) {
          throw new Error('Enter a valid email address');
        }

        if (!demoState.blacklisted_emails.some((item) => item.toLowerCase() === email.toLowerCase())) {
          demoState.blacklisted_emails.push(email);
          persistDemoState();
        }
      } else {
        throw new Error('Unknown automation action');
      }

      return {
        auto_replies: demoState.auto_replies,
        blacklisted_emails: demoState.blacklisted_emails
      };
    }

    if (path === '/api/logs' && options.method === 'DELETE') {
      demoState.logs = [];
      persistDemoState();
      return { total: 0, success: 0, failed: 0, entries: [] };
    }

    if (path === '/api/settings' && options.method === 'POST') {
      const smtpServer = (body.smtpServer || '').trim();
      return {
        status: 'saved',
        configured: true,
        email: (body.email || '').trim(),
        smtpServer: smtpServer && !smtpServer.includes('@') ? smtpServer : 'smtp.gmail.com',
        port: (body.port || '587').toString().trim() || '587'
      };
    }

    throw new Error(`Unsupported demo request: ${path}`);
  }

  const baseUrl = getApiBaseUrl();
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });

  const contentType = response.headers.get('content-type') || '';
  const data = response.status === 204
    ? {}
    : contentType.includes('application/json')
      ? await response.json()
      : { error: await response.text() };
  if (!response.ok) {
    throw new Error(data.error || data.message || 'Request failed');
  }
  return data;
}

function setButtonLoading(button, isLoading, label) {
  if (!button) return;
  if (!button.dataset.originalLabel) {
    button.dataset.originalLabel = button.textContent;
  }
  button.disabled = isLoading;
  button.textContent = isLoading ? label : button.dataset.originalLabel;
}

function activateTab(tabId) {
  const tabButton = $(`.tab-button[data-tab="${tabId}"]`);
  const panel = $(`#${tabId}`);

  if (!tabButton || !panel) {
    return;
  }

  $$('.tab-button').forEach((item) => item.classList.remove('is-active'));
  $$('.tab-panel').forEach((item) => item.classList.remove('is-active'));

  tabButton.classList.add('is-active');
  panel.classList.add('is-active');
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateBulkSelectionLabel() {
  const selectedCount = state.selectedRecipients.size;
  $('#selectedCount').textContent = `${selectedCount} selected`;
  $('#selectAllBtn').textContent = selectedCount === state.contacts.length && state.contacts.length ? 'Deselect All' : 'Select All';
}

function renderMetrics(counts = {}) {
  $('#contactCount').textContent = counts.contacts || state.contacts.length || 0;
  $('#successCount').textContent = counts.success || 0;
  $('#failedCount').textContent = counts.failed || 0;
  $('#ruleCount').textContent = counts.autoReplies || state.automation.auto_replies.length || 0;
}

function renderStatus(config = {}) {
  const demoMode = config.mode === 'demo';
  const configured = config.emailConfigured && config.passwordConfigured;
  elements.configBadge.textContent = demoMode ? 'Demo mode' : configured ? 'SMTP ready' : 'Setup needed';
  elements.configBadge.className = `status-badge ${demoMode ? 'is-warning' : configured ? 'is-ready' : 'is-warning'}`;
  elements.setupAlert.classList.toggle('is-hidden', configured || demoMode);

  const files = config.files || {};
  const smtpValue = demoMode ? 'Browser demo / local storage' : `${config.smtpServer || 'smtp.gmail.com'}:${config.port || '587'}`;
  const rows = [
    ['Mode', demoMode ? 'Browser storage' : 'SMTP backend'],
    ['Email account', config.emailConfigured ? 'Connected' : 'Missing EMAIL'],
    ['Password', config.passwordConfigured ? 'Available' : 'Missing PASSWORD'],
    ['SMTP server', smtpValue],
    ['Contacts CSV', files.contacts ? 'Found' : 'Not found'],
    ['Logs file', files.logs ? 'Found' : 'Not found'],
    ['Rules file', files.autoReplies ? 'Found' : 'Not found']
  ];

  elements.statusList.innerHTML = rows.map(([label, value]) => `
    <div class="status-row">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `).join('');
}

function populateSettings(settings = {}) {
  elements.settingsEmail.value = settings.email || '';
  elements.settingsPassword.value = '';
  elements.settingsSmtp.value = settings.smtpServer || 'smtp.gmail.com';
  elements.settingsPort.value = settings.port || '587';
  elements.settingsMeta.textContent = settings.configured
    ? 'Settings loaded. Leave password empty to keep the current one.'
    : 'Enter your email and password to enable sending.';
}

function applyEmailProviderDefaults() {
  const email = elements.settingsEmail.value.trim().toLowerCase();
  if (email.endsWith('@gmail.com') || email.endsWith('@googlemail.com')) {
    elements.settingsSmtp.value = 'smtp.gmail.com';
    elements.settingsPort.value = '587';
    elements.settingsMeta.textContent = 'Gmail detected. Using smtp.gmail.com:587 and a Google App Password.';
  }
}

async function getCurrentSettings() {
  try {
    return await api('/api/settings');
  } catch (error) {
    return { configured: false };
  }
}

function sanitizeSettingsInput() {
  applyEmailProviderDefaults();

  const smtpServer = elements.settingsSmtp.value.trim();
  if (!smtpServer || smtpServer.includes('@') || smtpServer.toLowerCase().startsWith('mailto:')) {
    elements.settingsSmtp.value = 'smtp.gmail.com';
  }

  if (!elements.settingsPort.value.trim()) {
    elements.settingsPort.value = '587';
  }
}

function renderContacts() {
  if (!state.contacts.length) {
    elements.contactsList.textContent = 'No contacts found in contacts.csv.';
    elements.contactsList.className = 'data-list empty-state';
    elements.bulkRecipients.textContent = 'Add contacts before sending bulk email.';
    elements.bulkRecipients.className = 'recipient-list empty-state';
    updateBulkSelectionLabel();
    return;
  }

  elements.contactsList.className = 'data-list';
  elements.contactsList.innerHTML = state.contacts.map((contact) => `
    <article class="data-row">
      <div>
        <strong>${escapeHtml(contact.name)}</strong>
        <span>${escapeHtml(contact.email)}</span>
      </div>
    </article>
  `).join('');

  elements.bulkRecipients.className = 'recipient-list';
  elements.bulkRecipients.innerHTML = state.contacts.map((contact) => {
    const checked = state.selectedRecipients.has(contact.email) ? 'checked' : '';
    return `
      <label class="recipient-row">
        <input type="checkbox" value="${escapeHtml(contact.email)}" ${checked} />
        <span>
          <strong>${escapeHtml(contact.name)}</strong>
          <small>${escapeHtml(contact.email)}</small>
        </span>
      </label>
    `;
  }).join('');

  updateBulkSelectionLabel();
}

function renderAutomation() {
  const replies = state.automation.auto_replies || [];
  const blocked = state.automation.blacklisted_emails || [];

  elements.replyList.className = replies.length ? 'data-list' : 'data-list empty-state';
  elements.replyList.innerHTML = replies.length
    ? replies.map((rule) => `
      <article class="data-row">
        <div>
          <strong>${escapeHtml(rule.subject)}</strong>
          <span>${escapeHtml(rule.reply_message)}</span>
        </div>
      </article>
    `).join('')
    : 'No auto-reply rules saved.';

  elements.blacklistList.className = blocked.length ? 'data-list' : 'data-list empty-state';
  elements.blacklistList.innerHTML = blocked.length
    ? blocked.map((email) => `<div class="data-row"><strong>${escapeHtml(email)}</strong></div>`).join('')
    : 'No blacklisted senders.';
}

function groupLogEntries(entries = []) {
  const grouped = new Map();
  const orderedEntries = Array.isArray(entries) ? entries : [];

  orderedEntries.forEach((entry) => {
    const statusValue = String(entry.status || '').toUpperCase();
    const directionValue = statusValue === 'RECEIVED' ? 'Received' : 'Sent';
    const recipientLabel = entry.recipient || 'Unknown';
    const key = `${directionValue.toLowerCase()}:${recipientLabel.toLowerCase()}`;

    if (!grouped.has(key)) {
      grouped.set(key, {
        recipient: recipientLabel,
        subject: entry.subject || 'No subject',
        timestamp: entry.timestamp || '',
        status: statusValue,
        direction: directionValue,
        message: entry.message || '',
        count: 1
      });
      return;
    }

    const existing = grouped.get(key);
    existing.count += 1;
    if (entry.timestamp) {
      existing.timestamp = entry.timestamp;
    }
    if (entry.subject) {
      existing.subject = entry.subject;
    }
    if (entry.message) {
      existing.message = entry.message;
    }
  });

  return Array.from(grouped.values());
}

function renderLogs(payload = {}) {
  state.logs = payload.entries || [];
  if (!state.logs.length) {
    elements.logsList.className = 'log-list empty-state';
    elements.logsList.textContent = 'No log entries yet.';
    elements.recentActivity.className = 'activity-list empty-state';
    elements.recentActivity.textContent = 'No recent activity.';
    return;
  }

  // Render individual entries as cards (page-2 style)
  const entries = Array.isArray(state.logs) ? state.logs : [];
  // build contact lookup for display names
  const contactLookup = new Map((state.contacts || []).map((c) => [String(c.email || '').toLowerCase(), c.name || '']));
  const logMarkup = entries.map((entry, idx) => {
    const statusValue = String(entry.status || '').toUpperCase();
    const directionValue = statusValue === 'RECEIVED' ? 'Received' : 'Sent';
    const recipientLabel = entry.recipient || 'Unknown';
    const emailKey = String(recipientLabel).toLowerCase();
    const displayName = contactLookup.get(emailKey) || recipientLabel;
    const messagePreview = entry.message ? String(entry.message).replace(/\s+/g, ' ').trim() : '';
    let statusClass = 'failed';
    if (statusValue === 'SUCCESS') statusClass = 'success';
    else if (statusValue === 'RECEIVED') statusClass = 'received';

    return `
      <article class="log-card" data-index="${idx}">
        <div class="log-card-main">
          <div class="log-card-left">
            <strong class="log-subject">${escapeHtml(entry.subject || 'No subject')}</strong>
            <div class="log-meta">${escapeHtml(displayName)} • ${escapeHtml(entry.timestamp || '')}</div>
          </div>
          <div class="log-card-right">
            <span class="status-pill ${statusClass}">${escapeHtml(statusValue || 'UNKNOWN')}</span>
          </div>
        </div>
      </article>
    `;
  }).join('');

  elements.logsList.className = 'log-list';
  elements.logsList.innerHTML = logMarkup;

  // recent activity: show latest 4 entries compactly
  elements.recentActivity.className = 'activity-list';
  elements.recentActivity.innerHTML = entries.slice(0, 4).map((entry) => `
    <div class="activity-row">
      <span>${escapeHtml(entry.subject || 'No subject')} • ${escapeHtml(entry.recipient || 'Unknown')}</span>
      <strong>${escapeHtml(String(entry.status || '').toUpperCase() || 'UNKNOWN')}</strong>
    </div>
  `).join('');
}

// Log detail pane handling
const logDetailEl = $('#logDetail');
const logDetailBody = $('#logDetailBody');
const logDetailTitle = $('#logDetailTitle');

function showLogDetail(recipient, direction) {
  if (!recipient) return;
  const recipientKey = String(recipient).toLowerCase();
  const wantReceived = String(direction || '').toLowerCase() === 'received';
  const matches = (state.logs || []).filter((e) => {
    const r = String(e.recipient || '').toLowerCase();
    const s = String(e.status || '').toUpperCase();
    const isReceived = s === 'RECEIVED';
    return r === recipientKey && (wantReceived ? isReceived : !isReceived);
  }).sort((a,b) => (b.timestamp || '').localeCompare(a.timestamp || ''));

  logDetailTitle.textContent = `${recipient} — ${direction}`;
  if (!matches.length) {
    logDetailBody.innerHTML = `<div class="empty-state">No messages for ${escapeHtml(recipient)}</div>`;
  } else {
    logDetailBody.innerHTML = matches.map((m) => `
      <article class="log-message">
        <header>
          <strong>${escapeHtml(m.subject || 'No subject')}</strong>
          <span class="meta">${escapeHtml(m.timestamp || '')} • ${escapeHtml(m.status || '')}</span>
        </header>
        <div class="body">${escapeHtml(m.message || '')}</div>
      </article>
    `).join('');
  }

  if (logDetailEl) logDetailEl.classList.remove('is-hidden');
}

if (elements.logsList) {
  elements.logsList.addEventListener('click', (ev) => {
    const row = ev.target.closest && ev.target.closest('article');
    if (!row) return;
    const idx = row.dataset && row.dataset.index;
    if (typeof idx !== 'undefined') {
      const i = parseInt(idx, 10);
      if (!Number.isNaN(i) && state.logs[i]) {
        showLogDetailByIndex(i);
      }
    }
  });
}

function showLogDetailByIndex(index) {
  const entry = (state.logs || [])[index];
  if (!entry) return;
  const recipient = entry.recipient || 'Unknown';
  const direction = String(entry.status || '').toUpperCase() === 'RECEIVED' ? 'Received' : 'Sent';
  logDetailTitle.textContent = `${recipient} — ${direction}`;
  logDetailBody.innerHTML = `
    <article class="log-message">
      <header>
        <strong>${escapeHtml(entry.subject || 'No subject')}</strong>
        <span class="meta">${escapeHtml(entry.timestamp || '')} • ${escapeHtml(entry.status || '')}</span>
      </header>
      <div class="body">${escapeHtml(entry.message || '')}</div>
    </article>
  `;
  if (logDetailEl) logDetailEl.classList.remove('is-hidden');
}

const closeBtn = $('#closeLogDetail');
if (closeBtn) closeBtn.addEventListener('click', () => logDetailEl && logDetailEl.classList.add('is-hidden'));

async function loadDashboard() {
  try {
    const [status, contacts, logs, automation] = await Promise.all([
      api('/api/status'),
      api('/api/contacts'),
      api('/api/logs'),
      api('/api/automation')
    ]);
    const settings = await api('/api/settings');

    state.contacts = contacts.contacts || [];
    const currentSelections = new Set(state.selectedRecipients);
    state.selectedRecipients = new Set(
      state.contacts
        .map((contact) => contact.email)
        .filter((email) => currentSelections.size ? currentSelections.has(email) : true)
    );

    if (!state.selectedRecipients.size && state.contacts.length) {
      state.selectedRecipients = new Set(state.contacts.map((contact) => contact.email));
    }

    state.automation = automation;

    renderMetrics(status.counts);
    renderStatus(status.config);
    populateSettings(settings);
    renderContacts();
    renderAutomation();
    renderLogs(logs);
  } catch (error) {
    showToast(error.message, 'error');
  }
}

async function refreshLogsAndStatus() {
  const [status, logs, settings] = await Promise.all([api('/api/status'), api('/api/logs'), api('/api/settings')]);
  renderMetrics(status.counts);
  renderStatus(status.config);
  populateSettings(settings);
  renderLogs(logs);
}

$$('.tab-button').forEach((button) => {
  button.addEventListener('click', () => {
    activateTab(button.dataset.tab);
  });
});

$$('[data-jump-tab]').forEach((button) => {
  button.addEventListener('click', () => {
    activateTab(button.dataset.jumpTab);
  });
});

$$('.metric-card.metric-action').forEach((card) => {
  const handleAction = () => activateTab(card.dataset.tabTarget);
  card.addEventListener('click', handleAction);
  card.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleAction();
    }
  });
});

$('#templateSelect').addEventListener('change', (event) => {
  const template = templates[event.target.value];
  if (!template) return;
  $('#subject').value = template.subject;
  $('#message').value = template.message;
  $('#message').dispatchEvent(new Event('input'));
});

$('#message').addEventListener('input', () => {
  elements.composeMeta.textContent = `${$('#message').value.length} characters`;
});

elements.bulkRecipients.addEventListener('change', (event) => {
  if (event.target.type !== 'checkbox') return;
  if (event.target.checked) {
    state.selectedRecipients.add(event.target.value);
  } else {
    state.selectedRecipients.delete(event.target.value);
  }
  $('#selectedCount').textContent = `${state.selectedRecipients.size} selected`;
});

$('#selectAllBtn').addEventListener('click', () => {
  const shouldSelectAll = state.selectedRecipients.size !== state.contacts.length;
  state.selectedRecipients = new Set(shouldSelectAll ? state.contacts.map((contact) => contact.email) : []);
  renderContacts();
});

$('#refreshBtn').addEventListener('click', async () => {
  try {
    await loadDashboard();
    showToast('Dashboard refreshed.', 'success');
  } catch (error) {
    showToast(error.message, 'error');
  }
});

elements.jumpToSettingsBtn.addEventListener('click', () => {
  elements.settingsForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
  elements.settingsEmail.focus();
});

elements.settingsSmtp.addEventListener('blur', sanitizeSettingsInput);
elements.settingsEmail.addEventListener('blur', applyEmailProviderDefaults);

elements.sendForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = $('#sendBtn');
  setButtonLoading(button, true, 'Sending...');

  try {
    const settings = await getCurrentSettings();
    if (!settings.configured) {
      sanitizeSettingsInput();
      const email = elements.settingsEmail.value.trim();
      const password = elements.settingsPassword.value;
      if (!email || !password) {
        activateTab('composePanel');
        elements.settingsForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
        elements.settingsEmail.focus();
        showToast('Enter SMTP settings first, then send again.', 'warning');
        return;
      }

      await api('/api/settings', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password,
          smtpServer: elements.settingsSmtp.value.trim(),
          port: elements.settingsPort.value.trim()
        })
      });

      elements.settingsPassword.value = '';
      showToast('SMTP settings saved. Sending email now...', 'success');
    }

    const data = await api('/api/send_email', {
      method: 'POST',
      body: JSON.stringify({
        receiver: $('#receiver').value.trim(),
        subject: $('#subject').value.trim(),
        message: $('#message').value.trim()
      })
    });
    elements.sendForm.reset();
    elements.composeMeta.textContent = '0 characters';
    showToast(`Email sent to ${data.recipient}.`, 'success');
    await refreshLogsAndStatus();
  } catch (error) {
    if (error.message.includes('EMAIL and PASSWORD')) {
      showToast('Enter SMTP settings first, then send again.', 'warning');
    } else {
      showToast(error.message, 'error');
    }
  } finally {
    setButtonLoading(button, false);
  }
});

elements.bulkForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = $('#bulkSendBtn');

  if (!state.selectedRecipients.size) {
    showToast('Select at least one contact.', 'error');
    return;
  }

  setButtonLoading(button, true, 'Sending...');
  try {
    const data = await api('/api/bulk_send', {
      method: 'POST',
      body: JSON.stringify({
        subject: $('#bulkSubject').value.trim(),
        message: $('#bulkMessage').value.trim(),
        recipients: Array.from(state.selectedRecipients)
      })
    });
    showToast(`Bulk complete: ${data.sent} sent, ${data.failed} failed.`, data.failed ? 'warning' : 'success');
    await refreshLogsAndStatus();
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setButtonLoading(button, false);
  }
});

elements.contactForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const data = await api('/api/contacts', {
      method: 'POST',
      body: JSON.stringify({
        name: $('#contactName').value.trim(),
        email: $('#contactEmail').value.trim()
      })
    });
    state.contacts = data.contacts || [];
    state.selectedRecipients = new Set(state.contacts.map((contact) => contact.email));
    elements.contactForm.reset();
    renderContacts();
    await refreshLogsAndStatus();
    showToast('Contact added.', 'success');
  } catch (error) {
    showToast(error.message, 'error');
  }
});

elements.replyForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    state.automation = await api('/api/automation', {
      method: 'POST',
      body: JSON.stringify({
        action: 'add_reply',
        subject: $('#replySubject').value.trim(),
        reply_message: $('#replyMessage').value.trim()
      })
    });
    elements.replyForm.reset();
    renderAutomation();
    showToast('Auto-reply rule saved.', 'success');
  } catch (error) {
    showToast(error.message, 'error');
  }
});

elements.blacklistForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    state.automation = await api('/api/automation', {
      method: 'POST',
      body: JSON.stringify({
        action: 'add_blacklist',
        email: $('#blacklistEmail').value.trim()
      })
    });
    elements.blacklistForm.reset();
    renderAutomation();
    showToast('Sender blocked.', 'success');
  } catch (error) {
    showToast(error.message, 'error');
  }
});

elements.settingsForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = $('#saveSettingsBtn');
  setButtonLoading(button, true, 'Saving...');

  try {
    sanitizeSettingsInput();
    const data = await api('/api/settings', {
      method: 'POST',
      body: JSON.stringify({
        email: elements.settingsEmail.value.trim(),
        password: elements.settingsPassword.value,
        smtpServer: elements.settingsSmtp.value.trim(),
        port: elements.settingsPort.value.trim()
      })
    });

    elements.settingsPassword.value = '';
    elements.settingsMeta.textContent = 'Settings saved. You can send email now.';
    showToast('SMTP settings saved.', 'success');
    await refreshLogsAndStatus();
    if (data.configured) {
      elements.configBadge.textContent = 'SMTP ready';
      elements.configBadge.className = 'status-badge is-ready';
    }
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setButtonLoading(button, false);
  }
});

$('#clearLogsBtn').addEventListener('click', async () => {
  const confirmed = window.confirm('Clear all email log entries?');
  if (!confirmed) return;

  try {
    const logs = await api('/api/logs', { method: 'DELETE' });
    renderLogs(logs);
    await refreshLogsAndStatus();
    showToast('Logs cleared.', 'success');
  } catch (error) {
    showToast(error.message, 'error');
  }
});

loadDashboard();
