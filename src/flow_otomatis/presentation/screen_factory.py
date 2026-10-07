"""Production screen builders for all frozen STEP 04 UI states."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.presentation.fixtures import UiFixture
from flow_otomatis.presentation.widgets import (
    card,
    danger_button,
    info_banner,
    labeled_value,
    metric_card,
    muted_label,
    page_header,
    primary_button,
    progress,
    secondary_button,
    section_header,
    status_badge,
    table_widget,
)


def _page_root(fixture: UiFixture) -> tuple[QWidget, QVBoxLayout]:
    root = QWidget()
    layout = QVBoxLayout(root)
    layout.setContentsMargins(22, 18, 22, 18)
    layout.setSpacing(13)
    layout.addWidget(page_header(fixture.title, fixture.subtitle))
    return root, layout


def _button_row(labels: Sequence[tuple[str, str]]) -> QWidget:
    widget = QWidget()
    row = QHBoxLayout(widget)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    for text, kind in labels:
        if kind == "primary":
            button = primary_button(text)
        elif kind == "danger":
            button = danger_button(text)
        else:
            button = secondary_button(text)
        row.addWidget(button)
    row.addStretch(1)
    return widget


def _project_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)
    if fixture.code == "UI-IMG-001B":
        layout.addWidget(
            info_banner(
                "Project dapat dipulihkan",
                "Snapshot lokal EP001 • Steve Jobs ditemukan. Periksa status sebelum melanjutkan.",
                "warning",
            )
        )

    hero, hero_layout = card(12)
    hero_layout.addWidget(section_header("Mulai produksi episode biography"))
    hero_layout.addWidget(
        muted_label(
            "Impor satu paket episode untuk menyiapkan Scene ID, approved image, "
            "motion prompt, timing, dan rekomendasi Durasi Flow secara otomatis."
        )
    )
    hero_layout.addWidget(
        _button_row(
            [
                ("Impor Paket Episode", "primary"),
                ("Buat Project", "secondary"),
                ("Buka Project", "secondary"),
            ]
        )
    )
    layout.addWidget(hero)

    layout.addWidget(
        section_header(
            "Project terbaru", "0 project" if fixture.code == "UI-IMG-001A" else "1 project"
        )
    )
    if fixture.code == "UI-IMG-001A":
        empty, empty_layout = card(7)
        empty_layout.addWidget(QLabel("Belum ada project."))
        empty_layout.addWidget(
            muted_label(
                "Impor paket episode, buat project baru, atau buka project "
                "yang sudah ada untuk memulai."
            )
        )
        layout.addWidget(empty, 1)
    else:
        recent = table_widget(
            ["Project", "Episode", "Scene", "Status", "Terakhir dibuka"],
            [
                [
                    "EP001 Steve Jobs",
                    "100 Famous People",
                    "60",
                    "Recovery tersedia",
                    "Hari ini • 10:24",
                ]
            ],
            stretch_column=0,
        )
        layout.addWidget(recent, 1)
    return root


def _scene_rows(code: str) -> list[list[str]]:
    base = [
        [
            "S016",
            "Auto • Approved",
            "Camera pushes slowly toward...",
            "7.32s",
            "8s",
            "Akun Produksi 01",
            "Siap",
            "Belum",
            "Siap",
        ],
        [
            "S017",
            "Auto • Approved",
            "Subtle parallax across the...",
            "5.42s",
            "6s",
            "Akun Produksi 01",
            "Siap",
            "Belum",
            "Siap",
        ],
        [
            "S018",
            "Auto • Approved",
            "Slow controlled dolly left...",
            "9.27s",
            "10s",
            "Akun Produksi 01",
            "Siap",
            "Belum",
            "Siap",
        ],
        [
            "S019",
            "Auto • Approved",
            "Gentle cinematic push in...",
            "3.81s",
            "4s",
            "Akun Produksi 01",
            "Siap",
            "Belum",
            "Siap",
        ],
        [
            "S020",
            "Auto • Approved",
            "Character remains stable...",
            "7.90s",
            "8s",
            "Akun Produksi 01",
            "Siap",
            "Belum",
            "Siap",
        ],
        [
            "S021",
            "Auto • Approved",
            "Soft handheld movement...",
            "6.00s",
            "6s",
            "Akun Produksi 01",
            "Siap",
            "Belum",
            "Siap",
        ],
        [
            "S022",
            "Auto • Approved",
            "Controlled rack focus...",
            "8.20s",
            "10s",
            "Akun Produksi 01",
            "Siap",
            "Belum",
            "Siap",
        ],
        [
            "S023",
            "Auto • Approved",
            "Slow pan reveals the room...",
            "4.55s",
            "6s",
            "Akun Produksi 01",
            "Siap",
            "Belum",
            "Siap",
        ],
    ]
    if code == "UI-IMG-002B":
        base[0][6:] = ["Sedang", "Belum", "Sedang Diproses"]
        base[1][6:] = ["Menunggu", "Belum", "Menunggu"]
        base[2][6:] = ["Menunggu", "Belum", "Menunggu"]
    elif code == "UI-IMG-002C":
        base[0][5:] = ["Akun Produksi 02", "Tertahan", "Belum", "Butuh Perhatian"]
        base[1][5:] = ["Akun Produksi 02", "Tertahan", "Belum", "Butuh Perhatian"]
    elif code == "UI-IMG-002D":
        base[0][1] = "MISSING_IMAGE"
        base[0][6:] = ["Diblokir", "Belum", "Gambar Hilang"]
        base[1][1] = "DUPLICATE_IMAGE"
        base[1][6:] = ["Diblokir", "Belum", "Duplikat"]
        base[2][1] = "IMAGE_UNREADABLE"
        base[2][6:] = ["Diblokir", "Belum", "Tidak Terbaca"]
    return base


def _workspace_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)

    if fixture.code == "UI-IMG-002B":
        layout.addWidget(
            info_banner(
                "Batch berjalan • 1/60",
                "Scene diproses satu per satu. Jeda menghentikan penjadwalan scene berikutnya.",
                "info",
            )
        )
    elif fixture.code == "UI-IMG-002C":
        layout.addWidget(
            info_banner(
                "Sesi profil perlu login ulang",
                "Batch dijeda dengan aman. Selesaikan login secara manual "
                "lalu pilih Cek Ulang Sesi.",
                "warning",
            )
        )
    elif fixture.code == "UI-IMG-002D":
        layout.addWidget(
            info_banner(
                "3 masalah pemetaan gambar",
                "Scene dengan gambar hilang, duplikat, atau tidak terbaca tidak dapat dijalankan.",
                "error",
            )
        )
    else:
        layout.addWidget(
            info_banner(
                "Paket biography tersinkron",
                "60 scene • approved image auto-mapped • Target dari SRT • "
                "Omni Flash 1.1 • 720p • 16:9",
                "success",
            )
        )

    controls = QWidget()
    controls_row = QHBoxLayout(controls)
    controls_row.setContentsMargins(0, 0, 0, 0)
    search = QLineEdit()
    search.setPlaceholderText("Cari Scene ID atau prompt...")
    search.setMaximumWidth(330)
    controls_row.addWidget(search)
    filter_box = QComboBox()
    filter_box.addItems(["Semua status", "Siap", "Sedang Diproses", "Butuh Perhatian"])
    filter_box.setMaximumWidth(170)
    controls_row.addWidget(filter_box)
    controls_row.addStretch(1)
    controls_row.addWidget(secondary_button("Scan Ulang Gambar"))
    if fixture.code == "UI-IMG-002B":
        controls_row.addWidget(primary_button("Jeda Batch"))
    else:
        controls_row.addWidget(primary_button("Mulai Batch"))
    layout.addWidget(controls)

    table = table_widget(
        ["Scene", "Gambar", "Prompt", "Target", "Flow", "Profil", "Generate", "Download", "Status"],
        _scene_rows(fixture.code),
        stretch_column=2,
    )
    table.setCurrentCell(0, 0)
    layout.addWidget(table, 1)

    footer = QWidget()
    footer_row = QHBoxLayout(footer)
    footer_row.setContentsMargins(0, 0, 0, 0)
    footer_row.addWidget(
        muted_label(
            "60 scene • 57 Siap • 3 perlu diperiksa"
            if fixture.code == "UI-IMG-002D"
            else "60 scene • 60 siap"
        )
    )
    footer_row.addStretch(1)
    footer_row.addWidget(status_badge("Omni Flash 1.1 • 720p • 16:9", "info"))
    layout.addWidget(footer)
    return root


def _results_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)
    metrics = QWidget()
    row = QHBoxLayout(metrics)
    row.setContentsMargins(0, 0, 0, 0)
    if fixture.code == "UI-IMG-003B":
        values = [
            ("Generate", "60/60", "Selesai", "success"),
            ("Download", "57/60", "3 perlu diulang", "warning"),
            ("Perhatian", "3", "Retry download", "warning"),
        ]
    else:
        values = [
            ("Generate", "60/60", "Selesai", "success"),
            ("Download", "60/60", "Tersimpan", "success"),
            ("Perhatian", "0", "Bersih", "success"),
        ]
    for title, value, detail, kind in values:
        row.addWidget(metric_card(title, value, detail, kind), 1)
    layout.addWidget(metrics)

    rows = [
        ["S016", "7.32s", "8s", "Selesai", "Tersimpan", "EP001_SCENE_016.mp4"],
        ["S017", "5.42s", "6s", "Selesai", "Tersimpan", "EP001_SCENE_017.mp4"],
        ["S018", "9.27s", "10s", "Selesai", "Tersimpan", "EP001_SCENE_018.mp4"],
        ["S019", "3.81s", "4s", "Selesai", "Tersimpan", "EP001_SCENE_019.mp4"],
        ["S020", "7.90s", "8s", "Selesai", "Tersimpan", "EP001_SCENE_020.mp4"],
    ]
    if fixture.code == "UI-IMG-003B":
        rows[1][4:] = ["Gagal", "Retry download"]
        rows[3][4:] = ["Gagal", "Retry download"]
        rows[4][4:] = ["Gagal", "Retry download"]
    layout.addWidget(
        table_widget(
            ["Scene", "Target", "Flow", "Generate", "Download", "Output"],
            rows,
            stretch_column=5,
        ),
        1,
    )
    if fixture.code == "UI-IMG-003C":
        layout.addWidget(
            info_banner(
                "Handoff siap",
                "60/60 video generated • 60/60 video downloaded • "
                "FLOW_OTOMATIS_RESULT.json diperbarui.",
                "success",
            )
        )
        layout.addWidget(
            _button_row(
                [("Tandai Siap untuk Editing", "primary"), ("Buka Folder Output", "secondary")]
            )
        )
    elif fixture.code == "UI-IMG-003B":
        layout.addWidget(
            _button_row([("Retry Download Terpilih", "primary"), ("Buka Diagnostik", "secondary")])
        )
    return root


def _profiles_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)
    layout.addWidget(_button_row([("Tambah Profil", "primary"), ("Cek Semua Sesi", "secondary")]))
    rows = [
        ["Akun Produksi 01", "Siap", "Tersedia", "10:22", "Sesi tervalidasi"],
        ["Akun Produksi 02", "Siap", "Tersedia", "10:21", "Sesi tervalidasi"],
        ["Akun Produksi 03", "Perlu Login", "Tidak tersedia", "09:48", "Login manual diperlukan"],
    ]
    table = table_widget(
        ["Profil", "Status", "Ketersediaan", "Cek terakhir", "Catatan"], rows, stretch_column=4
    )
    table.setCurrentCell(0 if fixture.code == "UI-IMG-004B" else 2, 0)
    layout.addWidget(table, 1)
    if fixture.code == "UI-IMG-004B":
        detail, detail_layout = card(6)
        detail_layout.addWidget(
            section_header("Akun Produksi 01", "Profil internal milik pengguna")
        )
        detail_layout.addWidget(labeled_value("Status", "Siap", strong=True))
        detail_layout.addWidget(labeled_value("Session", "Authorized persistent context"))
        detail_layout.addWidget(labeled_value("Terakhir dicek", "Hari ini • 10:22"))
        detail_layout.addWidget(
            _button_row(
                [
                    ("Buka Sesi", "secondary"),
                    ("Nonaktifkan", "secondary"),
                    ("Hapus Profil", "danger"),
                ]
            )
        )
        layout.addWidget(detail)
    return root


def _login_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)
    kind = "success" if fixture.code == "UI-IMG-005B" else "warning"
    title = (
        "Sesi berhasil diverifikasi" if fixture.code == "UI-IMG-005B" else "Login manual diperlukan"
    )
    detail = (
        "Akun Produksi 03 sekarang siap digunakan."
        if fixture.code == "UI-IMG-005B"
        else (
            "Aplikasi tidak mengisi password, MFA, atau CAPTCHA. "
            "Selesaikan sendiri pada halaman resmi."
        )
    )
    layout.addWidget(info_banner(title, detail, kind))
    steps, steps_layout = card(8)
    steps_layout.addWidget(section_header("Langkah aman"))
    steps_layout.addWidget(labeled_value("1", "Buka / fokuskan sesi login resmi Google"))
    steps_layout.addWidget(labeled_value("2", "Selesaikan login, MFA, atau CAPTCHA secara manual"))
    steps_layout.addWidget(labeled_value("3", "Kembali ke Flow-Otomatis lalu pilih Cek Ulang Sesi"))
    steps_layout.addWidget(
        _button_row([("Buka / Fokuskan Sesi Login", "primary"), ("Cek Ulang Sesi", "secondary")])
    )
    layout.addWidget(steps)
    layout.addStretch(1)
    return root


def _keys_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)
    if fixture.code == "UI-IMG-006B":
        layout.addWidget(
            info_banner(
                "Preview impor key",
                "Full API key hanya digunakan saat penyimpanan dan tidak ditampilkan kembali.",
                "info",
            )
        )
    layout.addWidget(_button_row([("Impor TXT / Paste", "primary"), ("Cek Health", "secondary")]))
    rows = [
        ["Gemini Utama", "••••••••••7H2K", "Aktif", "10:18", "AI Agent"],
        ["Gemini Cadangan", "••••••••••9PQM", "Aktif", "10:17", "AI Agent"],
        ["Key 03", "••••••••••4ZXT", "Belum dicek", "—", "Tidak aktif"],
    ]
    if fixture.code == "UI-IMG-006B":
        rows = [
            ["Baris 1", "••••••••••7H2K", "Valid", "Baru", "Akan disimpan"],
            ["Baris 2", "••••••••••9PQM", "Duplikat", "Sudah ada", "Lewati"],
            ["Baris 3", "••••••••••4ZXT", "Valid", "Baru", "Akan disimpan"],
        ]
    layout.addWidget(
        table_widget(
            ["Label", "Key", "Status", "Cek terakhir", "Penggunaan"], rows, stretch_column=0
        ),
        1,
    )
    return root


def _settings_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)
    production, production_layout = card(7)
    production_layout.addWidget(section_header("Pengaturan Produksi (Terkunci)"))
    production_layout.addWidget(labeled_value("Model", "Omni Flash 1.1", strong=True))
    production_layout.addWidget(labeled_value("Resolusi", "720p", strong=True))
    production_layout.addWidget(labeled_value("Rasio Aspek", "16:9", strong=True))
    production_layout.addWidget(
        muted_label(
            "Jika model tidak tersedia atau berubah, workflow masuk HOLD "
            "untuk review formal. Tidak ada switch diam-diam."
        )
    )
    layout.addWidget(production)

    app_card, app_layout = card(7)
    app_layout.addWidget(section_header("Aplikasi"))
    app_layout.addWidget(labeled_value("Bahasa", "Bahasa Indonesia"))
    app_layout.addWidget(labeled_value("Queue R1", "Serial • concurrency 1"))
    app_layout.addWidget(labeled_value("Autosave", "Aktif untuk state lokal"))
    app_layout.addWidget(labeled_value("Provider berbayar", "Nonaktif • perlu persetujuan biaya"))
    layout.addWidget(app_card)
    layout.addStretch(1)
    return root


def _diagnostics_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)
    layout.addWidget(
        _button_row([("Export Diagnostik Tersamarkan", "secondary"), ("Refresh", "primary")])
    )
    events = [
        ["10:24:12", "S016", "Download selesai", "Download", "Sukses"],
        ["10:23:58", "S017", "Generation selesai", "Generate", "Sukses"],
        ["10:23:31", "S018", "Menunggu hasil provider", "Generate", "Info"],
        ["10:22:44", "S017", "Source image SCENE_017 tervalidasi", "Input", "Sukses"],
        ["10:21:07", "Profil 03", "Login manual diperlukan", "Session", "Perhatian"],
    ]
    table = table_widget(["Waktu", "Terkait", "Pesan", "Stage", "Status"], events, stretch_column=2)
    table.setCurrentCell(3 if fixture.code == "UI-IMG-008B" else 0, 0)
    layout.addWidget(table, 1)
    if fixture.code == "UI-IMG-008B":
        detail, detail_layout = card(5)
        detail_layout.addWidget(section_header("Detail teknis • S017"))
        detail_layout.addWidget(labeled_value("Event", "IMAGE_SOURCE_VALIDATED"))
        detail_layout.addWidget(
            labeled_value("Source", "…/ApprovedImages/EP001_STEVE_JOBS__IMAGE__SCENE_017__v1.0.png")
        )
        detail_layout.addWidget(labeled_value("Profile ID", "profile_•••03"))
        detail_layout.addWidget(labeled_value("Credential", "Tidak disertakan"))
        layout.addWidget(detail)
    else:
        layout.addWidget(
            info_banner(
                "AI Agent tidak melakukan retry otomatis",
                "Agent dapat mengusulkan retry. Tindakan material selalu "
                "ditinjau dan disetujui pengguna.",
                "info",
            )
        )
    return root


def _recovery_screen(fixture: UiFixture) -> QWidget:
    root, layout = _page_root(fixture)
    if fixture.code == "UI-IMG-009B":
        layout.addWidget(
            info_banner(
                "Status external belum dapat dipastikan",
                "Job S018 mungkin sudah terkirim sebelum aplikasi berhenti. "
                "Verifikasi dulu; jangan submit ulang.",
                "warning",
            )
        )
        recovery, recovery_layout = card(7)
        recovery_layout.addWidget(section_header("Job ambigu • S018"))
        recovery_layout.addWidget(labeled_value("State lokal", "SUBMITTING sebelum shutdown"))
        recovery_layout.addWidget(labeled_value("External evidence", "Belum cukup"))
        recovery_layout.addWidget(labeled_value("Tindakan aman", "Verifikasi Status"))
        recovery_layout.addWidget(
            _button_row([("Verifikasi Status", "primary"), ("Lewati Sementara", "secondary")])
        )
        layout.addWidget(recovery)
    else:
        layout.addWidget(
            info_banner(
                "Snapshot recovery tersedia",
                "Project EP001 dapat dikembalikan ke state lokal terakhir "
                "tanpa membuat generation baru.",
                "warning",
            )
        )
        recovery, recovery_layout = card(7)
        recovery_layout.addWidget(section_header("EP001 Steve Jobs"))
        recovery_layout.addWidget(labeled_value("Scene", "60"))
        recovery_layout.addWidget(labeled_value("Progress", "17/60 tersimpan"))
        recovery_layout.addWidget(labeled_value("Snapshot", "Hari ini • 10:23"))
        recovery_layout.addWidget(progress(28))
        recovery_layout.addWidget(
            _button_row([("Pulihkan Project", "primary"), ("Buang Snapshot", "secondary")])
        )
        layout.addWidget(recovery)
    layout.addStretch(1)
    return root


def _dialog_screen(fixture: UiFixture) -> QWidget:
    root = QWidget()
    outer = QVBoxLayout(root)
    outer.setContentsMargins(80, 50, 80, 50)
    outer.addStretch(1)
    modal, modal_layout = card(11)
    modal.setMaximumWidth(790)
    modal_layout.addWidget(page_header(fixture.title, fixture.subtitle))

    if fixture.code == "UI-IMG-001C":
        modal_layout.addWidget(labeled_value("Paket", "EP001_STEVE_JOBS_FLOW_OTOMATIS.zip"))
        modal_layout.addWidget(labeled_value("Scene", "60"))
        modal_layout.addWidget(labeled_value("Manifest", "FLOW_OTOMATIS_IMPORT.json • ditemukan"))
        modal_layout.addWidget(
            info_banner(
                "Siap divalidasi", "Credential tidak pernah diimpor dari paket episode.", "success"
            )
        )
        modal_layout.addWidget(_button_row([("Validasi Paket", "primary"), ("Batal", "secondary")]))
    elif fixture.code == "UI-IMG-012A":
        editor = QPlainTextEdit()
        editor.setPlainText(
            "SCENE_016 | prompt gerakan...\\n"
            "SCENE_017 | prompt gerakan...\\n"
            "SCENE_018 | prompt gerakan..."
        )
        editor.setMinimumHeight(170)
        modal_layout.addWidget(editor)
        modal_layout.addWidget(
            info_banner(
                "3 scene terbaca",
                "Bulk TXT adalah fallback. Episode package tetap jalur utama biography.",
                "info",
            )
        )
        modal_layout.addWidget(_button_row([("Preview Import", "primary"), ("Batal", "secondary")]))
    elif fixture.code == "UI-IMG-012B":
        modal_layout.addWidget(
            table_widget(
                ["Scene", "Gambar", "Prompt", "Target", "Rekomendasi", "Pilihan", "Status"],
                [
                    ["S016", "Approved", "Ada", "7.32s", "8s", "8s", "Valid"],
                    ["S017", "Approved", "Ada", "5.42s", "6s", "6s", "Valid"],
                    ["S018", "Approved", "Ada", "9.27s", "10s", "10s", "Valid"],
                ],
                stretch_column=2,
            )
        )
        modal_layout.addWidget(
            info_banner(
                "60/60 scene valid",
                "Durasi rekomendasi bukan pilihan final sampai dikonfirmasi operator.",
                "success",
            )
        )
        modal_layout.addWidget(_button_row([("Buat Workspace", "primary"), ("Batal", "secondary")]))
    elif fixture.code == "UI-IMG-013A":
        modal_layout.addWidget(
            info_banner(
                "Tindakan ini hanya menghapus data lokal aplikasi",
                "Akun Google tidak akan dihapus.",
                "warning",
            )
        )
        modal_layout.addWidget(labeled_value("Profil", "Akun Produksi 03"))
        modal_layout.addWidget(labeled_value("Yang dihapus", "Hubungan profil + session lokal"))
        modal_layout.addWidget(_button_row([("Hapus Profil", "danger"), ("Batal", "secondary")]))
    elif fixture.code == "UI-IMG-014A":
        modal_layout.addWidget(
            info_banner(
                "1 scene sedang diproses",
                "Flow-Otomatis tidak menjanjikan batch tetap berjalan setelah aplikasi ditutup.",
                "warning",
            )
        )
        modal_layout.addWidget(labeled_value("Scene aktif", "S016"))
        modal_layout.addWidget(labeled_value("Aksi aman", "Jeda penjadwalan lalu keluar"))
        modal_layout.addWidget(
            _button_row([("Jeda & Keluar", "primary"), ("Tetap Buka", "secondary")])
        )
    else:
        modal_layout.addWidget(
            info_banner(
                "Provider berbayar masih nonaktif",
                "Aktivasi dapat menimbulkan biaya. Tidak ada janji kredit gratis.",
                "warning",
            )
        )
        modal_layout.addWidget(labeled_value("Model", "Omni Flash 1.1"))
        modal_layout.addWidget(labeled_value("Mode", "Provider API berbayar • opsional"))
        consent = QCheckBox("Saya memahami kemungkinan biaya dan ingin mengaktifkan provider ini.")
        modal_layout.addWidget(consent)
        action = primary_button("Aktifkan Provider")
        action.setEnabled(False)
        modal_layout.addWidget(_button_row([("Batal", "secondary")]))
        modal_layout.addWidget(action, alignment=Qt.AlignmentFlag.AlignRight)

    center = QWidget()
    center_layout = QHBoxLayout(center)
    center_layout.addStretch(1)
    center_layout.addWidget(modal, 1)
    center_layout.addStretch(1)
    outer.addWidget(center)
    outer.addStretch(1)
    return root


def build_screen(fixture: UiFixture) -> QWidget:
    """Build the central production screen for a frozen fixture."""

    builders = {
        "project": _project_screen,
        "workspace": _workspace_screen,
        "results": _results_screen,
        "profiles": _profiles_screen,
        "login": _login_screen,
        "keys": _keys_screen,
        "settings": _settings_screen,
        "diagnostics": _diagnostics_screen,
        "recovery": _recovery_screen,
        "dialog": _dialog_screen,
    }
    return builders[fixture.family](fixture)


def _scene_panel(fixture: UiFixture) -> QWidget:
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(12, 10, 12, 12)
    layout.setSpacing(9)
    layout.addWidget(section_header("Scene", "S016"))
    thumb = QLabel("APPROVED IMAGE\\nSCENE_016")
    thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    thumb.setMinimumHeight(160)
    thumb.setStyleSheet(
        "background:#E5E7EB; border:1px solid #CBD5E1; border-radius:7px; color:#64748B;"
    )
    layout.addWidget(thumb)
    layout.addWidget(
        status_badge("Auto-mapped • Approved", "success"), alignment=Qt.AlignmentFlag.AlignLeft
    )
    layout.addWidget(labeled_value("Target", "7.32s", strong=True))
    layout.addWidget(labeled_value("Rekomendasi", "8s"))
    layout.addWidget(section_header("Durasi Flow"))
    buttons = QWidget()
    row = QHBoxLayout(buttons)
    row.setContentsMargins(0, 0, 0, 0)
    for value in ("4s", "6s", "8s", "10s"):
        button = secondary_button(value)
        if value in {"4s", "6s"}:
            button.setEnabled(False)
        if value == "8s":
            button.setObjectName("Primary")
        row.addWidget(button)
    layout.addWidget(buttons)
    layout.addWidget(labeled_value("Model", "Omni Flash 1.1"))
    layout.addWidget(labeled_value("Resolusi", "720p"))
    layout.addWidget(labeled_value("Rasio", "16:9"))
    prompt = QPlainTextEdit()
    prompt.setPlainText(
        "Camera pushes slowly toward the subject with subtle parallax "
        "and stable character continuity."
    )
    prompt.setMinimumHeight(95)
    layout.addWidget(prompt)
    layout.addStretch(1)
    return panel


def _agent_panel(fixture: UiFixture) -> QWidget:
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(12, 10, 12, 12)
    layout.setSpacing(9)
    layout.addWidget(section_header("AI Agent", "EP001 • S016"))
    if fixture.right_panel == "agent_preview":
        layout.addWidget(info_banner("Tinjau Aksi AI", "Aksi material belum dijalankan.", "info"))
        preview, preview_layout = card(5)
        preview_layout.addWidget(labeled_value("Aksi", "Retry download S017"))
        preview_layout.addWidget(labeled_value("Scope", "1 scene"))
        preview_layout.addWidget(
            labeled_value("Alasan", "Generate sukses, file lokal belum tersimpan")
        )
        preview_layout.addWidget(labeled_value("Risiko", "Rendah • tidak membuat generation baru"))
        preview_layout.addWidget(_button_row([("Terapkan", "primary"), ("Batal", "secondary")]))
        layout.addWidget(preview)
    elif fixture.right_panel == "agent_partial":
        layout.addWidget(
            info_banner(
                "Selesai sebagian", "2 langkah berhasil, 1 langkah memerlukan perhatian.", "warning"
            )
        )
        layout.addWidget(labeled_value("✓", "S016 download berhasil"))
        layout.addWidget(labeled_value("✓", "S017 status diverifikasi"))
        layout.addWidget(labeled_value("!", "S018 sesi profil perlu login"))
        layout.addWidget(_button_row([("Buka Bantuan Login", "primary")]))
    else:
        bubble, bubble_layout = card(6)
        bubble_layout.addWidget(
            QLabel("Saya siap membantu membaca status project dan mengusulkan tindakan yang aman.")
        )
        bubble_layout.addWidget(
            muted_label("Aksi material akan selalu ditampilkan untuk ditinjau sebelum dijalankan.")
        )
        layout.addWidget(bubble)
        layout.addWidget(
            status_badge("Tidak ada aksi otomatis", "info"), alignment=Qt.AlignmentFlag.AlignLeft
        )
    layout.addStretch(1)
    input_box = QLineEdit()
    input_box.setPlaceholderText("Tanyakan status project atau minta usulan tindakan...")
    layout.addWidget(input_box)
    layout.addWidget(primary_button("Kirim"))
    return panel


def build_right_panel(fixture: UiFixture) -> QWidget | None:
    """Build the right Scene/AI Agent dock when required by the fixture."""

    if fixture.right_panel is None:
        return None
    tabs = QTabWidget()
    tabs.setObjectName("RightDock")
    scene = _scene_panel(fixture)
    agent = _agent_panel(fixture)
    tabs.addTab(scene, "Scene")
    tabs.addTab(agent, "AI Agent")
    if fixture.right_panel.startswith("agent"):
        tabs.setCurrentIndex(1)
    return tabs
