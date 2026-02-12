
import os

file_path = r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya\Alpha_Emlak_Sunum_Mobil.html"

# The exact content we want to replace (including the newline/whitespace structure we found)
target_content = """<p><strong>🗣️ Siz: </strong> "Beşiktaş'ta 3+1 daire var mı?" </p> <p style="margin-top: 10px;" ><strong>🤖 AZI:</strong> "Evet, portföyümüzde 2 adet,
 piyasa takibinde 5 yeni 'Sahibinden' ilan var. Sahibinden olanları listelememi ister misiniz?"</p>"""

replacement_content = """<p style="margin-top: 10px;" ><strong>🔔 AZI Bildirim:</strong> "Beşiktaş bölgesinde kriterlerinize uygun 5 yeni 'Sahibinden' ilan, 2 portföy eşleşmesi tespit edildi. Raporu hazırlamamı ister misiniz?"</p>"""

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Try exact match first
    if target_content in content:
        new_content = content.replace(target_content, replacement_content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully replaced content using exact match.")
    else:
        # If exact match fails (due to whitespace invisible chars), try a more loose replacement
        # We know the structure is specific enough.
        print("Exact match not found. Trying flexible match...")
        
        # Construct a regex or just find the start and end
        start_marker = '<p><strong>🗣️ Siz: </strong> "Beşiktaş\'ta 3+1 daire var mı?" </p>'
        end_marker = 'Sahibinden olanları listelememi ister misiniz?"</p>'
        
        start_idx = content.find(start_marker)
        if start_idx != -1:
            end_idx = content.find(end_marker, start_idx)
            if end_idx != -1:
                # Include the length of end_marker
                end_idx += len(end_marker)
                
                original_segment = content[start_idx:end_idx]
                print(f"Found segment to replace: {original_segment[:50]}...{original_segment[-50:]}")
                
                new_content = content[:start_idx] + replacement_content + content[end_idx:]
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print("Successfully replaced content using marker match.")
            else:
                print("Start marker found but end marker not found.")
        else:
            print("Start marker not found.")

except Exception as e:
    print(f"Error: {e}")
