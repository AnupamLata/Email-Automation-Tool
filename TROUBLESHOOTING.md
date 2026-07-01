# 🔧 Troubleshooting Guide

Common issues and their solutions for Email Automation Tool.

---

## 🚨 Critical Issues

### ❌ "EMAIL and PASSWORD environment variables are required"

**Cause:** `.env` file is missing or not properly configured

**Solution:**
```bash
# 1. Create .env from template
cp .env.example .env

# 2. Edit .env with your credentials
notepad .env  # Windows
nano .env     # Mac/Linux

# 3. Add your email and password
EMAIL=your_email@gmail.com
PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
PORT=587

# 4. Save and restart application
python main.py
```

**Verify:**
```bash
# Check if .env exists
ls -la .env

# Check .env content (don't share output!)
cat .env
```

---

### ❌ "Authentication failed. Check EMAIL and PASSWORD"

**Cause 1:** Wrong email or password in `.env`
```bash
# Solution: Verify credentials
# For Gmail:
# - Use your full email address (username@gmail.com)
# - Use App Password (not your regular password)
# - Go to: https://myaccount.google.com/apppasswords
```

**Cause 2:** Gmail security settings
```bash
# Solution: Enable App Passwords
# 1. Go to https://myaccount.google.com
# 2. Click "Security" in left menu
# 3. Enable "2-Step Verification" if not done
# 4. Find "App passwords" (shows only after 2-Step enabled)
# 5. Select "Mail" and "Windows Computer"
# 6. Copy the 16-character password
# 7. Update PASSWORD in .env
```

**Cause 3:** Special characters in password
```bash
# Solution: Escape special characters if needed
# Example: If password is "P@ss!word", it should work as-is in .env
# But if it has quotes or backslashes, escape them:
PASSWORD=P@ss\!word
```

---

### ❌ "ModuleNotFoundError: No module named 'rich'"

**Cause:** Required packages not installed

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install manually
pip install rich>=13.0.0
pip install python-dotenv>=0.19.0

# Verify installation
pip list | grep rich
pip list | grep python-dotenv
```

---

### ❌ "contacts.csv file not found"

**Cause:** Bulk email attempted but `contacts.csv` missing

**Solution:**
```bash
# 1. Create contacts.csv in project directory
# 2. Add header row and contacts:

name,email
John Doe,john@example.com
Jane Smith,jane@example.com

# 3. Make sure file is in main project folder
# 4. Try bulk email again
```

**CSV Format:**
- First row: `name,email` (headers)
- Each row: `Name,email@example.com`
- No spaces after commas
- One contact per line

---

## ⚠️ Common Issues

### Issue: "Invalid email format. Please try again."

**Possible Causes:**
- Missing @ symbol: `johnexample.com` ❌
- Space in email: `john @example.com` ❌
- Invalid domain: `john@.com` ❌

**Valid Formats:**
- `john@example.com` ✅
- `jane.smith@example.co.uk` ✅
- `user+tag@domain.com` ✅

---

### Issue: "Subject cannot be empty" or "Message cannot be empty"

**Cause:** User tried to send with empty subject/message

**Solution:**
- Subject: Enter at least 1 character
- Message: Enter at least 1 character
- Both are required for sending

---

### Issue: Email not received by recipient

**Causes & Solutions:**

1. **Email sent to spam/junk folder**
   - Check recipient's spam folder
   - Mark as "Not Spam"
   - Ask recipient to add you to safe senders

2. **Wrong email address**
   - Verify recipient email in logs
   - Check contacts.csv for typos
   - Use "View Email Logs" to see what was sent

3. **Email provider blocking**
   - Some ISPs/companies block bulk emails
   - Try sending single test email first
   - Contact recipient's email admin

4. **Delayed delivery**
   - SMTP can take 5-30 seconds
   - Check log to confirm sent status
   - Wait a few minutes before retrying

---

### Issue: "SMTP Error: 421 Service not available"

**Cause:** SMTP server temporarily unavailable

**Solutions:**
```bash
# Solution 1: Try again after a few seconds
# Solution 2: Check internet connection
ping smtp.gmail.com

# Solution 3: Verify SMTP settings in .env
SMTP_SERVER=smtp.gmail.com
PORT=587

# Solution 4: Try different time of day
# (Gmail might rate-limit heavy usage)
```

---

### Issue: Progress bar not showing during bulk send

**Cause:** Terminal doesn't support rich library features

**Solutions:**
```bash
# Solution 1: Use Windows Terminal instead of CMD
# Solution 2: Update terminal color settings
# Solution 3: Disable rich formatting (advanced)
#    - Edit main.py
#    - Change console.print() calls to print()
```

---

### Issue: "contacts.csv file not found" but file exists

**Cause:** CSV file not in correct location

**Solution:**
```bash
# 1. Check file location
ls -la  # or dir (Windows)
# Should see: contacts.csv

# 2. Make sure you're in project directory
cd Email_automation_tool
python main.py

# 3. Verify file name
# Must be exactly: contacts.csv (lowercase, .csv extension)
```

---

### Issue: Logs not appearing in "View Email Logs"

**Cause 1:** No emails sent yet
**Solution:** Send at least one email first

**Cause 2:** Logs were cleared
**Solution:** Send new emails - they will be logged automatically

**Cause 3:** Permissions issue with email_log.txt
**Solution:**
```bash
# Delete old log file and let app recreate it
rm email_log.txt
# or in Windows
del email_log.txt

