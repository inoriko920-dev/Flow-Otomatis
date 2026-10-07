# FLOW-OTOMATIS STEP04 UI PROMPTS — UIB v1.2


---
## BATCH_01_UI_PROMPTS_SYNC_V1_2_01-10.txt
---

FLOW-OTOMATIS STEP 04 — UI PROMPT BATCH 1 — UIB v1.2 BIOGRAPHY SYNC
PROMPTS: 01-10
Each prompt below generates ONE separate UI image.

====================================================================================================
PROMPT #01
CODE: UI-IMG-001A
SURFACE: SCR-001 Project Hub
STATE: EMPTY / first run
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-001A
SURFACE: SCR-001 Project Hub
STATE: EMPTY / first run
PRIORITY: P0

VARIANT REQUIREMENTS:
Show first-launch Project Hub. Left nav with Beranda active. No project selected in top bar. Main area has page title “Beranda”, a calm empty-state panel titled “Mulai project pertama Anda”. Primary action for the biography workflow is “Impor Paket Episode”, with secondary buttons “Buat Project” and “Buka Project”. Explain briefly that a package can contain Scene ID, approved images, motion prompts, and timing so the queue is prepared automatically. Below, an empty “Project terbaru” section with no cards. Small connectivity/status line may show “Online”. No AI dock open. Keep the page simple and reassuring for a non-programmer.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #02
CODE: UI-IMG-001B
SURFACE: SCR-001 Project Hub
STATE: READY + recovery banner
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-001B
SURFACE: SCR-001 Project Hub
STATE: READY + recovery banner
PRIORITY: P0

VARIANT REQUIREMENTS:
Show Beranda with 4 realistic recent project rows/cards in a compact list, each with project name, Windows path, last opened timestamp and last state. At top of content show an amber recovery banner: “Pemulihan tersedia — Dokumenter 60 Scene”, with buttons “Buka Recovery” and “Abaikan untuk sekarang”. Keep actions “Impor Paket Episode”, “Buat Project”, and “Buka Project” visible. One recent project can show “Butuh Perhatian”.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #03
CODE: UI-IMG-001C
SURFACE: DLG-001 Episode Package Import
STATE: SELECT PACKAGE / contract detected
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-001C
SURFACE: DLG-001 Episode Package Import
STATE: SELECT PACKAGE / contract detected
PRIORITY: P0

VARIANT REQUIREMENTS:
Centered large import dialog over Beranda titled “Impor Paket Episode”. Show two supported entry paths: “Pilih ZIP Episode” and “Pilih FLOW_OTOMATIS_IMPORT.json”. Display a selected example package “EP001_STEVE_JOBS_COMPLETE.zip” with detected Episode ID EP001_STEVE_JOBS, 60 scenes, approved-image folder detected, motion prompts detected, timing contract detected. Production profile read-only: Omni Flash 1.1 • 720p • 16:9. Explain that credentials are never imported. Buttons “Batal” and primary “Validasi Paket”.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #04
CODE: UI-IMG-002A
SURFACE: SCR-002 Workspace
STATE: READY + scene selected
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-002A
SURFACE: SCR-002 Workspace
STATE: READY + scene selected
PRIORITY: P0

