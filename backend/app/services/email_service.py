import os
import base64
import requests


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_report_email(
    recipients: str,
    report_name: str,
    file_path: str,
):
    api_key = os.getenv("BREVO_API_KEY")
    smtp_from = os.getenv("SMTP_FROM")

    if not api_key:
        raise ValueError("BREVO_API_KEY is not configured")

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

    # Read and encode the report
    with open(file_path, "rb") as file:
        file_data = base64.b64encode(file.read()).decode("utf-8")

    file_name = os.path.basename(file_path)

    payload = {
        "sender": {
            "email": smtp_from,
            "name": "RetailPulse Analytics",
        },
        "to": [
            {
                "email": email,
            }
            for email in recipient_list
        ],
        "subject": f"{report_name} - Scheduled Report",
        "textContent": (
            f"Hello,\n\n"
            f"Your scheduled {report_name} has been generated successfully.\n\n"
            f"Please find the report attached.\n\n"
            f"Regards,\n"
            f"RetailPulse Analytics"
        ),
        "attachment": [
            {
                "content": file_data,
                "name": file_name,
            }
        ],
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    response = requests.post(
        BREVO_API_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )

    if not response.ok:
        raise RuntimeError(
            f"Brevo API error {response.status_code}: "
            f"{response.text}"
        )

    return response.json()