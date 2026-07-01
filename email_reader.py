"""Email Reader Module - Fetch emails from Gmail using IMAP

This module handles connecting to Gmail mailbox, fetching unread emails,
and extracting sender, subject, and body content.

Features:
    - Connect to Gmail IMAP server
    - Fetch unread emails (optionally from last N hours)
    - Parse email content (From, Subject, Body)
    - Handle IMAP connection errors
    - Return structured email data

Dependencies:
    - imaplib: IMAP client for Gmail
    - email: Standard library for parsing email messages
    - config: Application configuration (EMAIL, PASSWORD)
    - datetime: For time-based email filtering
"""

import imaplib
from email.parser import BytesParser
from email.policy import default
from datetime import datetime, timedelta
from config import EMAIL, PASSWORD

class EmailReader:
    """Handles reading emails from Gmail inbox using IMAP protocol"""
    
    def __init__(self):
        """Initialize email reader with Gmail credentials"""
        self.email = EMAIL
        self.password = PASSWORD
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.connection = None
    
    def connect(self):
        """Connect to Gmail IMAP server
        
        Returns:
            bool: True if connection successful, False otherwise
        
        Raises:
            imaplib.IMAP4.error: If connection fails
        """
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.email, self.password)
            print("[SUCCESS] Connected to Gmail IMAP")
            return True
        except imaplib.IMAP4.error as e:
            print(f"[FAILED] IMAP Connection Error: {str(e)}")
            return False
        except Exception as e:
            print(f"[FAILED] Unexpected error connecting to IMAP: {str(e)}")
            return False
    
    def disconnect(self):
        """Safely disconnect from IMAP server"""
        try:
            if self.connection:
                self.connection.close()
                self.connection.logout()
                print("[SUCCESS] Disconnected from Gmail IMAP")
        except Exception as e:
            print(f"[WARNING] Error disconnecting: {str(e)}")
    
    def fetch_unread_emails(self, hours_back=1):
        """Fetch unread emails from inbox (from last N hours)
        
        Optimized to fetch only recent unread emails to reduce processing time.
        Uses IMAP SINCE parameter to filter by date.
        
        Args:
            hours_back (int): Fetch emails from last N hours (default: 1 hour)
        
        Returns:
            list: List of email dicts with keys:
                - 'from': Sender email address
                - 'subject': Email subject
                - 'body': Email body content
                - 'uid': Email unique ID
        
        Example:
            emails = reader.fetch_unread_emails(hours_back=1)
            for email in emails:
                print(f"From: {email['from']}, Subject: {email['subject']}")
        """
        try:
            # Select inbox
            self.connection.select("INBOX")
            
            # Calculate date from N hours ago
            past_date = datetime.now() - timedelta(hours=hours_back)
            date_str = past_date.strftime("%d-%b-%Y")
            
            # Search for unread emails since the past date
            # This significantly reduces the number of emails to fetch
            status, email_ids = self.connection.search(None, "UNSEEN", "SINCE", date_str)
            
            if status != "OK":
                print("[WARNING] Could not search for unread emails")
                return []
            
            emails = []
            email_list = email_ids[0].split()
            
            if not email_list:
                print(f"[INFO] No unread emails from last {hours_back} hour(s)")
                return []
            
            print(f"[INFO] Found {len(email_list)} unread email(s) from last {hours_back} hour(s)")
            
            # Fetch each email
            for email_id in email_list:
                status, email_data = self.connection.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    continue
                
                # Parse email message
                msg = BytesParser(policy=default).parsebytes(email_data[0][1])
                
                email_dict = {
                    "from": msg.get("From", "Unknown"),
                    "subject": msg.get("Subject", "No Subject"),
                    "body": self._get_email_body(msg),
                    "uid": email_id.decode()
                }
                
                emails.append(email_dict)
            
            return emails
            
        except Exception as e:
            print(f"[FAILED] Error fetching emails: {str(e)}")
            return []
    
    def _get_email_body(self, msg):
        """Extract plain text body from email message
        
        Args:
            msg: Email message object
        
        Returns:
            str: Plain text email body
        """
        body = ""
        
        try:
            if msg.is_multipart():
                for part in msg.iter_parts():
                    if part.get_content_type() == "text/plain":
                        body = part.get_content()
                        break
            else:
                body = msg.get_content()
        except Exception as e:
            print(f"[WARNING] Error extracting email body: {str(e)}")
        
        return body.strip()
    
    def extract_sender_email(self, from_field):
        """Extract email address from 'From' field
        
        Args:
            from_field (str): Email 'From' field (e.g., "John Doe <john@example.com>")
        
        Returns:
            str: Email address only (e.g., "john@example.com")
        
        Example:
            email = reader.extract_sender_email("John Doe <john@example.com>")
            # Returns: "john@example.com"
        """
        try:
            if "<" in from_field and ">" in from_field:
                return from_field.split("<")[1].split(">")[0]
            else:
                return from_field
        except Exception:
            return from_field


# Example usage
if __name__ == "__main__":
    reader = EmailReader()
    if reader.connect():
        # Fetch unread emails from last 1 hour (default)
        emails = reader.fetch_unread_emails(hours_back=1)
        print(f"\n📧 Found {len(emails)} unread emails\n")
        
        for email in emails:
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print(f"Body Preview: {email['body'][:100]}...")
            print("-" * 50)
        
        reader.disconnect()
