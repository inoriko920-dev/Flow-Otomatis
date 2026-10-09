"""Pure read-only local Scene preflight: never creates or dispatches generation jobs.

This is deliberately separate from LocalGenerationQueueService, which owns the
durable generation ledger and can invoke a provider when explicitly composed.
A preview report is non-executable and cannot authorize any live action.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

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
}


def prepare_local_scene_preflight(workspace: WorkspaceState) -> dict[str, Any]:
    """Classify actual local inputs without trusting a cached READY flag.

    Does not access the filesystem, decrypt credentials, calculate provider
    credits, or call the existing durable generation job service. Image
    existence here is *persisted metadata*, not proof that bytes are intact.
    """
    seen = Counter(scene.scene_id for scene in workspace.scenes)
    ready: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []
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
        "image_bytes_verified": False,
        "warning": (
            "Hanya kelayakan input lokal dari metadata tersimpan. "
            "Tidak membuktikan byte gambar, izin provider, saldo, atau sesi. "
            "Bukan antrean yang dapat dijalankan; semua Generate live tetap diblokir."
        ),
    }
