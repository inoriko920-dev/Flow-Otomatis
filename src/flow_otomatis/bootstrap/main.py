"""Application entry point for Flow-Otomatis."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import cast

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from flow_otomatis.application.services import EpisodeImportService, ScenePlanningService
from flow_otomatis.infrastructure.filesystem import EpisodePackageReader, PathService
from flow_otomatis.infrastructure.persistence import SqliteWorkspaceRepository
from flow_otomatis.presentation.fixtures import DEFAULT_FIXTURE_CODE
from flow_otomatis.presentation.main_window import MainWindow


def build_main_window(fixture_code: str = DEFAULT_FIXTURE_CODE) -> MainWindow:
    """Create the production shell with local import/planning adapters."""

    paths = PathService.discover()
    package_reader = EpisodePackageReader()
    workspace_repository = SqliteWorkspaceRepository(paths.projects_root)
    import_service = EpisodeImportService(package_reader, workspace_repository)
    planning_service = ScenePlanningService(package_reader, workspace_repository)
    return MainWindow(
        fixture_code=fixture_code,
        episode_import_service=import_service,
        scene_planning_service=planning_service,
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