VARIANT REQUIREMENTS:
Core workspace after importing an episode package. Workspace nav active. Top bar: project “EP001 — Steve Jobs”, green “Tersimpan”, summary “60 scene • 60 gambar terpetakan • 0 selesai”. Toolbar: “Impor Paket Episode”, “Scan Ulang Gambar”, search/filter, primary “Mulai Batch”. Main table shows about 12 visible rows with columns Scene, Gambar, Prompt, Target, Durasi Flow, Profil, Generate, Download, Status. Gambar column shows thumbnail plus small “Auto”/check indicator for canonical SCENE_### mapping. Use examples: Target 3.81s with recommended/selected 4s; 5.42s→6s; 7.32s→selected 8s; 9.27s→10s. Select S016 with pale blue highlight. Right dock Scene tab: canonical key “SCENE_016”, editable Motion Prompt, required approved-image card showing auto-mapped file “EP001_STEVE_JOBS__IMAGE__SCENE_016__v1.0.png” with badge “Auto-mapped • Approved” and small fallback button “Ganti File”; Profil dropdown; locked production block “Omni Flash 1.1 • 720p • 16:9”; Target “7.32 detik”; recommendation “8 detik”; segmented duration buttons 4s / 6s / 8s / 10s where 4s and 6s are disabled, 8s highlighted “Direkomendasikan”, 10s remains valid; current state “Siap”. AI Agent tab visible but inactive. Model/resolution/aspect ratio are locked labels, not dropdowns.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #05
CODE: UI-IMG-002B
SURFACE: SCR-002 Workspace
STATE: WORKING / batch running
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-002B
SURFACE: SCR-002 Workspace
STATE: WORKING / batch running
PRIORITY: P0

VARIANT REQUIREMENTS:
Same synchronized workspace shell during active batch. Top summary: “12/60 selesai”, progress 20%, current “S016”. Primary control becomes “Jeda”; destructive cancel is secondary and visually cautious. Table columns remain Scene, Gambar, Prompt, Target, Durasi Flow, Profil, Generate, Download, Status. Mix Selesai, Sedang Diproses, Menunggu states. Current S016 shows a thumbnail with Auto-mapped check, Target “7.32s”, selected Flow “8s”, spinner/progress and profile label. Generate and Download are separate stages. Right dock shows compact run detail with status “Sedang memantau batch”, locked production labels “Omni Flash 1.1 • 720p • 16:9”, image filename, Target 7.32s, Selected Flow 8s, and note that final edit trims to Target. Do not invent automatic account rotation. Bottom status bar shows Online • Autosave aktif.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #06
CODE: UI-IMG-002C
SURFACE: SCR-002 Workspace
STATE: NEEDS_ATTENTION / profile error
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-002C
SURFACE: SCR-002 Workspace
STATE: NEEDS_ATTENTION / profile error
PRIORITY: P0

VARIANT REQUIREMENTS:
Same synchronized workspace with an amber banner beneath top bar: “S016 butuh perhatian — sesi profil perlu diperiksa.” Buttons “Buka Detail” and “Cek Profil”. S016 row has amber “Butuh Perhatian”; its approved image remains mapped, Target 7.32s and selected Flow 8s remain unchanged, while other queued rows remain intact and batch is paused safely. Right dock Scene tab shows locked production labels “Omni Flash 1.1 • 720p • 16:9”, approved image filename, human-readable profile/session reason, last check timestamp, recommended next actions “Buka Sesi Login”, “Coba Lagi”, “Lewati”. No bypass language, no automatic switch. Include “Lihat Diagnostik”.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #07
CODE: UI-IMG-002D
SURFACE: SCR-002 Workspace
STATE: IMAGE MAPPING ISSUES
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-002D
SURFACE: SCR-002 Workspace
STATE: IMAGE MAPPING ISSUES
PRIORITY: P0

VARIANT REQUIREMENTS:
Workspace after package validation with image-mapping problems. Show summary banner “57 siap • 1 gambar hilang • 1 duplikat • 1 gambar tidak terbaca”. Table keeps canonical Scene ID, Gambar, Prompt, Target, Rekomendasi, Pilihan Flow, Status. Example SCENE_027 = MISSING_IMAGE with no thumbnail and action “Cari File”; SCENE_031 = DUPLICATE_IMAGE with two candidate filenames and action “Pilih yang Benar”; SCENE_044 = IMAGE_UNREADABLE with action “Ganti File”. Valid scenes remain Ready. Primary batch action is disabled or labeled “Selesaikan 3 masalah”. Button “Scan Ulang Gambar”. No automatic guessing for ambiguous duplicates.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #08
CODE: UI-IMG-003A
SURFACE: SCR-003 Hasil
STATE: SUCCESS / complete
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-003A
SURFACE: SCR-003 Hasil
STATE: SUCCESS / complete
PRIORITY: P0

