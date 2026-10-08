# ARCHIVE — MASTER PLAN V1.0 / Original text extraction

**Use:** Audit/reference parent for implementation-ready V1.1; newer V1.1 governs task-level details. **Text extraction only**, tables are flattened; not byte-identical DOCX and not substitute for visual DOCX layouts.

**Original DOCX SHA-256:** `2b62e023f50a20da698ee8c47819d1e1246e7b8a6610bf6be27436bd5a02b70a`.

**Coverage:** 30/30 page markers, 17 waves, 45 original test IDs.

---

<PARSED TEXT FOR PAGE: 1 / 30>
                                                                                                 FLOW-OTOMATIS / MASTER PLAN




                                   ASTRA → SOL | MASTER HANDOFF




                                    FLOW-OTOMATIS
END-TO-END GOOGLE FLOW + SMART CREDIT PLANNER
          + MULTI-ACCOUNT EXECUTION


   Perencanaan implementasi komprehensif berbasis audit kode; dibuat untuk
          dilanjutkan di chat/AI lain tanpa mengulang pekerjaan lama



 Kendali dokumen                      Nilai
 Tanggal / zona                       8 Oktober 2026 / WIB (Asia/Jakarta)
 Repository                           https://github.com/inoriko920-dev/Flow-Otomatis
 Branch / commit audit                main / e560684e04ed3a5fad40bb00a91823de68ca5431
 Tahap pabrik software                STEP 12 - Integrations & External Services (IN PROGRESS)
 Otoritas UI                          30 komposisi UI final + docs/ui/IMPLEMENTATION_OVERRIDES.md
                                      1 proyek → N akun berizin → scene dibagi menurut kredit → Generate, rekonsiliasi, Download,
 Tujuan akhir
                                      hasil terurut
 Status dokumen                       PLANNING MASTER V1.0 / belum disetujui sebagai implementasi
 Perubahan GitHub selama
                                      TIDAK ADA. Audit dan penyusunan dokumen baca-saja.
 penyusunan




PENTING: dokumen ini bukan klaim bahwa Google Flow sudah dapat diotomatisasi. Setiap kemampuan
live wajib melalui gate izin layanan, verifikasi akun dan uji nyata.




                           DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 1
<PARSED TEXT FOR PAGE: 2 / 30>
                                                                                          FLOW-OTOMATIS / MASTER PLAN




Peta isi dokumen
Dokumen ini mencakup 27 bagian bernomor (00–26). Cari judul bagian melalui panel Navigasi / Heading di
Microsoft Word untuk berpindah langsung. Semua ketentuan implementasi wajib dibaca bersama lampiran dan
gate.
 Bagian   Pokok bahasan                                  Bagian    Pokok bahasan
 00       Cara menggunakan dokumen ini                   01        Ringkasan eksekutif & kelulusan
 02       Audit kode dan inventaris fitur                03        Otoritas, dependensi & aturan perubahan
 04       Alur end-to-end                                05        Kontrak impor, scan & durasi
 06       Tarif kredit dan quotation                     07        Kredit snapshot/reservation/ledger
 08       Smart Credit Planner                           09        Profil Google & browser worker
 10       Driver Google Flow live                        11        Scheduler paralel & recovery
 12       Download & manifest                            13        Arsitektur dan ports
 14       SQLite & migrasi                               15        UI/UX extension
 16       Keamanan & kepatuhan                           17        45 test cases & QA
 18       17 implementasi waves E12                      19        Gate, DoR/DoD, rollback
 20       Risk register                                  21        Keputusan terkunci vs menunggu
 22       Dokumen & handoff AI                           23        Demo penerimaan
 24       Lampiran struktur data                         25        Matriks dependensi
 26       Referensi resmi & bukti                        —         —




                          DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 2
<PARSED TEXT FOR PAGE: 3 / 30>
                                                                                                  FLOW-OTOMATIS / MASTER PLAN




00. Cara menggunakan dokumen ini
Dokumen ini adalah instruksi rencana, bukan izin melakukan coding, mengubah repo, atau menghabiskan kredit.
SOL wajib membaca bukti baseline dan menjalankan gate satu per satu.

00.1 Urutan baca untuk AI pelaksana
1. Mulai dari AGENTS.md, PROJECT_STATE.md, TASKS.md dan
   docs/software_factory/SOFTWARE_FACTORY_V2_TEXT_GUIDE.md di repository.
2. Periksa seluruh DOCX planning STEP 00-07 yang sudah menjadi source-of-truth, lalu referensi UI final 30-
   state dan override tertulis.
3. Cocokkan commit/branch aktual terhadap baseline audit di dokumen ini; jika berbeda, buat delta audit
   berbasis bukti sebelum coding.
4. Baca dokumen master ini seluruhnya, termasuk tabel risiko, keputusan, test matrix, migrasi, gate live, dan
   prompt handoff di akhir.
5. Jangan mengerjakan integrasi live hingga kebijakan layanan, izin pemilik, dan validasi profil READY setelah
    restart lulus.
6. Kerjakan hanya satu wave implementasi yang sudah melewati Definition of Ready; setiap wave harus punya
   tes dan bukti PASS.

00.2 Klasifikasi pernyataan
    Kode             Arti                                                  Konsekuensi
    TERVERIFIKASI-   Dibuktikan dari file pada main yang dibaca saat
                                                                           Boleh menjadi baseline, tetap cek HEAD sebelum edit.
    KODE             audit.
                     Pernyataan pada dokumen handoff, TASKS, atau          Terima sebagai catatan bukti, jangan samakan dengan uji
    TERCATAT-REPO
                     bukti CI dalam repo.                                  live.
                     Tidak ada bukti penggunaan akun Flow nyata pada
    BELUM-LIVE                                                             Harus melewati uji yang diotorisasi.
                     kondisi ini.
    USULAN           Desain target dari dokumen ini.                       Tidak boleh diklaim sudah ada.
    PENDING-         Memerlukan verifikasi kebijakan/UI atau persetujuan
                                                                           Tahan scope terkait, bukan tebak.
    KEPUTUSAN        pengguna.




00.3 Ringkasan status
STEP 00-11 tercatat PASS pada repository. STEP 12 masih IN PROGRESS. PR #22 yang menangani error layar
Hasil dan ekspor telah merged; 233 pytest, UI 30/30 dan Windows portable PASS menurut laporan CI tertulis.
Namun I12-02B2-LIVE (Generate nyata) dan I12-03-LIVE (Download nyata) belum selesai. Login Google pernah
dilaporkan berhasil, tetapi bukti validasi READY setelah restart aplikasi belum tercatat PASS. [R1-R6]


01. Ringkasan eksekutif dan definisi keberhasilan
01.1 Masalah yang hendak diselesaikan
Saat ini pengguna dapat membuka aplikasi, mengimpor paket episode, memvalidasi Scene ID/gambar/prompt,
memilih durasi 4/6/8/10 detik, menyimpan proyek, memakai profil Google, dan mengakses Gemini Agent read-
only. Namun aplikasi belum mengeksekusi rantai operasional lengkap: membuka konteks Flow yang benar,
mengunggah gambar, menyetel prompt/durasi, mengirim Generate, menunggu hasil, mengunduh MP4, serta
membagi scene dan menghitung kredit antar-akun. UI visual yang menampilkan batch atau hasil tidak otomatis
membuktikan backend live sudah tersambung.

01.2 Sasaran produk yang dikunci
     Satu episode/proyek lokal menjadi sumber kebenaran yang memuat semua SCENE_### serta Target
      Duration dari paket audio/SRT.



                       DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 3
<PARSED TEXT FOR PAGE: 4 / 30>
                                                                                                            FLOW-OTOMATIS / MASTER PLAN



        Jumlah akun aktif dipilih dari akun berizin/siap yang pengguna setujui dan kebutuhan kredit hasil scan; bukan
         angka tetap 2/3/5.
        Scene dengan durasi target ≤4, >4-6, >6-8, >8-10 detik dipetakan ke 4/6/8/10 detik; durasi akhir tetap
         mengikuti target untuk editing.
        Sebelum menjalankan proyek, UI menampilkan total kredit, estimasi per akun, scene yang ditugaskan,
         kekurangan kredit, dan alasan setiap blokir.
        Aplikasi hanya menganggap saldo terverifikasi jika benar-benar memperoleh bukti sah dan segar dari
         layanan; tidak menetapkan otomatis 50.
        Satu scene hanya boleh punya satu submit aktif yang aman. Tidak ada pengiriman ulang diam-diam ketika
         hasil submit tidak pasti.
        Beberapa profil yang telah disetujui dapat bekerja bersamaan hanya jika penggunaan tersebut diizinkan oleh
         aturan Google dan pengguna.
        Semua hasil video yang sukses dikumpulkan ke struktur proyek lokal yang terurut, dan manifest hasil tidak
         boleh mengklaim download yang belum selesai.
        Pause, stop, restart, profil gagal, biaya berubah, dan download gagal harus tertangani tanpa kehilangan
         histori atau menggandakan Generate.
        GUI tetap berbahasa Indonesia, putih-biru dan kompatibel UI final lama; layar/dialog tambahan memerlukan
         proses persetujuan UI.

01.3 Kriteria kelulusan produk akhir
    ID                      Kriteria objektif (harus terbukti)
                            Satu akun berhasil menyelesaikan alur real 1 Scene: siap sesi → Flow project → upload → prompt → setting →
    P-FINAL-01
                            satu submit → result-id stabil → download file valid.
                            Satu proyek berisi berbagai durasi terbagi ke ≥2 profil yang diizinkan, tanpa scene terduplikasi, job hilang, atau
    P-FINAL-02
                            pembengkakan cadangan kredit.
                            Saldo awal, reservasi, biaya yang terkonfirmasi, dan sisa terlapor mempunyai evidence + timestamp serta dapat
    P-FINAL-03
                            direkonsiliasi.
                            Restart saat pre-submit dan post-submit menghasilkan state yang benar; post-submit ambigu tidak langsung
    P-FINAL-04
                            diulang.
    P-FINAL-05              Semua hasil dibuat rapi berdasarkan scene; checksum, ukuran, format dan kaitan source/remote/result terbukti.
    P-FINAL-06              Seluruh frozen UI regression, unit/integration/contract/security/Windows portable PASS; izin/policy tidak dilanggar.
    P-FINAL-07              Dokumentasi source-of-truth, ADR, migrasi, SOP pengguna, audit trail dan handoff untuk AI berikutnya lengkap.




01.4 Non-goals / bukan tujuan proyek ini
        Tidak membuat robot login, CAPTCHA, MFA, stealth, pemecah batas layanan, pencurian cookie/token, atau
         rotasi akun untuk mengelak kuota.
        Tidak membuat layanan cloud multi-user, browser headless server tanpa supervisi, atau API Google Flow
         tidak terdokumentasi.
        Tidak membangun timeline editor video, proses audio/TTS atau video merger; keluaran berupa aset video
         scene terurut dan manifest handoff.
        Tidak merombak UI 30-state lama atau memindahkan repo lama; perubahan hanya pada repo Flow-Otomatis
         setelah semua gate disetujui.
        Tidak mengasumsikan klik Generate selalu berhasil, tarif selalu tetap, semua akun berhak memakai model,
         atau kredit selalu dipotong sama.


02. Bukti audit dan peta fitur yang sudah ada
02.1 Inventaris fitur aplikasi (audit code, bukan klaim live)
    Kapabilitas                 Status               Peran/manfaat                                       Bukti utama
                                                     Buka daftar proyek lokal, warning untuk             MainWindow.show_project_hub /
    Beranda / Project Hub       Ada, wired
                                                     project rusak                                       project_library
                                                     ZIP, manifest JSON, folder via reader domain;       EpisodeImportService /
    Import paket                Ada, wired
                                                     dialog GUI menerima ZIP/JSON                        EpisodePackageReader
                                                     cek image, motion prompt, Target dan Flow
    Scan validasi scene         Ada, wired                                                               scene_planning / workspace_views
                                                     duration




                             DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 4
<PARSED TEXT FOR PAGE: 5 / 30>
                                                                                                               FLOW-OTOMATIS / MASTER PLAN



    Kapabilitas                   Status             Peran/manfaat                                          Bukti utama
                                                     pilih 4/6/8/10; target tidak boleh dilampaui ke
    Duration chooser              Ada, wired                                                                ScenePlanningService
                                                     bawah
    Project SQLite                Ada, wired         workspace tersimpan, browse, recovery rusak            SqliteWorkspaceRepository
                                                                                                            GoogleSessionWorker/
    Google profile                Ada, wired         profil terpisah, login Chrome normal, cek sesi
                                                                                                            SystemChromeCdpPool
                                                     butuh real READY pada app instance
    Restart login gate            Fondasi ada                                                               RestartGatedGenerationProvider
                                                     berikutnya
                                                     hingga 100 key, keyring, health check, pilih
    Gemini Keys                   Ada, wired                                                                GeminiKeyService / Keys view
                                                     manual
                                                     tanya jawab konteks scene; tidak punya alat
    Gemini Agent                  Ada, wired                                                                GeminiAgentService
                                                     untuk tindakan
                                  Ada, tidak         prepare, claim, lease, recovery; tested fake
    Antrean serial                                                                                          LocalGenerationQueueService
                                  dipasang UI        provider
                                                     buka halaman resmi/cek reachable, bukan
    Google Flow preflight         Fondasi                                                                   GoogleFlowPreflightWorker
                                                     Generate
    Google Flow Generate          Kontrak saja       driver submit-one tanpa selector live                  google_flow_generation.py
    Google Flow Download          Kontrak saja       driver download-one tanpa selector live                google_flow_download.py
    Hasil & handoff               Ada, wired         status dari DB; ekspor hasil atomik saat siap          LocalResultsService/results_view
                                  UI fixture         visual state belum setara backend operasi
    Diagnostik / Pengaturan                                                                                 fixtures.py / screen_factory.py
                                  dominan            penuh
                                                                                                            New scoped modules; ownership to be
    Credit monitor / allocator    Tidak ada          perlu data dan mesin baru
                                                                                                            decided
                                                     queue saat ini serial dan blocker tingkat
    Multi-profile parallel        Tidak ada                                                                 GenerationJobRepo.claim_next
                                                     episode




