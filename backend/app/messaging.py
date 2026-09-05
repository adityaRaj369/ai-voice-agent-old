from app.config import settings
from app.models import OutreachMessage


def build_whatsapp_body(name: str, role: str, company: str, location: str) -> str:
    return (
        f"Hi {name}, this is {company} hiring for {role} in {location}. "
        "A voice assistant may call you shortly. Reply YES if you are open to a 3-minute screening. "
        "Reply STOP to opt out."
    )


def build_email_body(name: str, role: str, company: str) -> str:
    return (
        f"Hello {name},\n\nWe matched your profile to {role} at {company}. "
        "Our voice hiring assistant will call to confirm interest and a few basic details.\n\n"
        "If this was a mistake, ignore this note.\n"
    )


def deliver_channel(channel: str, to_phone: str, to_email: str, body: str) -> str:
    """Attempt live send when credentials exist; otherwise log as simulated."""
    if channel == "whatsapp" and settings.twilio_account_sid and settings.twilio_auth_token:
        try:
            import httpx

            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
            from_number = settings.twilio_whatsapp_from
            httpx.post(
                url,
                auth=(settings.twilio_account_sid, settings.twilio_auth_token),
                data={"From": from_number, "To": f"whatsapp:{to_phone}", "Body": body},
                timeout=20,
            )
            return "sent"
        except Exception:
            return "simulated_failed_live"
    if channel == "email" and settings.smtp_host and to_email:
        try:
            import smtplib
            from email.message import EmailMessage

            msg = EmailMessage()
            msg["Subject"] = "Role match — brief screening call"
            msg["From"] = settings.smtp_from or settings.smtp_user
            msg["To"] = to_email
            msg.set_content(body)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
                smtp.starttls()
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(msg)
            return "sent"
        except Exception:
            return "simulated_failed_live"
    return "simulated"


def queue_message(db, campaign_id: int, candidate_id: int, channel: str, body: str, status: str) -> OutreachMessage:
    row = OutreachMessage(
        campaign_id=campaign_id,
        candidate_id=candidate_id,
        channel=channel,
        body=body,
        status=status,
    )
    db.add(row)
    return row
