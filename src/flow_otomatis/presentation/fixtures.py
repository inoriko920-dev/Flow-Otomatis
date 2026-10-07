"""Frozen STEP 09 UI fixture registry.

The registry maps each approved STEP 04 visual state to one production
presentation state. It contains display-only sample data; business persistence
and provider integration remain outside STEP 09.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UiFixture:
    """One approved visual state from the STEP 04 reference pack."""

    code: str
    surface: str
    state: str
    priority: str
    nav_item: str
    family: str
    title: str
    subtitle: str
    right_panel: str | None = None


_FIXTURES = (
    UiFixture(
        "UI-IMG-001A",
        "Project Hub",
        "Empty / first run",
        "P0",
        "Beranda",
        "project",
        "Beranda",
        "Mulai project pertama Anda",
    ),
    UiFixture(
        "UI-IMG-001B",
        "Project Hub",
        "Recovery available",
        "P0",
        "Beranda",
        "project",
        "Beranda",
        "Project terakhir dapat dipulihkan",
    ),
    UiFixture(
        "UI-IMG-001C",
        "Episode Package Import",
        "Import dialog",
        "P0",
        "Beranda",
        "dialog",
        "Impor Paket Episode",
        "Validasi paket sebelum membuat workspace",
    ),
    UiFixture(
        "UI-IMG-002A",
        "Workspace",
        "Ready synchronized package",
        "P0",
        "Workspace",
        "workspace",
        "Workspace",
        "Paket biography siap diproses",
        "scene",
    ),
    UiFixture(
        "UI-IMG-002B",
        "Workspace",
        "Active batch",
        "P0",
        "Workspace",
        "workspace",
        "Workspace",
        "Batch sedang berjalan secara serial",
        "scene",
    ),
    UiFixture(
        "UI-IMG-002C",
        "Workspace",
        "Profile needs attention",
        "P0",
        "Workspace",
        "workspace",
        "Workspace",
        "Sesi profil membutuhkan perhatian",
        "agent",
    ),
    UiFixture(
        "UI-IMG-002D",
        "Workspace",
        "Image mapping problems",
        "P0",
        "Workspace",
        "workspace",
        "Workspace",
        "Periksa pemetaan approved image",
        "scene",
    ),
    UiFixture(
        "UI-IMG-003A",
        "Hasil",
        "Successful run",
        "P0",
        "Hasil",
        "results",
        "Hasil",
        "Semua generation dan download selesai",
    ),
    UiFixture(
        "UI-IMG-003B",
        "Hasil",
        "Partial download",
        "P0",
        "Hasil",
        "results",
        "Hasil",
        "Generation selesai, sebagian download perlu diulang",
    ),
    UiFixture(
        "UI-IMG-003C",
        "Hasil",
        "Editing handoff ready",
        "P0",
        "Hasil",
        "results",
        "Hasil",
        "Output video siap diteruskan ke editing",
    ),
    UiFixture(
        "UI-IMG-004A",
        "Profil Google",
        "Profiles ready",
        "P0",
        "Profil Google",
        "profiles",
        "Profil Google",
        "Kelola sesi Google yang Anda otorisasi",
    ),
    UiFixture(
        "UI-IMG-004B",
        "Profil Google",
        "Profile detail",
        "P0",
        "Profil Google",
        "profiles",
        "Profil Google",
        "Status dan detail sesi produksi",
    ),
    UiFixture(
        "UI-IMG-005A",
        "Bantuan Login",
        "Manual login required",
        "P0",
        "Profil Google",
        "login",
        "Bantuan Login",
        "Selesaikan login pada halaman resmi Google",
    ),
    UiFixture(
        "UI-IMG-005B",
        "Bantuan Login",
        "Login successful",
        "P0",
        "Profil Google",
        "login",
        "Bantuan Login",
        "Sesi berhasil diverifikasi",
    ),
    UiFixture(
        "UI-IMG-006A",
        "Gemini Keys",
        "Vault active",
        "P0",
        "Gemini Keys",
        "keys",
        "Gemini Keys",
        "Kunci tersimpan aman dalam bentuk tersamarkan",
    ),
    UiFixture(
        "UI-IMG-006B",
        "Gemini Keys",
        "Bulk import",
        "P0",
        "Gemini Keys",
        "keys",
        "Gemini Keys",
        "Preview impor key sebelum disimpan",
    ),
    UiFixture(
        "UI-IMG-007A",
        "Pengaturan",
        "Production lock",
        "P1",
        "Pengaturan",
        "settings",
        "Pengaturan",
        "Profil produksi biography dikunci",
    ),
    UiFixture(
        "UI-IMG-008A",
        "Diagnostik",
        "Activity ready",
        "P1",
        "Diagnostik",
        "diagnostics",
        "Diagnostik & Aktivitas",
        "Riwayat aktivitas yang mudah dipahami",
    ),
    UiFixture(
        "UI-IMG-008B",
        "Diagnostik",
        "Technical detail",
        "P1",
        "Diagnostik",
        "diagnostics",
        "Diagnostik & Aktivitas",
        "Detail teknis tersamarkan untuk S017",
    ),
    UiFixture(
        "UI-IMG-009A",
        "Recovery Center",
        "Recovery available",
        "P0",
        "Beranda",
        "recovery",
        "Recovery Center",
        "Pulihkan state lokal tanpa submit ulang",
    ),
    UiFixture(
        "UI-IMG-009B",
        "Recovery Center",
        "Ambiguous external job",
        "P0",
        "Beranda",
        "recovery",
        "Recovery Center",
        "Verifikasi status job sebelum tindakan berikutnya",
    ),
    UiFixture(
        "UI-IMG-010A",
        "AI Agent",
        "Idle assistant",
        "P0",
        "Workspace",
        "workspace",
        "Workspace",
        "AI Agent siap membantu dalam scope aktif",
        "agent",
    ),
    UiFixture(
        "UI-IMG-010B",
        "AI Agent",
        "Action preview",
        "P0",
        "Workspace",
        "workspace",
        "Workspace",
        "Tinjau aksi AI sebelum diterapkan",
        "agent_preview",
    ),
    UiFixture(
        "UI-IMG-010C",
        "AI Agent",
        "Partial result",
        "P0",
        "Workspace",
        "workspace",
        "Workspace",
        "Aksi AI selesai sebagian dan perlu perhatian",
        "agent_partial",
    ),
    UiFixture(
        "UI-IMG-011A",
        "Scene Inspector",
        "Duration selection",
        "P0",
        "Workspace",
        "workspace",
        "Workspace",
        "Periksa scene dan pilih Durasi Flow",
        "scene",
    ),
    UiFixture(
        "UI-IMG-012A",
        "Bulk TXT Import",
        "Preview dialog",
        "P0",
        "Workspace",
        "dialog",
        "Impor TXT Banyak Scene",
        "Jalur fallback untuk input manual",
    ),
    UiFixture(
        "UI-IMG-012B",
        "Episode Package Validation",
        "Validation dialog",
        "P0",
        "Workspace",
        "dialog",
        "Validasi Paket Episode",
        "Konfirmasi mapping, timing, dan Durasi Flow",
    ),
    UiFixture(
        "UI-IMG-013A",
        "Destructive Confirm",
        "Remove profile",
        "P1",
        "Profil Google",
        "dialog",
        "Hapus Profil",
        "Hapus hanya hubungan dan sesi lokal aplikasi",
    ),
    UiFixture(
        "UI-IMG-014A",
        "Close App",
        "Batch running",
        "P1",
        "Workspace",
        "dialog",
        "Batch Masih Berjalan",
        "Jeda dengan aman sebelum menutup aplikasi",
    ),
    UiFixture(
        "UI-IMG-015A",
        "Paid Provider Consent",
        "Cost consent",
        "P1 Conditional",
        "Pengaturan",
        "dialog",
        "Aktifkan Provider Berbayar",
        "Aktif hanya setelah persetujuan biaya eksplisit",
    ),
)

FIXTURES: dict[str, UiFixture] = {fixture.code: fixture for fixture in _FIXTURES}
FIXTURE_CODES: tuple[str, ...] = tuple(fixture.code for fixture in _FIXTURES)

NAV_ITEMS: tuple[str, ...] = (
    "Beranda",
    "Workspace",
    "Hasil",
    "Profil Google",
    "Gemini Keys",
    "Diagnostik",
    "Pengaturan",
)

DEFAULT_FIXTURE_CODE = "UI-IMG-001A"


def get_fixture(code: str) -> UiFixture:
    """Return a frozen UI fixture or raise a useful error."""

    try:
        return FIXTURES[code]
    except KeyError as exc:
        raise ValueError(f"Unknown UI fixture: {code}") from exc
