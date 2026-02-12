import requests

def get_weather(city="Eskisehir"):
    """
    wttr.in servisinden hava durumunu çeker.
    API Key gerektirmez.
    """
    try:
        # JSON formatında al: format=j1
        url = f"https://wttr.in/{city}?format=%C+%t&lang=tr"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Hava durumu verisi alınamadı."
            
    except Exception as e:
        print(f"WEATHER ERROR: {e}")
        return "Hava durumu servisine ulaşılamıyor."

def get_daily_briefing():
    """Günlük özet bilgi (Hava + Özlü Söz vb.)"""
    weather = get_weather()
    return f"Bugün hava {weather}. Sistemler stabil. İyi çalışmalar dilerim."