02.2 Peta modul utama dan aturan reuse
    File/owner saat ini                               Jangan dibongkar                                 Ekstensi yang diusulkan
                                                                                                       Wiring tersertifikasi untuk
                                                      Jangan ubah tanggung jawab
    bootstrap/main.py                                                                                  scheduler/credit/account/browser setelah
                                                      composition root
                                                                                                       gate.
                                                                                                       Pisahkan quotation dan plan assignments;
    domain/scene/model.py                             4/6/8/10, readiness, scene id
                                                                                                       tidak paksa kredit ke scene base.
                                                                                                       Versi tambahan kompatibel; adapter
    contracts/package/import_manifest.py              Schema 1.0 dibaca dan divalidasi
                                                                                                       SRT/MP4 hanya bila disetujui.
                                                      Fingerprint, anti-duplicate, result              Jadikan core reusable atau orchestrated
    application/services/local_generation_queue.py
                                                      ownership                                        per-account; jangan copy logic.
    infrastructure/persistence/                       Transaction, lease,                              Migrasi v2→v3+; claim per-account dengan
    sqlite_generation_job_repository.py               mark_submit_started                              isolasi unik dan snapshot.
                                                                                                       Profile-affine worker; operasi Playwright
    workers/browser/system_chrome_cdp.py              Login manual terpisah dari CDP
                                                                                                       hanya thread pemilik.
                                                      Satu permintaan/satu submit, outcome             Tambah implementation live di
    workers/browser/google_flow_generation.py
                                                      typed                                            adapter/driver setelah selector disahkan.
                                                                                                       Implement hasil nyata yang bersumber dari
    workers/browser/google_flow_download.py           Temp file unik, no-clobber, errors typed
                                                                                                       remote result stabil.
    application/services/                                                                              Rangkaian scheduler post-GENERATED
                                                      Download tidak otomatis Generate
    generated_media_download.py                                                                        dengan status terpisah.
                                                                                                       Tambahkan event/callback layar baru
    presentation/main_window.py                       UI shell/frozen visual, konteks Agent
                                                                                                       setelah UI approval.
                                                                                                       Jangan kaitkan kuota Gemini API dengan
    application/services/gemini_keys.py               Keyring+aktivasi manual
                                                                                                       kredit Flow.
    docs/ui/                                                                                           Extension hanya setelah gambar UI
                                                      30 UI komposisi final
    04_STEP_04_FINAL_UI_REFERENCE...docx                                                               tambahan disetujui.




02.3 Hasil audit teknis yang memengaruhi desain
      LocalGenerationQueueService.run_until_idle() mengeksekusi serial melalui run_next(); belum ada pemilihan
       akun pada GenerationRequest maupun job.
      Repo claim_next() saat ini menolak klaim tambahan jika episode memiliki RUNNING atau
       ATTENTION_REQUIRED; multi-akun butuh perubahan transaksi dan batas isolasi, bukan menambah thread
       saja.
      google_flow_generation.py dan google_flow_download.py secara eksplisit menyebut belum memiliki live
       selector; driver hanyalah Protocol/provider adapter.


                                 DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 5
<PARSED TEXT FOR PAGE: 6 / 30>
                                                                                                        FLOW-OTOMATIS / MASTER PLAN



      bootstrap/main.py menyuntikkan repository jobs dan download ke LocalResultsService, tetapi tidak
       memasang LocalGenerationQueueService/Generate provider ke MainWindow.
      GoogleSessionDriver memeriksa URL myaccount.google.com sebagai READY; status itu tidak membuktikan
       Flow model tersedia, kredit cukup, atau perizinan proyek.
      Input contract hanya menerima target_duration_s >0 dan ≤10; scene >10 harus dipecah upstream atau
       dikembangkan melalui revisi kontrak yang sah.
      UI start/status memiliki elemen statis (“Online”, “Autosave aktif”); nanti indikator operasional kritis tidak boleh
       diturunkan dari label dekoratif.
      Riwayat Generate/Download dipisah; PR #22 memperbaiki error bounds Hasil dan ekspor, sehingga perlu
       mempertahankan error containment tersebut.
      PR #22: 233 pytest, 30/30 UI, portable ZIP menurut laporan CI; ini bukan live Flow test.

02.4 Klasifikasi gate existing
    Gate existing                  Status audit                               Aturan lanjut
    STEP 00–11                     PASS menurut repo                          Tidak diulang tanpa delta spesifik.
    STEP 12 safe foundation        PRE-LIVE READY                             Reusable untuk kode/live sesudah gate.
                                   Manual login dilaporkan bekerja; restart   Pemilik harus memastikan READY, tutup aplikasi, buka
    I12-01 login
                                   belum terbukti                             kembali, READY + restart LULUS.
    I12-02B2-LIVE                  BLOCKED                                    Satu scene satu submit; belum boleh dianggap selesai.
    I12-03-LIVE                    BLOCKED                                    Mulai hanya setelah result-id live terbukti.
    PR #22 / Hasil                 MERGED, automated PASS                     Jangan regress; baseline 233 tests.
    Smart Credit + Multi-account   BELUM ADA                                  Planning/UI gate terlebih dahulu.




03. Aturan otoritas, dependency, dan tata kelola perubahan
03.1 Source of truth (urutan prioritas operasional)
1. Perintah terbaru pengguna yang eksplisit dan sah.
2. AGENTS.md dan aturan safety/arsitektur repo.
3. PROJECT_STATE.md + TASKS.md + ADR existing untuk gating.
4. Dokumen planning final dan UI reference yang sudah disetujui + IMPLEMENTATION_OVERRIDES.md.
5. Kontrak domain/schema + test yang aktif di commit HEAD.
6. Dokumen master ini sebagai ekstensi yang belum menggantikan planning/UI lama.
7. Tangkapan layar Flow real yang diperoleh secara berizin saat gate live (bukan selector hasil tebakan).

03.2 Aturan pengembangan tidak dapat dinegosiasikan
      Sebelum coding: commit DOCX master yang telah disetujui, DOCX referensi UI final tambahan, status/ADR
       dan handoff ke repo yang sama; jika belum lengkap, STOP.
      Bila diperlukan UI baru: buat prompt desain UI, WAJIB STOP untuk review; gambar final diperiksa/revisi lalu
       disatukan dalam satu DOCX sebelum implementasi UI.
      ASTRA merencanakan/memutuskan cross-cutting; SOL baru melakukan coding setelah gate planning dan UI
       PASS.
      Buat branch terfokus per wave; jangan force-push, reset, overwrite, atau mengubah repo lain.
      Sebelum setiap wave: bandingkan HEAD dan working tree; seluruh temuan diverifikasi terhadap file aktual.
       Pembaruan status hanya berdasarkan bukti.
      Dilarang menyimpan kredensial Google, cookies, session profile, token, OTP/MFA, atau API key dalam
       GitHub, dokumentasi, log, ZIP output, dan screenshot.
      Jika halaman Google, model, quota, tarif, izin, atau Terms belum terverifikasi: fail-closed dengan status jelas,
       tidak mengarang data.
      Tidak ada klaim “fully automatic” sebelum seluruh live test berhasil dan dicatat dengan bukti teranonim.




                              DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 6
<PARSED TEXT FOR PAGE: 7 / 30>
                                                                                                     FLOW-OTOMATIS / MASTER PLAN




03.3 Pemisahan tanggung jawab
 Pihak              Boleh                                                        Tidak boleh tanpa persetujuan/gate
 ASTRA              audit, desain, ADR, test matrix, dokumen, review status      coding lintas boundary tanpa otorisasi
                    implement 1 wave sesuai DoR, tulis tes, jalankan CI,         melompat wave, modifikasi UI frozen, live mutation
 SOL
                    ajukan PR                                                    sebelum gate
                    pilih profil, login manual, tinjau UI, setujui plan/live
 Pengguna/pemilik                                                                diminta membagikan password atau cookie
                    submit
                                                                                 mengambil identitas profil rahasia, retry mutasi ambigu,
 Aplikasi           validasi, simulasi, tindakan yang disetujui, monitor hasil
                                                                                 evasi batas




04. Alur kerja end-to-end yang ditargetkan
04.1 Perjalanan pengguna
1. Buka aplikasi → tampilkan proyek terakhir, status kredensial non-rahasia, dan state proses nyata (bukan label
   statis).
2. Impor paket episode valid → parse manifest, cek SCENE ID unik, gambar approved, motion prompt, Target
    Duration, selected duration, dan sumber file.
3. Lakukan Scan dan Validasi → scene keliru diberi alasan spesifik; scene >10 ditandai perlu split upstream;
    tidak membuat Generate dari input rusak.
4. Pilih parameter produksi yang disetujui: model Omni Flash kompatibel, 720p, 16:9, hasil per request, durasi,
   dan kebijakan retry.
5. Pilih daftar profil Google yang berizin → lakukan cek sesi, cek akses Flow/model, cek kredit aktual (read-only)
   dan timestamp pemeriksaan.
6. Klik Hitung Rencana → quote biaya immutable sesuai versi harga, scene dipasangkan ke akun terpilih;
   tampilkan total, sisa, dan yang tidak tertampung.
7. Lakukan koreksi manual pilihan akun/assignment/durasi jika diperlukan, lalu Freeze Plan dan minta
    persetujuan berdasarkan ringkasan kredit.
8. Jalankan pilot satu scene → hanya jika passed; berikutnya akun tunggal serial end-to-end, baru naikkan
    concurrency ke 2 dan seterusnya.
9. Setiap akun mempunyai worker yang memvalidasi prasyarat, melakukan satu submit aman, menunggu bukti
   result-id, lalu mengantrekan download terpisah.
10. Saldo diperbarui setelah outcome yang dapat dikonfirmasi; akun yang kreditnya kurang/stale tidak menerima
    job baru.
11. Periksa hasil dan retry yang eksplisit; ekspor manifest hasil ketika syarat lengkap, jaga output terurut
    berdasarkan SCENE ID.
12. Jika aplikasi ditutup saat bekerja, simpan state; saat dibuka lagi lakukan rekonsiliasi read-only sebelum
    mengizinkan mutasi tambahan.

04.2 State yang wajib terlihat di UI
 Tingkat                 Status minimum                                                   Operator action
                         DRAFT, PLAN_READY, RUNNING, PAUSING, PAUSED,                     Lihat peringatan, setujui ulang plan, resume
 Proyek
                         WAIT_CREDIT, ATTENTION, COMPLETED, CANCELLED                     setelah alasan selesai
                         UNKNOWN, LOGIN_REQUIRED, READY_CHECKED,
                                                                                          Buka login manual, perbarui sesi/kredit,
 Akun                    FLOW_UNAVAILABLE, CREDIT_UNKNOWN,
                                                                                          pilih/nonaktifkan
                         CREDIT_LOW, BUSY, RATE_LIMITED, SUSPENDED
                         INVALID, READY, QUEUED, RESERVED, CLAIMED,
 Scene / Generate        PRE_SUBMIT, SUBMIT_UNCERTAIN, ACCEPTED,                          Periksa bukti, approve retry jika aman
                         GENERATING, GENERATED, FAILED_SAFE, ATTENTION
                         NOT_READY, QUEUED, DOWNLOADING, DOWNLOADED,
 Scene / Download                                                                         Unduh ulang yang terbukti aman, pilih take
                         FAILED, ATTENTION
                         UNVERIFIED, OBSERVED, USER_ENTERED,                              Sumber/timestamp jelas; blokir jika konflik
 Kredit
                         RESERVED_LOCAL, RECONCILING, CONFLICT                            serius



                       DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 7
<PARSED TEXT FOR PAGE: 8 / 30>
                                                                                                            FLOW-OTOMATIS / MASTER PLAN




Catatan implementasi: state baru adalah desain konseptual. Hindari mengganti enum yang sudah dipakai schema
lama secara destruktif. Gunakan versioned mapping atau state terpisah yang dapat dimigrasikan.


05. Kontrak input, scan scene, dan durasi
05.1 Kontrak lama yang harus dipertahankan
Schema impor existing v1.0 mensyaratkan episode_id, project_name, production_profile, scene_count, scenes,
created_at dan source_versions. Setiap scene berisi scene_id SCENE_###, target_duration_s (0,10],
recommended_flow_duration_s, selected_flow_duration_s opsional, image_file, motion_prompt, model,
resolution, aspect_ratio, status, dan trim_target_s yang harus cocok Target. [R7]

05.2 Hasil ScanReport target
    Field                                   Definisi / validasi
    scan_id / workspace_version             identitas hasil scan immutable; berkaitan dengan source SHA dan saat scan.
    total / ready / invalid_scene_count     jumlah scene sesuai manifest; keadaan derived bukan dipalsukan.
    scene_id / source_time_range            ID unik dan posisi target source untuk handoff; jika timestamp belum ada jangan karang.
    target_duration_s                       durasi authoritative dari paket audio/SRT; numeric finite >0.
    recommended_flow_duration_s             ceiling 4/6/8/10; untuk target>10 hasil BLOCK_SPLIT.
    selected_flow_duration_s                pilihan final disetujui; >= Target dan anggota set valid.
    image_file / image_sha256               approved image readable, safe path, digest sebelum submit.
    prompt / prompt_sha256                  motion prompt nonempty, canonical digest, redaksi sensitif.
    model/resolution/aspect                 nilai frozen 1.1/720p/16:9 sampai extension diratifikasi.
    estimated_generations                   jumlah hasil per request (default 1 hanya setelah diverifikasi).
    readiness_codes                         array alasan blocking; actionable.
    tariff_quote_id / credit_estimate       dari price catalog, bukan hasil scan file mentah sendiri.




