# READABLE COPY — Not the original approved DOCX

This is a text-only extraction for review/search. Do NOT treat this copy as the DOCX required by Software Factory G0. The source DOCX must still be uploaded as binary and SHA-256 checked before G0 can pass.

Original file SHA-256: `2df71a84b3f33ba3e04114f0508764d9de7d798fa6926b1aa5dfbfbd7f0f5452`

---























FLOW-OTOMATIS  /  ASTRA  /  E12-00  •  08 October 2026, 15:20 WIB
E12-00
BASELINE & PLANNING GOVERNANCE
ASTRA — EVIDENCE + HANDOFF KE E12-01
Flow-Otomatis • STEP 12 — Integrations & External Services
Disusun pada 08 October 2026, 15:20 WIB
	Parameter
	Status / bukti

	Repositori
	https://github.com/inoriko920-dev/Flow-Otomatis

	Branch / audit HEAD
	main / e560684e04ed3a5fad40bb00a91823de68ca5431

	Induk master plan
	V1.0 (8 Oktober 2026) + V1.1 Implementation Ready (8 Oktober 2026)

	Sifat kerja
	READ-ONLY — audit GitHub / kebijakan / perencanaan; tidak ada commit, kode, UI atau penggunaan kredit

	Penilaian E12-00
	TASK T01–T04: REVIEW COMPLETE. T05: PREPARED, AWAIT OWNER APPROVAL + REPO-UPLOAD PERMISSION.

	Gate governance
	BLOCKED — G0 dokumen belum disetujui secara eksplisit dan belum menjadi source-of-truth di repo

	Live external
	BLOCKED — izin otomasi Flow/multi-akun dan READY pasca-restart belum diverifikasi



Aturan penting: hasil audit baca-saja tidak sama dengan otorisasi mengedit GitHub. Tidak ada klaim bahwa Google Flow dapat diotomatisasi secara penuh.
01. Putusan eksekutif
E12-00 selesai sebagai paket audit dan pemetaan governance yang tidak mengubah repositori. Kondisi minimal untuk menyatakan wave E12-00 PASS sebagai dokumentasi repo belum terpenuhi: pemilik perlu secara eksplisit menyetujui Master Plan V1.1 dan memberi izin terpisah untuk commit dokumen ke repo Flow-Otomatis. Sementara itu, peninjauan E12-01 dapat disiapkan sebagai perencanaan lokal, tetapi implementasi/commit tidak boleh dimulai.
	Gate
	Status
	Dasar

	Repo SHA & drift
	PASS (read-only)
	HEAD, parent dan daftar perubahan diperiksa.

	Module owners
	PASS (inventaris)
	Kontrak/owner repository dibaca, calon baru dinyatakan proposal.

	Pemetaan harga/Terms
	PASS (pencatatan)
	Dokumen Google ditinjau; policy masih belum membuktikan izin live.

	Product scope
	PASS
	Tujuan final sesuai keputusan pengguna; scope tidak diperluas diam-diam.

	Source-of-truth DOCX
	BLOCKED
	Belum ada persetujuan eksplisit V1.1 dan izin upload GitHub.

	Otomasi live / multi-akun
	BLOCKED
	Belum ada dasar resmi khusus yang mengizinkan mekanisme yang direncanakan.

	UI baru
	NOT STARTED
	E12-02 memiliki stop gate sendiri; UI lama tetap frozen.



