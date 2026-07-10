#!/usr/bin/env python3
"""SMTP sender for liv — send email via ProtonMail or other SMTP host.
Usage: python3 send_email.py --to "recipient@example.com" --subject "Hello" --body "Message here"
Or: cat message.txt | python3 send_email.py --to "recipient@example.com" --subject "Hello" --stdin
"""
import argparse, smtplib, ssl, sys, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Default config — override via env vars
SMTP_HOST = os.environ.get("SMTP_HOST", "127.0.0.1")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))  # ProtonMail Bridge default
SMTP_USER = os.environ.get("SMTP_USER", "hello@livtheagent.dev")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "hello@livtheagent.dev")

def send_email(to_addr, subject, body, html=False):
    if not SMTP_PASS:
        print("Error: SMTP_PASS not set.", file=sys.stderr)
        sys.exit(1)
    if not to_addr:
        print("Error: recipient required.", file=sys.stderr)
        sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"liv <{SMTP_FROM}>"
    msg["To"] = to_addr

    msg.attach(MIMEText(body, "html" if html else "plain"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=ctx)
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [to_addr], msg.as_string())
        print(f"Sent to {to_addr}: {subject}")
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send email from liv")
    parser.add_argument("--to", required=True, help="Recipient address")
    parser.add_argument("--subject", default="Message from liv", help="Email subject")
    parser.add_argument("--body", default=None, help="Message body")
    parser.add_argument("--stdin", action="store_true", help="Read body from stdin")
    parser.add_argument("--html", action="store_true", help="Body is HTML")
    args = parser.parse_args()

    body = args.body
    if args.stdin:
        body = sys.stdin.read()
    if not body:
        body = "(empty message)"

    send_email(args.to, args.subject, body, html=args.html)
