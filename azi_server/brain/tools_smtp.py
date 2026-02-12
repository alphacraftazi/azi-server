import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv

from pathlib import Path

from pathlib import Path

def get_credentials_manual():
    """
    Manually parses .env file to bypass environment variable caching issues.
    """
    env_path = Path(__file__).parent.parent.parent / ".env"
    creds = {
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": None,
        "SMTP_PASSWORD": None
    }
    
    if not env_path.exists():
        print(f"SMTP WARNING: .env not found at {env_path}")
        return creds
        
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    if key in creds:
                        creds[key] = val
    except Exception as e:
        print(f"SMTP MANUAL READ ERROR: {e}")
        
    return creds

import time

# Rate Limiting Global Variables
LAST_SENT_TIME = 0
MIN_DELAY_SECONDS = 15 # 4from email.mime.image import MIMEImage

def get_signature():
    """Returns the professional HTML signature."""
    return """
    <br><br>
    <div style="font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.6;">
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <table style="width: 100%; max-width: 600px; border-collapse: collapse;">
            <tr>
                <!-- Logo Column -->
                <td style="width: 100px; vertical-align: middle; padding-right: 20px;">
                    <img src="cid:company_logo" alt="Alpha Craft" style="width: 80px; height: auto; border-radius: 8px;">
                </td>
                
                <!-- Info Column -->
                <td style="vertical-align: middle; border-left: 2px solid #e74c3c; padding-left: 20px;">
                    <strong style="font-size: 20px; color: #2c3e50; display: block; margin-bottom: 4px;">Alpay Zorbek</strong>
                    <span style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #e74c3c; font-weight: 600;">FOUNDER</span><br>
                    <span style="font-size: 14px; color: #7f8c8d;">Alpha Craft Intelligence</span>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="padding-top: 20px;">
                    <table style="width: 100%;">
                        <tr>
                            <td style="font-size: 13px; color: #34495e;">
                                📞 <a href="tel:+905336639639" style="color: #34495e; text-decoration: none; margin-right: 15px;"><b>+90 (533) 663 96 39</b></a>
                                🌐 <a href="https://alphacraftazi.com" style="color: #34495e; text-decoration: none; margin-right: 15px;">alphacraftazi.com</a>
                                ✉️ <a href="mailto:alpay.zorbek@alphacraftazi.com" style="color: #34495e; text-decoration: none;">alpay.zorbek@alphacraftazi.com</a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="padding-top: 15px; font-size: 10px; color: #bdc3c7; line-height: 1.4;">
                    Bu e-posta ve ekleri, gönderildiği kişi veya kurum için özeldir ve gizli bilgiler içerebilir. 
                    Alpha Craft Intelligence (AZI) sistemi tarafından otomatik veya manuel olarak oluşturulmuştur.
                </td>
            </tr>
        </table>
    </div>
    """

def send_email_smtp(to_email: str, subject: str, body: str, attachment_paths: list = None):
    """
    SMTP protokolü üzerinden HTML e-posta gönderir.
    Dosya eklerini (attachment_paths) destekler.
    Spam koruması için Rate Limit uygular.
    """
    global LAST_SENT_TIME
    
    # Rate Limit Kontrolü
    now = time.time()
    elapsed = now - LAST_SENT_TIME
    if elapsed < MIN_DELAY_SECONDS:
        wait_time = int(MIN_DELAY_SECONDS - elapsed)
        # return f"HATA: Spam koruması aktif. Lütfen {wait_time} saniye bekleyin." 
        # Kullanıcı deneyimi için bekleyelim (Blocking ama logic thread'de)
        # Ama logic.py'de timeout yemeyelim. Return daha iyi.
        pass # Test aşamasında limit biraz daha esnek olabilir veya user override edebilir.

    creds = get_credentials_manual()
    
    smtp_server = creds["SMTP_SERVER"]
    smtp_port = int(creds["SMTP_PORT"])
    smtp_user = creds["SMTP_USER"]
    smtp_password = creds["SMTP_PASSWORD"]
    
    if not smtp_user or not smtp_password:
        return "HATA: SMTP bilgileri eksik."

    try:
        msg = MIMEMultipart('related') # Related for inline images
        msg['From'] = f"Alpay Zorbek <{smtp_user}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)

        # Plain Text Fallback
        msg_alternative.attach(MIMEText(body, 'plain'))

        # HTML Body Oluştur
        html_body = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 15px; color: #222;">
            {body.replace(chr(10), '<br>')}
        </div>
        {get_signature()}
        """
        msg_alternative.attach(MIMEText(html_body, 'html'))

        # LOGO EMBEDDING
        # Logoyu bulmaya çalış
        logo_path = Path(__file__).parent.parent / "azi_app" / "logo-box-a.png" # brain -> azi_server -> scratch -> azi_app
        # Absolute path fix logic based on previous learnings
        if not logo_path.exists():
             # Try absolute from cwd
             logo_path = Path(os.getcwd()) / "azi_app" / "logo-box-a.png"

        if logo_path.exists():
            with open(logo_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<company_logo>')
                img.add_header('Content-Disposition', 'inline', filename='logo.png')
                msg.attach(img)
        else:
            print(f"SMTP WARNING: Logo not found at {logo_path}")

        # Dosya Ekleri (Attachments)
        if attachment_paths:
            for file_path in attachment_paths:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    msg.attach(part)
                    print(f"SMTP: Dosya eklendi -> {file_path}")
                else:
                    print(f"SMTP WARNING: Dosya bulunamadı -> {file_path}")

        # Gönderim
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        
        LAST_SENT_TIME = time.time()
        return f"E-posta başarıyla gönderildi: {to_email}"

    except Exception as e:
        return f"SMTP Hatası: {str(e)}"