VARIANT REQUIREMENTS:
Results screen after successful run. Hasil nav active. Header “Hasil Run” with summary cards: 60 Total, 60 Generate Selesai, 60 File Tersimpan, 0 Perlu Cek. Show green success banner “Batch selesai”. Table rows show Scene ID, Target, Selected Flow, Generate, Download, Output, Waktu. Use S016 Target 7.32s and Selected Flow 8s. Select S016 and show right preview panel with video thumbnail placeholder, canonical output filename including SCENE_016, folder path, production metadata “Omni Flash 1.1 • 720p • 16:9”, Target “7.32s”, Generated “8s”, Trim Target “7.32s”, and buttons “Buka File” and “Buka Folder”. Show a small status that FLOW_OTOMATIS_RESULT.json has been updated. Do not imply the final timeline became 8s.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #09
CODE: UI-IMG-003B
SURFACE: SCR-003 Hasil
STATE: PARTIAL / failed download
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-003B
SURFACE: SCR-003 Hasil
STATE: PARTIAL / failed download
PRIORITY: P0

VARIANT REQUIREMENTS:
Results screen with separate generation and download outcomes. Summary: “60 Generate Selesai”, “56 File Tersimpan”, “4 Download Perlu Perhatian”. Amber banner explains generation succeeded but some output files need download/recheck. Table includes Target and Selected Flow durations and visibly separates Generate = Selesai from Download = Gagal / Belum Diambil for affected rows. Primary safe action “Coba Download Lagi”; secondary “Lihat Workspace”. A compact manifest status shows “FLOW_OTOMATIS_RESULT.json — 56 success, 4 pending download”. No claim that generated video is lost.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #10
CODE: UI-IMG-003C
SURFACE: SCR-003 Hasil
STATE: RESULT MANIFEST / handoff ready
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-003C
SURFACE: SCR-003 Hasil
STATE: RESULT MANIFEST / handoff ready
PRIORITY: P0

VARIANT REQUIREMENTS:
Results screen focused on downstream handoff after all downloads succeed. Header card “Handoff Siap” with checks for 60/60 generate, 60/60 downloaded, FLOW_OTOMATIS_RESULT.json updated. Show a compact manifest preview for selected SCENE_016: Target 7.32s, Selected Flow 8s, output canonical filename, take ID TAKE_01, trim_target_s 7.32, QA status Pending. Buttons “Buka Folder Episode”, “Buka FLOW_OTOMATIS_RESULT.json”, and primary “Tandai Siap untuk Editing”. Do not expose credentials or session data.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.





---
## BATCH_02_UI_PROMPTS_SYNC_V1_2_11-20.txt
---

FLOW-OTOMATIS STEP 04 — UI PROMPT BATCH 2 — UIB v1.2 BIOGRAPHY SYNC
PROMPTS: 11-20
Each prompt below generates ONE separate UI image.

====================================================================================================
PROMPT #11
CODE: UI-IMG-004A
SURFACE: SCR-004 Profil Google
STATE: READY profile list
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-004A
SURFACE: SCR-004 Profil Google
STATE: READY profile list
PRIORITY: P0

VARIANT REQUIREMENTS:
Profil Google screen. Header “Profil Google” with explanation that only authorized profiles are stored locally as sessions; no passwords. Primary “Tambah Profil”, search field, filter “Semua / Siap / Nonaktif”. Compact table with 10–12 profiles, columns Nama Profil, Status Sesi, Ketersediaan, Terakhir Dicek, Catatan, Aksi. All visible rows mostly green “Siap”. Each row uses friendly labels such as “Akun Produksi 01”. Row menu actions include “Buka Sesi”, “Ubah Nama”, “Nonaktifkan”, “Hapus”.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #12
CODE: UI-IMG-004B
SURFACE: SCR-004 Profil Google
STATE: Mixed Ready / Login / Attention
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-004B
SURFACE: SCR-004 Profil Google
STATE: Mixed Ready / Login / Attention
PRIORITY: P0

