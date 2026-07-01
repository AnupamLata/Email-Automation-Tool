import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
PORT = int(os.getenv("PORT", 587))

# Validate configuration
if not EMAIL or not PASSWORD:
    raise ValueError("❌ EMAIL and PASSWORD environment variables are required. Create a .env file with your credentials.")

