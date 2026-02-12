
import os

file_path = r"C:\Users\alpay\.gemini\antigravity\scratch\Alpha_Sunumlar_TekDosya\Alpha_Yatirim_Sunum_Mobil.html"

new_slides = """
            <!-- 3. ECOSYSTEM OVERVIEW -->
            <section data-background-color="#0f172a">
                <h3 style="color: var(--brand-blue); margin-bottom: 40px;">THE ALPHA ECOSYSTEM</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; padding: 20px;">
                    
                    <!-- Stock & Staff -->
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: left;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <i class="fa-solid fa-boxes-stacked" style="font-size: 1.5em; color: var(--brand-blue);"></i>
                            <h4 style="margin: 0; font-size: 1em;">Stock & Staff</h4>
                        </div>
                        <p style="font-size: 0.7em; color: #94a3b8; margin: 0;">
                            Unified inventory and workforce management. seamless tracking of assets and employee shifts in one core system.
                        </p>
                    </div>

                    <!-- Real Estate (Emlak) -->
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: left;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <i class="fa-solid fa-city" style="font-size: 1.5em; color: var(--brand-purple);"></i>
                            <h4 style="margin: 0; font-size: 1em;">Alpha Emlak</h4>
                        </div>
                        <p style="font-size: 0.7em; color: #94a3b8; margin: 0;">
                            Next-gen property CRM. Automated portfolio matching and client management with visual data insights.
                        </p>
                    </div>

                    <!-- Class & Education -->
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: left;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <i class="fa-solid fa-graduation-cap" style="font-size: 1.5em; color: var(--brand-green);"></i>
                            <h4 style="margin: 0; font-size: 1em;">Alpha Class</h4>
                        </div>
                        <p style="font-size: 0.7em; color: #94a3b8; margin: 0;">
                            Educational institution management. Student tracking, attendance (AI-ready), and performance analytics.
                        </p>
                    </div>

                    <!-- Legacy CRM Integration -->
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: left;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <i class="fa-solid fa-link" style="font-size: 1.5em; color: #fff;"></i>
                            <h4 style="margin: 0; font-size: 1em;">Unified CRM</h4>
                        </div>
                        <p style="font-size: 0.7em; color: #94a3b8; margin: 0;">
                            Centralized customer data across all modules. One identity, multiple touchpoints.
                        </p>
                    </div>

                </div>
            </section>

            <!-- 4. AZI AI ADVANTAGE -->
            <section data-background-color="#020617">
                <div style="text-align: center; margin-bottom: 40px;">
                    <div style="font-size: 3em; margin-bottom: 20px; color: var(--brand-green);">
                        <i class="fa-solid fa-eye"></i>
                    </div>
                    <h3 style="color: #fff;">AZI: BEYOND "CHATBOT"</h3>
                    <p style="color: var(--brand-green); font-size: 0.9em; letter-spacing: 2px; text-transform: uppercase;">Proactive Stewardship</p>
                </div>

                <div style="display: flex; flex-direction: column; gap: 20px; width: 80%; margin: 0 auto;">
                    
                    <div style="background: linear-gradient(90deg, rgba(16, 185, 129, 0.1), transparent); padding: 20px; border-left: 4px solid var(--brand-green); text-align: left;">
                        <h5 style="margin: 0 0 5px 0; color: #fff;">Neural Link (Voice & Vision)</h5>
                        <p style="margin: 0; font-size: 0.7em; color: #cbd5e1;">Allows completely hands-free operation. Speak naturally to control business logic.</p>
                    </div>

                    <div style="background: linear-gradient(90deg, rgba(14, 165, 233, 0.1), transparent); padding: 20px; border-left: 4px solid var(--brand-blue); text-align: left;">
                        <h5 style="margin: 0 0 5px 0; color: #fff;">Proactive Alerts</h5>
                        <p style="margin: 0; font-size: 0.7em; color: #cbd5e1;">AZI doesn't wait for you. It notices low stock, absent students, or market shifts and alerts YOU.</p>
                    </div>

                    <div style="background: linear-gradient(90deg, rgba(139, 92, 246, 0.1), transparent); padding: 20px; border-left: 4px solid var(--brand-purple); text-align: left;">
                        <h5 style="margin: 0 0 5px 0; color: #fff;">Self-Learning</h5>
                        <p style="margin: 0; font-size: 0.7em; color: #cbd5e1;">Analyzes usage patterns to optimize workflows and code its own improvements.</p>
                    </div>

                </div>
            </section>

            <!-- 5. COMPARISON: LEGACY VS ALPHA -->
            <section>
                <h3 style="color: #fff; margin-bottom: 40px;">WHY ALPHA CRAFT?</h3>
                
                <table style="font-size: 0.6em; width: 90%; margin: 0 auto; color: #e2e8f0; border-collapse: separate; border-spacing: 0 10px;">
                    <thead>
                        <tr style="color: #94a3b8; text-transform: uppercase; font-size: 0.8em;">
                            <th style="text-align: left; padding: 10px;">Metric</th>
                            <th style="text-align: center; padding: 10px; color: #64748b;">Legacy ERP</th>
                            <th style="text-align: center; padding: 10px; color: var(--brand-blue); font-weight: bold;">ALPHA SYSTEM</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="background: rgba(255,255,255,0.03);">
                            <td style="padding: 15px; border-radius: 10px 0 0 10px;">User Interaction</td>
                            <td style="text-align: center; color: #64748b;">Manual Typing / Clicks</td>
                            <td style="text-align: center; background: rgba(14, 165, 233, 0.1); border-radius: 0 10px 10px 0; color: #fff;">Voice / Neural Link</td>
                        </tr>
                        <tr style="background: rgba(255,255,255,0.03);">
                            <td style="padding: 15px; border-radius: 10px 0 0 10px;">Operation Mode</td>
                            <td style="text-align: center; color: #64748b;">Reactive (Wait for Input)</td>
                            <td style="text-align: center; background: rgba(14, 165, 233, 0.1); border-radius: 0 10px 10px 0; color: #fff;">Proactive (Alerts / Acts)</td>
                        </tr>
                        <tr style="background: rgba(255,255,255,0.03);">
                            <td style="padding: 15px; border-radius: 10px 0 0 10px;">Integration</td>
                            <td style="text-align: center; color: #64748b;">Fragmented Modules</td>
                            <td style="text-align: center; background: rgba(14, 165, 233, 0.1); border-radius: 0 10px 10px 0; color: #fff;">Unified Ecosystem</td>
                        </tr>
                        <tr style="background: rgba(255,255,255,0.03);">
                            <td style="padding: 15px; border-radius: 10px 0 0 10px;">Mobile Access</td>
                            <td style="text-align: center; color: #64748b;">Limited / Clunky App</td>
                            <td style="text-align: center; background: rgba(14, 165, 233, 0.1); border-radius: 0 10px 10px 0; color: #fff;">Native PWA + Offline</td>
                        </tr>
                    </tbody>
                </table>
            </section>

            <!-- 6. MOBILE FIRST -->
            <section data-background-color="#000">
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                    <div style="position: relative; width: 250px; height: 500px; border: 2px solid #334155; border-radius: 30px; margin-bottom: 30px; background: #0f172a; overflow: hidden; box-shadow: 0 0 50px rgba(14, 165, 233, 0.2);">
                        <!-- Screen Content Mock -->
                        <div style="padding: 20px; text-align: left;">
                            <div style="width: 40px; height: 40px; background: var(--brand-blue); border-radius: 10px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center;">
                                <span style="font-weight: bold; color: #fff;">A</span>
                            </div>
                            <div style="font-size: 1.2em; font-weight: bold; color: #fff; margin-bottom: 5px;">Good Morning,</div>
                            <div style="font-size: 0.8em; color: #94a3b8; margin-bottom: 30px;">Overview: Growth +15%</div>
                            
                            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 80px; margin-bottom: 10px;"></div>
                            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; height: 60px; margin-bottom: 10px;"></div>
                            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; height: 60px;"></div>
                        </div>
                        
                        <!-- Floating Mic -->
                        <div style="position: absolute; bottom: 20px; right: 20px; width: 50px; height: 50px; background: var(--brand-green); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px var(--brand-green);">
                            <i class="fa-solid fa-microphone" style="color: #fff;"></i>
                        </div>
                    </div>

                    <h3 style="color: #fff; margin-bottom: 10px;">BUSINESS IN YOUR POCKET</h3>
                    <p style="color: #94a3b8; font-size: 0.8em;">Full control. Anywhere. Anytime.</p>
                </div>
            </section>
"""

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the insertion point (after the second section, which is the Detailed Info section)
# We look for the 2nd </section> tag.
parts = content.split("</section>")

if len(parts) >= 3:
    # Insert new slides after the 2nd section (parts[0] is cover, parts[1] is detailed info)
    # So we join parts[0], parts[1], NEW_SLIDES, then the rest.
    # Note: split consumes the delimiter, so we need to add it back.
    
    new_content = parts[0] + "</section>" + parts[1] + "</section>" + new_slides + "</section>".join(parts[2:])
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully injected new slides.")
else:
    print("Could not find enough </section> tags to insert correctly. File structure might be unexpected.")
    # Fallback: Just insert before the closing slides div if structure is weird.
    if '<div class="slides">' in content and '</div>' in content:
        # This is risky doing blindly, but let's try to find the last </section> before the end of slides.
        last_section_index = content.rfind("</section>")
        if last_section_index != -1:
             new_content = content[:last_section_index + 10] + new_slides + content[last_section_index + 10:]
             with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
             print("Fallback insertion successful.")
        else:
            print("CRITICAL: No </section> tag found.")

