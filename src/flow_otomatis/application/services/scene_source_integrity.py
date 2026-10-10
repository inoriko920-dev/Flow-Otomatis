"""Shared, read-only source integrity check for a persisted Generate revision."""

from __future__ import annotations

from pathlib import Path

from flow_otomatis.application.ports.episode_package import EpisodeImageVerifierPort
from flow_otomatis.application.services.local_generation_queue import _scene_fingerprint
from flow_otomatis.domain.job import GenerationJob
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene


def matches_current_generated_scene(
    job: GenerationJob,
    scene: WorkspaceScene,
    source_package_path: str,
    image_verifier: EpisodeImageVerifierPort | None,
) -> bool:
    """Require matching prepared metadata and, when configured, source bytes.

    An unverified/missing source must not authorize cached or new Download.
    The optional verifier preserves old offline consumers; production callers
    must compose the canonical package reader before certifying real results.
    """

    metadata_current = (
        job.has_verified_request_snapshot
        and scene.image_exists
        and scene.readiness is SceneReadiness.READY
        and job.target_duration_s == scene.target_duration_s
        and job.flow_duration_s == scene.selected_flow_duration_s
        and job.image_file == scene.image_file
        and job.motion_prompt == scene.motion_prompt
        and job.model == scene.model
        and job.resolution == scene.resolution
        and job.aspect_ratio == scene.aspect_ratio
    )
    if not metadata_current:
        return False
    if image_verifier is None:
        return True
    try:
        digest = image_verifier.image_digest(
            Path(source_package_path), scene.scene_id, scene.image_file
        )
    except Exception:
        # Files/ZIP contents and external verifier implementations are untrusted.
        # No raw path, session URL or exception text may appear in handoff.
        return False
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(char not in "0123456789abcdef" for char in digest)
    ):
        return False
    if scene.image_sha256_imported is not None and digest != scene.image_sha256_imported:
        return False
    return job.request_fingerprint == _scene_fingerprint(job.episode_id, scene, digest)
