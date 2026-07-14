import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.project_data import read_json_body, write_json_response


def _normalize_smtp_server(value):
    candidate = (value or "").strip()
    if not candidate:
        return "smtp.gmail.com"

    lowered = candidate.lower()
    if "@" in candidate or lowered.startswith("mailto:"):
        return "smtp.gmail.com"

    return candidate


def _is_gmail_address(email):
    lowered = (email or "").strip().lower()
    return lowered.endswith("@gmail.com") or lowered.endswith("@googlemail.com")


def _current_settings():
    email = os.getenv("EMAIL", "")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port = os.getenv("PORT", "587")

    if _is_gmail_address(email):
        smtp_server = "smtp.gmail.com"
        port = "587"

    return {
        "email": email,
        "smtpServer": smtp_server,
        "port": port,
        "configured": bool(email) and bool(os.getenv("PASSWORD")),
    }


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        write_json_response(self, 204, {})

    def do_GET(self):
        write_json_response(self, 200, _current_settings())

    def do_POST(self):
        try:
            body = read_json_body(self)
        except json.JSONDecodeError:
            write_json_response(self, 400, {"error": "Invalid JSON body"})
            return

        email = (body.get("email") or "").strip()
        password = (body.get("password") or "").strip()
        smtp_server = _normalize_smtp_server(body.get("smtpServer"))
        port = str((body.get("port") or "587")).strip() or "587"

        if _is_gmail_address(email):
            smtp_server = "smtp.gmail.com"
            port = "587"

        if not email or not password:
            write_json_response(self, 400, {"error": "EMAIL and PASSWORD are required to save settings"})
            return

        os.environ["EMAIL"] = email
        os.environ["PASSWORD"] = password
        os.environ["SMTP_SERVER"] = smtp_server
        os.environ["PORT"] = port

        write_json_response(
            self,
            200,
            {
                "status": "saved",
                "configured": True,
                "email": email,
                "smtpServer": smtp_server,
                "port": port,
            },
        )
