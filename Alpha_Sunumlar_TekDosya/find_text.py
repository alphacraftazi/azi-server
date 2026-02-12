import os

file_path = r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya\Alpha_Emlak_Sunum_Mobil.html"
marker = "AZI INTEGRATION SCENARIO"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    start_index = content.find(marker)
    if start_index == -1:
        print("Marker not found")
        exit()
        
    # Find base64 start
    b64_idx = content.find("base64,", start_index)
    if b64_idx == -1:
        print("Base64 not found after marker")
        # Just print context around marker
        print(content[start_index:start_index+500])
        exit()
        
    # Find end of attribute
    # Since it's src="data:...", we look for " starting from b64_idx
    quote_idx = content.find('"', b64_idx + 10)
    if quote_idx == -1:
        print("Closing quote not found")
        exit()
        
    with open("output.txt", "w", encoding="utf-8") as out:
        out.write("Content after image:\n")
        out.write(content[quote_idx:quote_idx+2000])
        
except Exception as e:
    with open("output.txt", "w", encoding="utf-8") as out:
        out.write(f"Error: {e}")