02. E12-00-T01 — Verifikasi baseline dan delta bukti
Inspeksi GitHub baca-saja pada main memastikan Git ref HEAD e560684e04ed3a5fad40bb00a91823de68ca5431 dan pohon git commit sama. API tree recursive melaporkan 254 node, truncated=false. HEAD berinduk 1c7ade1922e45b987a45f495fb0784588a3c1291.
Commit HEAD hanya memperbarui PROJECT_STATE.md, TASKS.md dan docs/planning/audits/STEP12_RESULTS_ERROR_RECOVERY_2026-10-08.md dengan catatan PASS/handoff dan [skip ci]. Tidak boleh menganggap head dokumentasi ini menjalankan pipeline baru. Bukti CI terakhir terkait code sebelum commit adalah run 37734144006 yang dilaporkan SUCCESS untuk 1c7ade1922e45b987a45f495fb0784588a3c1291.
PR #22 merged; TASKS.md menyebut 233 pytest PASS, UI 30/30, Windows portable dan pengujian integritas ZIP PASS. Itu adalah CI-REPORTED untuk code lama, bukan pytest yang dijalankan selama E12-00 ini.
	Sumber
	Temuan
	Klasifikasi

	git/refs/heads/main
	e560684e04ed3a5fad40bb00a91823de68ca5431
	VERIFIED GITHUB

	git/trees/main?recursive=1
	254 nodes, not truncated
	VERIFIED GITHUB

	git/commits/e560...
	Parent 1c7ade; 3 berkas docs/state
	VERIFIED GITHUB

	Actions/37734144006
	SUCCESS / SHA 1c7ade…
	CI-REPORTED

	TASKS.md latest
	233 tests + 30/30 UI + ZIP verifier
	REPO-REPORTED

	PROJECT_STATE.md awal
	90 tests riwayat gate auth, bukan status tes terbaru
	HISTORICAL

	README.md
	STEP 12 in progress; live belum siap
	REPO-REPORTED



Catatan drift: tidak ada perubahan kode baru dibanding baseline V1.1. Namun ringkasan atas PROJECT_STATE.md menyimpan angka lama; ketika mutasi docs diizinkan, tambahkan status terkini tanpa menghilangkan kronologi atau salah menafsirkan baseline.
03. E12-00-T02 — Module Ownership Map terkini
Prinsip: pertahankan pemilik kode existing, jangan menambahkan manager/helper generik. Bidang kredit global dan scheduler baru memerlukan ADR E12-01 sebelum penamaan/DDL final. Semua nama target berikut adalah rencana, bukan kode yang sudah ada.
	Area & owner
	Kondisi kode yang diperiksa
	E12-01 decision / uji acuan

	Scene + import
domain/scene + contracts/package
	4/6/8/10, schema 1.0; scene >10 ditolak
	Source fingerprint; tetap kompatibel; tests/unit/test_scene_duration.py; test_contracts.py

	Job queue
application/services/local_generation_queue.py
	run_until_idle() serial; provider neutral
	Rencanakan facade serial lama; tests/integration/test_local_generation_queue_wave.py

	Job persistence
sqlite_generation_job_repository.py
	schema version 2; claim_next menolak seluruh episode jika RUNNING/ATTENTION
	Isolasi per scene/profile; pertahankan orphan/ambiguity; multi-process transaction tests

	Browser owner
workers/browser/system_chrome_cdp.py + session commands
	Chrome login manual, CDP pasca-login
	Actor per profile harus hormati thread owner; system Chrome unit/Qt tests

	Provider adapter
workers/browser/google_flow_generation.py
	Protocol + fake semantics; belum live selector
	Verifikasi izin, rekening hasil dan 1-submit boundary sebelum live driver

	Download adapter
workers/browser/google_flow_download.py
	Protocol + atomic/no-clobber; belum live selector
	Status post-Generate; result-id stable; test_generated_media_download_foundation.py

	Qt/composition
presentation + bootstrap/main.py
	Shell & services lokal; live queue belum diwiring ke MainWindow
	UI freeze dan approved new views; test_ui_contract.py

	Global accounting
proposed: application/domain + persistence
	Belum ada implementasi credit snapshot/ledger/allocator
	Desain single authority dan outbox projection; ADR E12-01 wajib





