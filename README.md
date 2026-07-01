# 📧 Email Automation Tool

A professional, feature-rich email automation tool built with Python. Send single or bulk emails with beautiful terminal UI, comprehensive logging, and error handling.

![Python Version](https://img.shields.io/badge/Python-3.7+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## ✨ Features

### 🎯 Core Features
- **Single Email** - Send personalized emails to individual recipients
- **Bulk Email** - Send emails to multiple recipients from CSV file
- **Email Validation** - Automatic email format validation before sending
- **Input Validation** - Subject and message content validation
- **Error Handling** - Comprehensive error handling with user-friendly messages

### 🎨 Professional UI
- **Beautiful Terminal Design** - Rich, colorful terminal interface with ASCII art
- **Progress Tracking** - Visual progress bar during bulk email sends
- **Contact Preview** - View all recipients before sending
- **Email Summary** - Preview email details before sending
- **Color-Coded Status** - ✅ Success, ❌ Failure, ⚠️ Warnings

### 🔐 Security
- **Environment Variables** - Credentials stored securely in `.env` file
- **No Hardcoded Secrets** - All sensitive data externalized
- **App Password Support** - Works with Gmail App Passwords
- **Multi-Provider Support** - Compatible with Gmail, Outlook, Yahoo, custom SMTP

### 📊 Logging & Analytics
- **Automatic Logging** - All emails logged to `email_log.txt`
- **Timestamp Tracking** - Every operation timestamped
- **Success/Failure Tracking** - Know which emails succeeded/failed
- **Log Viewer** - Built-in log viewing with formatted tables
- **Statistics** - View send statistics and history
- **Log Management** - Clear logs with confirmation

### 🚀 Performance
- **Fast Sending** - Optimized SMTP connection handling
- **Batch Processing** - Efficient bulk email sending
- **Minimal Dependencies** - Only 2 external packages required
- **Low Resource Usage** - Lightweight and fast

---

## 📦 Installation

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup credentials
cp .env.example .env
# Edit .env with your email credentials

# 3. Run the tool
python main.py
```

For detailed setup instructions, see [SETUP.md](SETUP.md)

---

## � Vercel Deployment

This repository now includes a Vercel serverless endpoint at `/api/send_email`.

### How to deploy

1. Install the Vercel CLI: `npm install -g vercel`
2. From the project root: `vercel --prod`
3. Set these environment variables in Vercel:
   - `EMAIL`
   - `PASSWORD`
   - `SMTP_SERVER` (default: `smtp.gmail.com`)
   - `PORT` (default: `587`)

### API usage

Send a POST request to `https://<your-vercel-app>/api/send_email` with JSON:

```json
{
  "receiver": "recipient@example.com",
  "subject": "Test email",
  "message": "Hello from Vercel"
}
```

Response example:

```json
{
  "status": "success",
  "recipient": "recipient@example.com",
  "timestamp": "2026-07-01 12:00:00"
}
```

> Note: Vercel functions are stateless serverless invocations. This endpoint can send email on demand, but it is not a persistent 24x7 background process.

---

## �🎮 Usage

### Main Menu Options

```
1. Send Single Email      - Send email to one recipient
2. Send Bulk Email        - Send emails to multiple recipients from CSV
3. View Email Logs        - View all sent emails history
4. Clear Logs             - Clear log file (with confirmation)
5. Exit                   - Exit the application
```

### Sending Single Email

```
1. Select "Send Single Email" from menu
2. Enter recipient email address (validated)
3. Enter email subject
4. Enter email message
5. Review email summary
6. Confirm to send
```

**Example:**
```
Enter receiver email: john@example.com
Enter subject: Project Update
Enter message: Hi John, here's the project update...
```

### Sending Bulk Email

```
1. Select "Send Bulk Email" from menu
2. Tool shows all contacts from contacts.csv
3. Enter email subject (same for all)
4. Enter email message (same for all)
5. Confirm to send to all contacts
6. View progress bar and summary
```

**Features:**
- See all recipients before sending
- Progress bar shows real-time status
- Summary shows success/failure count with percentages
- Lists all failed recipients for easy retry

---

## 📋 CSV Format

Create `contacts.csv` in the following format:

```csv
name,email
John Doe,john@example.com
Jane Smith,jane@example.com
Bob Johnson,bob@example.com
```

**Requirements:**
- First row must contain headers: `name,email`
- Each row = one contact
- Email column is required
- Name column is optional (used for display)

---

## 📊 Logging System

### Log File: `email_log.txt`

Format: `[YYYY-MM-DD HH:MM:SS] | To: email@example.com | Status: ✅ SUCCESS | Subject: ...`

### Features
- **Automatic Logging** - Every email send is logged
- **Timestamps** - Know exactly when emails were sent
- **Status Tracking** - ✅ SUCCESS or ❌ FAILED
- **Error Messages** - Failure reasons included in log
- **View Logs** - Built-in menu option to view formatted logs
- **Clear Logs** - Option to archive/clear old logs

### Example Log Output
```
[2026-06-29 14:30:45] | To: john@example.com | Status: ✅ SUCCESS | Subject: Project Update
[2026-06-29 14:30:48] | To: jane@example.com | Status: ✅ SUCCESS | Subject: Project Update
[2026-06-29 14:30:51] | To: bob@example.com | Status: ❌ FAILED | Subject: Project Update | Message: Invalid email format
```

---

## 🔧 Configuration

### `.env` File

Create a `.env` file with your credentials:

```env
EMAIL=your_email@gmail.com
PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
PORT=587
```

### Supported Email Providers

| Provider | SMTP Server | Port |
|----------|------------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |
| Office 365 | smtp.office365.com | 587 |
| Custom | custom.smtp.com | 587 |

**For Gmail:** Use [App Password](https://myaccount.google.com/apppasswords), not your regular password

---

## 💡 Examples

### Example 1: Send Single Test Email
```
Main Menu → Option 1
Enter receiver: myself@gmail.com
Subject: Test Email
Message: This is a test
→ Confirm → ✅ Email sent!
```

### Example 2: Send Newsletter
```
1. Prepare contacts.csv with subscriber emails
2. Main Menu → Option 2
3. Enter subject: "Monthly Newsletter - June 2026"
4. Enter message: Newsletter content...
5. Confirm → Progress bar shows sending...
→ Summary: ✅ 450 sent, ❌ 5 failed (98.9%)
```

### Example 3: Check Send History
```
Main Menu → Option 3
→ View formatted table of last 20 emails sent
→ See success/failure statistics
→ Check timestamps and recipients
```

---

## 🛠️ Project Structure

```
Email_automation_tool/
├── main.py              # Main application & UI
├── email_sender.py      # Email sending logic & validation
├── config.py            # Configuration & environment setup
├── logger.py            # Logging system
├── contacts.csv         # Contact list for bulk sends
├── email_log.txt        # Email send history (auto-generated)
├── .env                 # Your credentials (private, not in git)
├── .env.example         # Template for .env
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── SETUP.md             # Setup & installation guide
└── TROUBLESHOOTING.md   # Common issues & solutions
```

---

## 📚 File Descriptions

### Core Files

**main.py**
- Application entry point
- Menu system and user interface
- Email sending orchestration
- Logging integration

**email_sender.py**
- Email sending implementation
- Email format validation
- SMTP connection handling
- Error handling and reporting

**config.py**
- Environment variable loading
- Configuration validation
- Secure credential handling

**logger.py**
- Email event logging
- Log file management
- Statistics calculation
- Log viewing utilities

**contacts.csv**
- CSV file with recipient emails
- Format: name, email
- Used for bulk email sending

---

## 🔒 Security Features

✅ **No Hardcoded Credentials** - All secrets in `.env` (not committed to git)
✅ **Environment Variables** - Uses `python-dotenv` for secure loading
✅ **App Password Support** - Works with Gmail App Passwords
✅ **Input Validation** - Email format verification before sending
✅ **Error Handling** - Graceful handling of authentication failures
✅ **Git Protection** - `.gitignore` prevents `.env` from being committed

### Security Best Practices

1. **Never share your `.env` file**
   ```bash
   cat .env  # DON'T share this!
   ```

2. **Use App Passwords for Gmail** (not your main password)
   - Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Generate app-specific password

3. **Keep `.env` out of version control**
   - Already in `.gitignore`
   - Verify before committing: `git status`

4. **Change password if `.env` is exposed**
   - Immediately update your email password
   - Generate new app password if using Gmail

---

## 🧪 Testing

### Test Sending a Single Email
```bash
python main.py
# Select Option 1
# Enter your own email
# Send test email
# Verify you receive it ✅
```

### Test Bulk Sending
```bash
python main.py
# Select Option 2
# Verify contact preview shows correct recipients
# Send test to small group first
# Check logs for success/failure ✅
```

### Test Logging
```bash
python main.py
# Select Option 3
# View email logs
# Check statistics ✅
```

---

## ⚠️ Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| "EMAIL and PASSWORD required" | Create `.env` from `.env.example` |
| "Authentication failed" | Verify credentials, use App Password for Gmail |
| "'rich' module not found" | Run `pip install -r requirements.txt` |
| "contacts.csv not found" | Create CSV file with recipients |
| Gmail: "Less secure app access" | Use App Password instead |
| Email not received | Check spam/junk folder, verify recipient |
| Progress bar not showing | Terminal might not support rich library features |

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📈 Performance Notes

- **Single Email**: ~2-3 seconds (includes SMTP connection)
- **Bulk Email (100 recipients)**: ~5-10 seconds
- **Bulk Email (1000 recipients)**: ~1-2 minutes
- **Log Operations**: Instant (<1 second)

---

## 🤝 Contributing

To improve this tool:

1. Test thoroughly before changes
2. Maintain security standards
3. Keep UI user-friendly
4. Add tests for new features
5. Update documentation

---

## 📄 License

This project is open source and available under the MIT License.

---

## 💬 Support

### Getting Help

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
2. Review [SETUP.md](SETUP.md) for installation help
3. Check `.env.example` for configuration examples
4. Review logs in `email_log.txt` for error details

### Common Questions

**Q: Is my password secure?**
A: Yes! Your password is never exposed. It's stored in `.env` (not in git) and only used for SMTP connection.

**Q: Can I use it on multiple machines?**
A: Yes! Create a `.env` file on each machine with the same credentials.

**Q: How many emails can I send?**
A: Depends on your email provider's rate limits. Most allow 300-2000 per day.

**Q: Do I need an internet connection?**
A: Yes, to connect to SMTP server and send emails.

---

## 🚀 Roadmap

Potential future features:
- [ ] Email templates
- [ ] HTML email support
- [ ] Email scheduling
- [ ] Attachment support
- [ ] Email tracking
- [ ] API support
- [ ] Web interface

---

## 📊 Statistics

- **Languages Used**: Python
- **External Dependencies**: 2 (rich, python-dotenv)
- **Lines of Code**: ~400
- **Test Coverage**: Core functionality
- **Performance**: Optimized for bulk sending

---

## 🎉 Version History

### v1.0 (Current)
- ✅ Single and bulk email sending
- ✅ Beautiful terminal UI
- ✅ Comprehensive logging
- ✅ Email validation
- ✅ Security features
- ✅ Error handling

---

**Made with ❤️ by Email Automation Team**

For the latest version and updates, visit the project repository.

Happy emailing! 📧
