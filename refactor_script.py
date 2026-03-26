import codecs

new_logic = """        try:
            from azi_server.brain import tools_definitions
            import json
            
            # 1. Chat nesnesini hazirla (Tarihçe + Sistem + Araçlar)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=self.system_instruction,
                tools=tools_definitions.azi_tool_list
            )
            
            # API Gecmis formatini sekillendir
            formatted_history = []
            for mem in history_objs:
                r = "model" if mem.memory_type == "azi_response" else "user"
                formatted_history.append({"role": r, "parts": [mem.content]})
            
            chat = model.start_chat(history=formatted_history)
            
            MAX_TURNS = 5
            current_turn = 0
            prompt = text
            
            while current_turn < MAX_TURNS:
                current_turn += 1
                
                response = chat.send_message(prompt)
                
                # Fonksiyon cagrisi (Tool Call) var mi?
                if response.parts and hasattr(response.parts[0], 'function_call') and response.parts[0].function_call:
                    fc = response.parts[0].function_call
                    func_name = fc.name
                    args = {k: v for k, v in fc.args.items()}
                    print(f"AZI ARAÇ KULLANIYOR: {func_name}")
                    
                    tool_result = "Araç bulunamadı."
                    
                    # Dağıtıcı (Dispatcher)
                    try:
                        func_to_call = next((f for f in tools_definitions.azi_tool_list if f.__name__ == func_name), None)
                        if func_to_call:
                            tool_result = func_to_call(**args)
                        else:
                            # Eger manuel function handler gerekirse:
                            pass
                    except Exception as exe:
                        tool_result = f"Araç çalıştırılırken hata oluştu: {str(exe)}"
                        
                    # Ajanlara (Local PC) giden özel emirler kontrolü
                    if tool_result == "COMMAND_QUEUED_FOR_AGENT":
                        if func_name == "get_system_status":
                            action = "agent_command:PC_STATUS"
                        elif func_name == "run_system_command_terminal":
                            action = f"agent_command:TERM:{args.get('command')}"
                        elif func_name == "kill_process":
                            action = f"agent_command:KILL:{args.get('process_name')}"
                        elif func_name == "open_application":
                            app_name = args.get('app_name', '')
                            action = f"agent_command:OPEN_APP:{app_name}"
                            
                        system_log = f"Ajan Emri Gönderildi: {func_name}"
                        # Ajan asenkron oldugu icin LLM e yalandan sonuc donuyoruz ki cevap uretmeyi bitirsin
                        tool_result = "Sistem komutu Ajan'a (istemci bilgisayarına) başarıyla iletildi. Kullanıcıya işlemin arka planda başlatıldığını ve kullanıcının birazdan sonucu göreceğini bildirin."
                        
                    # Push/Email vs
                    if func_name in ["send_email_smtp", "push_notification_to_mobile"]:
                         system_log = f"Dışa Aktarım: {func_name}"
                    
                    # Sonucu LLM'e geri fırlat (ReAct Loop Devamı)
                    from google.generativeai.types import content_types
                    prompt = content_types.Part(
                        function_response=content_types.FunctionResponse(
                            name=func_name, response={"result": str(tool_result)}
                        )
                    )
                    continue # Döngüye devam et, yeni karari LLM versin
                    
                else:
                    # Fonksiyon yok, standart metin dönmüş
                    if response.text:
                        response_text = response.text
                        break
                    else:
                        response_text = "HMM... Boş yanıt (Belki güvenlik filtresi takıldı)."
                        break
                        
            if current_turn >= MAX_TURNS:
                response_text = "Düşünce döngüm işlem limitine takıldı (Çok fazla araç kullanımı)."
"""

def modify_logic():
    with codecs.open("azi_server/brain/logic.py", "r", "utf-8") as f:
        lines = f.readlines()
        
    start_idx = -1
    end_idx = -1
    in_process = False
    
    for i, l in enumerate(lines):
        if l.startswith("    def process(self"):
            in_process = True
            
        if in_process:
            if l.startswith("        try:") and start_idx == -1:
                start_idx = i
            elif l.startswith("        except Exception as e:") and start_idx != -1:
                end_idx = i
                break
            
    if start_idx != -1 and end_idx != -1:
        new_lines = lines[:start_idx] + [new_logic + "\n"] + lines[end_idx:]
        with codecs.open("azi_server/brain/logic.py", "w", "utf-8") as f:
            f.writelines(new_lines)
        print(f"SUCCESS: Replaced from line {start_idx} to {end_idx}")
    else:
        print(f"ERROR: start={start_idx}, end={end_idx}")

modify_logic()
