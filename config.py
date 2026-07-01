import os

try:
	from dotenv import load_dotenv
except ImportError:
	def load_dotenv():
		return None

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
PORT = int(os.getenv("PORT", 587))

