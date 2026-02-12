from googleapiclient.discovery import build
from . import auth
import datetime
import base64
from email.mime.text import MIMEText

def get_service(service_name, version):
    """Google servisine bağlanır."""
    creds = auth.authenticate_google()
    if not creds:
        return None
    return build(service_name, version, credentials=creds)

def get_unread_emails(count=5):
    """Okunmamış e-postaları getirir."""
    try:
        service = get_service('gmail', 'v1')
        if not service: return "Google bağlantısı kurulamadı."
        
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread", maxResults=count).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return "Okunmamış e-posta yok."
        
        output = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = txt['payload']
            headers = payload.get("headers")
            subject = [i['value'] for i in headers if i["name"]=="Subject"]
            sender = [i['value'] for i in headers if i["name"]=="From"]
            
            subject_val = subject[0] if subject else "(Konu Yok)"
            sender_val = sender[0] if sender else "(Bilinmiyor)"
            
            output.append(f"- Kimden: {sender_val} | Konu: {subject_val}")
            
        return "\n".join(output)
    except Exception as e:
        return f"Mail Hatası: {str(e)}"

def send_email(to_email, subject, body):
    """E-posta gönderir."""
    try:
        service = get_service('gmail', 'v1')
        if not service: return "Google bağlantısı kurulamadı."
        
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return f"E-posta başarıyla gönderildi: {to_email}"
    except Exception as e:
        return f"Gönderim Hatası: {str(e)}"

def get_calendar_events(count=5):
    """Gelecek takvim etkinliklerini getirir."""
    try:
        service = get_service('calendar', 'v3')
        if not service: return "Google bağlantısı kurulamadı."
        
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=count, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return "Yaklaşan etkinlik yok."

        output = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output.append(f"- {start}: {event['summary']}")
            
        return "\n".join(output)
    except Exception as e:
        return f"Takvim Hatası: {str(e)}"