04. E12-00-T03 — Kebijakan dan sumber tarif (policy register)
Semua URL berikut adalah dokumentasi resmi publik yang ditinjau pada 08 October 2026, 15:20 WIB. Tidak ada akses ke akun nyata atau klik Generate. Sumber laman dapat berbeda antar bahasa/versi; bukti per akun berasal dari UI resmi pada saat submit, bukan snapshot dokumentasi.
	ID
	Topik & bukti
	Status live

	POL-01
	Harga Omni Flash 720p 4/6/8/10: 7/10/12/15 kredit PER HASIL; 1 request dapat menghasilkan 2 hasil. Sumber P1.
	OBSERVED DOC; harga UI per akun PENDING

	POL-02
	Versi halaman desktop lama memberi 15/20/25/30 dan menyebut kredit gratis hanya model Veo; P2. KONFLIK DOKUMEN.
	CONFLICT → FAIL-CLOSED

	POL-03
	Halaman memulai Flow memuat syarat langganan/jenis akun; tidak membuktikan model boleh digunakan semua profil. P3.
	ENTITLEMENT PER AKUN PENDING

	POL-04
	Halaman fitur model menyebut durasi 4/6/8/10 dan dukungan Omni; tidak membuktikan izin robot/multi-akun. P4.
	CAPABILITY PENDING

	POL-05
	Google Terms melarang akses otomatis yang melanggar instruksi machine-readable dan perilaku melawan persyaratan; P5.
	LIVE AUTOMATION PERMISSION UNKNOWN

	POL-06
	Generative AI prohibited use policy mencakup pembatasan penyalahgunaan; P6. Tidak ada persetujuan spesifik terhadap orkestrasi akun.
	MULTI-ACCOUNT PERMISSION UNKNOWN



P1  https://support.google.com/flow/answer/16526234?hl=id
P2  https://support.google.com/flow/answer/16526234?co=GENIE.Platform%3DDesktop&hl=id
P3  https://support.google.com/flow/answer/16353333?hl=id
P4  https://support.google.com/flow/answer/16352836?hl=en
P5  https://policies.google.com/terms?hl=id
P6  https://policies.google.com/terms/generative-ai/use-policy?hl=id
Putusan ASTRA: tidak ada bukti spesifik dari dokumen publik yang ditinjau bahwa kontrol browser dan penggunaan banyak akun untuk menjalankan scene paralel diperbolehkan. Jangan menafsirkan tidak ditemukan larangan eksplisit sebagai izin. Jika Google menyediakan jalur resmi/API yang cocok, kaji ulang sebagai ADR dan produk; jika tidak, live mutating ditahan. Planner lokal, simulasi, audit data, serta manual-assisted workflow tetap bisa dikerjakan.
Harga catalog: 7/10/12/15 hanya snapshot simulasi bersumber resmi (P1); pastikan UI per akun, model, output_count, dan TTL quote tepat sebelum submit. Bila terdapat konflik 15/20/25/30, status QUOTE_STALE/CONFLICT. Jangan diam-diam mengambil harga termurah.
05. E12-00-T04 — Scope/freeze matrix
	Item
	Keputusan terkunci / konsekuensi

	Target final
	Scan → quote → pembagian scene → Freeze Approval → Generate → pantau → Download → manifest terurut; mode multi-akun bersyarat izin provider.

	Perangkat / distribusi
	Windows 11 x64, portable folder multi-file ZIP; PySide6 UI Indonesia putih/biru.

	UI lama
	30 komposisi frozen + written overrides; tidak redesign.

	UI baru
	E12-02: 9 UI state calon; prompt → STOP → gambar final review → DOCX addendum; dilarang coding UI dulu.

	Input wajib
	Import ZIP/JSON/folder schema 1.0 (image approved+prompt). MP4/SRT langsung belum scope; jika suatu manifest mensyaratkan keduanya maka missing/unreadable menghentikan proses.

	Scene timing
	Audio/SRT Target authoritative. Flow duration 4/6/8/10 ceil; >10 split upstream; output video jangan dipalsukan.

	Provider/model
	Omni Flash 1.1 • 720p • 16:9 tetap frozen; saldo/capability/izin harus live-verified per akun.

	Idempotency
	Satu scene satu attempt submit aktif; unknown post-submit tidak auto-retry atau auto-reassign.

	Output
	Video valid dengan checksum/manifest/download evidence; Generate/Download separate.

	Non-goals
	Tidak auto-login, bypass MFA/CAPTCHA, stealth, penghindaran limit, undocumented API, auto-merger video, TTS, impor SRT/MP4 tanpa revisi kontrak.