05.3 Aturan durasi yang tidak boleh ditawar
      durasi_target <= 0                     -> INVALID_DURATION
      0 < durasi_target <= 4                 -> rekomendasi 4 detik
      4 < durasi_target <= 6                 -> rekomendasi 6 detik
      6 < durasi_target <= 8                 -> rekomendasi 8 detik
      8 < durasi_target <= 10                -> rekomendasi 10 detik
      durasi_target > 10                     -> BLOCK_SPLIT (jangan submit)
      selected_duration < target             -> BLOCK_SELECTION
      trim_target_s != target               -> INVALID_MANIFEST


05.4 Cara menangani scene lebih dari 10 detik
      Pertahankan alur existing yang mewajibkan split upstream. Jangan diam-diam memangkas target audio
       menjadi 10 detik.
      Jika menambah split wizard suatu hari, itu scope independen: pembagian berdasarkan timestamp SRT, suffix
       Scene ID yang kompatibel, crossfade/overlap hanya setelah konfirmasi, dan rekonsiliasi aset.
      Sementara, UI harus mengembalikan daftar scene yang melanggar agar proyek tetap dapat diperbaiki di alat
       pembuat paket.
      Jika sumber MP4/SRT diwajibkan oleh manifest/fitur yang disetujui dan tidak ada/tidak terbaca, proses harus
       berhenti sebelum menulis job.

05.5 Validasi dan keamanan input
      Baca gambar melalui resolver yang sama dengan EpisodePackageReader; tidak menerima traversal,
       absolute path tak sah, NUL, symlink/hardlink mencurigakan.
      Rehash gambar dan prompt pada tahap Freeze Plan dan tepat sebelum submit; perubahan membuat
       REQUEST_STALE, bukan submit isi lama.
      Validasi scene_count, scene IDs, schema_version, encoding UTF-8, duplikat, ZIP bomb, file ukuran 0, dan
       izin baca.


                                DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 8
<PARSED TEXT FOR PAGE: 9 / 30>
                                                                                            FLOW-OTOMATIS / MASTER PLAN



       Input eksternal/prompt dianggap DATA tak terpercaya, tidak boleh mengeksekusi perintah untuk mengubah
        setting atau izin.
       Deteksi duplikat proyek tidak boleh menimpa riwayat pekerjaan/download yang sudah ada.


06. Tarif resmi Google Flow dan mesin quotation
06.1 Data harga terverifikasi 8 Okt 2026
Sumber utama: Google Flow Help “Manage your Google Flow credits”, ditinjau 8 Oktober 2026. Harga adalah per
generation/output, bukan selalu per request. Google menyatakan limit bisa berubah dan harus diperiksa kembali
pada Settings/Options di UI saat eksekusi. [G1]
    Produk                                 4 detik   6 detik         8 detik   10 detik   Catatan
                                                                                          Sasaran utama aplikasi; ketersediaan
    Gemini Omni Flash 720p                 7         10              12        15
                                                                                          akun harus diverifikasi.
                                                                                          HANYA skenario masa depan; kontrak
    Gemini Omni Flash 360p                 4         5               6         7
                                                                                          repo sekarang terkunci 720p.
                                                                                          Biaya per generasi non-Ultra;
    Veo 3.1 Lite                           10        10              10        —
                                                                                          entitlement berbeda.
    Veo 3.1 Fast                           20        20              20        —          Bukan target frozen Omni Flash.
    Veo 3.1 Quality                        —         —               100       —          Bukan target frozen Omni Flash.


Catatan bukti: sumber versi bahasa yang berbeda memuat informasi kompatibilitas kredit gratis yang tidak
sepenuhnya konsisten, misalnya halaman berbahasa Indonesia lama menyebut kredit gratis hanya untuk Veo.
Karena itu rencana TIDAK menjamin akun gratis dapat memakai Omni Flash. Capability model harus dibuktikan
untuk tiap profil pada UI resmi dan jika tidak tersedia, status UNSUPPORTED / STOP. [G1, G2]

06.2 Aturan katalog harga versi
       Gunakan katalog tariff immutable dengan model canonical_id, provider_display_name, resolution, duration,
        generation_count, cost_per_generation, source_url, last_verified_at, availability_scope, pricing_version.
       Harga default berasal dari sumber resmi bertanggal, tetapi ditampilkan sebagai ESTIMASI hingga tombol
        Options Flow / status biaya aktual terverifikasi per profil.
       Setiap project plan mengunci price_catalog_version + quote_id + valid_until. Bila tarif berubah
        sebelum/selama eksekusi, blokir job baru dan tampilkan delta agar pengguna setuju kembali.
       Biaya satu permintaan = credit_per_generation × jumlah hasil yang benar-benar diminta/terkonfirmasi. Jika UI
        membuat 2 hasil, estimasi harus mengalikan 2; jangan sembunyikan biaya.
       Model yang tidak sesuai kontrak frozen tidak boleh dipilih diam-diam karena lebih murah. Penambahan 360p
        atau Veo memerlukan keputusan produk, UI, schema, test dan gate kompatibilitas.
       Bila UI Flow memunculkan harga berbeda dari dokumentasi atau katalog, harga UI aktual yang terbukti dan
        disetujui mengendalikan submit; jika tak dapat dibaca, hentikan otomatisasi.

06.3 Formula yang harus diuji
        scene_cost_i = tariff(model_i, resolution_i, duration_i, entitlement_i) * output_count_i
        project_estimate = SUM(scene_cost_i for all VALID + SELECTED scenes)
        account_available_a = max(observed_balance_a - local_reserved_a - safety_hold_a, 0)
        plan_feasible = (forall scene: assigned_account has enough balance)
                        AND policy_permission_valid
                        AND quote_fresh
                        AND compatible_model
        saldo akhir = OBSERVASI PROVIDER; bukan "saldo awal - estimasi" sebagai fakta.


06.4 Contoh perhitungan 12 scene / tiga akun
    Akun              Durasi scene                             Jumlah kredit                      Sisa dari saldo awal 50
    A                 4s + 10s + 8s + 4s                       7+15+12+7=41                       9
    B                 6s + 8s + 10s + 4s                       10+12+15+7=44                      6
    C                 4s + 6s + 6s + 8s                        7+10+10+12=39                      11
    TOTAL             12 scene campuran                        124                                26 dari 150




                             DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 9
<PARSED TEXT FOR PAGE: 10 / 30>
                                                                                                    FLOW-OTOMATIS / MASTER PLAN



Contoh ini hanya simulasi kapasitas, bukan bukti akun benar-benar memiliki 50 kredit atau berhak menjalankan
model. Minimal teoritis 3 akun dari 124/50, tetapi pemilihan riil wajib memperhitungkan saldo terverifikasi,
eligibility, policy, dan kualitas jadwal.

06.5 Aturan refresh, langganan, dan credit pool
      Google Help menyebut 50 kredit harian dan siklus terkait generasi pertama; kredit harian tidak rollover.
       Jangan mengisi 50 otomatis saat pukul 00.00 WIB atau setelah sleep.
      Pengguna berlangganan bisa memiliki tambahan kredit bulanan; jangan menjumlah berdasarkan label paket
       tanpa membaca alokasi yang benar-benar berlaku/ditampilkan.
      Sumber kepastian dibedakan: OBSERVED_UI; OFFICIAL_ACCOUNT_PAGE; USER_DECLARED;
       ESTIMATED; UNKNOWN. Hanya OBSERVED yang segar dapat membuka auto-submit pada mode strict.
      Jika kredit provider terlihat terkumpul lintas layanan/perangkat, aplikasi harus siap saldo berubah karena
       aktivitas di luar aplikasi.
      Ketika saldo sulit dibaca atau tidak memiliki antarmuka yang stabil, sediakan input manual sebagai
       perencanaan saja, dan minta verifikasi akhir sebelum submit.


07. Monitor kredit: snapshot, reservation, ledger, reconciliation
07.1 Empat besaran yang harus dibedakan
    Besaran              Sifat                                                  Boleh ditampilkan sebagai
                         Bukti langsung dari halaman resmi yang terverifikasi
    Observed balance                                                            Saldo terverifikasi (terakhir diperiksa HH:MM WIB).
                         dan time-stamped.
                         Alokasi sementara untuk pekerjaan yang telah
    Local reservation                                                           Dicadangkan lokal (bukan potongan Flow).
                         dijadwalkan/claimed.
    Expected spend       Kalkulasi tarif dari request freeze.                   Estimasi penggunaan.
    Confirmed spend      Delta yang sudah diobservasi/statement provider.       Biaya terkonfirmasi dengan bukti.




07.2 Kontrak CreditSnapshot
      CreditSnapshot {
        profile_id: UUID;
        observed_balance: int | null;
        currency: "FLOW_CREDITS";
        account_entitlement: "FREE" | "PAID" | "UNKNOWN";
        provider_model_eligibility: map<model, status>;
        source: "FLOW_UI" | "ACCOUNT_PAGE" | "USER_DECLARED" | "UNKNOWN";
        confidence: "VERIFIED" | "MANUAL" | "STALE" | "UNAVAILABLE";
        observed_at_utc: timestamp | null;
        expires_at_utc: timestamp | null;
        next_refresh_at_utc: timestamp | null; // only if verified
        price_version: string | null;
        evidence_digest: sha256 | null; // sanitized, no cookies/screenshots secrets
      }


07.3 Ledger dan reservasi atomik
      Saat scheduler memberi scene pada akun, lakukan transaksi ACID: check account eligible, quote valid, saldo
       usable cukup, scene belum punya active claim; baru tulis assignment + reservation + lease dalam satu
       transaksi.
      Gunakan ledger append-only (event_id, job_id, attempt_id, account_id, event_type, expected_amount,
       confirmed_amount nullable, observed_balance nullable, timestamp, evidence hash).
      Tipe event: PLAN_QUOTED, RESERVED, SUBMIT_STARTED, PROVIDER_BALANCE_OBSERVED,
       PROVIDER_SPEND_CONFIRMED, RESERVATION_RELEASED, RECONCILIATION_CONFLICT,
       REFUND_OBSERVED, CREDIT_REFRESH_OBSERVED.
      Jangan menghitung saldo dengan menambahkan/mengurangi transaksi yang sama dua kali; gunakan
       idempotency key unik untuk ledger.
      Setelah SubmitStarted dengan outcome UNKNOWN, reservasi tidak otomatis dibebaskan; simpan status
       PENDING_RECONCILIATION agar scene dan saldo tidak dipakai lagi.

                        DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 10
<PARSED TEXT FOR PAGE: 11 / 30>
                                                                                                        FLOW-OTOMATIS / MASTER PLAN



      Saat Generate gagal SAFE_FAILURE, observasi provider bisa membuktikan tidak ada debit; bila belum ada
       bukti, jumlah biaya menjadi UNKNOWN dan tidak diakui nol.
      Perubahan kredit dari luar aplikasi tidak boleh dianggap “bug aplikasi”; lakukan delta reconciliation terpisah
       dan pemberitahuan.
      Satu akun yang berada pada CREDIT_UNKNOWN atau CONFLICT tidak menerima job baru; akun sehat lain
       hanya lanjut jika tidak melanggar aturan akun/layanan.

07.4 Jadwal refresh yang aman
    Pemicu                        Aksi read-only                                             Jika gagal
    Profil dibuka                 periksa sesi, Flow entitlement, kredit jika UI mendukung   CREDIT_UNKNOWN + tanda waktu
    Sebelum Freeze Plan           refresh semua akun terpilih dan quote                      jangan bisa Start dalam strict mode
    Tepat sebelum claim/submit    cek TTL saldo + reservation + harga                        blokir job terkait
    Hasil Submit terkonfirmasi    amati saldo/delta setelah stabil                           RECONCILING, bukan membuat debit palsu
    Generate gagal/timeout        rekonsiliasi read-only remote job dan saldo                ATTENTION, no automatic retry
    Klik Perbarui Kredit          probe ulang tanpa mutasi produksi                          sajikan alasan kegagalan
    Aplikasi restart              reconcile semua lease/reservasi sebelum resume             Pause project jika outcome ambigu




08. Smart Credit Planner: perencanaan multi-akun
08.1 Hasil yang wajib dikeluarkan planner
      Daftar scene VALID, durasi, cost quote, hasil per request, resource fingerprint, dan prioritas urutan output.
      Daftar profil berizin yang eligible dengan saldo usable yang benar-benar diketahui dan masa berlaku
       pemeriksaannya.
      Assignment scene→account yang deterministik, dengan alasan keterpilihan, expected cost, urutan per-
       account, estimasi residual credit, dan concurrency cap.
      Alternatif rencana: hemat akun (min akun aktif), seimbang (estimasi makespan), atau manual-assisted;
       pilihan utama user: Otomatis Pintar + Koreksi Manual.
      Scene tidak tertampung diberi status WAIT_CREDIT atau BLOCKED_MODEL/LOGIN/POLICY/UNKNOWN;
       jangan mengklaim semuanya bisa jalan.
      Jejak keputusan: algorithm_version, seed (jika ada), quote/version, input hash, tie-breakers, dan audit
       timestamp.

