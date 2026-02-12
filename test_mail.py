import smtplib
import os
from dotenv import load_dotenv

# Load explicitly to ensure we get the latest file content
load_dotenv(override=True)

smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_user = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMTP_PASSWORD")

print(f"Testing connectivity to {smtp_server}:{smtp_port}...")
print(f"User: {smtp_user}")
print(f"Pass: {smtp_password[:2]}...{smtp_password[-2:]} (Length: {len(smtp_password)})")

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    print("TLS Start: OK")
    
    server.login(smtp_user, smtp_password)
    print("Login: SUCCESS!")
    server.quit()
except Exception as e:
    print(f"LOGIN FAILED: {type(e).__name__} - {e}")
