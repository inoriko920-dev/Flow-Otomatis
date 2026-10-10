# FLOW-OTOMATIS — TARGET AKHIR END-TO-END (KEPUTUSAN PEMILIK)

Tanggal: **11 Oktober 2026 WIB**. Status: **TARGET PRODUK DIKUNCI — BELUM DIKLAIM SELESAI**.
Repo: `inoriko920-dev/Flow-Otomatis`.

## Pernyataan target pemilik

Pengguna menegaskan kembali tujuan yang telah direncanakan di awal:

> Masukkan puluhan Scene, bagikan pekerjaan ke beberapa akun Google Flow berdasarkan kredit yang tersedia, secara otomatis hasilkan video dan unduh seluruh MP4.

**Ini penegasan tujuan fitur yang sudah direncanakan, bukan izin menambah fitur baru.** `docs/FEATURE_FREEZE_POLICY.md` tetap mengikat semua branch, ASTRA, SOL, PR, dan release. Jangan mengubah spesifikasi UI/produk yang telah disetujui dan jangan menyatakan aplikasi final hanya karena build atau tes offline lolos.

## Definisi selesai (Acceptance / DoD)

1. **Input:** impor paket manifest yang sah beserta gambar approved, prompt Scene, target durasi SRT/audio, dan validasi format/path/file; input wajib hilang/rusak => stop, tanpa mengubah data lama.
2. **Batch:** 60 Scene berbeda digunakan sebagai *contoh pengujian penerimaan*, bukan batas maksimal baru. Identitas dan fingerprint input tiap Scene persisten dan dapat dipulihkan setelah restart.
3. **Kredit:** setiap saldo/capability/tarif nyata memiliki asal bukti, waktu pengamatan, dan masa berlaku. Jika tidak diketahui atau kedaluwarsa => `UNKNOWN / WAIT_CREDIT`. Kredit simulasi tidak pernah diakui sebagai saldo akun nyata.
4. **Pembagian kerja:** alokasikan Scene hanya ke akun milik pengguna yang telah memilih ikut serta, login valid, memiliki hak menggunakan model/durasi, cukup kredit, dan kebijakan penggunaan memperbolehkan pola operasi. Proposal rencana tampil jelas dan perlu persetujuan eksplisit pengguna sebelum pengeluaran kredit; tidak ada rotasi tersembunyi.
5. **Generate:** tepat satu upaya mutasi per Scene/attempt pada satu waktu, dengan penjagaan identitas dan anggaran; timeout atau hasil tidak pasti => `ATTENTION_REQUIRED`, **tidak** auto-submit ulang.
6. **Download:** hanya untuk result yang telah terbukti valid dengan identitas per-account/per-Scene/per-attempt. MP4 per Scene disimpan secara aman, tidak menimpa file yang sudah ada; proses dapat dipulihkan setelah crash tanpa kehilangan riwayat.
7. **Output:** daftar hasil yang benar, MP4 valid yang terpasang ke Scene yang tepat, dan manifest handoff. Kegagalan parsial terlihat secara jujur; tidak boleh mengklaim semua Scene berhasil jika sebagian belum siap.
8. **Windows:** portable ZIP Windows 11 x64 berhasil dibangun, diperiksa checksum/CRC/source, lulus tes automated/fake, dan **pengguna menguji fungsi live yang relevan**. Jangan klaim hasil live jika belum diuji.

## Yang sudah terbukti dan yang belum

- **Sudah teruji secara otomatis:** UI/Scene/SQLite lokal, Hasil + manifest, kontrak Generate/Download, simulator kredit *offline*, pengamanan file, quality/visual/Windows portable CI. CI terakhir sebelum pencatatan keputusan ini: run `38069177682` pada SHA `ec421e4cf5a5f7f4effd0dac17687e7d6e4897a2`, SUCCESS 5/5 jobs.
- **Belum terpenuhi:** identitas login Flow nyata/READY pasca restart, eligibility model dan kredit tiap akun nyata, izin otomasi multiakun/provider (G1), live Generate, deteksi result dan Download nyata, konsumsi kredit dengan approval, dan pengujian penerimaan puluhan Scene melalui Flow.
- **Pengarsipan/otoritas:** original DOCX dan UI final masih tersebar dalam beberapa Draft PR (#25–#27); G0 integrasi di `main` belum selesai, meskipun sebagian sumber dan keputusan desain telah diterima di branch review.
- Rencana V1.1 dan ADR-020–023 bukan otorisasi otomatis untuk coding berisiko, transaksi kredit, browser mutation, atau merge. Recheck status gate dari sumber terbaru saat eksekusi.

## Urutan kerja paling aman dalam cakupan fitur awal

1. Verifikasi kembali source-of-truth: bandingkan Master Plan V1.1 asli, gambar/DOCX UI final, keputusan ADR yang telah disetujui, seluruh Draft PR, dan baseline code. Jangan merge bila gate/diff/CI tidak memenuhi syarat.
2. Selesaikan tahapan *offline-only* yang diizinkan setelah gate dokumentasi: skema koordinasi kredit/attempt yang disepakati, dry-run deterministik 60 Scene, integritas lintas proyek, crash/restart/no-double-spend tests, dan UI existing yang sesuai referensi. **Jangan mengklaim ada saldo nyata dalam simulasi.**
3. Saat validasi real Google dibutuhkan: minta hanya aksi pemilik yang memang harus ia lakukan di Windows untuk manual login + `READY` setelah full restart; jangan minta password/cookies/tokens. Jangan menghindari langkah ini dengan data buatan.
4. Review kebijakan Google Flow terbaru dan cara akses resmi yang diperbolehkan. Jika izin browser/multiakun tidak jelas, **jangan** jalankan otomasi browser massal. Opsi Gemini/Omni official API adalah jalur produk berbeda dengan billing/entitlement sendiri dan **memerlukan perintah eksplisit baru**; jangan mengganti provider atau memakai API secara diam-diam.
5. Jika gate provider, hak model, kredit, dan persetujuan eksplisit telah lulus, validasi satu Scene live dengan anggaran yang disetujui; baru tingkatkan bertahap ke batch dan multiakun yang diizinkan, dengan rekonsiliasi/rollback. Jika tidak lulus, hentikan fungsi live terkait, pertahankan planner lokal dan status jujur.
6. Jalankan regresi code/UI, CI Windows, build portable, lalu beri pengguna paket uji beserta batas kemampuan nyata. Perbaikan bug setelah pengguna mencoba tetap sesuai kebijakan *feature freeze*.

## Larangan klaim

Tidak boleh melabeli simulator sebagai LIVE, menjanjikan multiakun gratis tanpa pemeriksaan entitlement/policy, menjamin 100% keberhasilan Generate, memakai metode bypass CAPTCHA/limit/akun, atau menyatakan FINAL bila DoD di atas belum memenuhi bukti.

**Jangan tambahkan fitur di luar daftar yang telah disepakati. Hanya pemilik yang boleh memberi instruksi fitur baru yang spesifik.**