06. E12-00-T05 — Source-of-truth dan tindakan yang membutuhkan izin
	Dokumen / lokasi target
	Status sekarang
	Tindakan aman berikutnya

	MASTER_PLAN...V1_1_IMPLEMENTATION_READY_2026-10-08.docx → docs/planning/
	Sudah tersedia lokal, belum disetujui eksplisit
	Pemilik tinjau + approve. Baru setelah izin repo, upload biner ke Flow-Otomatis.

	MASTER_PLAN...V1_0...docx
	Sudah tersedia lokal; jangan timpa
	Jika berguna, arsipkan di docs/planning/master/ dengan nama final berbeda.

	E12_00_ASTRA_BASELINE_GOVERNANCE...docx
	Dokumen lokal ini
	Upload bersama paket authority hanya setelah izin mutasi terpisah.

	PROMPT_HANDOFF_SOL_FLOW_OTOMATIS_V1_1...txt
	Sudah tersedia lokal
	Source-of-truth operasional; commit TXT hanya saat sudah diotorisasi.

	AGENTS.md / TASKS.md / PROJECT_STATE.md
	Ada di repo HEAD
	Sinkronkan status gate hanya setelah izin; jangan menghapus sejarah atau salah klaim PASS.

	docs/ui/frozen UI reference
	Sudah ada
	Tidak diubah. UI addendum baru disiapkan kelak pada E12-02.



Tidak ada perubahan lokal terhadap sumber GitHub dan tidak ada operasi write melalui connector. Gate G0: BLOCKED sampai V1.1 disetujui dan di-upload ke repo beserta referensi relevan. Approval untuk DOCX bukan persetujuan menghabiskan kredit atau menjalankan browser live.


07. Pengamanan arsitektur yang wajib diputuskan E12-01
Bagian ini daftar keputusan, BUKAN membuat kode dan BUKAN melewati E12-01. Dibuat agar SOL tidak menafsirkan overview V1.1 sebagai instruksi langsung migrasi database.
AR-01: Database global akun sebagai satu authority reservasi kredit, lintas proyek; project SQLite tetap projection/riwayat per proyek, bukan authority saldo.
AR-02: Desain single-writer coordinator + durable outbox/inbox untuk menghindari cross-DB 2PC; deteksi crash antara reservasi global dan materialisasi row project. Seluruh operasi memakai idempotency key.
AR-03: Aturan exactly-one active mutation attempt per (project, scene, revision) dengan durable fencing owner, lease token monotonic, UNIQUE constraint, dan recovery safe.
AR-04: Bagaimana WAIT_CREDIT pada scene A memengaruhi scene lain yang aman? Pisahkan project pause dari account pause dan scene ambiguity; jangan blokir satu episode karena satu attention scene tanpa analisis.
AR-05: Kredensial dan browser user-data-dir per profile terisolasi; CDP hanya pasca-login manusia; satu owner thread/browser lifecycle.
AR-06: Reconciliation ketika file MP4 terbit tetapi commit ke SQLite gagal, atau remote result terkirim tetapi browser timeout; harus recheck dengan bukti sebelum izin retry.
AR-07: Merumuskan bukti harga/capability per akun, masa kedaluwarsa snapshot, status tarif berubah, dan bagaimana quote disetujui ulang.
AR-08: Definisikan transisi state job/execution/download global tanpa merombak enum legacy secara destruktif; siapkan v2→v3+ migrasi, backup, dry-run, rollback.
08. Definition of Ready untuk E12-01 dan batas wewenang
	Syarat
	Status
	Keputusan

	Master V1.1 disetujui
	PENDING
	Minta persetujuan eksplisit pengguna.

	Izin upload docs ke Flow-Otomatis saja
	PENDING
	Minta izin eksplisit. Tidak membuat commit tanpa ini.

	Baseline current HEAD identik baseline audit
	PASS
	Bila lanjut, cek ulang HEAD tepat sebelum mutasi.

	UI reference lama di repo dan freeze
	PASS (observed)
	Pertahankan 30-state reference dan overrides.

	Policy untuk perancangan offline
	NON-BLOCKING
	Boleh ADR/prioritas desain berbasis simulasi.

	Policy untuk browser live/multi-akun
	BLOCKED
	Tidak ada live submit, credit polling user profile, atau 2-account pilot.

	Pengujian runtime baru
	NOT RUN
	E12-00 berupa dokumentasi; tidak mengklaim pytest baru.



