import csv
import json
import os
import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
CONTACTS_FILE = ROOT_DIR / "contacts.csv"
LOG_FILE = ROOT_DIR / "email_log.txt"
AUTO_REPLIES_FILE = ROOT_DIR / "auto_replies.json"
BLACKLIST_FILE = ROOT_DIR / "blacklist.json"

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
LOG_PATTERN = re.compile(
    r"^\[(?P<timestamp>[^\]]+)\]\s+\|\s+To:\s+(?P<recipient>.*?)\s+\|\s+Status:\s+(?P<status>.*?)\s+\|\s+Subject:\s+(?P<subject>.*?)(?:\s+\|\s+Message:\s+(?P<message>.*))?$"
)


def write_json_response(request, status_code, payload):
    request.send_response(status_code)
    request.send_header("Content-Type", "application/json")
    request.send_header("Access-Control-Allow-Origin", "*")
    request.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    request.send_header("Access-Control-Allow-Headers", "Content-Type")
    request.end_headers()

    if status_code != 204:
        request.wfile.write(json.dumps(payload).encode("utf-8"))


def read_json_body(request):
    content_length = int(request.headers.get("Content-Length", "0"))
    raw_body = request.rfile.read(content_length).decode("utf-8") if content_length else "{}"
    return json.loads(raw_body or "{}")


def validate_email_address(email):
    return bool(email and EMAIL_PATTERN.match(email))


def load_contacts():
    if not CONTACTS_FILE.exists():
        return []

    with CONTACTS_FILE.open("r", newline="", encoding="utf-8") as contact_file:
        reader = csv.DictReader(contact_file)
        contacts = []
        for row in reader:
            name = (row.get("name") or "").strip()
            email = (row.get("email") or "").strip()
            if email:
                contacts.append({"name": name or email.split("@")[0], "email": email})
        return contacts


def save_contacts(contacts):
    with CONTACTS_FILE.open("w", newline="", encoding="utf-8") as contact_file:
        writer = csv.DictWriter(contact_file, fieldnames=["name", "email"])
        writer.writeheader()
        writer.writerows(contacts)


def parse_log_line(line):
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return {
            "timestamp": "",
            "recipient": "",
            "status": "UNKNOWN",
            "subject": line.strip(),
            "message": "",
        }

    data = match.groupdict()
    status_text = data.get("status") or ""
    normalized_status = "SUCCESS" if "SUCCESS" in status_text.upper() else "FAILED" if "FAILED" in status_text.upper() else status_text
    return {
        "timestamp": data.get("timestamp") or "",
        "recipient": data.get("recipient") or "",
        "status": normalized_status,
        "subject": data.get("subject") or "",
        "message": data.get("message") or "",
    }


def load_logs(limit=30):
    if not LOG_FILE.exists():
        return {"total": 0, "success": 0, "failed": 0, "entries": []}

    with LOG_FILE.open("r", encoding="utf-8") as log_file:
        entries = [parse_log_line(line) for line in log_file if line.strip()]

    success = sum(1 for entry in entries if entry["status"] == "SUCCESS")
    failed = sum(1 for entry in entries if entry["status"] == "FAILED")
    return {
        "total": len(entries),
        "success": success,
        "failed": failed,
        "entries": entries[-limit:][::-1],
    }


def load_json_file(path, fallback):
    if not path.exists():
        return fallback

    with path.open("r", encoding="utf-8") as json_file:
        return json.load(json_file)


def save_json_file(path, payload):
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, indent=2)
        json_file.write("\n")


def load_auto_reply_data():
    replies = load_json_file(AUTO_REPLIES_FILE, {"auto_replies": []})
    blacklist = load_json_file(BLACKLIST_FILE, {"blacklisted_emails": []})
    return {
        "auto_replies": replies.get("auto_replies", []),
        "blacklisted_emails": blacklist.get("blacklisted_emails", []),
    }


def config_status():
    return {
        "emailConfigured": bool(os.getenv("EMAIL")),
        "passwordConfigured": bool(os.getenv("PASSWORD")),
        "smtpServer": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "port": os.getenv("PORT", "587"),
        "files": {
            "contacts": CONTACTS_FILE.exists(),
            "logs": LOG_FILE.exists(),
            "autoReplies": AUTO_REPLIES_FILE.exists(),
            "blacklist": BLACKLIST_FILE.exists(),
        },
    }
