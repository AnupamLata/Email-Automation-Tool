const form = document.getElementById('sendForm');
const statusBox = document.getElementById('status');
const sendButton = document.getElementById('sendBtn');
const receiverInput = document.getElementById('receiver');
const subjectInput = document.getElementById('subject');
const messageInput = document.getElementById('message');

const templates = {
  followup: {
    subject: 'Follow-up on our conversation',
    message: 'Hi there,\n\nI wanted to follow up on our previous conversation and check if there is anything else you need from my side.\n\nBest regards,\n'
  },
  update: {
    subject: 'Project update',
    message: 'Hi team,\n\nHere is the latest project update. Everything is moving forward as planned and I will share the next milestone soon.\n\nThanks,'
  },
  support: {
    subject: 'Support reply',
    message: 'Hello,\n\nThanks for reaching out. I reviewed your request and I am looking into it now. I will get back to you with the next steps shortly.\n\nBest,'
  }
};

function setStatus(text, cls) {
  statusBox.textContent = text;
  statusBox.className = `status ${cls || 'idle'}`;
}

function setSendingState(isSending) {
  sendButton.disabled = isSending;
  sendButton.textContent = isSending ? 'Sending...' : 'Send email';
}

document.querySelectorAll('[data-template]').forEach((button) => {
  button.addEventListener('click', () => {
    const template = templates[button.dataset.template];
    if (!template) {
      return;
    }

    if (!subjectInput.value.trim()) {
      subjectInput.value = template.subject;
    }

    if (!messageInput.value.trim()) {
      messageInput.value = template.message;
    }

    setStatus('Template loaded. Review the message and send when ready.', 'idle');
  });
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const receiver = receiverInput.value.trim();
  const subject = subjectInput.value.trim();
  const message = messageInput.value.trim();

  if (!receiver || !subject || !message) {
    setStatus('Please fill in all fields before sending.', 'error');
    return;
  }

  setSendingState(true);
  setStatus('Sending email through the Vercel function...', 'sending');

  try {
    const res = await fetch('/api/send_email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receiver, subject, message })
    });

    const data = await res.json();

    if (res.ok) {
      setStatus(`Email sent to ${data.recipient}${data.timestamp ? ` at ${data.timestamp}` : ''}.`, 'success');
      form.reset();
      receiverInput.focus();
    } else {
      setStatus(data.error || data.message || 'Failed to send email.', 'error');
    }
  } catch (err) {
    setStatus(`Network error: ${err.message}`, 'error');
  } finally {
    setSendingState(false);
  }
});