VARIANT REQUIREMENTS:
Same Profil Google screen with mixed semantic states: green “Siap”, amber “Perlu Login”, gray “Nonaktif”, red/amber “Butuh Perhatian”, stale “Belum Dicek”. Add a top compact summary 7 Siap • 2 Perlu Login • 1 Nonaktif. Selected profile opens a small detail side area or right dock with last check, note and buttons “Buka Sesi Login”, “Cek Ulang”, “Nonaktifkan”. Never display email passwords/cookies/tokens.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #13
CODE: UI-IMG-005A
SURFACE: SCR-005 Bantuan Login
STATE: WAITING_FOR_USER
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-005A
SURFACE: SCR-005 Bantuan Login
STATE: WAITING_FOR_USER
PRIORITY: P0

VARIANT REQUIREMENTS:
Session/Login Assistance screen for one profile. Title “Selesaikan Login — Akun Produksi 03”. A three-step vertical status: 1 Sesi browser dibuka (complete), 2 “Selesaikan login/MFA/CAPTCHA di jendela Google” (current, amber), 3 Cek ulang sesi (pending). Main callout clearly states Flow-Otomatis tidak mengisi password atau melewati verifikasi. Buttons “Buka / Fokuskan Sesi Login”, “Cek Ulang”, “Batal”. Queue context card shows “S013 menunggu profil ini” but remains safe.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #14
CODE: UI-IMG-005B
SURFACE: SCR-005 Bantuan Login
STATE: SUCCESS / ERROR handoff
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-005B
SURFACE: SCR-005 Bantuan Login
STATE: SUCCESS / ERROR handoff
PRIORITY: P0

VARIANT REQUIREMENTS:
Show Session/Login Assistance after recheck. Use a split or single-state layout focused on SUCCESS: green panel “Sesi siap digunakan”, last checked time, profile label, CTA “Kembali ke Workspace” and secondary “Cek Ulang”. Include a compact inline example/error strip beneath: if session fails, message “Sesi belum siap — selesaikan login lalu cek ulang”, not a technical dump. No credential fields.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #15
CODE: UI-IMG-006A
SURFACE: SCR-006 Gemini Key Vault
STATE: READY populated vault
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-006A
SURFACE: SCR-006 Gemini Key Vault
STATE: READY populated vault
PRIORITY: P0

VARIANT REQUIREMENTS:
Gemini Keys screen. Header “Gemini Keys” with helper “API key disimpan secara lokal dan ditampilkan dalam bentuk tersamarkan.” Buttons “Impor API Key”, “Tambah Key”, secondary “Cek Kesehatan”. Summary chips 96 Aktif • 3 Perlu Cek • 1 Nonaktif. Table with masked rows like “Key 001 ••••••••A1B2”, Label, Status, Terakhir Dicek, Dipakai Agent, Aksi. No raw key reveal button. Search/filter. Professional dense table suited for up to 100 keys.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #16
CODE: UI-IMG-006B
SURFACE: DLG-006 Import Key + SCR-006
STATE: PARTIAL import result
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-006B
SURFACE: DLG-006 Import Key + SCR-006
STATE: PARTIAL import result
PRIORITY: P0

