$ErrorActionPreference = "Stop"
Write-Host "Building Alpha Craft Stock..."
cd "C:\Users\alpay\.gemini\antigravity\scratch\alpha_craft_stok"
python -m PyInstaller --onefile --windowed --name AlphaCraftStock --add-data "index_stock.html;." main.py
if ($?) {
    Write-Host "Build Successful!" -ForegroundColor Green
} else {
    Write-Host "Build Failed!" -ForegroundColor Red
    exit 1
}
