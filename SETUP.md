# 🚀 Quick Start Guide

## Prerequisites
- Python 3.7+
- pip (Python package manager)

## Installation Steps

### Step 1: Clone/Download the Project
```bash
cd Email_automation_tool
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- **rich** (v13.0.0+) - Beautiful terminal formatting
- **python-dotenv** (v0.19.0+) - Environment variable management

### Step 3: Setup Credentials
#### Option A: Using Gmail with App Password (Recommended)

1. Enable 2-Step Verification on your Google Account:
   - Go to [myaccount.google.com](https://myaccount.google.com)
   - Click "Security" in the left sidebar
   - Enable "2-Step Verification"

2. Generate an App Password:
   - Go back to Security settings
   - Find "App passwords" (appears only after 2-Step Verification is enabled)
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` with your credentials:
   ```
   EMAIL=your_email@gmail.com
   PASSWORD=your_16_char_app_password
   SMTP_SERVER=smtp.gmail.com
   PORT=587
   WEB_PORT=8001
   ```

   - `PORT` is the SMTP server port for sending email
   - `WEB_PORT` is the local port where the web dashboard is served


#### Option B: Using Other Email Providers

For **Outlook/Hotmail**:
```
EMAIL=your_email@outlook.com
PASSWORD=your_password
SMTP_SERVER=smtp-mail.outlook.com
PORT=587
```

For **Yahoo Mail**:
```
EMAIL=your_email@yahoo.com
PASSWORD=your_app_password
SMTP_SERVER=smtp.mail.yahoo.com
PORT=587
```

For **Custom SMTP**:
```
EMAIL=your_email@domain.com
PASSWORD=your_password
SMTP_SERVER=your_smtp_server
PORT=your_port
```

### Step 4: Verify `.env` File
Make sure `.env` file is created and NOT in git:
```bash
# Check that .env exists
ls -la .env

# Verify .gitignore includes .env
cat .gitignore
```

### Step 5: Run the Application
```bash
python main.py
```

You should see the beautiful banner and menu! 🎉

---

## 📋 CSV Format for Bulk Emails

The `contacts.csv` file should have this format:

```csv
name,email
John Doe,john@example.com
Jane Smith,jane@example.com
Bob Johnson,bob@example.com
```

- **First row**: Column headers (must include "name" and "email")
- **Name column**: Recipient's name (optional, but recommended)
- **Email column**: Valid email address (required)

### Example contacts.csv:
```csv
name,email
Rahul Sharma,rahul@gmail.com
Riya Patel,riya@gmail.com
Aman Verma,aman@gmail.com
Priya Singh,priya@gmail.com
```

---

## 🎯 First Time Usage

1. **Start the app:**
   ```bash
   python main.py
   ```

2. **Choose Option 1** to send a test email to yourself

3. **Enter details:**
   - Receiver Email: your_email@gmail.com
   - Subject: Test Email
   - Message: This is a test message

4. **Confirm** the email summary

5. **Check your inbox** - You should receive the email! ✅

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "EMAIL and PASSWORD environment variables are required" | Create `.env` file from `.env.example` |
| "Authentication failed" | Check EMAIL and PASSWORD in `.env` |
| "Module 'rich' not found" | Run `pip install -r requirements.txt` |
| "contacts.csv file not found" | Ensure `contacts.csv` exists in project directory |
| Gmail says "Less secure app access" | Use App Password instead (see above) |

---

## 📝 Next Steps

- Read [README.md](README.md) for detailed features
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Customize `contacts.csv` with your recipients

Happy emailing! 📧