VARIANT REQUIREMENTS:
Overlay a large import-result dialog over Gemini Keys. Title “Hasil Impor API Key”. Summary: 100 baris dibaca; 92 valid; 5 duplikat; 3 tidak valid. Show a table of line number, masked key suffix only, result, reason. Never show complete key. Footer: secondary “Kembali Edit”, primary “Simpan 92 Key Valid”. Provide a checkbox/option to ignore duplicates only if already implied; do not create secret-reveal controls.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #17
CODE: UI-IMG-007A
SURFACE: SCR-007 Pengaturan
STATE: READY settings/provider
PRIORITY: P1
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-007A
SURFACE: SCR-007 Pengaturan
STATE: READY settings/provider
PRIORITY: P1

VARIANT REQUIREMENTS:
Settings screen with left subnavigation inside content: Umum, Output, AI Agent, Provider & Biaya, Privasi. Show “Provider & Biaya” selected. At top show a prominent read-only card “Mode Produksi Dikunci” with Model “Omni Flash 1.1”, Resolusi “720p”, Aspect “16:9”, and “Durasi tersedia: 4 / 6 / 8 / 10 detik”. Add policy text: “App merekomendasikan durasi terkecil yang mencakup Target; pilihan final dikonfirmasi pengguna; opsi lebih pendek dinonaktifkan.” These are labels, not dropdowns. Default provider card “Flow Web — menggunakan sesi profil yang Anda kelola” with status. Optional official paid API card is OFF/disabled by default with cost warning. Link to Gemini Keys rather than raw key field. Also show safe toggles for autosave and agent confirmation policy. No hidden auto-rotation setting.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #18
CODE: UI-IMG-008A
SURFACE: SCR-008 Diagnostik
STATE: READY activity history
PRIORITY: P1
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-008A
SURFACE: SCR-008 Diagnostik
STATE: READY activity history
PRIORITY: P1

VARIANT REQUIREMENTS:
Diagnostics screen. Header “Diagnostik & Aktivitas”. Filter row by severity, Scene ID, Profile, type; search. Main list/timeline with timestamp, human-readable message, linked identifiers and status icon. Examples: “S012 selesai dibuat”, “Akun Produksi 03 memerlukan login”, “Agent mengusulkan retry S013”. Right detail panel collapsed or showing selected event summary. Button “Salin Diagnostik Tersamarkan”. No secrets.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #19
CODE: UI-IMG-008B
SURFACE: SCR-008 Diagnostik
STATE: Expanded DOWNLOAD ERROR diagnostic
PRIORITY: P1
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-008B
SURFACE: SCR-008 Diagnostik
STATE: Expanded DOWNLOAD ERROR diagnostic
PRIORITY: P1

VARIANT REQUIREMENTS:
Same diagnostics screen with one ERROR event selected. Human message at top: “Download hasil S017 gagal, tetapi generate berhasil.” Under it an expandable technical section titled “Detail teknis (tersamarkan)” using monospace short diagnostic code, stage, timestamp, retry count and redacted path/profile ID. Show production metadata “Omni Flash 1.1 • 720p • 16:9”, image mapping source, and timing “Target 7.32s • Recommended 8s • Selected 8s”. Actions “Coba Download Lagi”, “Buka Scene”, “Salin Diagnostik Tersamarkan”. Maintain clear hierarchy: human explanation first, technical detail second.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #20
CODE: UI-IMG-009A
SURFACE: SCR-009 Recovery Center
STATE: Recovery available
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-009A
SURFACE: SCR-009 Recovery Center
STATE: Recovery available
PRIORITY: P0

VARIANT REQUIREMENTS:
Recovery Center after app restart. Title “Pemulihan Project”. Large recovery card for “Dokumenter 60 Scene” with snapshot timestamp, 60 scenes, last known progress 18/60, safe note “State lokal ditemukan setelah aplikasi tertutup.” Show affected summary and primary “Pulihkan Project”, secondary “Lihat Detail”, tertiary/destructive “Buang Snapshot”. Explain that restoring does not automatically resubmit external jobs.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.





---
## BATCH_03_UI_PROMPTS_SYNC_V1_2_21-30.txt
---