09. Checklist pelaksanaan dan pengukuran status
	E12-00 task
	Evidence status
	Penilaian

	T01 Baseline + SHA + delta
	main SHA + parent + tree + Actions/PR diinspeksi
	PASS

	T02 Canonical owners
	8 owner group + tests + boundary diinventaris
	PASS

	T03 Policy/harga
	POL-01 sampai POL-06 dengan konflik dan fail-closed
	PASS dokumentasi; live BLOCKED

	T04 Scope/handoff
	Scope/freeze/feature-by-feature disusun
	PASS

	T05 Authority package
	Berkas siap lokal; belum ada persetujuan dan commit
	PREPARED / PENDING

	G0 Docs Authority
	Master approved & commit ke repo
	BLOCKED

	G1 Google Live Policy
	Izin Google untuk mekanisme spesifik
	UNKNOWN / BLOCKED

	G2 Repo Baseline
	Known sha + clean change log dari GitHub
	PASS (read-only)



Kesimpulan: E12-00 audit/read-only COMPLETE; gelar E12-00 keseluruhan = BLOCKED (dokumen authority belum di-approve/commit). Wave E12-01 belum dimulai. Tidak ada klaim CI/APP/live baru. No code/no UI/no GitHub changes.
10. Handoff ASTRA → SOL / AI penerus
Buka repo Flow-Otomatis dan verifikasi git SHA baru vs e560684e; jangan mengandalkan ringkasan lama bila berubah.
Baca V1.0 + V1.1 + E12-00 DOCX, AGENTS.md, TASKS.md, PROJECT_STATE.md, Software Factory V2, final UI references dan architecture ADR.
Jangan mulai coding saat planning gate BLOCKED; jangan push DOCX tanpa perintah khusus pemilik.
Jika pemilik menyetujui V1.1 dan mengizinkan write ke repo, gunakan hanya repo Flow-Otomatis. Simpan berkas source-of-truth dan catat commit/file hash tanpa mengubah kode.
Setelah G0 PASS, ASTRA kerjakan E12-01 untuk menetapkan ADR/schema/state/contracts/rollback; tiap desain masih memerlukan approval sebelum kode.
E12-02 adalah UI prompt stop gate; tidak dilanjutkan hanya dengan kata “lanjutkan” jika prompt belum ditinjau dan UI final belum disetujui.
Sampai G1 live PASS, hanya simulasikan credits dan multi-profile. Jangan melakukan mutasi provider, auto-login atau bypass.
Kondisi berlanjut yang paling tepat sekarang: minta konfirmasi “Saya menyetujui Master Plan V1.1 dan mengizinkan kamu menyimpan paket DOCX/TXT E12-00 ke repo Flow-Otomatis saja; jangan coding.” Setelah itu jalankan sinkronisasi source-of-truth sebagai pekerjaan dokumentasi terpisah.
11. Referensi eksplisit
https://github.com/inoriko920-dev/Flow-Otomatis
https://github.com/inoriko920-dev/Flow-Otomatis/commit/e560684e04ed3a5fad40bb00a91823de68ca5431
https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37734144006
https://github.com/inoriko920-dev/Flow-Otomatis/pull/22
https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/AGENTS.md
https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/TASKS.md
https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/PROJECT_STATE.md
https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/docs/ui/IMPLEMENTATION_OVERRIDES.md
https://support.google.com/flow/answer/16526234?hl=id
https://support.google.com/flow/answer/16526234?co=GENIE.Platform%3DDesktop&hl=id
https://support.google.com/flow/answer/16353333?hl=id
https://support.google.com/flow/answer/16352836?hl=en
https://policies.google.com/terms?hl=id
https://policies.google.com/terms/generative-ai/use-policy?hl=id
FLOW-OTOMATIS  /  ASTRA  /  E12-00  •  Perencanaan baca-saja

