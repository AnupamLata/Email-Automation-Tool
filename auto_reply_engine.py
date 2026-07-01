"""Auto-Reply Engine Module - Match emails and send auto-replies

This module handles matching incoming emails to auto-reply rules,
checking blacklists, tracking replies, and sending automatic responses.

Features:
    - Load auto-reply rules from JSON
    - Load blacklisted emails from JSON
    - Track replied emails to avoid duplicates
    - Match email subject to reply rules
    - Send auto-replies via SMTP
    - Update reply tracking

Dependencies:
    - json: For loading configuration files
    - email_sender: For sending email replies
    - datetime: For tracking timestamps
"""

import json
import os
from datetime import datetime
from email_sender import send_email
from logger import log_email_send

class AutoReplyEngine:
    """Handles auto-reply matching and sending logic"""
    
    def __init__(self):
        """Initialize auto-reply engine and load configuration"""
        self.auto_replies_file = "auto_replies.json"
        self.blacklist_file = "blacklist.json"
        self.replied_file = "replied_emails.json"
        
        self.auto_replies = []
        self.blacklist = []
        self.replied_emails = []
        
        self.load_configs()
    
    def load_configs(self):
        """Load all configuration files (auto-replies, blacklist, replied tracking)
        
        Returns:
            bool: True if all configs loaded successfully
        """
        try:
            # Load auto-replies
            if os.path.exists(self.auto_replies_file):
                with open(self.auto_replies_file, 'r') as f:
                    data = json.load(f)
                    self.auto_replies = data.get("auto_replies", [])
                print(f"[SUCCESS] Loaded {len(self.auto_replies)} auto-reply rules")
            
            # Load blacklist
            if os.path.exists(self.blacklist_file):
                with open(self.blacklist_file, 'r') as f:
                    data = json.load(f)
                    self.blacklist = data.get("blacklisted_emails", [])
                print(f"[SUCCESS] Loaded {len(self.blacklist)} blacklisted emails")
            
            # Load replied emails tracking
            if os.path.exists(self.replied_file):
                with open(self.replied_file, 'r') as f:
                    data = json.load(f)
                    self.replied_emails = data.get("replied", [])
                print(f"[SUCCESS] Loaded {len(self.replied_emails)} tracked replies")
            
            return True
        
        except Exception as e:
            print(f"[FAILED] Error loading configs: {str(e)}")
            return False
    
    def is_blacklisted(self, sender_email):
        """Check if sender email is in blacklist
        
        Args:
            sender_email (str): Sender's email address
        
        Returns:
            bool: True if sender is blacklisted, False otherwise
        """
        return sender_email.lower() in [e.lower() for e in self.blacklist]
    
    def already_replied(self, sender_email):
        """Check if we've already replied to this sender
        
        Args:
            sender_email (str): Sender's email address
        
        Returns:
            bool: True if already replied, False otherwise
        """
        return sender_email.lower() in [e.lower() for e in self.replied_emails]
    
    def find_reply(self, subject):
        """Find matching auto-reply for email subject
        
        Performs keyword matching (case-insensitive) against configured auto-reply subjects.
        Checks if the rule keyword is contained ANYWHERE in the subject.
        
        This allows matching:
        - "Hello" → matches "Hello", "Re: Hello", "Re: Re: Hello", "Hello!", etc.
        - "Support" → matches "Support", "Re: Support", "Need Support", etc.
        
        Args:
            subject (str): Email subject line
        
        Returns:
            str: Reply message if match found, None otherwise
        
        Example:
            reply = engine.find_reply("Re: Hello")
            # Returns: "Hello! Thank you for reaching out..." (because "Hello" is in the subject)
        """
        subject_lower = subject.lower().strip()
        
        for rule in self.auto_replies:
            rule_keyword = rule.get("subject", "").lower().strip()
            # Check if rule keyword is contained in the subject (keyword matching)
            if rule_keyword and rule_keyword in subject_lower:
                return rule.get("reply_message", "")
        
        return None
    
    def send_auto_reply(self, sender_email, reply_message):
        """Send auto-reply to sender and track it
        
        Args:
            sender_email (str): Recipient's email address
            reply_message (str): Reply message to send
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            subject = "Auto-Reply"
            
            # Send the reply
            success, metadata = send_email(
                sender_email,
                subject,
                reply_message
            )
            
            if success:
                # Track this reply
                self.track_reply(sender_email)
                print(f"[SUCCESS] Auto-reply sent to {sender_email}")
                return True
            else:
                print(f"[FAILED] Could not send auto-reply to {sender_email}")
                return False
        
        except Exception as e:
            print(f"[FAILED] Error sending auto-reply: {str(e)}")
            return False
    
    def track_reply(self, sender_email):
        """Add sender to replied tracking list
        
        Args:
            sender_email (str): Email address to track
        """
        try:
            if sender_email.lower() not in [e.lower() for e in self.replied_emails]:
                self.replied_emails.append(sender_email)
            
            # Update replied_emails.json
            with open(self.replied_file, 'w') as f:
                json.dump(
                    {"replied": self.replied_emails},
                    f,
                    indent=2
                )
            
            print(f"[SUCCESS] Tracked reply to {sender_email}")
        
        except Exception as e:
            print(f"[FAILED] Error tracking reply: {str(e)}")
    
    def process_email(self, sender_email, subject):
        """Process incoming email and send auto-reply if applicable
        
        Complete workflow:
        1. Check if sender is blacklisted
        2. Check if already replied to sender
        3. Match subject to auto-reply rule
        4. Send reply if all checks pass
        
        Args:
            sender_email (str): Sender's email address
            subject (str): Email subject line
        
        Returns:
            tuple: (success: bool, message: str)
        
        Example:
            success, msg = engine.process_email("user@example.com", "Hello")
            if success:
                print(f"Auto-reply sent: {msg}")
        """
        # Extract email from "Name <email>" format
        if "<" in sender_email:
            sender_email = sender_email.split("<")[1].split(">")[0]
        
        # Check blacklist
        if self.is_blacklisted(sender_email):
            return False, f"Sender {sender_email} is blacklisted"
        
        # Check if already replied
        if self.already_replied(sender_email):
            return False, f"Already replied to {sender_email}"
        
        # Find matching reply
        reply = self.find_reply(subject)
        if not reply:
            return False, f"No matching reply for subject: {subject}"
        
        # Send auto-reply
        if self.send_auto_reply(sender_email, reply):
            return True, f"Auto-reply sent to {sender_email}"
        else:
            return False, f"Failed to send auto-reply to {sender_email}"
    
    def add_auto_reply(self, subject, message):
        """Add new auto-reply rule
        
        Args:
            subject (str): Subject to match
            message (str): Reply message
        
        Returns:
            bool: True if added successfully
        """
        try:
            self.auto_replies.append({
                "subject": subject,
                "reply_message": message
            })
            
            with open(self.auto_replies_file, 'w') as f:
                json.dump({"auto_replies": self.auto_replies}, f, indent=2)
            
            print(f"[SUCCESS] Added auto-reply for subject: {subject}")
            return True
        except Exception as e:
            print(f"[FAILED] Error adding auto-reply: {str(e)}")
            return False
    
    def add_blacklist(self, email):
        """Add email to blacklist
        
        Args:
            email (str): Email address to blacklist
        
        Returns:
            bool: True if added successfully
        """
        try:
            if email.lower() not in [e.lower() for e in self.blacklist]:
                self.blacklist.append(email)
                
                with open(self.blacklist_file, 'w') as f:
                    json.dump({"blacklisted_emails": self.blacklist}, f, indent=2)
                
                print(f"[SUCCESS] Added {email} to blacklist")
                return True
            else:
                print(f"[WARNING] {email} already in blacklist")
                return False
        except Exception as e:
            print(f"[FAILED] Error adding to blacklist: {str(e)}")
            return False
    
    def get_stats(self):
        """Get auto-reply statistics
        
        Returns:
            dict: Statistics dictionary with keys:
                - 'total_rules': Number of auto-reply rules
                - 'blacklisted': Number of blacklisted emails
                - 'replied': Number of tracked replies
        """
        return {
            "total_rules": len(self.auto_replies),
            "blacklisted": len(self.blacklist),
            "replied": len(self.replied_emails)
        }


# Example usage
if __name__ == "__main__":
    engine = AutoReplyEngine()
    
    # Process example email
    success, msg = engine.process_email("user@example.com", "Hello")
    print(f"\nResult: {msg}")
    
    # Get stats
    stats = engine.get_stats()
    print(f"\nStats: {stats}")