08.2 Aturan optimasi deterministik
Masalah ini adalah penempatan item dengan kapasitas (bin-packing) plus syarat readiness, biaya, urutan, dan
waktu kerja. Jangan menjanjikan hasil global optimum untuk jumlah scene besar. Implementasikan greedy
deterministik + bounded local improvement, dengan exact solver opsional untuk dataset kecil bila dapat
dibuktikan.
      INPUT: valid_scenes, accounts(opted-in), quote_version, credit_snapshots
      FILTER: exclude ineligible, session_not_ready, stale_credit, policy_blocked
      FOR scene: require duration selected, compatible model, cost > 0
      SORT scenes: cost DESC, target_time ASC, scene_id ASC
      FOR each scene:
         candidates = eligible_accounts with usable_credit >= scene.cost
         IF none: mark WAIT_CREDIT (no mutation)
         ELSE choose by configured objective and stable tie breakers
              (estimated load, leftover capacity, profile_id)
              reserve in PLAN ONLY; do not spend provider credits
      IMPROVE: bounded pairwise swap; never break capacity or readiness
      OUTPUT: immutable DraftPlan + explainability + checksum
      USER REVIEW → PlanFreeze with approval and per-job allocation
      DISPATCH: revalidate account/session/credit/policy just-in-time




                             DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 11
<PARSED TEXT FOR PAGE: 12 / 30>
                                                                                                              FLOW-OTOMATIS / MASTER PLAN




08.3 Dua mode objective + satu mode manual
    Mode                              Prioritas                                                    Catatan
                                      Minimalkan jumlah akun opt-in yang aktif kemudian            Tidak berarti bebas menambah akun demi
    Hemat akun
                                      fragmen saldo                                                bypass limit.
                                                                                                   Perlu durasi proses historis yang anonim;
                                      Ratakan estimasi waktu kerja agar progres multi-akun
    Seimbang                                                                                       tanpa bukti gunakan durasi sebagai proksi
                                      masuk akal
                                                                                                   kasar saja.
    Otomatis Pintar + Koreksi         Planner merekomendasi, pengguna boleh memindah               Perubahan harus revalidate credit, fingerprint
    Manual                            scene yang masih queued                                      dan beku ulang.
                                                                                                   Tetap ada validasi biaya, model, quota dan
    Manual penuh                      Operator pilih setiap akun/scene
                                                                                                   batas concurrency.




08.4 Kebijakan perubahan rencana saat eksekusi
      Hanya QUEUED yang belum claim dapat dipindahkan otomatis setelah pengguna menyetujui perubahan;
       RUNNING, SUBMIT_STARTED, GENERATED dan AMBIGUOUS tidak dapat “dipindah begitu saja”.
      Replanning baru menghasilkan revision ID baru, diff (scene moved, account changed, cost delta), dan
       approval baru; rencana lama diarsip tidak dihapus.
      Jika satu akun gagal login dan job belum submit, job yang safe dapat kembali ke pool setelah lease dilepas
       berdasarkan bukti.
      Jika credit residual akun tidak memenuhi biaya scene terkecil, akun berhenti menerima job baru dan
       menampilkan sisa saldo.
      Planner tidak boleh memaksakan penggunaan semua akun karena targetnya adalah proyek selesai sesuai
       izin, bukan mengonsumsi semua kredit.

08.5 Ketentuan keluaran preview
      Ringkasan contoh: 60 scene, 12 invalid, 48 ready; total kebutuhan kredit dihitung dari durasi scene valid dan
       harga terkini, bukan angka tetap.
      Rincian setiap akun: label aman, status READY setelah restart, last credit check, kredit tersedia, reserved,
       scene count, daftar Scene ID, remaining estimate.
      Tunjukkan biaya total berdasarkan generation count; bila sekali klik menghasilkan 2 video, data dan total
       kredit langsung berubah.
      Warning: saldo belum terverifikasi, tarif berubah, paket model tidak tersedia, akun tidak diizinkan, scene
       output belum jelas, atau project Flow account mismatch.
      Tombol Start hanya aktif setelah semua gate; jika sebagian scene WAIT_CREDIT, user boleh memilih
       jalankan subset yang aman dengan menyadari project belum lengkap.


09. Profil Google, hak akses, dan browser worker
09.1 Pertahankan login yang sudah dibangun
Alur existing: Google Chrome terpasang dibuka normal untuk login manual (tanpa CDP), setelah selesai
pengguna menutup jendela tersebut, kemudian Cek Ulang Sesi menggunakan Chrome profil yang sama dan
CDP localhost. `RestartGatedGenerationProvider` hanya meneruskan Generate jika sesi masih READY dan telah
terbukti READY setelah aplikasi direstart. Jangan merombak atau melewati flow ini. [R8]

09.2 Akun Flow bukan Gemini API key
Google Flow profile adalah browser profile berizin. Gemini API key hanya untuk AI Agent yang sudah ada, dipilih
manual. Satu layanan bukan bukti kredit/kuota layanan lain; jangan lakukan account/key rotation otomatis untuk
mengelak rate/usage limits.

09.3 Account registry target
    Kolom                                         Keterangan
    profile_id, user_label                        Id acak lokal, display name sanitasi; tidak ada email wajib di export.
    session_state, restart_proof                  status Google login actual; READY_AFTER_RESTART gate.



                                DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 12
<PARSED TEXT FOR PAGE: 13 / 30>
                                                                                                     FLOW-OTOMATIS / MASTER PLAN



    Kolom                                  Keterangan
    flow_access_state, observed_at         Flow reachable dan hak memakai model tertentu.
    approved_for_project, approval_at      persetujuan eksplisit proyek tertentu, tidak menyiratkan semua proyek.
    max_concurrent_jobs                    default 1 per akun; kenaikan memerlukan live evidence/izin.
    browser_worker_id                      owner thread/process untuk Playwright/CDP page; tidak share silang thread.
    credit_snapshot_id                     reference data kredit, bukan isi saldo disamarkan sebagai fakta.
    remote_flow_project_id/url_safe        project Flow terikat akun, tanpa token/cookie/query rahasia.
    policy_status                          APPROVED, RESTRICTED, UNKNOWN; stop jika UNKNOWN untuk mutasi.
    last_provider_error                    kode non-rahasia untuk triage.




09.4 Model worker paralel
      Satu worker aktor per profil (browser-affine) atau desain isolated process yang aman; Playwright sync API
       dan page harus dimiliki oleh thread/process yang sama sepanjang lifecycle.
      Tidak boleh membuka dua Chrome yang mengunci user-data-dir sama secara bersamaan; pool harus
       mengenali state manual-login vs debug attach.
      Global scheduler hanya mengirim command typed lewat message queue dan menerima evidence typed;
       tidak boleh memegang objek Page/Browser lintas-thread.
      Batas aktif efektif = min(izin pengguna, jumlah akun siap+eligible, batas kebijakan provider, batas sumber
       daya mesin, pembatasan per akun).
      Setiap worker harus mendukung idempotent Stop request, cancel pre-submit, timeout terkontrol dan
       structured result; Qt event loop harus tetap responsif.
      Jangan memaksa website dengan stealth/fingerprint masking, captcha bypass, request privat yang tidak
       terdokumentasi, proxy pool, atau simultaneous profile clones.
      Jika penggunaan multi-akun untuk menambah kuota tidak diizinkan oleh Google, fitur tersebut harus
       dibatasi/ditolak; planner masih bisa dipakai untuk simulasi tanpa mengirim job.

09.5 Gate akun siap
      account_can_generate =
          profile_selected_by_user
          AND policy_review_pass
          AND session_state == READY
          AND restart_gate == PASS
          AND flow_access == REACHABLE
          AND requested_model_available == TRUE
          AND credit_snapshot.confidence == VERIFIED
          AND quote_is_fresh
          AND available_after_reserve >= job_cost
          AND no_conflicting_profile_worker



10. Driver Google Flow LIVE: dari open → submit → result-id
10.1 Prasyarat keras sebelum membuat selector live
      Verifikasi kebijakan layanan dan apakah browser automation serta multi-account orchestration diizinkan. Bila
       tidak, pilih jalur penggunaan yang sah/manual atau API resmi yang tersedia; jangan pakai jalur tak resmi.
      Selesaikan I12-01 nyata: pengguna login manual, check READY, tutup app, buka kembali, check READY
       dan “Validasi restart: Lulus”.
      Pengguna secara eksplisit memberi izin satu Scene pilot beserta akun dan anggaran kredit maksimum.
      Inspect halaman Flow aktual lewat profil yang berizin, catat DOM/aria/label non-sensitif; jangan menebak
       selector dari tutorial lama.
      Pastikan model/entitlement sesuai kontrak repo Omni Flash 1.1/720p/16:9 atau lakukan ADR bila di UI nama
       berubah.
      Pastikan project remote Flow yang benar dapat ditemukan/dibuat (sesuai izin layanan) dan identitasnya
       dipersist secara aman.




                             DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 13
<PARSED TEXT FOR PAGE: 14 / 30>
                                                                                                              FLOW-OTOMATIS / MASTER PLAN




10.2 Tahapan driver satu Scene
    Langkah          Aksi                                                       Bukti wajib
    10-A             Acquire verified account lease; open Flow home             page URL domain resmi, session gate PASS
    10-B             Resolve/create remote project owned by profile             remote project identity stable, matches local workspace
    10-C             Map approved image; upload via normal UI                   image attachment evidence and digest mapping
    10-D             Fill motion prompt exactly as approved                     prompt preview checksum matches job snapshot
    10-E             Select model, resolution, aspect, duration, output count   visible setting matched to immutable quote
    10-F             Run pre-submit read-only checklist                         cost confirmation + inputs + no pending duplicate
    10-G             Commit local SUBMIT_STARTED with owner/lease               durable atomic boundary before mutating click
    10-H             Do exactly one authenticated Generate click                outcome evidence ACCEPTED/AMBIGUOUS/SAFE_FAILURE
    10-I             Capture stable result reference                            remote_result_id + screenshot digest/redacted event source
    10-J             Poll/status monitor read-only with timeout/backoff         completed/failed/pending with structured reasons
    10-K             Persist GENERATED only on confirmed remote result          job state + identity + credit reconciliation start




10.3 Selector abstraction dan perubahan UI Flow
      Driver memakai semantic locators (role/name/testid yang ada secara nyata) dan beberapa assertion sentinel;
       jangan menyimpan koordinat klik tetap.
      Setiap selector punya version/expected state yang diuji pada halaman saat itu; mismatch -> UI_CHANGED +
       stop sebelum mutation.
      Jika modal Generate menampilkan dua output default atau harga berubah, job diblokir sampai
       snapshot/quote cocok.
      Dilarang retry klik Generate karena timeout DOM tepat setelah click dapat berarti provider sudah menerima
       pekerjaan.
      Remote ID yang tidak stabil menjadi SUBMIT_AMBIGUOUS/ATTENTION_REQUIRED; manual reconciler
       memeriksa remote timeline/project tanpa submit baru.
      Upload, prompt, duration dan account terkait harus mempunyai “evidence of match” sebelum submit.

10.4 Deteksi hasil + antrean download
Accepted bukan sama dengan Generated; provider harus memisahkan acceptance dari completion. Jika Flow
tidak menyediakan stable result identity secara langsung, rancang correlation berbasis
project+scene+attempt+time+digest nonrahasia tanpa menganggap elemen visual sama sebagai ID unik. Jangan
menandai GENERATED bila tidak ada bukti yang cukup.

10.5 Klasifikasi kegagalan
    Kondisi                                               Tindakan aman
                                                          ACCOUNT_AUTH_REQUIRED; job tidak diganti ke akun lain jika submit mungkin
    Login expired
                                                          sudah terjadi.
                                                          SAFE_FAILURE jika TERBUKTI belum submit; no charge assumed hanya setelah
    Flow 4xx/5xx/read timeout sebelum submit
                                                          saldo diverifikasi.
    Timeout setelah tombol Generate                       SUBMIT_AMBIGUOUS, stop auto retry dan tahan credit reserve.
    Model tidak tersedia                                  CAPABILITY_BLOCKED; jangan ganti model diam-diam.
    Kredit kurang                                         WAIT_CREDIT; refresh evidence; jangan pindah ke akun lain secara tersembunyi.
    UI changed / selector mismatch                        UI_CHANGED; stop affected worker, capture sanitized evidence.
    Policy / unusual activity / rate limited              PAUSE_ACCOUNT; hormati pembatasan layanan; jangan menyiasati.
    Output moderation/rejected                            REJECTED_POLICY; tangani manual, tidak reword prompt otomatis.
    Credit cost mismatch                                  PAUSE_NEW_SUBMITS; rekonsiliasi saldo dan cari akar sebab.
                                                          RECOVER_REMOTE_READONLY; require stable result evidence before completion or
    App crash after submit
                                                          retry.




11. Scheduler paralel, state machine, crash recovery
11.1 Prinsip klaim pekerjaan
Repo serial saat ini memiliki episode-wide RUNNING/ATTENTION_REQUIRED blocker. Untuk multi-akun, aturan
itu perlu diganti dengan unique active attempt per scene serta isolasi attention pada scene atau akun terkait.


                                DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 14
<PARSED TEXT FOR PAGE: 15 / 30>
                                                                                   FLOW-OTOMATIS / MASTER PLAN



Jangan hanya menghapus kondisi blocker: perlindungan antiduplikasi harus bergeser ke constraint transaksi
yang dapat diuji.
   Unique index: satu active generation attempt per (episode_id, scene_id, generation_revision); hanya satu
    klaim dapat menang secara atomik.
   Per-account lease memastikan satu worker owns satu job (default 1) dan resource Chrome profil tidak saling
    berebut.
   No duplicate submit across process restart: durably mark submit_started before click; recover dengan
    klasifikasi yang berbasis bukti.
   Jika attention satu scene tidak memengaruhi scene lain, scheduler boleh lanjut scene lain pada akun sehat
    setelah memastikan tidak ada konflik global kebijakan/model/kredit.
   Jika attention berarti tarif/provider/policy tidak terpercaya, scope block lebih luas: account/project/global
    sampai diverifikasi.
   Dukung pause: hentikan klaim baru; pekerjaan pre-submit dapat dibatalkan, pekerjaan post-submit
    ditunggu/reconcile tanpa click ulang.
   Dukung stop: jangan hapus job, manifest, saldo atau file; definisikan token cancel per tahap.
   Worker crash harus disertai recover expired lease + ambiguity analysis; lease expiry sendiri BUKAN bukti
    submit gagal.

