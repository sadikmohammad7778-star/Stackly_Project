import os
import smtplib
from email.message import EmailMessage


def send_report_email(
    recipients: str,
    report_name: str,
    file_path: str,
):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM")

    if not smtp_host:
        raise ValueError("SMTP_HOST is not configured")

    if not smtp_username:
        raise ValueError("SMTP_USERNAME is not configured")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is not configured")

    if not smtp_from:
        raise ValueError("SMTP_FROM is not configured")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"Report file not found: {file_path}"
        )

    recipient_list = [
        email.strip()
        for email in recipients.split(",")
        if email.strip()
    ]

    if not recipient_list:
        raise ValueError("No valid recipients configured")

    message = EmailMessage()

    message["Subject"] = f"{report_name} - Scheduled Report"
    message["From"] = smtp_from
    message["To"] = ", ".join(recipient_list)

    message.set_content(
        f"Hello,\n\n"
        f"Your scheduled {report_name} has been generated successfully.\n\n"
        f"Please find the report attached.\n\n"
        f"Regards,\n"
        f"RetailPulse Analytics"
    )

    with open(file_path, "rb") as file:
        file_data = file.read()

    file_name = os.path.basename(file_path)

    if file_name.lower().endswith(".pdf"):
        maintype = "application"
        subtype = "pdf"
    elif file_name.lower().endswith(".csv"):
        maintype = "text"
        subtype = "csv"
    else:
        maintype = "application"
        subtype = "octet-stream"

    message.add_attachment(
        file_data,
        maintype=maintype,
        subtype=subtype,
        filename=file_name,
    )

    with smtplib.SMTP(
        smtp_host,
        smtp_port,
        timeout=30,
    ) as server:
        server.starttls()
        server.login(
            smtp_username,
            smtp_password,
        )
        server.send_message(message)