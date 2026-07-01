import json
from http.server import BaseHTTPRequestHandler

from api.project_data import load_contacts, read_json_body, validate_email_address, write_json_response


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        write_json_response(self, 204, {})

    def do_POST(self):
        try:
            from email_sender import send_email
        except Exception as exc:
            write_json_response(self, 500, {"error": f"Server configuration error: {str(exc)}"})
            return

        try:
            body = read_json_body(self)
        except json.JSONDecodeError:
            write_json_response(self, 400, {"error": "Invalid JSON body"})
            return

        subject = (body.get("subject") or "").strip()
        message = (body.get("message") or "").strip()
        requested_recipients = body.get("recipients")

        if not subject or not message:
            write_json_response(self, 400, {"error": "Subject and message are required"})
            return

        contacts = load_contacts()
        if isinstance(requested_recipients, list) and requested_recipients:
            requested = {email.lower() for email in requested_recipients}
            contacts = [contact for contact in contacts if contact["email"].lower() in requested]

        contacts = [contact for contact in contacts if validate_email_address(contact["email"])]
        if not contacts:
            write_json_response(self, 400, {"error": "No valid contacts found"})
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
        status_code = 200 if sent else 500
        write_json_response(
            self,
            status_code,
            {"status": "complete", "sent": sent, "failed": failed, "total": len(results), "results": results},
        )
