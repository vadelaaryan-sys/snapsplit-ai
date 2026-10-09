"""
send_action.py - Multi-channel action tool dispatcher for SnapSplit
Supports:
1. Gmail (SMTP)
2. Telegram (Bot API)
3. WhatsApp (Twilio / Webhook API)
4. Demo / Simulator mode
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

def send_email(to_address, subject, body, gmail_address, gmail_app_password):
    """
    Sends an email using Gmail SMTP_SSL.
    """
    if not gmail_address or not gmail_app_password:
        return False, "Gmail credentials (GMAIL_ADDRESS & GMAIL_APP_PASSWORD) are not set."
    
    try:
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = gmail_address
        message["To"] = to_address
        
        # Attach plain text
        message.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(gmail_address, gmail_app_password)
            server.send_message(message)
            
        return True, f"Email successfully sent to {to_address}!"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


def send_telegram(chat_id, text, bot_token):
    """
    Sends a message via Telegram Bot API using HTTP requests.
    """
    if not bot_token or not chat_id:
        return False, "Telegram Bot Token or Chat ID missing."
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        res_json = response.json()
        
        if res_json.get("ok"):
            return True, f"Telegram message sent to chat_id {chat_id}!"
        else:
            description = res_json.get("description", "Unknown error")
            return False, f"Telegram API error: {description}"
    except Exception as e:
        return False, f"Failed to send Telegram message: {str(e)}"


def send_whatsapp(to_number, text, twilio_sid, twilio_token, twilio_from):
    """
    Sends a WhatsApp message using Twilio API via requests.
    """
    if not twilio_sid or not twilio_token or not twilio_from:
        return False, "Twilio WhatsApp credentials missing."
    
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
        
        from_str = twilio_from if twilio_from.startswith("whatsapp:") else f"whatsapp:{twilio_from}"
        to_str = to_number if to_number.startswith("whatsapp:") else f"whatsapp:{to_number}"
        
        payload = {
            "From": from_str,
            "To": to_str,
            "Body": text
        }
        
        response = requests.post(url, data=payload, auth=(twilio_sid, twilio_token), timeout=10)
        res_json = response.json()
        
        if response.status_code in [200, 201]:
            return True, f"WhatsApp message sent to {to_number}!"
        else:
            message = res_json.get("message", "Twilio error")
            return False, f"Twilio API error ({response.status_code}): {message}"
    except Exception as e:
        return False, f"Failed to send WhatsApp message: {str(e)}"
