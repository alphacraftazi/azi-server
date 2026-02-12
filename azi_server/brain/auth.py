import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# İzinler (Gmail Okuma/Yazma, Takvim, Drive vb.)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

def authenticate_google():
    """
    Google hesabına giriş yapar ve token.json oluşturur.
    Kullanıcı tarayıcıdan onay vermelidir.
    """
    creds = None
    # Token dosyası varsa yükle
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # Token yoksa veya geçersizse giriş yap
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("HATA: 'credentials.json' bulunamadı! Lütfen Google Cloud Console'dan indirip buraya atın.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Token'ı kaydet
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

if __name__ == "__main__":
    print("Google Kimlik Doğrulama Başlatılıyor...")
    creds = authenticate_google()
    if creds:
        print("BAŞARILI: Google Kapıları Açıldı! (token.json oluşturuldu)")
    else:
        print("BAŞARISIZ: Kimlik doğrulama yapılamadı.")