11.2 Transisi state yang dipertahankan
    READY -> QUEUED -> RESERVED -> CLAIMED -> PRE_SUBMIT
    PRE_SUBMIT -> SUBMIT_STARTED -> ACCEPTED -> GENERATING -> GENERATED
    PRE_SUBMIT -> SAFE_FAILURE / AUTH_REQUIRED / CREDIT_BLOCKED
    SUBMIT_STARTED -> SUBMIT_AMBIGUOUS (if uncertain)
    SUBMIT_AMBIGUOUS -> RECONCILED_GENERATED (read-only proof)
    SUBMIT_AMBIGUOUS -> MANUAL_RETRY_ELIGIBLE (proof no accepted submit)
    GENERATED -> DOWNLOAD_QUEUED -> DOWNLOADING -> DOWNLOADED
    Do not allow ATTENTION_REQUIRED -> SUBMIT_STARTED without explicit proof+approval.


11.3 Ownership, lease, dan fencing
   Setiap claimer mempunyai owner_id + generation/fencing_token monotonic; stale owner tidak boleh
    menandai sukses di atas owner baru.
   Lease TTL cukup untuk operasi browser; long-running Generate harus punya heartbeat selama polling dan
    tidak menciptakan owner kedua saat timeout.
   Dalam satu transaction, klaim job, catat assign/quote, reservasi dan owner; commit sebelum memulai side
    effect.
   Penyelesaian side effect harus CAS UPDATE berdasarkan owner_id + token + state expected.
   Work stealing hanya untuk QUEUED yang tidak terikat dan masih aman; jangan pindahkan post-submit job.
   Recovery classification harus membedakan ORPHAN_PRE_SUBMIT vs ORPHAN_POSSIBLE_SUBMIT
    seperti proteksi existing.

11.4 Prosedur startup recovery
1. Buka database read-only dan periksa schema/version/integrity; jika corrupt jangan modifikasi otomatis.
2. Muat plan aktif, jobs, download history, account/session state, credit snapshots, reservations dan remote
   mapping.
3. Recover expired leases dengan upsert event log tanpa submit.
4. Refresh sesi/Flow access/credit secara read-only (setelah user membuka sesi jika perlu).
5. Reconcile remote output hanya untuk job yang punya bukti attempt; jangan mengandalkan urutan tile yang
   berubah.
6. Jangan membuka scheduler RUNNING otomatis bila ada unknown post-submit/credit conflict; tampilkan
    Recovery Center.
7. Resume memerlukan user action atau kebijakan auto-resume yang sudah disetujui dan hanya untuk job
   terbukti aman.




                      DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 15
<PARSED TEXT FOR PAGE: 16 / 30>
                                                                                                       FLOW-OTOMATIS / MASTER PLAN




12. Download aman, manifest final, dan integritas output
12.1 Arsitektur target
Manfaatkan GeneratedMediaDownloadService serta GoogleFlowDownloadProvider yang sudah ada. Keduanya
memisahkan Download dari Generate, memakai berkas .part unik dan publish atomik, serta menolak overwrite
tak sengaja. Implementasi perlu mengisi live GoogleFlowDownloadDriver setelah I12-03-LIVE gate.

12.2 Perilaku download
      Tidak ada download tanpa job GENERATED + remote_result_id stabil + profile owner yang masih valid.
      Download berjalan dengan akun yang benar; akun Generate dan identitas remote project dicatat agar tidak
       salah mengambil hasil milik akun lain.
      Simpan file ke `{projects_root}/{episode_id}/downloads/SCENE_###_takeNN.mp4`; nama output kanonik
       dengan whitelist, tidak ambigu.
      Gunakan unique `.part`/temporary file, verifikasi format/video header atau ffprobe jika tersedia, bytes>0,
       durasi/codec expected range, checksum dan atomic rename.
      Jika target final sudah ada, jangan ditimpa; cek apakah file sama dan catat idempotent success atau
       tampilkan konflik.
      Simpan sidecar metadata aman (scene ID, profile alias/UUID, remote id sanitized, attempt, duration, SHA,
       source quote/revision).
      Kegagalan download tidak boleh mengubah Generate sukses menjadi gagal, dan delayed failure tidak boleh
       merusak confirmed download history.
      Manifest final hanya menyatakan complete bila setiap scene wajib memiliki hasil download yang valid atau
       waiver eksplisit.
      Jika Flow menawarkan resolusi output berbeda dari kontrak, verifikasi dan hentikan publikasi untuk output
       yang salah.

