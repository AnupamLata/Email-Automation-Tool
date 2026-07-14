import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.project_data import (
    load_contacts,
    read_json_body,
    save_contacts,
    validate_email_address,
    write_json_response,
)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        write_json_response(self, 204, {})

    def do_GET(self):
        try:
            write_json_response(self, 200, {"contacts": load_contacts()})
        except Exception as exc:
            write_json_response(self, 500, {"error": str(exc)})

    def do_POST(self):
        try:
            body = read_json_body(self)
        except json.JSONDecodeError:
            write_json_response(self, 400, {"error": "Invalid JSON body"})
            return

        name = (body.get("name") or "").strip()
        email = (body.get("email") or "").strip()

        if not validate_email_address(email):
            write_json_response(self, 400, {"error": "Enter a valid email address"})
            return

        contacts = load_contacts()
        if any(contact["email"].lower() == email.lower() for contact in contacts):
            write_json_response(self, 409, {"error": "This contact already exists"})
            return

        contact = {"name": name or email.split("@")[0], "email": email}
        contacts.append(contact)
        save_contacts(contacts)
        write_json_response(self, 201, {"contact": contact, "contacts": contacts})
