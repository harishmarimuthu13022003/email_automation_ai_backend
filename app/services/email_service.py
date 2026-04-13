import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from imap_tools import MailBox, AND
from ..core.config import settings
import os

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str, attachment_path: str = None, reply_to_id: str = None):
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.FINANCE_EMAIL
            msg['To'] = to_email
            
            # Formatting as a "Reply" if an ID is provided
            if reply_to_id:
                msg['Subject'] = f"Re: {subject}" if not subject.lower().startswith("re:") else subject
                msg['In-Reply-To'] = reply_to_id
                msg['References'] = reply_to_id
            else:
                msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                    msg.attach(part)

            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.FINANCE_EMAIL, settings.EMAIL_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    def fetch_emails():
        emails = []
        try:
            print(f"Connecting to IMAP: {settings.IMAP_SERVER}...")
            # Use 'seen=False' to only get unread emails
            mailbox = MailBox(settings.IMAP_SERVER)
            print(f"📡 IMAP: Attempting login for {settings.FINANCE_EMAIL}...")
            mailbox.login(settings.FINANCE_EMAIL, settings.EMAIL_PASSWORD)
            print("✅ IMAP: Connection Successful!")
            with mailbox:
                for msg in mailbox.fetch(AND(seen=False), limit=20, reverse=True): 
                    # 🛡️ LAYER 1: Ignore emails sent by the Bot itself
                    if msg.from_.lower() == settings.FINANCE_EMAIL.lower():
                        continue
                        
                    # Safely get Message-ID from headers
                    msg_id = msg.headers.get('message-id', [None])[0]
                    
                    emails.append({
                        "id": msg.uid,
                        "message_id": msg_id, 
                        "subject": msg.subject,
                        "sender": msg.from_,
                        "body": msg.text or msg.html,
                        "date": msg.date
                    })
                    
                    # 🛡️ LAYER 2: Mark as SEEN so it won't be fetched next time
                    mailbox.flag(msg.uid, r'\Seen', True)
                    
            return emails
        except Exception as e:
            print(f"CRITICAL ERROR FETCHING: {e}")
            return []
