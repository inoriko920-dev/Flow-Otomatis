"""Pure read-only local Scene preflight: never creates or dispatches generation jobs.

This is deliberately separate from LocalGenerationQueueService, which owns the
durable generation ledger and can invoke a provider when explicitly composed.
A preview report is non-executable and cannot authorize any live action.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from flow_otomatis.application.ports.episode_package import EpisodeImageVerifierPort
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import FLOW_DURATIONS, SceneReadiness, derive_scene_readiness

_SAFE_SCENE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
_REASON_LABELS = {
    "INVALID_SCENE_ID": "ID SCENE TIDAK VALID",
    "DUPLICATE_SCENE_ID": "ID SCENE GANDA",
    "INVALID_TARGET": "TARGET INVALID",
    "MISSING_IMAGE": "GAMBAR HILANG",
    "MISSING_PROMPT": "PROMPT HILANG",
    "NEEDS_DURATION_SELECTION": "PILIH DURASI",
    "INVALID_DURATION": "DURASI INVALID",
    "STALE_READINESS": "STATUS LOKAL TIDAK SESUAI",
    "IMAGE_BYTES_UNREADABLE": "BYTE GAMBAR TIDAK TERBACA",
}


def prepare_local_scene_preflight(
    workspace: WorkspaceState, *, image_verifier: EpisodeImageVerifierPort | None = None
) -> dict[str, Any]:
    """Classify saved metadata; optionally read approved bytes via a local-only port.

    An absent verifier means no filesystem I/O, preserving the fast metadata
    view. A supplied verifier *only reads* source ZIP/directory files and
    computes a fresh digest. Without a previously pinned digest this cannot
    prove the contents are unchanged since import. No durable jobs, accounts,
    credentials or network providers are ever accessed.
    """
    seen = Counter(scene.scene_id for scene in workspace.scenes)
    ready: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []
    checked_images = 0
    failed_images = 0
    for index, scene in enumerate(workspace.scenes, start=1):
        valid_id = _SAFE_SCENE_ID.fullmatch(scene.scene_id) is not None
        safe_id = scene.scene_id if valid_id else f"INVALID_SCENE_ID_AT_{index}"
        issues: list[str] = []
        if not valid_id:
            issues.append("INVALID_SCENE_ID")
        if seen[scene.scene_id] > 1:
            issues.append("DUPLICATE_SCENE_ID")

        target = scene.target_duration_s
        target_valid = type(target) in (int, float) and math.isfinite(target) and 0 < target <= 10
        if not target_valid:
            issues.append("INVALID_TARGET")
        if not scene.image_exists:
            issues.append("MISSING_IMAGE")
        if not scene.motion_prompt.strip():
            issues.append("MISSING_PROMPT")

        image_evidence = "TIDAK DIPERIKSA"
        if not scene.image_exists:
            image_evidence = "GAMBAR HILANG"
        elif image_verifier is not None:
            # Never include exception details, disk paths, or raw SHA-256 in exports.
            # Invalid or duplicated IDs cannot resolve unambiguously.
            try:
                if not valid_id or seen[scene.scene_id] != 1:
                    raise ValueError("Ambiguous Scene image identity")
                digest = image_verifier.image_digest(
                    Path(workspace.source_package_path),
                    scene.scene_id,
                    scene.image_file,
                )
                if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                    raise ValueError("Image verifier did not return a SHA-256 digest")
            except Exception:
                failed_images += 1
                image_evidence = "TIDAK TERBACA"
                issues.append("IMAGE_BYTES_UNREADABLE")
            else:
                checked_images += 1
                image_evidence = "BYTE TERBACA"

        chosen = scene.selected_flow_duration_s
        duration_valid = type(chosen) is int and chosen in FLOW_DURATIONS
        if chosen is None:
            issues.append("NEEDS_DURATION_SELECTION")
        elif not duration_valid or (target_valid and chosen < target):
            issues.append("INVALID_DURATION")

        if target_valid and (chosen is None or duration_valid):
            derived = derive_scene_readiness(
                target_duration_s=float(target),
                selected_flow_duration_s=chosen,
                image_exists=scene.image_exists,
                motion_prompt=scene.motion_prompt,
            )
            if derived is not scene.readiness:
                issues.append("STALE_READINESS")
        else:
            # A stored READY label is never accepted for invalid inputs.
            if scene.readiness is SceneReadiness.READY:
                issues.append("STALE_READINESS")

        row: dict[str, Any] = {
            "scene_id": safe_id,
            "target_duration_s": float(target) if target_valid else None,
            "flow_duration_s": chosen if duration_valid else None,
            "status": "SIAP INPUT LOKAL" if not issues else "DITAHAN",
            "image_evidence": image_evidence,
            "issues": [_REASON_LABELS[reason] for reason in issues],
        }
        if issues:
            held.append(row)
        else:
            ready.append(row)

    return {
        "mode": "NON_EXECUTABLE_LOCAL_SCENE_PREFLIGHT",
        "version": 1,
        "episode_id": workspace.episode_id,
        "total_scenes": len(workspace.scenes),
        "ready_count": len(ready),
        "held_count": len(held),
        "ready": ready,
        "held": held,
        "provider_evidence": "NONE",
        "live_dispatch_allowed": False,
        "durable_jobs_created": False,
        "credit_balance_verified": False,
        "image_bytes_verified": (
            image_verifier is not None and checked_images > 0 and failed_images == 0
        ),
        "image_integrity_check": (
            "LOCAL_SOURCE_BYTES_READ" if image_verifier is not None else "NOT_RUN"
        ),
        "verified_image_count": checked_images,
        "unreadable_image_count": failed_images,
        "warning": (
            "Byte gambar dibaca dari sumber paket asli (bukan bukti tidak berubah sejak "
            "impor); izin provider, saldo, dan sesi tetap tidak diketahui. "
            if image_verifier is not None
            else "Hanya metadata tersimpan; byte gambar belum dibaca. "
        ) + (
            "Bukan antrean yang dapat dijalankan; semua Generate live tetap diblokir."
        ),
    }
