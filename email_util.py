import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL


def send_winner_email(winner_name: str):
    sender_email = os.getenv("RPS_EMAIL")
    sender_pass = os.getenv("RPS_EMAIL_PASS")

    if not sender_email or not sender_pass:
        raise RuntimeError("Email credentials not set in environment variables")

    # For demo simplicity, send email to yourself
    receiver_email = sender_email

    msg = EmailMessage()
    msg["Subject"] = "🎉 Rock Paper Scissors - You Won!"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(
        f"Congratulations {winner_name}!\n\n"
        "You won the Rock Paper Scissors game.\n\n"
        "— RPS Network Game Server"
    )

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(sender_email, sender_pass)
            smtp.send_message(msg)
            print("Winner email sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)
