
# Alpha Craft Design System
# Bu dosya tüm ürünlerin ortak tasarım dilini tanımlar.

DESIGN_SYSTEM = {
    "fonts": {
        "primary": "'Inter', sans-serif",
        "cdn": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    },
    "themes": {
        "green": {
            "name": "Emlak Otomasyonu",
            "primary": "#10b981", # Emerald 500
            "secondary": "#059669",
            "accent": "#34d399",
            "bg_gradient": "from-emerald-400 to-emerald-600",
            "icon_color": "text-brand-400"
        },
        "blue": {
            "name": "Stok / Finans",
            "primary": "#3b82f6", # Blue 500
            "secondary": "#2563eb",
            "accent": "#60a5fa",
            "bg_gradient": "from-blue-400 to-blue-600",
            "icon_color": "text-blue-400"
        },
        "red": {
            "name": "Yönetim / Pro",
            "primary": "#ef4444", # Red 500
            "secondary": "#dc2626",
            "accent": "#f87171",
            "bg_gradient": "from-red-400 to-red-600",
            "icon_color": "text-red-400"
        }
    },
    "splash_screen_template": """
    <div id="splash-screen">
        <div class="flex flex-col items-center">
            <!-- Dynamic Logo Color based on Theme -->
            <div class="w-24 h-24 bg-gradient-to-br {bg_gradient} rounded-[2rem] flex items-center justify-center border border-white/10 shadow-2xl mb-8 splash-logo-box">
                <span class="text-white text-6xl font-bold tracking-tighter">A</span>
            </div>
            
            <h2 class="text-2xl font-bold text-white uppercase tracking-[0.4em] mb-4">
                Alpha Craft <span class="font-light opacity-50 text-lg">{product_name}</span>
            </h2>
            
            <div class="h-8 flex items-center justify-center">
                <p class="slogan-text" style="border-right-color: {primary_color}; color: {primary_color};">ARTIK KOLAY</p>
            </div>
            
            <!-- Loading Bar -->
            <div class="mt-12 w-56 h-0.5 bg-white/5 rounded-full overflow-hidden">
                <div class="h-full" style="background-color: {primary_color}; width: 0%; transition: width 3s linear;" id="splash-bar"></div>
            </div>
        </div>
    </div>
    """
}

def get_theme_config(theme_key):
    return DESIGN_SYSTEM["themes"].get(theme_key, DESIGN_SYSTEM["themes"]["green"])