FLOW-OTOMATIS STEP 04 — UI PROMPT BATCH 3 — UIB v1.2 BIOGRAPHY SYNC
PROMPTS: 21-30
Each prompt below generates ONE separate UI image.

====================================================================================================
PROMPT #21
CODE: UI-IMG-009B
SURFACE: SCR-009 Recovery Center
STATE: Ambiguous external job
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-009B
SURFACE: SCR-009 Recovery Center
STATE: Ambiguous external job
PRIORITY: P0

VARIANT REQUIREMENTS:
Recovery Center focused on ambiguous external job S019. Amber warning: “Status eksternal belum dapat dipastikan.” Show evidence: last local stage “Submitted”, no confirmed result, last check time. Present safe choices: primary “Verifikasi Status”, secondary “Tetap Butuh Perhatian”, and a disabled/absent automatic “Submit Ulang”. Explicit note: “Flow-Otomatis tidak akan mengirim ulang otomatis untuk mencegah duplikasi.”

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #22
CODE: UI-IMG-010A
SURFACE: PNL-001 AI Agent
STATE: Normal conversation
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-010A
SURFACE: PNL-001 AI Agent
STATE: Normal conversation
PRIORITY: P0

VARIANT REQUIREMENTS:
Show Workspace base with right dock “AI Agent” tab active. Agent panel header contains visible context chips “Project: Dokumenter 60 Scene” and “Scene: S013”. Conversation in Indonesian, natural and concise. Assistant says it found S013 needs login and offers safe options, with small suggested-action buttons “Buka Profil”, “Jelaskan Masalah”, “Lihat Diagnostik”. Input box at bottom “Tanyakan atau minta bantuan…”. No autonomous execution banner and no claims of certainty.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #23
CODE: UI-IMG-010B
SURFACE: DLG-008 / PNL-001 Agent
STATE: Action preview / approval
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-010B
SURFACE: DLG-008 / PNL-001 Agent
STATE: Action preview / approval
PRIORITY: P0

VARIANT REQUIREMENTS:
Workspace with AI Agent dock plus centered approval dialog titled “Tinjau Aksi AI”. It must show What: “Coba ulang download”; Scope: “1 scene — S017”; Reason: short explanation; Expected effect; Risk/side effect: no new generation request and no change to Target, selected Flow duration, approved image mapping, or motion prompt. Show locked production context “Omni Flash 1.1 • 720p • 16:9”. Buttons “Batal” and primary “Terapkan”. Show agent conversation behind the modal, dimmed.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #24
CODE: UI-IMG-010C
SURFACE: PNL-001 AI Agent
STATE: Working / partial failure
PRIORITY: P1-CONDITIONAL
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.

REFERENCE VIEWPORT: 1920x1080, 16:9, 100% scale. White / light-gray application background, professional blue accent, compact information density, crisp 1px dividers, subtle shadow only for dialogs/popovers. Use Segoe UI style typography. No glassmorphism, no neon, no gradients, no huge rounded cards, no decorative hero art.

GLOBAL SHELL: fixed 216px left navigation with items Beranda, Workspace, Hasil, Profil Google, Gemini Keys, Diagnostik, Pengaturan. 56px top project bar. Flexible main workspace. 376px resizable right dock where applicable, with tabs “Scene” and “AI Agent”. 28px bottom status bar. Primary blue #2563EB, app background #F5F7FA, white surfaces, dark text #111827, border #D8DEE8. Semantic green/amber/red only for status.

FLOW PRODUCTION LOCK — authoritative for this project: Model is always “Omni Flash 1.1”; Resolution is always “720p”; Aspect ratio is “16:9”. These are fixed production values in the main workflow and must NOT be editable dropdowns. Scene target duration comes from project timing/SRT mapping and is never rewritten by Flow-Otomatis. Flow-Otomatis recommends the smallest available duration that fully covers Target: <=4.00s → recommend 4s; >4.00–6.00s → recommend 6s; >6.00–8.00s → recommend 8s; >8.00–10.00s → recommend 10s. The USER still confirms the final valid Flow duration from 4/6/8/10. Options shorter than Target are disabled. Example: Target 7.32s → recommend 8s → valid choices 8s or 10s. Any scene >10.00s is INVALID and must not be submitted until split. Show Target, Recommended, and Selected Flow duration where selection matters.

