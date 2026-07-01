import json


def handler(event, context):
    # Import inside handler to avoid import-time failures when env is not set locally.
    try:
        from email_sender import send_email, validate_email
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Server configuration error: {str(e)}"}),
        }

    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    receiver = body.get("receiver")
    subject = body.get("subject")
    message = body.get("message")

    if not receiver or not subject or not message:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "receiver, subject, and message are required"}),
        }

    if not validate_email(receiver):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid receiver email address"}),
        }

    success, metadata = send_email(receiver, subject, message)
    if success:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "success", "recipient": receiver, "timestamp": metadata.get("timestamp")}),
        }

    return {
        "statusCode": 500,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "failure", "error": metadata.get("message")}),
    }
