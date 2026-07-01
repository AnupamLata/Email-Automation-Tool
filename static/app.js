const form = document.getElementById('sendForm');
const statusBox = document.getElementById('status');

function setStatus(text, cls) {
  statusBox.textContent = text;
  statusBox.className = cls || '';
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const receiver = document.getElementById('receiver').value.trim();
  const subject = document.getElementById('subject').value.trim();
  const message = document.getElementById('message').value.trim();

  if (!receiver || !subject || !message) {
    setStatus('Please fill in all fields.', 'error');
    return;
  }

  setStatus('Sending...', 'sending');

  try {
    const res = await fetch('/api/send_email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receiver, subject, message })
    });

    const data = await res.json();

    if (res.ok) {
      setStatus(`Email sent to ${data.recipient} at ${data.timestamp || ''}`, 'success');
      form.reset();
    } else {
      setStatus(data.error || data.message || 'Failed to send email', 'error');
    }
  } catch (err) {
    setStatus('Network error: ' + err.message, 'error');
  }
});
