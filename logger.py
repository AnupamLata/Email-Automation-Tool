import os
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "email_log.txt"
"""Log file path: email_log.txt

Contains all email send attempts with:
- Timestamp (auto-added)
- Recipient email
- Send status (✅ or ❌)
- Email subject
- Error message (if failed)

Format: [YYYY-MM-DD HH:MM:SS] | To: email | Status: ... | Subject: ...
File is appended to, never overwritten.
Can be cleared via clear_logs() function.
"""

def log_email_send(recipient, subject, status, message=""):
    """Log email send attempts with timestamp
    
    Appends a line to email_log.txt for each send attempt.
    Timestamp automatically added.
    
    Log Format:
    [YYYY-MM-DD HH:MM:SS] | To: recipient@email.com | Status: ✅/❌ | Subject: ... | Message: ...
    
    Args:
        recipient (str): Email recipient address
        subject (str): Email subject line
        status (str): '✅ SUCCESS' or '❌ FAILED'
        message (str): Optional error message for failures
    
    Returns:
        None
    
    Side Effects:
        - Writes to email_log.txt (creates if not exists)
        - Appends in append mode (non-destructive)
    
    Examples:
        log_email_send('user@example.com', 'Hello', '✅ SUCCESS')
        log_email_send('user@example.com', 'Hello', '❌ FAILED', 'Invalid email')
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] | To: {recipient} | Status: {status} | Subject: {subject}"
    if message:
        log_entry += f" | Message: {message}"
    log_entry += "\n"
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError:
        # Serverless platforms can expose the deployment as read-only.
        # Email sending should not fail just because file logging is unavailable.
        return

def get_log_summary():
    """Get summary statistics from log file
    
    Reads email_log.txt and counts success/failure entries.
    Returns structure containing statistics.
    
    Returns:
        dict: Statistics dictionary
        Keys:
        - 'total': Total log entries
        - 'success': Count of ✅ SUCCESS entries
        - 'failed': Count of ❌ FAILED entries
        - 'entries': List of last entries (if available)
        - 'error': Error message (if file read failed)
    
    Side Effects:
        None (read-only operation)
    
    Example:
        stats = get_log_summary()
        print(f"Sent: {stats['success']}, Failed: {stats['failed']}")
    """
    if not os.path.exists(LOG_FILE):
        return {"total": 0, "success": 0, "failed": 0, "entries": []}
    
    entries = []
    success_count = 0
    failed_count = 0
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            entries = f.readlines()
            success_count = sum(1 for line in entries if "✅ SUCCESS" in line)
            failed_count = sum(1 for line in entries if "❌ FAILED" in line)
    except Exception as e:
        return {"total": 0, "success": 0, "failed": 0, "error": str(e)}
    
    return {
        "total": len(entries),
        "success": success_count,
        "failed": failed_count,
        "entries": entries[-10:]  # Last 10 entries
    }

def clear_logs():
    """Clear log file
    
    Deletes email_log.txt if it exists.
    Used to archive/clear old logs.
    
    Returns:
        None
    
    Side Effects:
        - Deletes email_log.txt if exists
        - New logs will create fresh file
    
    Use With Caution:
        This permanently deletes all log history!
    """
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

def view_logs():
    """Return all logs for display
    
    Reads email_log.txt and returns all lines.
    Used by main.py to display formatted log table.
    
    Returns:
        list: Lines from email_log.txt, or None if file not found
    
    Side Effects:
        None (read-only operation)
    
    Example:
        logs = view_logs()
        for log_line in logs:
            print(log_line)
    """
    if not os.path.exists(LOG_FILE):
        return None
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception:
        return None
