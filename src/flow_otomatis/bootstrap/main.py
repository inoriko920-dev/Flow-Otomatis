"""Application entry point for Flow-Otomatis."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import cast

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from flow_otomatis.application.services import (
    EpisodeImportService,
    GeminiAgentService,
    GeminiKeyService,
    GoogleFlowPreflightService,
    GoogleSessionService,
    LocalResultsService,
    ProjectLibraryService,
    ScenePlanningService,
)
from flow_otomatis.infrastructure.external import (
    GeminiGenerateContentAgent,
    GeminiModelsHealthChecker,
)
from flow_otomatis.infrastructure.filesystem import (
    EpisodePackageReader,
    PathService,
    ResultManifestWriter,
)
from flow_otomatis.infrastructure.persistence import (
    SqliteDownloadResultRepository,
    SqliteGeminiKeyRepository,
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)
from flow_otomatis.infrastructure.secrets import KeyringSecretStore
from flow_otomatis.presentation.fixtures import DEFAULT_FIXTURE_CODE
from flow_otomatis.presentation.main_window import MainWindow
from flow_otomatis.workers.browser import (
    GoogleFlowPreflightWorker,
    GoogleSessionWorker,
    SystemChromeCdpPool,
    SystemChromeGoogleSessionDriver,
    ThreadedGoogleSessionCommands,
)


def build_main_window(fixture_code: str = DEFAULT_FIXTURE_CODE) -> MainWindow:
    """Create the production shell with local STEP 10/11 adapters."""

    paths = PathService.discover()
    package_reader = EpisodePackageReader()
    workspace_repository = SqliteWorkspaceRepository(paths.projects_root)
    import_service = EpisodeImportService(
        package_reader, workspace_repository, image_verifier=package_reader
    )
    planning_service = ScenePlanningService(
        package_reader, workspace_repository, image_verifier=package_reader
    )
    library_service = ProjectLibraryService(workspace_repository)
    job_repository = SqliteGenerationJobRepository(paths.projects_root)
    download_repository = SqliteDownloadResultRepository(paths.projects_root)
    results_service = LocalResultsService(
        workspace_repository,
        job_repository,
        download_repository,
        ResultManifestWriter(paths.projects_root),
    )
    chrome_pool = SystemChromeCdpPool()
    google_session_worker = GoogleSessionWorker(
        paths.session_root,
        driver=SystemChromeGoogleSessionDriver(context_pool=chrome_pool),
    )
    google_flow_worker = GoogleFlowPreflightWorker(
        paths.session_root,
        context_pool=chrome_pool,
    )
    google_browser_commands = ThreadedGoogleSessionCommands(
        google_session_worker,
        flow_preflight=google_flow_worker,
    )
    google_session_service = GoogleSessionService(
        google_session_worker,
        commands=google_browser_commands,
    )
    google_flow_preflight_service = GoogleFlowPreflightService(
        google_flow_worker,
        commands=google_browser_commands,
    )
    gemini_key_service = GeminiKeyService(
        SqliteGeminiKeyRepository(paths.settings_root / "gemini_keys.sqlite3"),
        KeyringSecretStore(),
        GeminiModelsHealthChecker(),
    )
    gemini_agent_service = GeminiAgentService(
        gemini_key_service,
        GeminiGenerateContentAgent(),
    )
    return MainWindow(
        fixture_code=fixture_code,
        episode_import_service=import_service,
        scene_planning_service=planning_service,
        image_verifier=package_reader,
        project_library_service=library_service,
        local_results_service=results_service,
        google_session_service=google_session_service,
        google_flow_preflight_service=google_flow_preflight_service,
        gemini_key_service=gemini_key_service,
        gemini_agent_service=gemini_agent_service,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the desktop application."""

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--fixture", default=DEFAULT_FIXTURE_CODE)
    parser.add_argument("--smoke-exit-ms", type=int)
    args, _unknown = parser.parse_known_args(list(argv) if argv is not None else sys.argv[1:])

    app = cast(QApplication | None, QApplication.instance())
    if app is None:
        app = QApplication([sys.argv[0]])
    app.setApplicationName("Flow-Otomatis")
    app.setOrganizationName("Flow-Otomatis")

    window = build_main_window(args.fixture)
    window.show()

    if args.smoke_exit_ms is not None:
        QTimer.singleShot(max(args.smoke_exit_ms, 0), app.quit)

    return app.exec()
