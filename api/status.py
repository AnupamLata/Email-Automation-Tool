from http.server import BaseHTTPRequestHandler

from api.project_data import config_status, load_auto_reply_data, load_contacts, load_logs, write_json_response


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        write_json_response(self, 204, {})

    def do_GET(self):
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
            write_json_response(self, 500, {"error": str(exc)})