BIOGRAPHY PACKAGE SYNC — normal production input is a complete episode package or FLOW_OTOMATIS_IMPORT.json. Every scene uses canonical SCENE_### as the machine key. Approved reference images are auto-mapped from the episode’s approved-images folder using SCENE_###; manual “Pilih/Ganti File” is fallback/recovery only. A scene is not Ready unless it has exactly one readable approved image, a motion prompt, Target <=10s, and a valid selected Flow duration. Key blocking states include MISSING_IMAGE, DUPLICATE_IMAGE, IMAGE_UNREADABLE, MISSING_PROMPT, DURATION_SELECTION_REQUIRED, and INVALID_DURATION_GT10. After processing, Flow-Otomatis writes/updates FLOW_OTOMATIS_RESULT.json without passwords, cookies, session data, API keys, tokens, or other credentials.

UX RULES: show status with icon + text, never color alone. Never show passwords, cookies, full API keys or tokens. Never imply CAPTCHA/MFA bypass. Never show automatic quota/rate-limit evasion or hidden multi-account rotation. Human approval is required for login, destructive actions, paid provider actions, and material AI actions. Keep Generate status and Download status as separate user-facing concepts where relevant. Internal capture mechanics may exist in diagnostics, but the main UI calls the final retrieval stage Download/Simpan Hasil.

AI AGENT: conversational and human-readable, but operational. It can explain, preview and propose actions. For material actions show scope/preview first, then explicit “Terapkan” / “Batal”. Do not portray AI as omnipotent or guaranteed-correct.

BRANDING: Flow-Otomatis is the visual brand. Google Flow/Gemini may appear only as text labels for integration/provider context. Do not copy Google Flow’s UI, Google branding, or proprietary assets.

TEXT: interface language is Indonesian. Use the exact important labels supplied by the variant prompt. Keep text crisp and readable. Avoid gibberish placeholder text. If a long prompt is needed, use realistic short Indonesian sentences. The mockup is a visual reference; do not invent new features, menus or controls beyond the prompt.

OUTPUT: one full desktop screenshot only, straight-on, no laptop/device frame, no perspective, no collage, no second screen, no annotation arrows, no watermark.

VARIANT ID: UI-IMG-010C
SURFACE: PNL-001 AI Agent
STATE: Working / partial failure
PRIORITY: P1-CONDITIONAL

VARIANT REQUIREMENTS:
AI Agent right dock in working state. Show one action plan with 3 steps: 1 inspect status complete, 2 retry download failed, 3 verify file pending. Progress indicator and button “Batalkan”. Then a partial result card: 2 berhasil, 1 masih butuh perhatian, with CTA “Buka Scene S017”. If timing is discussed, show Target / Recommended / Selected Flow duration and do not silently alter selection. No auto-account switching. Preserve conversation context.

DO NOT: create a website/landing page; use dark mode; use mobile cards; imitate Google Flow interface; expose secrets; add automatic account-credit rotation; add social/profile avatar clutter; use giant gradients; add unrequested video editor timeline; add multi-account parallel execution; hide critical warnings behind icon-only controls.



====================================================================================================
PROMPT #25
CODE: UI-IMG-011A
SURFACE: PNL-002 Scene Inspector
STATE: Scene selected / editable
PRIORITY: P0
====================================================================================================
PROMPT-UI-MASTER — FLOW-OTOMATIS UI REFERENCE
Create a high-fidelity desktop application UI mockup for Windows 11 named “Flow-Otomatis”. This is a production tool, not a landing page and not a mobile UI.