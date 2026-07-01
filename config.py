import os
from pathlib import Path

try:
	from dotenv import load_dotenv
except ImportError:
	def load_dotenv():
		return None

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
PORT = int(os.getenv("PORT", 587))

