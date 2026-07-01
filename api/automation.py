import json
from http.server import BaseHTTPRequestHandler

from api.project_data import (
    AUTO_REPLIES_FILE,
    BLACKLIST_FILE,
    load_auto_reply_data,
    load_json_file,
    read_json_body,
    save_json_file,
    validate_email_address,
    write_json_response,
)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        write_json_response(self, 204, {})

    def do_GET(self):
        try:
            write_json_response(self, 200, load_auto_reply_data())
        except Exception as exc:
            write_json_response(self, 500, {"error": str(exc)})

    def do_POST(self):
        try:
            body = read_json_body(self)
        except json.JSONDecodeError:
            write_json_response(self, 400, {"error": "Invalid JSON body"})
            return

        action = body.get("action")

        try:
            if action == "add_reply":
                subject = (body.get("subject") or "").strip()
                reply_message = (body.get("reply_message") or "").strip()

                if not subject or not reply_message:
                    write_json_response(self, 400, {"error": "Subject and reply message are required"})
                    return

                payload = load_json_file(AUTO_REPLIES_FILE, {"auto_replies": []})
                payload.setdefault("auto_replies", []).append({"subject": subject, "reply_message": reply_message})
                save_json_file(AUTO_REPLIES_FILE, payload)
                write_json_response(self, 201, load_auto_reply_data())
                return

            if action == "add_blacklist":
                email = (body.get("email") or "").strip()
                if not validate_email_address(email):
                    write_json_response(self, 400, {"error": "Enter a valid email address"})
                    return

                payload = load_json_file(BLACKLIST_FILE, {"blacklisted_emails": []})
                emails = payload.setdefault("blacklisted_emails", [])
                if email.lower() not in [item.lower() for item in emails]:
                    emails.append(email)
                    save_json_file(BLACKLIST_FILE, payload)

                write_json_response(self, 201, load_auto_reply_data())
                return

            write_json_response(self, 400, {"error": "Unknown automation action"})
        except Exception as exc:
            write_json_response(self, 500, {"error": str(exc)})