# Run app again - new log will be created
python main.py
```

---

## 🌐 Gmail-Specific Issues

### Gmail: "Less secure app access blocked"

**Old Error (Gmail deprecated this):**
```
Error: 535-5.7.8 Username and Password not accepted. Learn more at
535 5.7.8 https://support.google.com/mail/?p=BadCredentials
```

**Solution:** Use App Password instead

```bash
# 1. Go to https://myaccount.google.com
# 2. Security → 2-Step Verification (enable if needed)
# 3. Security → App passwords
# 4. Select Mail, Windows Computer
# 5. Use generated password in .env
# 6. Update PASSWORD field and try again
```

---

### Gmail: "Application-specific password required"

**Solution:**
- App Passwords only work with 2-Step Verification enabled
- Enable 2-Step: https://myaccount.google.com/u/1/security
- Then generate App Password

---

### Gmail: "The password you've entered is incorrect"

**Solutions:**
1. Copy-paste the App Password exactly (no typos)
2. Make sure you generated it for "Mail" and "Windows Computer"
3. Generate a new one and try again
4. Check `.env` file doesn't have extra spaces:
   ```
   PASSWORD=your_16_char_password  ✅ Good
   PASSWORD= your_16_char_password  ❌ Extra space
   ```

---

## 🏢 Outlook/Office 365 Issues

### "Outlook: Authentication failed"

**Solutions:**
```bash
# 1. Verify SMTP settings in .env
EMAIL=your_email@outlook.com
PASSWORD=your_password
SMTP_SERVER=smtp-mail.outlook.com  # NOT smtp.office365.com
PORT=587

# 2. If still failing, enable App Passwords
# 3. For Office 365, enable "Less secure apps" in settings
```

---

## 🛡️ Security & Privacy Issues

### Issue: ".env file was accidentally committed to git"

**Solution:**
```bash
# 1. Regenerate passwords immediately!
# 2. Remove .env from git history
git rm --cached .env
git commit -m "Remove .env from git"

# 3. Verify it's now ignored
git status  # .env should NOT appear

# 4. Update password in all places
# 5. Consider revoking app passwords and creating new ones
```

---

### Issue: "Concerned about password security"

**Best Practices:**
```bash
# 1. Never share your .env file
# 2. Use App Passwords (for Gmail) not regular password
# 3. Keep .env in .gitignore (already done)
# 4. Use different passwords for different services
# 5. Change password if .env exposed
# 6. Never paste password in chat/email
# 7. Audit who can access your computer
```

---

## 📊 Performance Issues

### Issue: Bulk send is very slow

**Causes & Solutions:**

1. **Too many recipients**
   - Gmail: ~300/day limit
   - Outlook: ~10,000/day limit
   - Solution: Break into smaller batches

2. **Large message size**
   - Each attachment/large content slows sending
   - Solution: Keep messages concise

3. **Poor internet**
   - Check connection speed
   - Move closer to router
   - Solution: Try again later

4. **Server overload**
   - Email servers sometimes slow at peak times
   - Solution: Send during off-peak hours

---

### Issue: "Email sending hangs/freezes"

**Cause:** Long timeout waiting for SMTP

**Solutions:**
```bash
# Option 1: Wait 30-60 seconds (SMTP timeout)
# Option 2: Press Ctrl+C to interrupt
# Option 3: Try again with fewer emails
```

---

## 🔍 Advanced Troubleshooting

### View Detailed Logs

```bash
# View email_log.txt
cat email_log.txt  # Mac/Linux
type email_log.txt  # Windows

# View last 20 entries
tail -20 email_log.txt  # Mac/Linux
```

---

### Check Email Configuration

```bash
# View .env settings (don't share output!)
cat .env

# Verify required fields exist
grep -E "EMAIL|PASSWORD|SMTP" .env
```

---

### Test SMTP Connection

```bash
# Quick Python test
python -c "import smtplib; s = smtplib.SMTP('smtp.gmail.com', 587); s.starttls(); print('SMTP working')"

# Expected output: SMTP working
```

---

### Enable Debug Mode

Add this to `main.py` for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📞 Still Having Issues?

### Debug Checklist

- [ ] `.env` file exists and readable
- [ ] EMAIL and PASSWORD set correctly
- [ ] Used App Password for Gmail
- [ ] internet connection working
- [ ] contacts.csv in correct format
- [ ] Python 3.7+ installed
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] No syntax errors (`python -m py_compile main.py`)

### Getting More Help

1. **Check logs:** `View Email Logs` in app menu
2. **Review code:** Check error messages in console
3. **Test step-by-step:**
   - Test single email first
   - Then test bulk with 1 contact
   - Then test with more contacts
4. **Verify settings:** Review .env carefully
5. **Try minimal test:** Send to your own email

---

## 💡 Pro Tips

### Tip 1: Test Before Bulk Send
```bash
# Always test with yourself first
Option 1: Single Email
Recipient: your_email@example.com
# Then do bulk send
```

### Tip 2: Check Logs Frequently
```bash
# After sending emails, always check:
Option 3: View Email Logs
# Verify success/failure counts
```

### Tip 3: Keep contacts.csv Updated
```bash
# Before bulk send, verify:
# - All emails are valid
# - No duplicates
# - CSV format correct
```

### Tip 4: Use Clear Subject Lines
```bash
# Good subject:
"Monthly Newsletter - June 2026"

# Bad subject:
"Email"
```

---

## 🎓 Learning Resources

- [Python SMTP Documentation](https://docs.python.org/3/library/smtplib.html)
- [Gmail App Passwords](https://myaccount.google.com/apppasswords)
- [Rich Library Docs](https://rich.readthedocs.io/)
- [CSV Format Guide](https://tools.ietf.org/html/rfc4180)

---

**Last Updated:** 2026-06-29

For additional help, refer to README.md or SETUP.md
