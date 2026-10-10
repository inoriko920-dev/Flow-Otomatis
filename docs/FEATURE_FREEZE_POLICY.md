# FEATURE FREEZE POLICY — Flow-Otomatis

**Status: AKTIF / WAJIB.** Penetapan pemilik: 11 Oktober 2026 (WIB).
**Lingkup:** seluruh repository, semua branch, pull request, ASTRA, SOL, coding agent, kontributor, pengujian, packaging dan rilis.
**Acuan tertinggi:** instruksi fitur baru yang jelas dan eksplisit dari pemilik aplikasi. Tidak ada izin implisit.

## 1. Keputusan pemilik

Mulai sekarang **tidak boleh ada penambahan fitur baru**. Fitur dan spesifikasi yang sebelumnya sudah disepakati dikunci. Siklus kerja selanjutnya difokuskan pada perbaikan fitur yang sudah ada, penyelesaian implementasi fitur lama yang memang telah disetujui, pencarian dan perbaikan bug, keamanan, stabilitas, pengujian, dan build untuk uji coba pemilik.

Ketentuan ini **bukan** pernyataan bahwa semua fitur telah selesai, semua provider live sudah siap, atau seluruh gate lolos. Klaim kesiapan harus selalu berdasarkan bukti pengujian.

## 2. Yang boleh dikerjakan tanpa izin fitur baru

- Memperbaiki cacat pada fungsi, proses Generate/Download, data/SQLite, UX yang tidak sesuai referensi yang telah disetujui, dan penanganan kegagalan.
- Menyelesaikan perilaku yang **sudah ditetapkan dan disetujui secara spesifik**, tanpa memperluas cakupan atau mengubah kontraknya; tetap mematuhi gate yang berlaku.
- Menambahkan/memperbaiki tes regresi, pemeriksaan keamanan, observabilitas non-sensitif, CI, dan packaging Windows untuk validasi fungsi yang disepakati.
- Refactor dan helper internal seperlunya untuk menghilangkan bug atau risiko; harus tetap mempertahankan perilaku, tampilan, workflow, dan data yang disepakati.
- Memperbaiki kesesuaian UI terhadap **aset referensi final milik pengguna**, bukan menciptakan rancangan UI baru.

## 3. Yang dilarang tanpa perintah baru yang spesifik

- Menambahkan atau memperluas fitur, menu, tombol, layar, mode, template, provider, integrasi, otomasi, opsi, atau perilaku pengguna.
- Menghapus atau mengganti fungsi yang telah disepakati, mendesain ulang alur atau tampilan, mengubah default/perilaku bisnis, atau merapikan UI dengan cara menyimpang dari referensi yang disetujui.
- Menafsirkan kalimat seperti **"lanjutkan"**, **"perbaiki bug"**, **"cek lagi"**, **"buat final"**, **"build"**, atau **"stabilkan"** sebagai persetujuan perluasan fitur.
- Menganggap saran ASTRA, SOL, AI lain, issue, roadmap, PR, atau rencana masa lalu sebagai izin menambah fitur.
- Menghasilkan sendiri gambar UI/aset yang harus dibuat pemilik, atau mengabaikan gate keamanan/login/credit/Flow yang masih BLOCKED.

## 4. Pengecualian: perintah eksplisit pemilik

Hanya pemilik yang boleh membuka pengecualian, misalnya: **"Tambahkan fitur X dengan perilaku Y"** atau **"Ubah fungsi Z menjadi W"**. Setiap pengecualian:
1. harus mengacu ke instruksi pemilik yang spesifik;
2. hanya berlaku untuk cakupan yang diminta, bukan fitur tambahan lain;
3. didokumentasikan dalam planning/PR sesuai alur ASTRA/SOL dan lulus pengujian/gate yang relevan.

Jika detailnya belum cukup, jangan mengarang ruang lingkup baru. Lanjutkan pekerjaan perbaikan lain yang aman tanpa mengubah fitur tersebut.

## 5. Checklist setiap pekerjaan dan pull request

- [ ] Apakah perubahan ini hanya perbaikan, penyelesaian fitur yang sudah disetujui, atau pengujian/build terkait?
- [ ] Apakah fungsi, UI, perilaku, data, dan alur yang disepakati tetap tidak berubah tanpa perintah eksplisit?
- [ ] Apakah perubahan teknis tetap menghormati keamanan, privasi, persetujuan, dan gate provider?
- [ ] Apakah tes/regresi/CI sesuai perubahan telah diperiksa dan hasilnya dilaporkan secara akurat?
- [ ] Jika ada fitur/perubahan baru, apakah instruksi eksplisit pemilik tercatat sebelum implementasi?

**Tidak ada persetujuan eksplisit = fitur tetap dikunci.** Ide baru boleh dicatat sebagai usulan, tetapi tidak boleh dicoding, dimasukkan ke produk, atau dirilis.
