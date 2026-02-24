import os
import mimetypes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # /app
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))

def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachments: list[str] | None = None,
) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM") or os.getenv("FROM_EMAIL") or smtp_user

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass, from_email]):
        print("[email] SMTP not configured. Skipping email send.")
        return

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    attachments = attachments or []
    for path in attachments:
        if not path or not os.path.exists(path):
            print(f"[email] Attachment missing: {path}")
            continue

        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        with open(path, "rb") as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(path)}"')
            msg.attach(part)

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port), timeout=25) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"[email] Email sent to {to_email}")
    except Exception as e:
        print(f"[email] Failed to send email: {e}")

def maybe_send_email(to_email: str, subject: str, body: str, attachments: list[str] | None = None) -> None:
    if not to_email or not to_email.strip():
        return
    send_email(to_email.strip(), subject, body, attachments=attachments)
