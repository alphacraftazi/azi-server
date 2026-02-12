from duckduckgo_search import DDGS

def search_web(query: str, max_results=3):
    """
    DuckDuckGo üzerinden web araması yapar (ddgs kütüphanesi ile).
    """
    try:
        results = []
        # DDGS().text() generator döndürür
        with DDGS() as ddgs:
            search_gen = ddgs.text(query, max_results=max_results)
            for r in search_gen:
                title = r.get('title', '')
                body = r.get('body', '')
                href = r.get('href', '')
                results.append(f"Başlık: {title}\nÖzet: {body}\nLink: {href}\n")
            
        if not results:
            return "Arama sonucu bulunamadı."
            
        return "\n---\n".join(results)
    except Exception as e:
        return f"Arama Hatası: {str(e)}"
