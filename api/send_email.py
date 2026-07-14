import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _write_json_response(request, status_code, payload):
    request.send_response(status_code)
    request.send_header("Content-Type", "application/json")
    request.send_header("Access-Control-Allow-Origin", "*")
    request.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    request.send_header("Access-Control-Allow-Headers", "Content-Type")
    request.end_headers()
    request.wfile.write(json.dumps(payload).encode("utf-8"))


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        _write_json_response(self, 204, {})

    def do_GET(self):
        _write_json_response(self, 200, {"status": "ok", "message": "Email API is running"})

    def do_POST(self):
        try:
            from email_sender import send_email, validate_email
        except Exception as exc:
            _write_json_response(self, 500, {"error": f"Server configuration error: {str(exc)}"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            _write_json_response(self, 400, {"error": "Invalid JSON body"})
            return

        receiver = body.get("receiver")
        subject = body.get("subject")
        message = body.get("message")

        if not receiver or not subject or not message:
            _write_json_response(self, 400, {"error": "receiver, subject, and message are required"})
            return

        if not validate_email(receiver):
            _write_json_response(self, 400, {"error": "Invalid receiver email address"})
            return

        success, metadata = send_email(receiver, subject, message)
        if success:
            _write_json_response(
                self,
                200,
                {
                    "status": "success",
                    "recipient": receiver,
                    "timestamp": metadata.get("timestamp"),
                },
            )
            return

        _write_json_response(self, 500, {"status": "failure", "error": metadata.get("message")})
