import smtplib
import re
from datetime import datetime
from email.message import EmailMessage
from config import EMAIL, PASSWORD, SMTP_SERVER, PORT
from logger import log_email_send

def validate_email(email):
    """Validate email format using regex pattern
    
    Pattern Validation:
    - Must contain exactly one @
    - User part: alphanumeric, dots, underscores, %, +, -
    - Domain part: alphanumeric, dots, hyphens
    - Extension: 2+ letters
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid format, False otherwise
    
    Examples:
        validate_email('user@example.com')    # True
        validate_email('invalid@')             # False
        validate_email('no-at-sign.com')       # False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_email(receiver, subject, message):
    """Send email via SMTP with validation and error handling
    
    Complete email sending workflow:
    1. Validate email format
    2. Validate subject (non-empty)
    3. Validate message (non-empty)
    4. Create EmailMessage object
    5. Connect to SMTP server
    6. Start TLS encryption
    7. Login with credentials
    8. Send message
    9. Log result with timestamp
    10. Return success status and metadata
    
    Args:
        receiver (str): Recipient email address
        subject (str): Email subject line
        message (str): Email body content
    
    Returns:
        tuple: (success: bool, metadata: dict)
        Metadata keys:
        - 'recipient': Email address sent to
        - 'subject': Email subject
        - 'timestamp': Send attempt timestamp
        - 'status': 'SUCCESS' or 'FAILED'
        - 'message': Error message if failed
    
    Exceptions Caught:
    - SMTPAuthenticationError: Login credentials wrong
    - SMTPException: SMTP protocol errors
    - Exception: Any other error
    
    All failures are logged to email_log.txt.
    """
    
    metadata = {
        "recipient": receiver,
        "subject": subject,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": None,
        "message": None
    }

    if not EMAIL or not PASSWORD:
        error_msg = "EMAIL and PASSWORD environment variables are required"
        print(f"[FAILED] {error_msg}")
        metadata["status"] = "FAILED"
        metadata["message"] = error_msg
        log_email_send(receiver, subject, "[FAILED]", error_msg)
        return False, metadata
    
    # Validate receiver email
    if not validate_email(receiver):
        error_msg = f"Invalid email format: {receiver}"
        print(f"[FAILED] {error_msg}")
        metadata["status"] = "FAILED"
        metadata["message"] = error_msg
        log_email_send(receiver, subject, "[FAILED]", error_msg)
        return False, metadata
    
    # Validate subject and message
    if not subject.strip():
        error_msg = "Subject cannot be empty"
        print(f"[FAILED] {error_msg}")
        metadata["status"] = "FAILED"
        metadata["message"] = error_msg
        log_email_send(receiver, subject, "[FAILED]", error_msg)
        return False, metadata
    
    if not message.strip():
        error_msg = "Message cannot be empty"
        print(f"[FAILED] {error_msg}")
        metadata["status"] = "FAILED"
        metadata["message"] = error_msg
        log_email_send(receiver, subject, "[FAILED]", error_msg)
        return False, metadata

    email = EmailMessage()
    email["From"] = EMAIL
    email["To"] = receiver
    email["Subject"] = subject
    email.set_content(message)

    try:
        with smtplib.SMTP(SMTP_SERVER, PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, PASSWORD)
            smtp.send_message(email)

        metadata["status"] = "SUCCESS"
        print(f"[SUCCESS] Email sent to {receiver}")
        log_email_send(receiver, subject, "[SUCCESS]")
        return True, metadata

    except smtplib.SMTPAuthenticationError as e:
        error_msg = "Authentication failed. Check EMAIL and PASSWORD in .env"
        print(f"[FAILED] {error_msg}")
        metadata["status"] = "FAILED"
        metadata["message"] = error_msg
        log_email_send(receiver, subject, "[FAILED]", error_msg)
        return False, metadata
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Error: {str(e)}"
        print(f"[FAILED] {error_msg}")
        metadata["status"] = "FAILED"
        metadata["message"] = error_msg
        log_email_send(receiver, subject, "[FAILED]", error_msg)
        return False, metadata
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"[FAILED] {error_msg}")
        metadata["status"] = "FAILED"
        metadata["message"] = error_msg
        log_email_send(receiver, subject, "[FAILED]", error_msg)
        return False, metadata
