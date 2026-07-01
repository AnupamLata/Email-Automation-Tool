#!/usr/bin/env python3
"""
Interactive Setup Script for Email Automation Tool
Guides user through Gmail credential setup
"""

import os
import sys
from getpass import getpass

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def setup_gmail():
    """Setup Gmail credentials interactively"""
    clear_screen()
    
    print_header("📧 EMAIL AUTOMATION TOOL - SETUP WIZARD")
    
    print("This wizard will help you setup Gmail credentials.")
    print("\nBefore continuing, make sure you have:")
    print("  1. A Gmail account")
    print("  2. 2-Step Verification enabled on your account")
    print("  3. An App Password generated\n")
    
    print("To generate App Password:")
    print("  1. Go to: https://myaccount.google.com")
    print("  2. Click 'Security' in left menu")
    print("  3. Enable '2-Step Verification' (if not done)")
    print("  4. Find 'App passwords' option")
    print("  5. Select 'Mail' and 'Windows Computer'")
    print("  6. Copy the 16-character password\n")
    
    input("Press Enter when you're ready to continue...")
    clear_screen()
    
    # Get email
    print_header("Step 1: Enter Your Gmail Address")
    while True:
        email = input("Enter your Gmail address (example: aniket@gmail.com): ").strip()
        if "@gmail.com" in email and email.count("@") == 1:
            break
        print("Invalid email! Must be a Gmail address (example@gmail.com)")
    
    # Get password
    print("\n" + "=" * 60)
    print("  Step 2: Enter Your App Password")
    print("=" * 60 + "\n")
    print("Enter the 16-character App Password (it won't be displayed):")
    
    while True:
        password = getpass("App Password: ").strip()
        if len(password) > 5:  # Basic validation
            break
        print("Password seems too short. Please try again.")
    
    # Confirm
    clear_screen()
    print_header("Confirm Your Settings")
    print(f"Email:    {email}")
    print(f"Password: {'*' * len(password)}")
    print("SMTP:     smtp.gmail.com")
    print("Port:     587")
    
    confirm = input("\nIs this correct? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("Setup cancelled.")
        return False
    
    # Write .env file
    try:
        env_content = f"""EMAIL={email}
PASSWORD={password}
SMTP_SERVER=smtp.gmail.com
PORT=587
"""
        with open(".env", "w") as f:
            f.write(env_content)
        
        clear_screen()
        print_header("✓ Setup Complete!")
        print("Your .env file has been created successfully.")
        print("\nYou can now run the application:")
        print("  python main.py")
        print("\nYour credentials are stored securely in .env")
        print("(This file is NOT shared in version control)")
        
        return True
        
    except Exception as e:
        print(f"Error writing .env file: {e}")
        return False

def main():
    """Main setup function"""
    try:
        if setup_gmail():
            print("\n" + "=" * 60)
            print("Ready to use Email Automation Tool!")
            print("=" * 60)
            return 0
        else:
            return 1
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
