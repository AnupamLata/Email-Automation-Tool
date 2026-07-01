# 📚 Code Documentation

Technical documentation for Email Automation Tool developers.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────┐
│         main.py (UI Layer)          │
│  - Menu system                      │
│  - User interaction                 │
│  - Display formatting (rich)        │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
   ┌─────────────┐  ┌─────────────┐
   │ email_      │  │  logger.py  │
   │ sender.py   │  │ - Logging   │
   │ - Sending   │  │ - Stats     │
   │ - Validation│  │ - Reporting │
   └─────────────┘  └─────────────┘
       │                │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │   config.py    │
       │  - Credentials │
       │  - SMTP setup  │
       └────────────────┘
```

---

## 📦 Module Reference

### main.py

**Purpose:** Application entry point and UI layer

**Key Functions:**

#### `display_banner()`
Shows the ASCII art banner
```python
def display_banner():
    """Display colorful banner"""
```

#### `display_menu()`
Shows main menu with 5 options
```python
def display_menu():
    """Display main menu"""
    # Shows options 1-5 with colors
```

#### `send_single_email()`
Handles single email workflow
- Validates recipient email
- Gets subject and message
- Shows preview table
- Confirms before sending
- Returns success/failure
```python
def send_single_email():
    """Send a single email with validation"""
```

**Flow:**
1. Input recipient email
2. Validate format
3. Input subject
4. Input message
5. Show preview
6. Confirm
7. Send and log

#### `send_bulk_email()`
Handles bulk email workflow
- Reads contacts.csv
- Shows contact preview table
- Gets subject and message
- Progress bar during sending
- Detailed summary report

```python
def send_bulk_email():
    """Send bulk emails from CSV"""
```

**Flow:**
1. Load contacts.csv
2. Show contact preview
3. Input subject/message
4. Show confirmation
5. Send with progress bar
6. Show summary with stats
7. List failed recipients

#### `view_email_logs()`
Displays email send history
```python
def view_email_logs():
    """Display email logs"""
```

**Shows:**
- Last 20 email entries
- Timestamp, recipient, status
- Overall statistics

#### `clear_email_logs()`
Clears log file with confirmation
```python
def clear_email_logs():
    """Clear logs with confirmation"""
```

#### `main()`
Main application loop
```python
def main():
    """Main application loop"""
```

**Flow:**
- Show banner
- Loop menu until exit
- Handle user choices
- Handle interrupts

---

### email_sender.py

**Purpose:** Email sending and validation logic

**Key Functions:**

#### `validate_email(email: str) -> bool`
Validates email format using regex
```python
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

**Pattern Validation:**
- Must have: `user@domain.ext`
- Allows: `.`, `_`, `%`, `+`, `-`
- Domain: alphanumeric, `.`, `-`
- Extension: 2+ letters

**Returns:** `True` if valid, `False` otherwise

#### `send_email(receiver, subject, message) -> (bool, dict)`
Sends email via SMTP
```python
def send_email(receiver, subject, message):
    """Send email with validation and error handling."""
```

**Validation:**
1. Email format check
2. Subject non-empty
3. Message non-empty

**Returns:**
```python
(success: bool, metadata: {
    'recipient': str,
    'subject': str,
    'timestamp': str,
    'status': str,  # "SUCCESS" or "FAILED"
    'message': str  # Error message if failed
})
```

**Process:**
1. Validate inputs
2. Create EmailMessage
3. Connect to SMTP
4. Start TLS
5. Login
6. Send message
7. Log result
8. Return status

**Error Handling:**
- `SMTPAuthenticationError` - Login failed
- `SMTPException` - SMTP protocol error
- Generic `Exception` - Unexpected error

---

### config.py

**Purpose:** Configuration and environment setup

**Key Functions:**

#### `load_dotenv()`
Loads environment variables from `.env`
```python
from dotenv import load_dotenv
load_dotenv()
```

#### Environment Variables:
```python
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
PORT = int(os.getenv("PORT", 587))
```

**Defaults:**
- SMTP_SERVER: `smtp.gmail.com`
- PORT: `587`