12.3 Definisi output lengkap
    Output                           Makna
                                     Handoff scene → file, target duration, selected flow duration, status generate/download, digest,
    FLOW_OTOMATIS_RESULT.json
                                     take, source revision.
    downloads/*.mp4                  Video yang sudah diverifikasi dengan hasil dari satu remote id.
                                     Metadata akun pseudonim, estimate vs observed, balance timing, status discrepancy; bukan data
    credit_usage_summary.json
                                     rahasia.
    run_report.txt                   Ringkasan operasi, blocking scene, audit ID, jumlah kredit tanpa token.
    recovery_state                   Database lokal; tidak dipaksa ikut paket ekspor pengguna kecuali pilih diagnostic sanitized.




13. Arsitektur ekstensi & kontrak antar lapisan
13.1 Struktur komponen target
      Qt Presentation (frozen existing UI + approved new credit planner dialogs)
                | typed commands/events, no provider/browser/sqlite imports
      Application Services:
        EpisodeImport / ScenePlanning / LocalResults (reuse)
        CreditCatalogService / CreditReconciliationService (new)
        SmartCreditPlanningService / MultiAccountSchedulerService (new)
        LocalGenerationQueueService (adapt; preserve safety)
                | Ports / immutable DTOs
      Domain:
        Scene + Job existing; CostQuote, PlanRevision, AccountCapacity,
        CreditReservation, CreditEvent, AssignmentDecision (new)
      Infrastructure:
        SQLite workspace/jobs/download + versioned credit tables (new)
        Keyring existing; atomic manifest writer existing
      Browser Workers:
        session worker existing; approved Flow credit probe (new)



                           DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 16
<PARSED TEXT FOR PAGE: 17 / 30>
                                                                                                            FLOW-OTOMATIS / MASTER PLAN



        live generation driver (future gated); live download driver (future gated)
      Bootstrap:
        build_main_window composition and shutdown ownership


13.2 Batas arsitektur wajib
      presentation hanya mengimpor application/domain view models, tidak boleh import SQLite/Playwright
       langsung.
      domain pure deterministic, tidak tahu Qt/browser/network/system clock langsung; sumber waktu disuntikkan
       agar tes stabil.
      application/services mengorkestrasi port; browser worker memegang semua interaksi Flow yang telah
       disetujui.
      infrastructure/persistence mengimplementasi transaksi, schema migration, integrity checks, dan recovery.
      Bootstrap hanya composition root; pilih provider fake/live melalui config yang jelas, tidak diam-diam fallback
       saat live gagal.
      Worker harus mengirim signal event yang tidak memblokir Qt dan tidak membocorkan data akun/URL
       sensitif.
      Satu canonical owner per konsep. Sebelum tambah class/file baru, jalankan aturan “search before create”
       AGENTS.md.

13.3 Port/DTO baru yang direkomendasikan
    Port/DTO                                   Operasi minimal                                  Jaminan
                                               check_balance(profile_id) →
    FlowCreditProbePort                                                                         Read-only; timestamp, source, confidence.
                                               CreditProbeEvidence
    FlowCapabilityPort                         check_model/outputs/project(profile_id)          Tidak mutasi; fail closed.
                                               get_quote(model,resolution,duration,outputs,
    TariffCatalogPort                                                                           Versioned; explicit unknown.
                                               scope)
                                               append_event, reserve, release, reconcile,
    CreditLedgerRepositoryPort                                                                  ACID + idempotency.
                                               snapshots
    PlanRepositoryPort                         save_draft, freeze, load_revision, diff          Immutable plan revisions.
    SchedulerRepositoryPort                    claim_for_profile, heartbeat, complete_cas       Atomic claim and fencing.
                                               get_or_bind local episode/profile to remote
    RemoteProjectMappingPort                                                                    Stable identity; never cross account.
                                               project
    FlowLiveGenerationDriver                   submit_one(request, profile_id)                  Exact one mutation, typed evidence.
    FlowLiveDownloadDriver                     download_one(profile,remote_id,destination)      Typed single attempt, atomic local path.




14. SQLite schema, migrasi, dan kompatibilitas
14.1 Prinsip migrasi
GenerationJobRepository saat audit menggunakan _SCHEMA_VERSION=2. Skema baru belum ditetapkan dan
tidak boleh dilabel v3 sebelum diuji. SOL harus mengusulkan ADR migrasi baru, melakukan backup local DB
terverifikasi sebelum DDL, transaction atomic, migrasi non-destruktif, dan downgrade/read-only failure yang
aman.

14.2 Tabel konseptual tambahan
    Tabel usulan                  Kolom inti                                                            Constraints / index
    flow_account_registry         profile_id, policy_status, approval_at, worker_concurrency            unique(profile_id); no secrets
                                  snapshot_id, profile_id, balance?, source, confidence, at_utc,
    flow_credit_snapshots                                                                               append-only; indexed (profile_id,at)
                                  expires_at
                                  tariff_id, provider_model, res, seconds, outputs, per_gen, source,    unique(version,model,res,seconds,scope
    flow_credit_tariffs
                                  verified                                                              )
                                  event_id, account_id, job_id?, attempt_id?, amount?, kind, at,        unique(event_id); idempotency_key
    flow_credit_ledger
                                  evidence_digest                                                       unique
    flow_credit_reservations      reservation_id, job_id, account_id, amount, status, plan_revision     one active reservation per attempt
                                  revision_id, episode_id, quote_id, hash, objective, status,           immutable frozen records; one active per
    flow_plan_revisions
                                  approved_at                                                           episode
                                  assignment_id, revision_id, scene_id, account_id, ordinal,
    flow_assignments                                                                                    unique(revision_id,scene_id)
                                  quote_cost



                               DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 17
<PARSED TEXT FOR PAGE: 18 / 30>
                                                                                                             FLOW-OTOMATIS / MASTER PLAN



 Tabel usulan                  Kolom inti                                                               Constraints / index
                               attempt_id, job_id, account_id, remote_project_id, submit_state,         one live attempt per job rev; explicit
 flow_generation_attempts
                               fencing, timestamps                                                      ambiguity
 flow_remote_project_map       episode_id, account_id, remote_project_id, checked_at                    unique(episode_id,account_id)
 flow_download_evidence        episode_id,scene_id,remote_id,path,digest,take,verified_at               do not overwrite confirmed download




14.3 Migrasi aman dari DB lama
1. Deteksi existing schema version dan feature flags tanpa membuat tabel pada read-only operations.
2. Salin DB ke backup transaksi lokal sebelum migrasi; catat SHA-256 dan ruang disk cukup.
3. Lakukan migrasi v2→target dengan tabel baru atau ALTER kompatibel, bukan drop data penting.
4. Legacy jobs tanpa account_id tidak boleh dianggap assigned; statusnya UNASSIGNED_LEGACY dan
    rekonsiliasi sebelum run.
5. Legacy GENERATED/result/download disalin atau dirujuk tanpa mengganti status sukses; jangan memaksa
    re-Generate.
6. Jika migrasi gagal, rollback dan file asli/backup tetap utuh, user mendapat pesan yang jelas.
7. Uji schema lama, kosong, besar, korup, read-only, path unicode, dan crash di tengah migrasi.
8. Jangan menggabungkan schema v1 import manifest dengan schema v2 job database; versioning masing-
    masing independen.

14.4 Atomic account reservation design
   BEGIN IMMEDIATE;
     assert active_plan_revision == expected;
     assert job.state == QUEUED and no active_attempt(job);
     assert account.policy == APPROVED and credit_snapshot.fresh;
     assert unreserved_verified_balance >= quoted_cost;
     INSERT reservation(idempotency_key, job, account, amount, ACTIVE);
     INSERT generation_attempt(job, account, state=CLAIMED, owner, fence);
     UPDATE job SET state=RUNNING, owner=?, lease=? WHERE state=QUEUED;
   COMMIT;
   // ONLY THEN command browser worker; before Generate click persist SUBMIT_STARTED.
   // On mismatch/zero rowcount: ROLLBACK, do not mutate browser.



15. UI/UX extension tanpa merombak desain lama
15.1 Keputusan yang harus dipertahankan
UI utama yang ada telah memperoleh referensi 30-state; pertahankan navigasi, header,
project/workspace/results, Profil Google, Gemini Keys, AI Agent dock, warna putih-biru, label Bahasa Indonesia,
dan modal existing. Perubahan UI baru dianggap extension terkontrol, bukan redesign. [R9]

15.2 Panel/dialog minimal yang diusulkan
 UI Baru                        Elemen wajib                                                                 Pemicu / catatan
                                ringkasan scene, harga, jumlah output, akun eligible, unknowns, total        di Workspace; tampil sebagai
 Perencanaan Kredit
                                quote                                                                        dialog/section sesuai review.
                                tabel akun→scene, expected spend/remaining, alasan assignment,               sebelum Freeze Plan; bisa simulasi
 Pembagian Akun
                                drag/manual move safe                                                        offline.
                                identitas proyek, jumlah akun, total maksimum kredit, tarif versi,           gate sebelum tombol Start; tidak
 Konfirmasi Eksekusi
                                kebijakan retry                                                              tampil jika blocked.
                                per-scene state, per-account worker, reservations, saldo last                data dinamis dari backend; bukan
 Monitor Proses
                                checked, tombol pause                                                        fixture statis.
 Perbarui Kredit                status reading, timestamp, spinner non-blocking, error/capability            tidak mengklik Generate.
                                ambiguity, expired lease, duplicate, saldo konflik, pilihan read-only        wajib review desain; tidak sebagai
 Recovery Center tambahan
                                reconcile                                                                    sidebar permanen.
                                                                                                             pertahankan hasil existing; tambah
 Ringkasan Hasil Multi-akun     outputs, SHA, kredit dipakai vs estimasi, download status, export
                                                                                                             data sesuai approval.



                            DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 18
<PARSED TEXT FOR PAGE: 19 / 30>
                                                                                 FLOW-OTOMATIS / MASTER PLAN




15.3 Aturan interaksi dan copy Bahasa Indonesia
   Tombol: “Scan Ulang”, “Perbarui Kredit”, “Hitung Rencana”, “Tinjau Pembagian”, “Bekukan Rencana”, “Mulai
    Generate”, “Jeda”, “Lanjutkan”, “Periksa Hasil”, “Ekspor Hasil”.
   Tidak menampilkan angka 50 sebagai saldo akun. Gunakan “Saldo belum diverifikasi” sampai terbukti.
   Pisahkan “Kredit terakhir terbaca” dari “Kredit tersedia setelah cadangan” dan “Estimasi biaya job”.
   Peringatan biaya menampilkan nilai sebelum persetujuan dan menjelaskan jika 1 request dapat
    menghasilkan beberapa video.
   Warna jangan satu-satunya indikator. Tambahkan teks/kode “Siap”, “Menunggu Kredit”, “Perlu Login”, “Hasil
    Tidak Pasti”.
   Progress bar dihitung dari state nyata (Generate dan Download terpisah), bukan dari submit saja.
   Menekan Close saat pekerjaan berjalan membuka dialog dengan informasi aman; tidak langsung
    membatalkan submit external yang sudah berjalan.
   Jangan meminta pengguna menyerahkan email/password Google, cookie, OTP, atau data profil untuk
    troubleshooting.

15.4 Gate UI wajib berhenti
1. ASTRA membuat prompt gambar UI tambahan spesifik per dialog/screen.
2. Setelah prompt selesai, STOP total; belum membuat UI kode walau ada permintaan “lanjutkan” tanpa final
   approval gambar.
3. Pengguna menghasilkan/menilai/revisi gambar UI sesuai kebutuhan.
4. Semua gambar final dan anotasi komponen, event, states, accessibility disatukan dalam satu DOCX UI
   Reference Addendum.
5. Hanya setelah addendum UI final tersimpan di repo dan gate PASS, SOL boleh coding UI extension.


16. Keamanan, privasi, dan kepatuhan penyedia
16.1 Kebijakan hard-stop
   Tidak ada pembuatan/rotasi akun otomatis untuk mengakali batas kuota atau rate limit.
   Tidak ada CAPTCHA/MFA bypass, stealth, proxy rotation, user-agent spoofing, scraping endpoint privat yang
    melanggar ketentuan.
   Tidak memaksa multi-account concurrency jika tidak diizinkan provider; review Terms dan scope sebelum
    implementasi mutasi.
   Tidak menyimpan atau mengunggah token/cookie/password/Chrome profile ke repo, file handoff, diagnostic
    ZIP, screenshot atau logs.
   Tidak menganggap log-in Google berarti pengguna mengizinkan semua akun ditautkan ke proyek atau
    semua kredit digunakan.
   Tidak mengirim prompt/gambar ke pihak lain selain layanan yang telah dipilih/disetujui.
   Tidak memodifikasi gambar approved, motion prompt, target duration atau output count tanpa approval baru.
   Jika terbaca “unusual activity”, batas kredit, atau kebijakan akun, hentikan secara wajar dan arahkan
    pengguna ke UI resmi.

16.2 Audit trail dan retensi
   Trace per job menggunakan correlation_id acak, bukan email/API key.
   UI evidence boleh disimpan redacted lokal untuk debug jangka terbatas; jangan menyimpan full browser
    profile atau rahasia.
   Redaksi screenshot harus mencakup nama/email jika dibagikan ke AI eksternal atau commit.
   Logging memisahkan error technical code dari detail sensitif; bounded length pada exception output.
   Untuk backup user, simpan source code/arsitektur saja, bukan database berisi sesi autentikasi.
   Menentukan retention configurable untuk ledger/diagnostics, dengan audit migrasi/hapus yang tidak
    menghapus job evidence penting.


                     DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 19
<PARSED TEXT FOR PAGE: 20 / 30>
                                                                                                    FLOW-OTOMATIS / MASTER PLAN




17. Rencana uji lengkap dan acceptance matrix
17.1 Piramida pengujian
        Unit domain: mapping durasi, quote cost, balance arithmetic, allocator deterministic, freeze/approval, state
         transitions.
        Contract: port browser credit/preflight/Generate/Download, dto backward compatibility, tariff catalog version,
         structured errors.
        SQLite integration: transaksi atomic, multi-worker races, migrations, recovery, no-clobber, legacy data.
        UI/Qt: tombol yang benar-benar tersambung, progress update, UI frozen 30/30, dialog approval dan
         accessibility.
        Browser fixture: mock live selectors/capability balance, changed DOM, transient loading, account mismatch, 1
         vs 2 outputs.
        Live pilot: satu profil real, satu scene, satu submit dengan izin dan kredit; kemudian download 1 hasil.
        Parallel soak: dua akun, mixed durations, pause/restart/account failure dan kredit limit; lalu concurrency
         bertahap.
        Windows portable: signed? hanya jika tersedia; build, extraction paths, Chrome discovery, user-data-dir
         ownership, smoke, ZIP CRC/SHA.

17.2 Test IDs dan expected outcome
    ID         Kasus / stimulus                                      Expected result
    T01        3.9s, 4.0s, 4.01s, 6, 6.01, 8.01, 10                  duration 4/4/6/6/8/10/10 tepat
    T02        target 0, -1, NaN, >10                                invalid/block; no job
    T03        selected duration < target                            block before plan
    T04        missing image/prompt/manifest                         block with typed reason; source untouched
    T05        valid 12 scene prices 720p                            A41 + B44 + C39 = 124
    T06        multiple results per request 2                        estimated charge ×2, approval revised
    T07        tariff changes 10s 15→new cost                        invalidate existing quote; stop new submit
    T08        credit UNKNOWN or manually declared                   strict auto dispatch blocked
    T09        all accounts have < minimum job cost                  WAIT_CREDIT, 0 submits
    T10        balances 50, 30, 5; mixed costs                       no negative usable credit
    T11        two workers claim same scene simultaneously           exactly one claim and one reservation
    T12        two threads reserve same last 15 credit               only one reservation commits
    T13        account A busy, B free                                B can dispatch safe independent scene
    T14        one scene ambiguous post-submit                       that scene blocked; no auto repeat
    T15        attention scene A while B safe                        B proceeds only if scoped attention safe
    T16        crash pre-submit                                      recovery may requeue only with proof safe
    T17        crash after submit                                    ATTENTION until remote reconciliation
    T18        account READY then login expires                      AUTH_REQUIRED and 0 new submits
    T19        login Chrome still open                               post-login CDP blocked with actionable message
    T20        Flow model unavailable on free account                UNSUPPORTED; no silent switch
    T21        Flow credit UI not readable/changed                   CREDIT_UNKNOWN; no fake 50
    T22        external account use reduces balance                  reconciliation conflict / plan re-eval
    T23        reset/recharge reported at odd local hour             refresh only observed; no midnight assumption
    T24        output success without stable remote id               AMBIGUOUS; no GENERATED
    T25        Generate accepted but not yet rendered                do not begin download
    T26        download file empty, HTML/error page                  reject publication; retain existing file
    T27        download collision of filenames                       no-clobber and typed conflict
    T28        delayed failure after DOWNLOADED                      confirmed result preserved
    T29        SQLite corrupt legacy DB                              read-only failure isolation; original checksum unchanged
    T30        DB v2 upgrade fails mid-DDL                           atomic rollback; backup valid
    T31        user changes scene prompt after Freeze                job REQUEST_STALE; reapproval
    T32        user manually moves queued scene                      revalidate capacity; plan revision increment
    T33        user tries moving RUNNING/AMBIGUOUS scene             reject and explain
    T34        two profiles point same remote result                 cross-account mapping conflict blocked
    T35        UI DOM changed for Generate click                     zero mutation; selector version warning
    T36        browser rate-limit / unusual activity                 pause account, do not bypass
    T37        Qt UI while long browser work                         responsive; no event loop blocking
    T38        close/reopen during RUNNING                           recovery center, no phantom “Selesai”
    T39        Windows portable runs in folder with spaces/unicode   correct path, no CWD dependency



                               DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 20
<PARSED TEXT FOR PAGE: 21 / 30>
                                                                                                 FLOW-OTOMATIS / MASTER PLAN



    ID         Kasus / stimulus                                      Expected result
    T40        frozen 30 UI baseline                                 30/30 UI regression PASS
    T41        pricing / service eligibility policy unresolved       never allow live mutation
    T42        user rejects cost approval                            0 provider submits/reservations released safely
    T43        one provider request yields multiple video cards      count/charge/evidence accurate; no misattribution
    T44        time display WIB vs UTC persistence                   timestamp ordering and conversions correct
    T45        file outputs from N accounts                          single project manifest sorted by SCENE_###




17.3 Pengujian performa & ketahanan
        Target aplikasi UI tetap responsif di laptop Windows 11 dengan 1–5 akun terdaftar dan concurrency bertahap
         sesuai izin. Tidak menentukan memori ambang sebelum baseline profiling.
        Simulasi 10, 60, 100, 500 scene untuk quote/allocator; time budget terukur dan tidak bergantung network.
        Stress 10000 credit ledger events, concurrent DB readers/writers, WAL/rollback mode behavior, crashing
         subprocess.
        Soak 1 project 60 scene dengan fake driver mixed-duration dan injected failures; tidak ada lost job, duplicate
         submit, negative balance, atau stale UI.
        Visual QA semua new screens state + 30 frozen baseline; label wrapping dan font Indonesia.
        Live browser tests terbatas, disetujui, tidak berkali-kali membakar kredit sebagai pengganti fixture tests.


18. Work packages implementasi terurut (untuk SOL)
Paket berikut membentuk jalur ekstensi STEP 12, tidak mengulang STEP 00-11. Gate harus PASS satu per satu;
pekerjaan yang melanggar urutan wajib STOP. Paket pra-live dan UI dapat diselesaikan tanpa menggunakan
kredit.

E12-00 — Baseline & planning governance
Tujuan dan pekerjaan: Ambil HEAD, verifikasi source-of-truth, buat scope diagram dan baseline CI; cek
policy/terms dan keputusan UI.
Kepemilikan kode/dokumen yang wajib diperiksa: AGENTS.md, PROJECT_STATE.md, TASKS.md,
docs/planning, docs/ui
Deliverable konkret: Tidak menyentuh kode produksi; docs master approved + status gate; baseline SHA
reproducible.
Gate PASS / alasan STOP: Planning gate PASS, DOCX/handoff tersedia di repo, keputusan policy non-
UNKNOWN untuk live.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-01 — Decision & ADR perubahan lintas-modul
Tujuan dan pekerjaan: Definisikan domain quote, multi-account identity, credit proof, scope blocking, transaction
semantics, migration, concurrency; ASTRA review.
Kepemilikan kode/dokumen yang wajib diperiksa: docs/architecture/ADR*, docs/planning, contracts existing
Deliverable konkret: ADR traceable, API/DTO sketches, migration plan, risk matrix disetujui.
Gate PASS / alasan STOP: Tidak ada breaking schema tanpa migrasi.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-02 — UI desain tambahan — WAJIB STOP
Tujuan dan pekerjaan: Buat UI prompt Perencanaan Kredit/Monitor/Recovery; berhenti sampai gambar
diperiksa dan DOCX UI Reference Addendum selesai.
Kepemilikan kode/dokumen yang wajib diperiksa: docs/ui/*; IMPLEMENTATION_OVERRIDES.md


                               DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 21
<PARSED TEXT FOR PAGE: 22 / 30>
                                                                                     FLOW-OTOMATIS / MASTER PLAN



Deliverable konkret: 30 UI existing retained; semua screens, states, labels, buttons final dan disetujui.
Gate PASS / alasan STOP: UI gate PASS tertulis sebelum coding UI.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-03 — Credit tariff catalog pure
Tujuan dan pekerjaan: Bangun tariff versioned immutable, capability checking, quote per generation, change
detection; fixture offline.
Kepemilikan kode/dokumen yang wajib diperiksa: domain; application/ports; tests/unit
Deliverable konkret: Tarif 720p 7/10/12/15 diuji + multi-result & unknown tariffs.
Gate PASS / alasan STOP: No provider network in pure domain; unit/contract PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-04 — Credit snapshots, ledger & migrations
Tujuan dan pekerjaan: Bangun repository read/write, read-only view, reservation ACID, idempotency, v2-safe
migrations and backup.
Kepemilikan kode/dokumen yang wajib diperiksa: sqlite_generation_job_repository, new sqlite credit
repository, migrations
Deliverable konkret: No double reserve; legacy projects safe; 10000 events stress.
Gate PASS / alasan STOP: Migration tests + rollback + backup checksum PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-05 — Smart planner offline
Tujuan dan pekerjaan: Scan→quote→sort→assign deterministik; preview, manual overrides, plan
freeze/versioning.
Kepemilikan kode/dokumen yang wajib diperiksa: scene_planning; local queue; new planning services
Deliverable konkret: Simulasi mixed duration and 12-scene/124-credit acceptance.
Gate PASS / alasan STOP: No live Generate; deterministic tests PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-06 — Qt credit planning extension
Tujuan dan pekerjaan: Implement dialog/panel approved, bind local services; avoid changing 30 base states.
Kepemilikan kode/dokumen yang wajib diperiksa: presentation/main_window, workspace_views, new
approved views
Deliverable konkret: Preview and approval functional, no fake status, keyboard accessible.
Gate PASS / alasan STOP: 30/30 existing + new UI tests PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-07 — Account capabilities + credit probe read-only
Tujuan dan pekerjaan: Satu profil: browser session, Flow availability, eligible model, UI credit observe,
TTL/provenance.




                      DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 22
<PARSED TEXT FOR PAGE: 23 / 30>
                                                                                   FLOW-OTOMATIS / MASTER PLAN



Kepemilikan kode/dokumen yang wajib diperiksa: google_sessions, google_flow_preflight,
system_chrome_cdp, new browser probe
Deliverable konkret: Read-only evidence typed and sanitized; capability unknown blocks.
Gate PASS / alasan STOP: Fixture UI-mismatch + security tests PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-08 — Satu akun live session gate
Tujuan dan pekerjaan: Dengan izin pengguna, cek READY-after-restart; inspect real Flow and lock selector.
Kepemilikan kode/dokumen yang wajib diperiksa: RestartGatedGenerationProvider, browser worker
Deliverable konkret: Gate evidence non-rahasia and acknowledged policy.
Gate PASS / alasan STOP: NO live mutation sampai user approval.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-09 — One-scene live Generate pilot
Tujuan dan pekerjaan: Implement current verified driver, upload/prompt/settings, at most one submit and remote
identity.
Kepemilikan kode/dokumen yang wajib diperiksa: google_flow_generation.py; request_plan; bootstrap; UI
action
Deliverable konkret: One real scene accepted once, exact input and outcome evidence.
Gate PASS / alasan STOP: Any ambiguous status blocks duplicate; user approved budget.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-10 — One-scene live result & Download
Tujuan dan pekerjaan: Stable result wait + live download driver + atomic publishing + manifest link.
Kepemilikan kode/dokumen yang wajib diperiksa: google_flow_download.py; generated_media_download;
results
Deliverable konkret: One verified downloadable video and correct result status.
Gate PASS / alasan STOP: No-clobber & result-id tests PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-11 — Account-aware queue and browser actors
Tujuan dan pekerjaan: Move serial queue to N workers with per-profile ownership, fencing, atomic reservations,
policy caps.
Kepemilikan kode/dokumen yang wajib diperiksa: local_generation_queue; sqlite_generation_job_repo;
workers/browser
Deliverable konkret: Two fake profiles run independent scenes without duplicate submits.
Gate PASS / alasan STOP: Concurrency/race/lease safety PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.




                      DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 23
<PARSED TEXT FOR PAGE: 24 / 30>
                                                                                   FLOW-OTOMATIS / MASTER PLAN




E12-12 — Two-profile live pilot
Tujuan dan pekerjaan: After explicit additional approval, parallel independent scenes, account credit update,
flow mappings.
Kepemilikan kode/dokumen yang wajib diperiksa: scheduler; live adapters; quote+ledger
Deliverable konkret: Two accounts operating without cross-account results; observed credit delta logged.
Gate PASS / alasan STOP: 2-account live acceptance, STOP if service disallows.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-13 — Dynamic N-account & replan
Tujuan dan pekerjaan: Load eligible profiles, choose active count per scan, move only safe queued jobs,
pause/wait credit.
Kepemilikan kode/dokumen yang wajib diperiksa: smart planner; scheduler; UI monitor
Deliverable konkret: Dynamic plan, no account with insufficient balance assigned job.
Gate PASS / alasan STOP: Mixed credit/scene fixtures and real limited soak PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-14 — Recovery & reconciliation hardening
Tujuan dan pekerjaan: Crash/restart pre/post submit, stale credit, unknown cost, account expiry, lost browser,
partial download.
Kepemilikan kode/dokumen yang wajib diperiksa: application services; sqlite; recovery center
Deliverable konkret: No extra provider mutation without proof/approval; idempotent recover.
Gate PASS / alasan STOP: Fault injection matrix T14-T38 PASS.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-15 — QA, packaging & release
Tujuan dan pekerjaan: Ruff/mypy/architecture/pytest/UI 30 states+extension, staged browser, Windows
portable, ZIP hash/CRC.
Kepemilikan kode/dokumen yang wajib diperiksa: tests/, scripts/build, workflows
Deliverable konkret: Reproducible archive; smoke using release artifact; no session data bundled.
Gate PASS / alasan STOP: Official CI PASS with sha, build report, checksum.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.

E12-16 — Final handoff & operational manual
Tujuan dan pekerjaan: SOP operator, module map, backup (source only), issues/known risks, release notes,
demo scenario.
Kepemilikan kode/dokumen yang wajib diperiksa: docs/handoff/current, TASKS, PROJECT_STATE,
docs/user-guide
Deliverable konkret: AI lain bisa restart without asking repeated questions; user can operate.
Gate PASS / alasan STOP: Docs/status claims align with actual tested commit.
Bukti yang harus dilampirkan SOL: branch, SHA awal/akhir, daftar berkas, diff ringkas, test command/result,
artefak CI, known risks, status DONE/PENDING, link PR/commit setelah disetujui.



                      DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 24
<PARSED TEXT FOR PAGE: 25 / 30>
                                                                                                              FLOW-OTOMATIS / MASTER PLAN




19. Gate formal, definisi selesai, dan rollback
19.1 Gate dan tindakan STOP
    Gate                               Syarat PASS                                                  Jika FAIL
                                       Master DOCX approved, UI addendum (jika diperlukan)
    G0: Docs Authority                                                                              STOP coding; lengkapi docs.
                                       approved, semua masuk repo sebelum coding
                                       Perjanjian/ketentuan provider dan ownership akun             Stop browser live/multi-account; cari jalur
    G1: Policy
                                       mendukung integrasi yang direncanakan                        resmi/manual.
    G2: Repo Baseline                  HEAD, clean diff, source+tests/CI direkam                    STOP jika repo drift tak dipahami.
    G3: Data Safety                    Migration/rollback, backup, checksum tests PASS              STOP schema changes.
                                       Addendum final didukung gambar, 30 original regression
    G4: UI Freeze                                                                                   STOP implementasi UI.
                                       intact
    G5: Pricing Credit                 Tariff model & observed account entitlement matching         STOP credit auto-dispatch.
    G6: Login                          Google account READY after real app restart                  STOP live mutation.
    G7: One-Scene Generate             1 submit, stable outcome, approved cost                      STOP batch atau parallel.
    G8: One-Scene Download             Stable remote ID, valid MP4, no-clobber                      STOP full chain claim.
    G9: Two-account                    Unique claim/account isolation and policy valid              STOP scale-up.
    G10: Final QA                      All tests/Windows ZIP/visual security/policy docs PASS       No final release.




19.2 Definition of Ready untuk setiap wave
        Baseline source-of-truth dibaca dan branch target benar.
        Scope dan non-goals ditulis eksplisit.
        Interface dan data migration diputuskan, tidak ada pending policy/UI blocker.
        Test ID, expected result, dan rollback diketahui.
        Tidak ada data rahasia dalam fixture atau commit.
        Batas kredit/user consent dipastikan bila mengakses live provider.

19.3 Definition of Done
        Fitur berjalan sesuai kontrak dengan tests baru yang dapat mereproduksi kegagalan sebelum fix.
        Ruff format/check, mypy, architecture guard, unit/integration/contract/smoke PASS; CI official SHA dicatat.
        Jika UI, frozen 30-state + extension visual review PASS; tak ada desain lama yang diam-diam diganti.
        Semua migration/backup/restore path diuji termasuk interupsi.
        Sukses hanya dilaporkan untuk pekerjaan yang benar-benar dibuktikan; batas live test dijelaskan.
        TASKS.md, PROJECT_STATE.md, ADR, handoff dan release notes diperbarui dalam wave yang sama.

19.4 Rollback
        Rollback release melalui tag/commit terakhir yang lulus dan restore DB dari backup yang cocok; jangan force
         reset work milik orang lain.
        Jika migrasi partial, app harus tidak memaksa melanjutkan dan menawarkan restore read-only/backup tanpa
         kehilangan sukses Generate/Download.
        Jika live selector rusak, disable feature flag live, pertahankan proyek dan status untuk recovery.
        Jika tariff/entitlement berubah, invalidate quote dan hentikan job baru; jangan rollback saldo dengan asumsi
         arithmetic.
        Jika perubahan UI merusak navigasi, rollback extension UI saja; frozen views tetap baseline.


20. Risiko prioritas dan mitigasi
    ID          Risiko                                           Level             Mitigasi
                Kebijakan provider melarang otomasi/pooling                        Lakukan review Terms dan izin; jika melarang, batasi mode
    R01                                                          CRITICAL
                akun                                                               simulasi/manual atau jalur resmi.
    R02         Harga/ketersediaan model berbeda per akun        CRITICAL          Verified quote+capability per profile; stop on unknown.
    R03         Klik submit timeout tetapi diterima Flow         CRITICAL          SUBMIT_AMBIGUOUS; no re-submit; reconcile read-only.
    R04         Dua workers klaim scene sama                     CRITICAL          unique attempt, lease fencing, BEGIN IMMEDIATE, race tests.
    R05         Reservasi ganda menghabiskan saldo               CRITICAL          ACID reservation + idempotent ledger.
    R06         Saldo dari luar aplikasi berubah                 HIGH              snapshot TTL + observed balance refresh + conflict handling.


                                DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 25
<PARSED TEXT FOR PAGE: 26 / 30>
                                                                                                               FLOW-OTOMATIS / MASTER PLAN



    ID        Risiko                                          Level               Mitigasi
                                                                                  semantic selector and pre-submit sentinel, versioned driver,
    R07       UI Flow berubah                                 HIGH
                                                                                  stop.
                                                                                  one worker/profile, separate manual login/CDP, resource
    R08       Browser Chrome profile locked                   HIGH
                                                                                  cleanup.
    R09       Account model unsupported                       HIGH                capability probe fail closed; no silent switch.
    R10       Provider generate returns 2 outputs             HIGH                request output_count binding + price approval; block mismatch.
    R11       Remote result ID not stable                     HIGH                manual reconciliation evidence; do not mark GENERATED.
    R12       Download corrupt/partial                        HIGH                unique .part, verification, atomic rename, SHA.
    R13       DB v2 migrasi rusak                             HIGH                backup, transaction rollback, migration fixtures.
                                                                                  remote mapping per episode/profile, sanitize and validate
    R14       Project mismatch antar-akun                     HIGH
                                                                                  ownership.
    R15       Freeze UI rusak oleh fitur baru                 MEDIUM              separate approved dialogs; UI visual 30/30.
              Status Online/Autosave dekoratif
    R16                                                       MEDIUM              replace with live state/view-model on approved scope.
              disalahartikan
              Tanggal reset kredit ditafsirkan tengah
    R17                                                       HIGH                refresh provider-based, never auto refill.
              malam WIB
    R18       Data akun bocor via logs/screenshots            CRITICAL            redaction, test scanner, no credential export.
    R19       Pengguna menekan Close saat submit              HIGH                safe-pause states and bounded shutdown, no duplicate.
              Beban 10 Chrome instances melumpuhkan
    R20                                                       MEDIUM              dynamic concurrency resource caps, pilot and profiling.
              PC
    R21       Schema import 1.0 diganti sembarangan           HIGH                versioned reader + backward contract.
    R22       Gemini API key dianggap saldo Flow              MEDIUM              strict separation domain and UI labels.




21. Keputusan produk yang sudah dikunci vs menunggu bukti
21.1 Dikunci berdasar arahan pengguna dan repo
        Satu proyek dibagi ke beberapa akun yang pengguna setujui.
        Jumlah akun aktif bergantung hasil scan dan saldo, tidak fixed.
        Durasi 4/6/8/10 dengan biaya sesuai pilihan Flow; default contract existing 720p, 16:9, Omni Flash 1.1.
        Kredit per akun dilihat dan di-update dengan sumber/ketepatan yang transparan.
        Rencana pembagian harus terlihat terlebih dahulu; dukung koreksi manual.
        UI utama yang disetujui tidak dibangun ulang.
        DOCX master lengkap untuk SOL di chat lain; tidak ada coding saat tahap dokumen ini.
        Audit awal pertahankan komponen existing; jangan mulai dari nol.
        Aplikasi Windows 11 portable, Bahasa Indonesia, safety-first.

21.2 Pending yang harus diselesaikan sebagai gate, bukan tebakan
    Kode           Hal yang harus dibuktikan                                                       Keputusan default sementara
                   Perizinan layanan untuk browser automation dan multi-account                    Tidak melakukan live mutating action tanpa
    D-01
                   concurrency                                                                     izin/konfirmasi kebijakan.
                                                                                                   UNSUPPORTED/UNKNOWN sampai Flow UI
    D-02           Apakah akun gratis saat itu eligible Gemini Omni Flash 720p
                                                                                                   menunjukkan kompatibel.
                                                                                                   CREDIT_UNKNOWN; manual input hanya
    D-03           Apakah saldo kredit dapat dibaca dari UI resmi dengan stabil
                                                                                                   simulasi.
                                                                                                   Inspect real UI setelah session gate; jangan
    D-04           Flow project API/URL/identitas remote stabil
                                                                                                   konstruksi endpoint tersembunyi.
                                                                                                   Asumsi plan 1 hanya untuk contoh; verifikasi
    D-05           Apakah satu Generate menghasilkan 1 atau 2 video
                                                                                                   sebelum budget approval.
                                                                                                   Mulai 1; 2 hanya setelah policy/safety gates;
    D-06           Kebijakan jumlah akun aktif paralel
                                                                                                   limit adaptif.
    D-07           Perlu 360p / model lain                                                         Tidak; 720p frozen sampai user review.
                                                                                                   Tidak. Login manual dan CDP pasca-login
    D-08           Apakah ada auto-login/perlu remote browser cloud
                                                                                                   existing.
    D-09           Apakah download langsung menyediakan MP4/format lain                            Verify live; no output assumption.
    D-10           UI tambahan persisnya bagaimana                                                 Prompt→review gambar→DOCX UI final dulu.
                                                                                                   Usulan: ya hanya scene yang safe, dengan
    D-11           Boleh generate sebagian scene ketika kredit habis
                                                                                                   status project partial terlihat.
                                                                                                   Usulan: off sampai service outcome & policy
    D-12           Recovery auto resume setelah restart
                                                                                                   terbukti.



                              DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 26
<PARSED TEXT FOR PAGE: 27 / 30>
                                                                                FLOW-OTOMATIS / MASTER PLAN




22. Dokumen, artefak, dan handoff lintas sesi
22.1 Minimum file yang WAJIB dibaca AI penerus
1. AGENTS.md — aturan arsitektur dan larangan.
2. PROJECT_STATE.md — status resmi, gate terblokir.
3. TASKS.md — detail pekerjaan yang telah selesai/belum.
4. docs/software_factory/SOFTWARE_FACTORY_V2_TEXT_GUIDE.md — aturan Factory.
5. docs/planning/00... sampai 07... DOCX — planning asli.
6. docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx — UI
    30 state.
7. docs/ui/IMPLEMENTATION_OVERRIDES.md — prioritas keputusan UI.
8. docs/architecture/ADR_REGISTER.md + ADR-015/016/017/018/019.
9. docs/planning/audits/ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx.
10. docs/planning/audits/STEP12_RESULTS_ERROR_RECOVERY_2026-10-08.md — PR22.
11. docs/handoff/current/HANDOFF_STEP_12_PRELIVE_READY.md + relevant latest handoff.
12. MASTER PLAN ini + DOCX UI addendum bila sudah disetujui dan ditambahkan ke repo.
13. Commit HEAD/PR/CI aktual; update bukti, bukan menyalin status lama.

22.2 Format update per wave untuk AI lain
   REPO: inoriko920-dev/Flow-Otomatis
   BASE / HEAD / BRANCH: ...
   WAVE: E12-XX
   GATE: PASS | FAIL | BLOCKED
   CHANGED FILES: ...
   TESTS: exact commands / counts / CI URLs / build sha
   WHAT WAS NOT TESTED: ...
   RISKS / OPEN ISSUES: ...
   UPDATES IN SOURCE OF TRUTH: TASKS / PROJECT_STATE / ADR / handoff
   NEXT EXACT WAVE: E12-YY
   REQUEST USER ACTION: if any
   NO CLAIM of live operation unless real authorized evidence exists.


22.3 Prompt handoff yang siap disalin ke chat SOL
   Anda adalah SOL untuk repo https://github.com/inoriko920-dev/Flow-Otomatis.
   Tugas pertama: BACA dokumen MASTER_PLAN_FLOW_OTOMATIS_END_TO_END_
   SMART_CREDIT_MULTI_AKUN_2026-10-08.docx SELURUHNYA dan AGENTS.md,
   PROJECT_STATE.md, TASKS.md, seluruh source-of-truth planning/UI/handoff.
   JANGAN langsung coding. Verifikasi commit HEAD vs baseline audit
   (e560684e04ed3a5fad40bb00a91823de68ca5431); jika berbeda,
   buat delta audit. Hormati DOCX master dan UI freeze gate.
   STEP 00–11 yang PASS jangan diulang; STEP 12 existing masih
   live-blocked sampai user validasi READY setelah restart.
   Jalankan hanya paket E12 berikutnya yang DoR/gate-nya PASS.
   Tidak boleh bypass MFA/captcha, rotasi akun untuk menghindari
   limit, menyimpan cookie/token, menebak selector Flow, atau
   mengirim Generate di akun nyata tanpa izin budget dan policy PASS.
   Satu pekerjaan Generate ambiguitas tidak boleh dikirim ulang.
   Simpan seluruh bukti dan update status; satu wave per giliran.
   Laporkan PASS/FAIL, yang belum diuji dan wave berikutnya.
   Tetap gunakan UI lama; untuk UI baru WAJIB stop setelah prompt
   sampai gambar dan 1 DOCX referensi UI final disetujui.
   Jangan mengubah repo lain apa pun.



                    DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 27
<PARSED TEXT FOR PAGE: 28 / 30>
                                                                                    FLOW-OTOMATIS / MASTER PLAN




23. Prosedur demo penerimaan pengguna (saat akhir, bukan sekarang)
1. Pilih satu proyek uji dengan 12 scene campuran; import paket dan pastikan Scene ID, gambar, prompt,
   durasi, checksum sesuai.
2. Tunjukkan kalkulator 720p: 4s=7, 6s=10, 8s=12, 10s=15 per output dan quotation total 124 kredit untuk
   contoh.
3. Tambahkan profil user-owned yang diizinkan; login manual dan buktikan restart gate. Perbarui kredit dan
   tunjukkan sumber + timestamp.
4. Tunjukkan rencana A41/B44/C39; jika saldo nyata berbeda, planner harus otomatis menggunakan saldo
   nyata dan mungkin menghasilkan pembagian lain.
5. Pengguna meninjau dan mengunci rencana, termasuk batas kredit maksimum, jumlah video per scene,
   model/720p/16:9.
6. Jalankan satu scene authorized, satu akun, satu submit lalu satu hasil MP4 valid; periksa perubahan saldo.
7. Jalankan dua akun authorized dengan dua scene berbeda yang aman; pantau progres terpisah dan credit
    reservation.
8. Simulasi salah satu akun logout: akun lain tetap aman sesuai scope; scene terkait tidak diduplikasi.
9. Simulasi provider menerima submit lalu browser timeout: job memerlukan rekonsiliasi, tidak langsung dikirim
   ke akun lain.
10. Periksa unduhan, urutan file, hasil/manifest, total credits actual vs estimate, dan laporan recovery.
11. Tutup aplikasi selama fase nonmutating dan buka kembali; status harus kembali konsisten dengan DB.
12. Perlihatkan hasil QA, uji Windows portable, ZIP SHA/CRC, changelog, backup source, dan dokumen
    handoff AI berikutnya.

23.1 Syarat menyatakan proyek selesai
Final hanya boleh diumumkan jika seluruh acceptance dan gate untuk satu proyek end-to-end lulus pada akun
yang diotorisasi, fitur parallel tidak melanggar ketentuan layanan, biaya aktual dapat dilacak, hasil tidak
terduplikasi, dan paket Windows portable bisa digunakan. Jika kebijakan tidak mengizinkan multi-account
automation, produk tidak boleh dipasarkan/ditandai sukses sebagai multi-account Flow bot; opsi aman adalah
planner lokal/manual yang patuh.


24. Lampiran A — contoh struktur data (ilustratif, bukan schema final)
   {
       "planning_schema": "proposed-v1",
       "episode_id": "EPISODE_001",
       "objective": "BALANCED",
       "source_workspace_version": "sha256:...",
       "tariff_catalog_version": "2026-10-08-official-flow-help",
       "approved": false,
       "generation_output_count": 1,
       "price_quote": {
          "model": "Gemini Omni Flash",
          "resolution": "720p",
          "aspect_ratio": "16:9",
          "cost_by_seconds": {"4":7,"6":10,"8":12,"10":15},
          "currency": "FLOW_CREDITS",
          "source_url": "https://support.google.com/flow/answer/16526234?hl=en"
       },
       "accounts": [
          {"profile_id":"profile-local-a", "balance":50,
           "balance_evidence":"SIMULATION_ONLY", "selected":true},
          {"profile_id":"profile-local-b", "balance":50,
           "balance_evidence":"SIMULATION_ONLY", "selected":true}
       ],



                      DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 28
<PARSED TEXT FOR PAGE: 29 / 30>
                                                                                                        FLOW-OTOMATIS / MASTER PLAN



         "assignments": [
            {"scene_id":"SCENE_001", "profile_id":"profile-local-a",
             "flow_duration_s":4, "cost_estimate":7}
         ],
         "unassigned": [],
         "estimated_total": 7
    }
Contoh menggunakan status SIMULATION_ONLY; tidak boleh dipakai memulai Generate nyata tanpa mengganti dengan balance dan
capability evidence yang terverifikasi serta persetujuan pengguna.



25. Lampiran B — matriks ketergantungan paket kerja
 Paket                   Bergantung pada                                                                   Boleh paralel?
 E12-00/01               Repo baseline + approved planning                                                 Tidak, sebelum coding.
 E12-02                  Prompt desain UI → gambar review final                                            Tidak; gate wajib stop.
                                                                                                           Dengan E12-04 unit design, tapi
 E12-03                  E12-00/01
                                                                                                           review schema diperlukan.
                                                                                                           Setelah ADR; independent
 E12-04                  E12-01
                                                                                                           testing.
 E12-05                  E12-03/04 + input contract                                                        Tidak live.
 E12-06                  E12-02 final + E12-05                                                             UI code setelah gate.
                                                                                                           Read-only, independent of live
 E12-07                  E12-01 + policy review
                                                                                                           mutation.
 E12-08                  I12-01 real restart gate + user                                                   Manual gate.
 E12-09                  E12-07/08 + user explicit approval                                                Live one-scene only.
 E12-10                  E12-09 remote ID stable                                                           Live download pilot.
 E12-11                  E12-04/05 + previous anti-duplicate tests                                         Fake-only initial parallel.
 E12-12                  E12-09/10/11 + policy + user                                                      Two accounts approved.
 E12-13                  E12-12 + dynamic tests                                                            Scale gradually.
 E12-14                  E12-11/12                                                                         Recovery hardening.
 E12-15/16               All enabled features and gates                                                    Final release/handoff.




26. Lampiran C — daftar referensi dan bukti yang diaudit
 ID          Referensi                                         URL
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/tree/
 [R1]        GitHub Repo main audit SHA
                                                               e560684e04ed3a5fad40bb00a91823de68ca5431
 [R2]        AGENTS.md                                         https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/AGENTS.md
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/
 [R3]        PROJECT_STATE.md
                                                               PROJECT_STATE.md
 [R4]        TASKS.md                                          https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/TASKS.md
 [R5]        PR #22 merged                                     https://github.com/inoriko920-dev/Flow-Otomatis/pull/22
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/docs/planning/
 [R6]        PR22 audit evidence
                                                               audits/STEP12_RESULTS_ERROR_RECOVERY_2026-10-08.md
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/src/
 [R7]        Import manifest schema 1.0
                                                               flow_otomatis/contracts/package/import_manifest.py
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/src/
 [R8]        Session & browser worker
                                                               flow_otomatis/workers/browser/system_chrome_cdp.py
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/docs/ui/
 [R9]        UI implementation overrides
                                                               IMPLEMENTATION_OVERRIDES.md
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/src/
 [R10]       Bootstrap main.py
                                                               flow_otomatis/bootstrap/main.py
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/src/
 [R11]       Local generation queue
                                                               flow_otomatis/application/services/local_generation_queue.py
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/src/
 [R12]       SQLite generation job repository
                                                               flow_otomatis/infrastructure/persistence/sqlite_generation_job_repository.py
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/src/
 [R13]       Google Flow generation adapter
                                                               flow_otomatis/workers/browser/google_flow_generation.py
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/src/
 [R14]       Google Flow download adapter
                                                               flow_otomatis/workers/browser/google_flow_download.py
                                                               https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/docs/handoff/
 [R15]       STEP 12 pre-live handoff
                                                               current/HANDOFF_STEP_12_PRELIVE_READY.md




                           DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 29
<PARSED TEXT FOR PAGE: 30 / 30>
                                                                                                   FLOW-OTOMATIS / MASTER PLAN



 ID      Referensi                                          URL
         Google Flow official credit costs (checked 8 Oct
 [G1]                                                       https://support.google.com/flow/answer/16526234?hl=en
         2026)
         Google Flow Indonesian localized credit page
 [G2]                                                       https://support.google.com/flow/answer/16526234?hl=id
         (cross-language caveat)
 [G3]    Google Flow official product plans                 https://labs.google/fx/tools/flow
         Google Flow getting started, availability and
 [G4]                                                       https://support.google.com/flow/answer/16353333?hl=id
         service behavior




26.1 Limitasi audit
Audit ini berbasis pembacaan file kode dan catatan CI/repository; tidak menjalankan login Google atau mutasi
Generate/Download live, tidak mengeksekusi build Windows baru, dan tidak memvalidasi UI remote Flow dengan
akun pengguna. Tarif adalah potret publik pada tanggal dokumen dan dapat berubah. Pemilik proyek perlu
menilai kepatuhan ketentuan layanan serta kemampuan akun secara nyata sebelum eksekusi. Tidak ada kode
GitHub yang diubah saat penyusunan dokumen.




                     AKHIR MASTER PLAN | SIAP UNTUK REVIEW & HANDOFF
Langkah berikutnya bukan langsung Generate: review/approve dokumen, lakukan gate sumber
kebenaran+UI, kemudian mulai paket E12-00/E12-01 sesuai perintah pengguna. Semua klaim selesai
harus merujuk tes dan bukti implementasi yang nyata.




                        DOKUMEN PERENCANAAN • BUKAN BUKTI IMPLEMENTASI | 8 OKT 2026 | Hal. 30
