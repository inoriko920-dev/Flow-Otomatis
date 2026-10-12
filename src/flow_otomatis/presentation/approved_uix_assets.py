"""Immutable owner-approved 22-image reference resolution and SHA-256 validation.

References are copied read-only from the UI approval branch into the standalone
Windows UI preview package. No provider, account, balance or remote data is used.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

APPROVED_IMAGES: dict[str, tuple[str, str]] = {
    "UIX-01-A": (
        "Flow_Otomatis_UIX_01_A_KOREKSI_12_DARI_60_2026-10-08.png",
        "b36c6ba4590db5d10fa182a2d00885449c19292c6e2f55d1af2adf5b5e542456",
    ),
    "UIX-01-B": (
        "Flow_Otomatis_UIX_01_B_PARTIAL_INVALID_DRAFT_2026-10-08.png",
        "235ff547063e6a366a8d0f3689d9ab5aa63f58beb4e60829efd85718d4f6fb11",
    ),
    "UIX-01-C": (
        "Flow_Otomatis_UIX_01_C_KREDIT_TARIF_BELUM_TERVERIFIKASI_DRAFT_2026-10-08.png",
        "123ff6aedc372c03f7c953fa44f9e0de56cd0565a8c52b62e79da8e4d86d431a",
    ),
    "UIX-02-A": (
        "Flow_Otomatis_UIX_02_A_SMART_CREDIT_PLAN_DRAFT_2026-10-08.png",
        "c2026aee7acfa71e2bcc114a7d57aaa2255f4b60ee7ad5bcb729cbb3f3388cb6",
    ),
    "UIX-02-B": (
        "Flow_Otomatis_UIX_02_B_KREDIT_TIDAK_CUKUP_DRAFT_2026-10-08.png",
        "5bb8cfaebea6ec0506458a0801d46872f73e44c2228564dba3ce43b097bcc394",
    ),
    "UIX-02-C": (
        "Flow_Otomatis_UIX_02_C_TIDAK_ADA_AKUN_MEMENUHI_SYARAT_DRAFT_2026-10-08.png",
        "5db9d7ef925f5c2966566d697a4932e21a0587b84592e0aa92e8767d45063690",
    ),
    "UIX-03-A": (
        "Flow_Otomatis_UIX_03_A_RINCIAN_KREDIT_PER_AKUN_DRAFT_2026-10-08.png",
        "6a7e4a1f30c83d6d4856f3a22c69b2c50825e7cf9589846616b5482c3a236bb7",
    ),
    "UIX-03-B": (
        "Flow_Otomatis_UIX_03_B_KREDIT_KADALUWARSA_MANUAL_TIDAK_DIKETAHUI_DRAFT_2026-10-08.png",
        "b745549dd066a935b4688672b636d4780c69bfee27712adf8625c2ca7b550c5a",
    ),
    "UIX-04-A": (
        "Flow_Otomatis_UIX_04_A_FREEZE_PLAN_APPROVAL_DRAFT_2026-10-08.png",
        "6b47b8db12c23cb76a87a6549754d9fc3bb63acc5a2771a09526c0073cb6b66c",
    ),
    "UIX-04-B": (
        "Flow_Otomatis_UIX_04_B_REVISI_KEDALUWARSA_DRAFT_2026-10-08.png",
        "95a6173049e889605bad4bcc7e226f2e59224ded6fe5e6e7abcbe43c1a5f7968",
    ),
    "UIX-05-A": (
        "Flow_Otomatis_UIX_05_A_RUN_MONITOR_SIMULASI_DRAFT_2026-10-08.png",
        "af17fcaf1dedfa66f9475d36e3083d435fb14be47b9660321120dbd6b67ea472",
    ),
    "UIX-05-B": (
        "Flow_Otomatis_UIX_05_B_RUN_MONITOR_JEDA_PARSIAL_DRAFT_2026-10-08.png",
        "710a151c7ed3d52b3fd03f1a0f51f84e441a8251db95c0602021536a3572624d",
    ),
    "UIX-05-C": (
        "Flow_Otomatis_UIX_05_C_SUBMIT_UNCERTAIN_DRAFT_2026-10-08.png",
        "627331e07642337c3067467c085fdc70399418fc2e4c761ecbadc75d9afb84ef",
    ),
    "UIX-06-A": (
        "Flow_Otomatis_UIX_06_A_RECOVERY_SUBMIT_UNCERTAIN_DRAFT_2026-10-08.png",
        "25e95dad2372cd8a62eab269a153c61c4a96c46f960d6bab711d9f884aa80b61",
    ),
    "UIX-06-B": (
        "Flow_Otomatis_UIX_06_B_KONFLIK_LOGIN_KREDIT_DRAFT_2026-10-08.png",
        "821c2851871a730514e527d15ba5db89ac9702087616cfc60b283b262328e142",
    ),
    "UIX-06-C": (
        "Flow_Otomatis_UIX_06_C_HASIL_GENERATE_DITEMUKAN_DRAFT_2026-10-08.png",
        "536f7774f555a2e6b7b7124cadb09710abde178125ccda606cdb6aa5fa4ffc21",
    ),
    "UIX-07-A": (
        "Flow_Otomatis_UIX_07_A_PARTIAL_REPLAN_DRAFT_2026-10-08.png",
        "f1ba5fb26b63df4785e683fcf623fb2302c06ee108179c031d87f1f6c75bccb5",
    ),
    "UIX-07-B": (
        "Flow_Otomatis_UIX_07_B_SCENE_TERKUNCI_DRAFT_2026-10-08.png",
        "f18876c55449f64c08d7d10e06adbf44f16c72fba2f73d128231453b7c383b61",
    ),
    "UIX-08-A": (
        "Flow_Otomatis_UIX_08_A_TARIF_KEDALUWARSA_DRAFT_2026-10-08.png",
        "8bf915b142ac1b6f3b8ab430485bc0ba88aebd6835cd3bf07ca45f4f0942c2b1",
    ),
    "UIX-08-B": (
        "Flow_Otomatis_UIX_08_B_KEBIJAKAN_BELUM_TERVERIFIKASI_DRAFT_2026-10-08.png",
        "546ceceabf7f713576950b23c31babc7edbf97e0730022df4589d6bf63e90db5",
    ),
    "UIX-09-A": (
        "Flow_Otomatis_UIX_09_A_HASIL_PARSIAL_DRAFT_2026-10-08.png",
        "78b1a48085a95f8311c756c9907a905fc82c5fc1cab13f323d48d5521022e7e9",
    ),
    "UIX-09-B": (
        "Flow_Otomatis_UIX_09_B_HANDOFF_12_DARI_60_DRAFT_2026-10-08.png",
        "603a1672db5c16e575106aa424f53b0c914254d3a5b0d647f77a10da1254bf49",
    ),
}


class ApprovedReferenceError(ValueError):
    """The requested UI reference is absent, ambiguous or has changed bytes."""


def reference_directories() -> tuple[Path, ...]:
    """Prefer frozen bundle images; allow an explicitly supplied owner folder."""
    candidate_paths: list[Path] = []
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        candidate_paths.append(Path(bundle) / "approved_ui")
    candidate_paths.append(Path(__file__).resolve().parents[3] / "docs/ui/final/assets")
    candidate_paths.append(Path(sys.executable).resolve().parent / "approved_ui")
    return tuple(candidate_paths)


def load_verified_reference(state_code: str, *, supplied_directory: Path | None = None) -> Path:
    """Return the exact approved PNG only after checking the pinned digest."""
    entry = APPROVED_IMAGES.get(state_code)
    if entry is None:
        raise ApprovedReferenceError("Kode UI tidak dikenal.")
    name, expected_digest = entry
    folders = (supplied_directory,) if supplied_directory is not None else reference_directories()
    any_candidate = False
    for folder in folders:
        candidate = folder / name
        if not candidate.is_file():
            continue
        any_candidate = True
        with candidate.open("rb") as stream:
            actual_digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual_digest == expected_digest:
            return candidate
        # Tampered/wrong versions must never be substituted by a later folder.
        raise ApprovedReferenceError(
            "Gambar UI ditemukan tetapi checksum SHA-256 tidak cocok. "
            "Pilih 22 PNG final yang sudah disetujui."
        )
    if any_candidate:  # Defensive; all existing candidates return or raise.
        raise ApprovedReferenceError("Gambar referensi tidak valid.")
    raise ApprovedReferenceError(
        "Gambar UI final tidak ditemukan. Pilih folder berisi 22 PNG yang disetujui."
    )
