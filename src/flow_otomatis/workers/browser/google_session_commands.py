"""Dedicated single-owner command executor for Google session browser work."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from threading import Lock
from typing import TypeVar

from flow_otomatis.application.ports.google_session import (
    GoogleSessionCommandPort,
    GoogleSessionPort,
    GoogleSessionProfile,
)
from flow_otomatis.domain.errors import FlowOtomatisError

_T = TypeVar("_T")


class ThreadedGoogleSessionCommands(GoogleSessionCommandPort):
    """Own every browser-touching Google session command on one worker thread."""

    def __init__(self, sessions: GoogleSessionPort) -> None:
        self._sessions = sessions
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="flow-browser-worker",
        )
        self._lock = Lock()
        self._busy_profiles: set[str] = set()
        self._closed = False
        self._shutdown_future: Future[None] | None = None
        self._executor_shutdown = False

    def submit_open_login(self, profile_id: str) -> Future[GoogleSessionProfile]:
        return self._submit(
            (profile_id,),
            lambda: self._sessions.open_login(profile_id),
        )

    def submit_check_profile(self, profile_id: str) -> Future[GoogleSessionProfile]:
        return self._submit(
            (profile_id,),
            lambda: self._sessions.check_profile(profile_id),
        )

    def submit_check_all(
        self,
        profile_ids: tuple[str, ...],
    ) -> Future[tuple[GoogleSessionProfile, ...]]:
        unique_ids = tuple(dict.fromkeys(profile_ids))
        return self._submit(
            unique_ids,
            lambda: tuple(self._sessions.check_profile(profile_id) for profile_id in unique_ids),
        )

    def submit_cancel_profile(self, profile_id: str) -> Future[None]:
        return self._submit(
            (profile_id,),
            lambda: self._sessions.cancel_profile(profile_id),
        )

    def submit_delete_profile(self, profile_id: str) -> Future[None]:
        return self._submit(
            (profile_id,),
            lambda: self._sessions.delete_profile(profile_id),
        )

    def shutdown(self, *, timeout_s: float) -> bool:
        """Queue worker-owned cleanup and bound only the caller's wait."""

        with self._lock:
            self._closed = True
            if self._shutdown_future is None:
                self._shutdown_future = self._executor.submit(self._safe_shutdown)
            future = self._shutdown_future

        completed = True
        try:
            future.result(timeout=max(timeout_s, 0.0))
        except TimeoutError:
            completed = False
        finally:
            with self._lock:
                if not self._executor_shutdown:
                    self._executor.shutdown(wait=False, cancel_futures=False)
                    self._executor_shutdown = True
        return completed

    def _submit(
        self,
        profile_ids: tuple[str, ...],
        action: Callable[[], _T],
    ) -> Future[_T]:
        unique_ids = tuple(dict.fromkeys(profile_ids))
        with self._lock:
            if self._closed:
                return self._failed_future("Browser Worker sedang ditutup.")
            if any(profile_id in self._busy_profiles for profile_id in unique_ids):
                return self._failed_future(
                    "Operasi profil Google ini masih berjalan. Tunggu hasil pemeriksaan sebelumnya."
                )
            self._busy_profiles.update(unique_ids)
            try:
                future = self._executor.submit(self._safe_call, action)
            except RuntimeError:
                self._busy_profiles.difference_update(unique_ids)
                return self._failed_future("Browser Worker sudah ditutup.")

        future.add_done_callback(lambda _future: self._release(unique_ids))
        return future

    def _safe_call(self, action: Callable[[], _T]) -> _T:
        try:
            return action()
        except FlowOtomatisError:
            raise
        except Exception as exc:
            raise FlowOtomatisError(
                "Operasi Browser Worker gagal tanpa mengekspos detail sesi."
            ) from exc

    def _safe_shutdown(self) -> None:
        try:
            self._sessions.shutdown()
        except FlowOtomatisError:
            raise
        except Exception as exc:
            raise FlowOtomatisError(
                "Browser Worker gagal ditutup dengan bersih tanpa mengekspos detail sesi."
            ) from exc

    def _release(self, profile_ids: tuple[str, ...]) -> None:
        with self._lock:
            self._busy_profiles.difference_update(profile_ids)

    @staticmethod
    def _failed_future[T](message: str) -> Future[T]:
        future: Future[T] = Future()
        future.set_exception(FlowOtomatisError(message))
        return future
