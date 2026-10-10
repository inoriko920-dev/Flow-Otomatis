# AGENTS.md — Flow-Otomatis

## Identity
Flow-Otomatis is a Windows 11 x64 desktop application distributed as a portable ZIP. Primary UI language: Indonesian.

## Read before changing anything
1. PROJECT_STATE.md
2. TASKS.md
3. docs/planning/
4. docs/ui/
5. docs/architecture/
6. docs/adr/
7. docs/handoff/current/

## ATURAN PEMILIK — FEATURE FREEZE / NO NEW FEATURES (MANDATORY)

**Berlaku untuk ASTRA, SOL, AI coding agent, kontributor, seluruh branch/PR, build, dan rilis.**
Fitur, fungsi, alur, perilaku, integrasi, serta UI yang telah disepakati **DIKUNCI**. Fokus pekerjaan berikutnya adalah menyelesaikan fitur yang SUDAH disetujui, memperbaiki bug, keamanan, kestabilan, regresi, kesesuaian UI dengan referensi final, dan kesiapan build/packaging. Jangan menambah, menghapus, mengganti, memperluas, atau merancang ulang fitur/UX tanpa instruksi baru yang **spesifik dan eksplisit** dari pemilik.

- DILARANG: fitur baru, menu/tombol/screen/mode/opsi/otomasi/provider baru, perubahan perilaku yang disepakati, perubahan UI tanpa referensi/persetujuan, serta "improvement" spekulatif.
- BOLEH: perbaikan bug, tes/regresi, refactor tanpa perubahan perilaku pengguna, hardening keamanan dan kompatibilitas, perbaikan implementasi yang sudah disetujui, serta build/rilis untuk diuji. Helper internal baru hanya bila diperlukan untuk perbaikan, bukan perluasan fungsi produk.
- Perintah **"lanjutkan"**, **"cek bug"**, **"perbaiki"**, **"final"**, atau **"build"** bukan izin menambah fitur. Saran ASTRA/SOL/AI, rencana terdahulu yang belum disetujui, dan asumsi teknis bukan izin.
- **Satu-satunya pengecualian:** pemilik secara eksplisit meminta fitur/perubahan tertentu; dokumentasikan cakupan persis dan izin tersebut sebelum menerapkannya. Tidak ada izin implisit untuk fitur terkait.
- Tetap patuhi seluruh gate keamanan, sumber UI/aset resmi, persyaratan file wajib, dan pembatasan penggunaan provider/kredit; feature freeze tidak membolehkan melewati gate.
- Sebelum commit/PR: verifikasi bahwa setiap perubahan merupakan perbaikan atau realisasi fitur lama yang disetujui. Jika ada ide fitur tambahan, tulis sebagai usulan saja, **jangan diimplementasikan**.

Kebijakan lengkap: `docs/FEATURE_FREEZE_POLICY.md`. **Aturan ini mengungguli usulan fitur di dokumen perencanaan lama, kecuali pemilik memberikan instruksi baru secara eksplisit.**

## Architecture
presentation -> application -> domain
infrastructure -> application ports/domain/contracts
workers/browser -> contracts + flow_web internals
bootstrap -> composition only

## Search before create
Before adding a file/class/service/helper:
- search exact concept + synonyms;
- search canonical owner, ports/interfaces, tests, config, call-sites/imports;
- read nearest tests/contracts;
- state why existing canonical owner is insufficient.

## Forbidden
- secrets/session/cookie/token in repo/log/docs/fixtures;
- hard-coded C:\ or D:\ paths or CWD dependence;
- presentation importing infrastructure/provider/browser/sqlite/keyring;
- direct Playwright outside browser worker/flow_web;
- generic utils.py/helpers2.py/Manager dumping grounds;
- hidden mutable global state;
- force reset/overwrite unknown work;
- generated build/cache/user-data commits;
- claiming tests/live provider behavior that were not run;
- production coding while PROJECT_STATE says documentation gate BLOCKED.

## Planned canonical commands
- uv sync --frozen
- uv run ruff format --check .
- uv run ruff check .
- uv run mypy src/flow_otomatis
- uv run python scripts/check_architecture.py
- uv run pytest -q tests/unit tests/contract

## Change protocol
BEFORE: verify branch/SHA/diff, identify canonical owner/tests.
DURING: keep scope focused, preserve frozen product/UI, update tests with behavior.
AFTER: run gates, review diff, update TASKS.md/PROJECT_STATE.md, record evidence.

## Astra review triggers
Stop affected work for cross-module contract/schema/migration/core dependency/security boundary/process model/UI freeze/provider-policy changes.

## Portable contract
Use canonical PathService. LocalAppData owns app/session/log/cache state. Projects are user-selectable. Never rely on shell CWD.