**Validation:**
- Raises `ValueError` if EMAIL or PASSWORD missing
- Ensures app fails fast if misconfigured

---

### logger.py

**Purpose:** Email logging and statistics

**Key Functions:**

#### `log_email_send(recipient, subject, status, message="")`
Logs email send attempt
```python
def log_email_send(recipient, subject, status, message=""):
    """Log email send attempts with timestamp"""
```

**Format:**
```
[2026-06-29 14:30:45] | To: recipient@email.com | Status: ✅ SUCCESS | Subject: Email Subject | Message: Optional message
```

**Parameters:**
- `recipient` - Email address
- `subject` - Email subject
- `status` - "✅ SUCCESS" or "❌ FAILED"
- `message` - Optional error message

#### `get_log_summary() -> dict`
Returns statistics from log file
```python
def get_log_summary():
    """Get summary statistics from log file"""
```

**Returns:**
```python
{
    'total': int,           # Total entries
    'success': int,         # Success count
    'failed': int,          # Failed count
    'entries': list,        # Raw log lines
    'error': str            # Error if any
}
```

#### `view_logs() -> list`
Returns all log entries
```python
def view_logs():
    """Return all logs for display"""
```

**Returns:** List of log line strings (newest first)

#### `clear_logs()`
Deletes log file
```python
def clear_logs():
    """Clear log file"""
```

---

## 📊 Data Flow

### Single Email Send Flow
```
User Input
    ↓
Validate Email Format
    ↓
Validate Subject & Message
    ↓
Show Preview
    ↓
Confirm Sending
    ↓
Create EmailMessage
    ↓
Connect to SMTP
    ↓
Login & Send
    ↓
Log Result
    ↓
Display Status
    ↓
Return to Menu
```

### Bulk Email Send Flow
```
Load contacts.csv
    ↓
Parse CSV into list
    ↓
Show Contact Preview
    ↓
Get Subject & Message
    ↓
Show Confirmation
    ↓
For Each Contact:
    ├─ Validate Email
    ├─ Send Email
    ├─ Log Result
    ├─ Update Counters
    └─ Show Progress
    ↓
Calculate Statistics
    ↓
Show Summary
    ├─ Success Count
    ├─ Failed Count
    ├─ Percentages
    └─ Failed List
    ↓
Return to Menu
```

---

## 🔄 Exception Handling

### Email Sending Exceptions

| Exception | Cause | Handling |
|-----------|-------|----------|
| `SMTPAuthenticationError` | Wrong credentials | Log & return False |
| `SMTPException` | Protocol error | Log & return False |
| `Exception` | Any other error | Log & return False |

### File Exceptions

| Exception | Cause | Handling |
|-----------|-------|----------|
| `FileNotFoundError` | CSV not found | Show error, return |
| `IOError` | Can't read file | Show error, return |
| `csv.Error` | Invalid CSV format | Show error, return |

---

## 📝 API Reference

### Main Functions

```python
# Send single email
success, metadata = send_email(
    receiver="user@example.com",
    subject="Hello",
    message="Content"
)

# Validate email
is_valid = validate_email("user@example.com")

# Log email
log_email_send(
    recipient="user@example.com",
    subject="Hello",
    status="✅ SUCCESS",
    message=""
)

# Get logs
logs = view_logs()
# Returns: ["[timestamp] | To: ... | Status: ...", ...]

# Get statistics
stats = get_log_summary()
# Returns: {total, success, failed, entries}
```

---

## 🎨 UI Components (rich library)

### Console
```python
from rich.console import Console
console = Console()
console.print("Text", style="bold cyan")
```

### Panel
```python
from rich.panel import Panel
console.print(Panel("Content", title="Title", border_style="blue"))
```

### Table
```python
from rich.table import Table
table = Table(title="Title")
table.add_column("Col1", style="cyan")
table.add_row("Value")
console.print(table)
```

### Progress Bar
```python
from rich.progress import track
for item in track(items, description="Processing"):
    # Process item
```

