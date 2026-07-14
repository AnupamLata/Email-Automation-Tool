import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.project_data import LOG_FILE, load_logs, write_json_response


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        write_json_response(self, 204, {})

    def do_GET(self):
        try:
            write_json_response(self, 200, load_logs())
        except Exception as exc:
            write_json_response(self, 500, {"error": str(exc)})

    def do_DELETE(self):
        try:
            if LOG_FILE.exists():
                LOG_FILE.unlink()
            write_json_response(self, 200, {"status": "cleared", "total": 0, "success": 0, "failed": 0, "entries": []})
        except Exception as exc:
            write_json_response(self, 500, {"error": str(exc)})
