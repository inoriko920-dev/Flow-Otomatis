# Flow-Otomatis — Unduh dan uji preview Windows 11 (9 Oktober 2026 WIB)

**Status:** Panduan pemakaian BUILD PREVIEW saja. Tidak menyatakan Google Flow Generate otomatis siap, tidak memberi izin pengeluaran kredit, tidak mengubah source code dan tidak mengubah gate.

## Paket Windows yang sudah benar-benar dibuat

- Repository: `inoriko920-dev/Flow-Otomatis`.
- Workflow resmi `main`: [CI run 37755852946](https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37755852946).
- Commit build: `5b74d686d44ff67f7473fe46d8fcb7a9904618bf`.
- Quality / UI visual / package-windows: ketiganya **SUCCESS**.
- Artifact untuk **Windows 11 x64**: `Flow-Otomatis-step12-i12-01-restart-proof-win-x64`.
- Artifact ID: `11539958226`, ukuran wrapper 435.727.114 byte.
- Artifact wrapper digest dari API GitHub: `sha256:5f554719b899bd7e348f7cb2062b398e4dd4c8db4e4e3acf96a987121e290faa`. **Ini digest wrapper Actions, BUKAN hash ZIP portable di dalamnya.**
- Expiration menurut GitHub: **22 Oktober 2026 09:23:21 UTC** (16:23:21 WIB). Setelah itu artifact tidak lagi dapat diandalkan. Belum tersedia GitHub Release.

## Cara mengunduh

1. Buka [halaman CI build](https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37755852946).
2. Login GitHub bila diminta.
3. Cari bagian **Artifacts**, lalu pilih `Flow-Otomatis-step12-i12-01-restart-proof-win-x64`.
4. Ekstrak ZIP artifact hasil download. Dari konfigurasi [workflow](https://github.com/inoriko920-dev/Flow-Otomatis/blob/main/.github/workflows/ci.yml), artifact seharusnya memuat:
   - `Flow-Otomatis-portable-win-x64.zip`
   - `SHA256SUMS.txt`
5. Periksa checksum ZIP portable terhadap `SHA256SUMS.txt` bila memungkinkan. Jangan menyamakan hash ZIP portable dengan digest wrapper Actions.
6. Ekstrak `Flow-Otomatis-portable-win-x64.zip` ke folder lokal biasa. Jalankan `Flow-Otomatis.exe` dari folder hasil ekstraksi. Ini aplikasi portable; tidak perlu instalasi Python.

## Uji manual wajib (I12-01)

1. Mulai `Flow-Otomatis.exe`, pilih profil Google milik sendiri.
2. Dari bantuan login, pilih **Buka / Fokuskan Sesi Login**. Login secara manual di Chrome yang terbuka. Selesaikan MFA/CAPTCHA sendiri.
3. Setelah sukses, **tutup semua jendela Chrome login** untuk profil aplikasi tersebut.
4. Di aplikasi, pilih **Cek Ulang Sesi**. Catat apakah profil memperlihatkan **READY / Siap**.
5. **Tutup sepenuhnya Flow-Otomatis**, lalu buka kembali `Flow-Otomatis.exe`.
6. Pilih profil **yang sama**, lalu jalankan **Cek Ulang Sesi** lagi.
7. Uji dianggap PASS oleh pengguna hanya bila kondisi kini tetap **READY** dan muncul **Restart berhasil diverifikasi** serta **Validasi restart: Lulus**.
8. Jika hanya `READY` dalam satu sesi, status `Belum lulus`, atau perlu login ulang, laporkan **PENDING/FAIL**, jangan klaim I12-01 lulus.

Yang boleh dibagikan untuk diagnosis: teks status, pesan error yang disamarkan, dan screenshot UI tanpa identitas akun pribadi. **Jangan bagikan** password, OTP/MFA, cookie, token, API key, profil browser, atau file sesi.

## Tetap diblokir

- Ini **preview pengujian lokal**, bukan produk multiakun otomatis yang sudah selesai.
- I12-02B2-LIVE satu Scene Google Flow Generate, I12-03-LIVE Download, serta otomatisasi multiakun **belum diizinkan/terbukti berfungsi**.
- Persetujuan desain pada Draft PR #25–#28 **bukan** persetujuan implementasi/merge/live.
- G1 izin metode otomatisasi Google Flow **UNKNOWN/BLOCKED**, G5 kuota akun **UNVERIFIED**, G6 READY pasca-restart **UNVERIFIED**, integrasi source-of-truth G0 masih perlu gate.
- **Jangan menjalankan Generate/Download live, mengonsumsi kredit, memulai coding multiakun, atau merge dari panduan ini.**

## Setelah masa simpan artifact

Jika artifact ini kedaluwarsa, jangan berikan URL sementara seolah masih hidup. Dibutuhkan build resmi baru atau keputusan terpisah untuk mengunggah ZIP portable ke mekanisme rilis yang tahan lama. Tidak ada release yang dipublikasikan oleh perubahan dokumentasi ini.