### Prompt & Confirm
```python
from rich.prompt import Prompt, Confirm
email = Prompt.ask("Email")
if Confirm.ask("Continue?"):
    # Process
```

---

## 🔒 Security Implementation

### Credential Management
```python
# ❌ WRONG: Hardcoded
EMAIL = "user@gmail.com"

# ✅ RIGHT: Environment variable
EMAIL = os.getenv("EMAIL")
```

### Input Validation
```python
# Validate before using
if validate_email(user_input):
    # Safe to use
```

### Error Messages
```python
# ❌ WRONG: Expose internals
raise Exception(f"Login failed for {EMAIL}: {PASSWORD}")

# ✅ RIGHT: Generic message
raise Exception("Authentication failed")
```

---

## 📈 Performance Considerations

### Email Sending
- **Connection pooling** - Reuse SMTP connection per send
- **Batch processing** - Process contacts sequentially
- **Rate limiting** - Gmail limits ~300/day, Outlook ~10,000/day

### Logging
- **Append mode** - Only write, don't rewrite entire file
- **In-memory stats** - Count while reading
- **Lazy loading** - Load logs only when needed

### UI
- **Progress bar** - Visual feedback during long operations
- **Streaming output** - Show each success immediately
- **Summary only** - Detailed summary at end

---

## 🧪 Testing Checklist

### Unit Tests (Manual)
```python
# Test email validation
validate_email("valid@example.com")  # True
validate_email("invalid@")           # False

# Test send_email
success, meta = send_email("test@gmail.com", "Hi", "Hello")
# Check: success is True/False
# Check: meta has all fields
```

### Integration Tests
```python
# Test single send
python main.py
# Option 1 → Enter email → Confirm → Check inbox

# Test bulk send
python main.py
# Option 2 → Confirm → Check results → View logs

# Test logs
python main.py
# Option 3 → View logs
# Option 4 → Clear logs
```

---

## 🚀 Extension Points

### Adding New Email Provider
1. Add to `.env.example`:
   ```
   SMTP_SERVER=smtp.provider.com
   PORT=587
   ```
2. Update config.py if needed
3. No code changes required!

### Adding New Features
1. Update `main.py` - Add menu option
2. Create new function for logic
3. Integrate with logging
4. Update documentation

### Adding Email Templates
1. Create template files
2. Add template selection to menu
3. Replace variables: `{name}`, `{email}`, etc.
4. Send using template

---

## 📚 Code Style

### Naming Convention
```python
# Functions: snake_case
def send_email(receiver, subject, message):

# Constants: UPPER_CASE
SMTP_SERVER = "smtp.gmail.com"
PORT = 587

# Variables: snake_case
email_address = "user@example.com"
is_valid = True
```

### Docstrings
```python
def function_name(param1, param2):
    """One-line description
    
    Longer description if needed.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Description of return value
    """
```

### Comments
```python
# Use for complex logic, not obvious code
if validate_email(email):  # Already clear
    # Complex validation rule
    if email.count("@") == 1:  # Need explanation
        process()
```

---

## 🔗 Dependencies

### Required
- **rich** (13.0.0+) - Terminal formatting
- **python-dotenv** (0.19.0+) - Environment variables

### Built-in
- **smtplib** - Email sending
- **csv** - CSV parsing
- **email** - EmailMessage
- **re** - Regex validation
- **datetime** - Timestamps
- **os** - Environment variables

---

## 📄 File Reference

| File | Lines | Purpose |
|------|-------|---------|
| main.py | ~250 | UI and main logic |
| email_sender.py | ~80 | Email sending |
| config.py | ~15 | Configuration |
| logger.py | ~45 | Logging system |
| requirements.txt | 2 | Dependencies |
| .env | 4 | Credentials |
| contacts.csv | N/A | Contact list |
| email_log.txt | N/A | Email history |

---

## 🎓 Learning Resources

- [Python SMTP](https://docs.python.org/3/library/smtplib.html)
- [Rich Library](https://rich.readthedocs.io/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Regex Guide](https://docs.python.org/3/library/re.html)

---

**Version:** 1.0
**Last Updated:** 2026-06-29
