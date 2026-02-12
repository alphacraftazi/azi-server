with open(r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya\Alpha_Emlak_Sunum_Mobil.html", "r", encoding="utf-8") as f:
    content = f.read()
    # Search for "Siz" near "AZI"
    # "AZI INTEGRATION SCENARIO" context
    # We found "Siz" in previous output.
    idx = content.find("Siz:")
    if idx == -1:
        # Tty searching for the emoji
        idx = content.find("\N{SPEAKING HEAD IN SILHOUETTE}") 
    
    if idx != -1:
        # Get from <p> before it
        start_p = content.rfind("<p", 0, idx)
        # Get until end of AZI response paragraph
        end_p_azi = content.find("</p>", idx + 100) # Skip the first </p> for Siz, find the next one for AZI
        end_p_azi = content.find("</p>", end_p_azi + 1) # Find the CLOSING </p> of the AZI message
        
        # Actually in output.txt it was: <p>...Siz...</p> <p>...AZI...</p>
        # So perform find twice
        
        if start_p != -1:
             # Grab a generous chunk
             chunk = content[start_p:start_p+500]
             with open("exact_output.txt", "w", encoding="utf-8") as out:
                 out.write(chunk)
    else:
        with open("exact_output.txt", "w", encoding="utf-8") as out:
            out.write("Not found")
