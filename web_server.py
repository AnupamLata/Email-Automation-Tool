from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from mimetypes import guess_type
from pathlib import Path
import os
import json

from api.project_data import (
    AUTO_REPLIES_FILE,
    BLACKLIST_FILE,
    CONTACTS_FILE,
    LOG_FILE,
    config_status,
    load_auto_reply_data,
    load_contacts,
    load_json_file,
    load_logs,
    read_json_body,
    save_contacts,
    save_json_file,
    validate_email_address,
    write_json_response,
)

ROOT_DIR = Path(__file__).resolve().parent
STATIC_DIR = ROOT_DIR / "static"
INDEX_FILE = ROOT_DIR / "index.html"
ENV_FILE = ROOT_DIR / ".env"


def _send_file(request, path):
    if not path.exists() or not path.is_file():
        request.send_response(404)
        request.end_headers()
        request.wfile.write(b"Not Found")
        return

    content_type, _ = guess_type(str(path))
    request.send_response(200)
    request.send_header("Content-Type", content_type or "application/octet-stream")
    request.send_header("Access-Control-Allow-Origin", "*")
    request.end_headers()
    request.wfile.write(path.read_bytes())


def _write_error(request, status_code, message):
    write_json_response(request, status_code, {"error": message})


def _read_env_values():
    values = {}
    if not ENV_FILE.exists():
        return values

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _write_env_values(values):
    lines = [
        "# Email Configuration",
        "# Saved from the web dashboard",
        f"EMAIL={values['EMAIL']}",
        f"PASSWORD={values['PASSWORD']}",
        f"SMTP_SERVER={values['SMTP_SERVER']}",
        f"PORT={values['PORT']}",
        "",
    ]
    ENV_FILE.write_text("\n".join(lines), encoding="utf-8")


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


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        write_json_response(self, 204, {})

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            _send_file(self, INDEX_FILE)
            return

        if self.path.startswith("/static/"):
            _send_file(self, ROOT_DIR / self.path.lstrip("/"))
            return

        if self.path == "/api/status":
            try:
                logs = load_logs()
                automation = load_auto_reply_data()
                write_json_response(
                    self,
                    200,
                    {
                        "config": config_status(),
                        "counts": {
                            "contacts": len(load_contacts()),
                            "logs": logs["total"],
                            "success": logs["success"],
                            "failed": logs["failed"],
                            "autoReplies": len(automation["auto_replies"]),
                            "blacklist": len(automation["blacklisted_emails"]),
                        },
                    },
                )
            except Exception as exc:
                _write_error(self, 500, str(exc))
            return

        if self.path == "/api/contacts":
            try:
                write_json_response(self, 200, {"contacts": load_contacts()})
            except Exception as exc:
                _write_error(self, 500, str(exc))
            return

        if self.path == "/api/logs":
            try:
                write_json_response(self, 200, load_logs())
            except Exception as exc:
                _write_error(self, 500, str(exc))
            return

        if self.path == "/api/automation":
            try:
                write_json_response(self, 200, load_auto_reply_data())
            except Exception as exc:
                _write_error(self, 500, str(exc))
            return

        if self.path == "/api/send_email":
            write_json_response(self, 200, {"status": "ok", "message": "Email API is running"})
            return

        if self.path == "/api/settings":
            current = _read_env_values()
            email = current.get("EMAIL", "")
            smtp_server = current.get("SMTP_SERVER", "smtp.gmail.com")
            port = current.get("PORT", "587")

            if _is_gmail_address(email):
                smtp_server = "smtp.gmail.com"
                port = "587"

            write_json_response(
                self,
                200,
                {
                    "email": email,
                    "smtpServer": smtp_server,
                    "port": port,
                    "configured": bool(email) and bool(current.get("PASSWORD")),
                },
            )
            return

        _send_file(self, INDEX_FILE)

    def do_POST(self):
        if self.path == "/api/send_email":
            try:
                from email_sender import send_email, validate_email
            except Exception as exc:
                _write_error(self, 500, f"Server configuration error: {str(exc)}")
                return

            try:
                body = read_json_body(self)
            except json.JSONDecodeError:
                _write_error(self, 400, "Invalid JSON body")
                return

            receiver = (body.get("receiver") or "").strip()
            subject = (body.get("subject") or "").strip()
            message = (body.get("message") or "").strip()

            if not receiver or not subject or not message:
                _write_error(self, 400, "receiver, subject, and message are required")
                return

            if not validate_email(receiver):
                _write_error(self, 400, "Invalid receiver email address")
                return

            success, metadata = send_email(receiver, subject, message)
            if success:
                write_json_response(
                    self,
                    200,
                    {
                        "status": "success",
                        "recipient": receiver,
                        "timestamp": metadata.get("timestamp"),
                    },
                )
                return

            _write_error(self, 500, metadata.get("message") or "Failed to send email")
            return

        if self.path == "/api/contacts":
            try:
                body = read_json_body(self)
            except json.JSONDecodeError:
                _write_error(self, 400, "Invalid JSON body")
                return

            name = (body.get("name") or "").strip()
            email = (body.get("email") or "").strip()

            if not validate_email_address(email):
                _write_error(self, 400, "Enter a valid email address")
                return

            contacts = load_contacts()
            if any(contact["email"].lower() == email.lower() for contact in contacts):
                _write_error(self, 409, "This contact already exists")
                return

            contact = {"name": name or email.split("@")[0], "email": email}
            contacts.append(contact)
            save_contacts(contacts)
            write_json_response(self, 201, {"contact": contact, "contacts": contacts})
            return

        if self.path == "/api/bulk_send":
            try:
                from email_sender import send_email
            except Exception as exc:
                _write_error(self, 500, f"Server configuration error: {str(exc)}")
                return

            try:
                body = read_json_body(self)
            except json.JSONDecodeError:
                _write_error(self, 400, "Invalid JSON body")
                return

            subject = (body.get("subject") or "").strip()
            message = (body.get("message") or "").strip()
            requested_recipients = body.get("recipients")

            if not subject or not message:
                _write_error(self, 400, "Subject and message are required")
                return

            contacts = load_contacts()
            if isinstance(requested_recipients, list) and requested_recipients:
                requested = {email.lower() for email in requested_recipients}
                contacts = [contact for contact in contacts if contact["email"].lower() in requested]

            contacts = [contact for contact in contacts if validate_email_address(contact["email"])]
            if not contacts:
                _write_error(self, 400, "No valid contacts found")
                return

            results = []
            for contact in contacts:
                success, metadata = send_email(contact["email"], subject, message)
                results.append(
                    {
                        "name": contact.get("name", ""),
                        "email": contact["email"],
                        "success": success,
                        "message": metadata.get("message") or "Sent",
                        "timestamp": metadata.get("timestamp"),
                    }
                )

            sent = sum(1 for result in results if result["success"])
            failed = len(results) - sent
            write_json_response(
                self,
                200 if sent else 500,
                {"status": "complete", "sent": sent, "failed": failed, "total": len(results), "results": results},
            )
            return

        if self.path == "/api/automation":
            try:
                body = read_json_body(self)
            except json.JSONDecodeError:
                _write_error(self, 400, "Invalid JSON body")
                return

            action = body.get("action")

            try:
                if action == "add_reply":
                    subject = (body.get("subject") or "").strip()
                    reply_message = (body.get("reply_message") or "").strip()

                    if not subject or not reply_message:
                        _write_error(self, 400, "Subject and reply message are required")
                        return

                    payload = load_json_file(AUTO_REPLIES_FILE, {"auto_replies": []})
                    payload.setdefault("auto_replies", []).append({"subject": subject, "reply_message": reply_message})
                    save_json_file(AUTO_REPLIES_FILE, payload)
                    write_json_response(self, 201, load_auto_reply_data())
                    return

                if action == "add_blacklist":
                    email = (body.get("email") or "").strip()
                    if not validate_email_address(email):
                        _write_error(self, 400, "Enter a valid email address")
                        return

                    payload = load_json_file(BLACKLIST_FILE, {"blacklisted_emails": []})
                    emails = payload.setdefault("blacklisted_emails", [])
                    if email.lower() not in [item.lower() for item in emails]:
                        emails.append(email)
                        save_json_file(BLACKLIST_FILE, payload)

                    write_json_response(self, 201, load_auto_reply_data())
                    return

                _write_error(self, 400, "Unknown automation action")
            except Exception as exc:
                _write_error(self, 500, str(exc))
            return

        if self.path == "/api/settings":
            try:
                body = read_json_body(self)
            except json.JSONDecodeError:
                _write_error(self, 400, "Invalid JSON body")
                return

            email = (body.get("email") or "").strip()
            password = (body.get("password") or "").strip()
            smtp_server = _normalize_smtp_server(body.get("smtpServer"))
            port = str((body.get("port") or "587")).strip() or "587"

            if _is_gmail_address(email):
                smtp_server = "smtp.gmail.com"
                port = "587"

            current = _read_env_values()
            if not password:
                password = current.get("PASSWORD", "")

            if not email or not password:
                _write_error(self, 400, "EMAIL and PASSWORD are required to save settings")
                return

            _write_env_values(
                {
                    "EMAIL": email,
                    "PASSWORD": password,
                    "SMTP_SERVER": smtp_server,
                    "PORT": port,
                }
            )

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
            return

        _write_error(self, 404, "Not found")

    def do_DELETE(self):
        if self.path == "/api/logs":
            try:
                if LOG_FILE.exists():
                    LOG_FILE.unlink()
                write_json_response(self, 200, {"status": "cleared", "total": 0, "success": 0, "failed": 0, "entries": []})
            except Exception as exc:
                _write_error(self, 500, str(exc))
            return

        _write_error(self, 404, "Not found")


def main():
    port = int(os.getenv("WEB_PORT", os.getenv("PORT", "8001")))
    server = ThreadingHTTPServer(("", port), handler)
    print(f"Serving Email Automation System on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
