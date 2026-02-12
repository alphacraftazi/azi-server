
import sys
import os

# Add azi_server to path to allow imports
sys.path.append(os.path.join(os.getcwd(), 'azi_server'))

try:
    from azi_server.brain import tools_smtp
    print("Successfully imported tools_smtp")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Test Credentials
creds = tools_smtp.get_credentials_manual()
print(f"SMTP User: {creds.get('SMTP_USER')}")
print(f"SMTP Server: {creds.get('SMTP_SERVER')}")
print(f"SMTP Port: {creds.get('SMTP_PORT')}")
# Do not print password

if not creds.get('SMTP_USER') or not creds.get('SMTP_PASSWORD'):
    print("ERROR: SMTP Credentials missing in .env")
    sys.exit(1)

print("\nAttempting to send test email...")
try:
    # Send to the sender's own email for testing
    to_email = creds.get('SMTP_USER') 
    result = tools_smtp.send_email_smtp(
        to_email, 
        "AZI System Test", 
        "This is a test email from AZI diagnostic system."
    )
    print(f"Result: {result}")
except Exception as e:
    print(f"EXCEPTION: {e}")
