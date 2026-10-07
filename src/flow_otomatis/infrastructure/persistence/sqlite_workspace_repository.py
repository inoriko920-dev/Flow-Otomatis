"""SQLite persistence for one imported project workspace."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene


class SqliteWorkspaceRepository:
    """Persist each episode in its own project.sqlite3 database."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def save(self, workspace: WorkspaceState) -> None:
        db_path = self._db_path(workspace.episode_id)
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(db_path) as connection:
                self._create_schema(connection)
                connection.execute("BEGIN")
                connection.execute(
                    """
                    INSERT OR REPLACE INTO project (
                        singleton, schema_version, episode_id, project_name,
                        source_package_path, created_at, imported_at,
                        model, resolution, aspect_ratio
                    ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        workspace.schema_version,
                        workspace.episode_id,
                        workspace.project_name,
                        workspace.source_package_path,
                        workspace.created_at.isoformat(),
                        workspace.imported_at.isoformat(),
                        workspace.model,
                        workspace.resolution,
                        workspace.aspect_ratio,
                    ),
                )
                connection.execute("DELETE FROM scenes")
                connection.executemany(
                    """
                    INSERT INTO scenes (
                        scene_order, scene_id, image_file, image_exists,
                        motion_prompt, target_duration_s,
                        recommended_flow_duration_s, selected_flow_duration_s,
                        readiness, trim_target_s, model, resolution, aspect_ratio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            index,
                            scene.scene_id,
                            scene.image_file,
                            int(scene.image_exists),
                            scene.motion_prompt,
                            scene.target_duration_s,
                            scene.recommended_flow_duration_s,
                            scene.selected_flow_duration_s,
                            scene.readiness.value,
                            scene.trim_target_s,
                            scene.model,
                            scene.resolution,
                            scene.aspect_ratio,
                        )
                        for index, scene in enumerate(workspace.scenes)
                    ],
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save workspace: {exc}") from exc

    def load(self, episode_id: str) -> WorkspaceState | None:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            return None
        try:
            with sqlite3.connect(db_path) as connection:
                connection.row_factory = sqlite3.Row
                project = connection.execute("SELECT * FROM project WHERE singleton = 1").fetchone()
                if project is None:
                    return None
                scene_rows = connection.execute(
                    "SELECT * FROM scenes ORDER BY scene_order"
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not load workspace: {exc}") from exc

        scenes = tuple(
            WorkspaceScene(
                scene_id=str(row["scene_id"]),
                image_file=str(row["image_file"]),
                image_exists=bool(row["image_exists"]),
                motion_prompt=str(row["motion_prompt"]),
                target_duration_s=float(row["target_duration_s"]),
                recommended_flow_duration_s=int(row["recommended_flow_duration_s"]),
                selected_flow_duration_s=(
                    int(row["selected_flow_duration_s"])
                    if row["selected_flow_duration_s"] is not None
                    else None
                ),
                readiness=SceneReadiness(str(row["readiness"])),
                trim_target_s=float(row["trim_target_s"]),
                model=str(row["model"]),
                resolution=str(row["resolution"]),
                aspect_ratio=str(row["aspect_ratio"]),
            )
            for row in scene_rows
        )
        return WorkspaceState(
            schema_version=str(project["schema_version"]),
            episode_id=str(project["episode_id"]),
            project_name=str(project["project_name"]),
            source_package_path=str(project["source_package_path"]),
            created_at=datetime.fromisoformat(str(project["created_at"])),
            imported_at=datetime.fromisoformat(str(project["imported_at"])),
            model=str(project["model"]),
            resolution=str(project["resolution"]),
            aspect_ratio=str(project["aspect_ratio"]),
            scenes=scenes,
        )

    def list_recent(self, limit: int = 10) -> tuple[WorkspaceState, ...]:
        """Read valid project databases and return newest persisted state first."""

        if limit < 1 or not self._projects_root.is_dir():
            return ()

        workspaces: list[WorkspaceState] = []
        for db_path in self._projects_root.glob("*/project.sqlite3"):
            episode_id = db_path.parent.name
            try:
                workspace = self.load(episode_id)
            except StorageError:
                continue
            if workspace is not None:
                workspaces.append(workspace)

        workspaces.sort(key=lambda item: item.imported_at, reverse=True)
        return tuple(workspaces[:limit])

    def _db_path(self, episode_id: str) -> Path:
        return self._projects_root / episode_id / "project.sqlite3"

    def _create_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS project (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                schema_version TEXT NOT NULL,
                episode_id TEXT NOT NULL UNIQUE,
                project_name TEXT NOT NULL,
                source_package_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                model TEXT NOT NULL,
                resolution TEXT NOT NULL,
                aspect_ratio TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scenes (
                scene_order INTEGER NOT NULL,
                scene_id TEXT PRIMARY KEY,
                image_file TEXT NOT NULL,
                image_exists INTEGER NOT NULL,
                motion_prompt TEXT NOT NULL,
                target_duration_s REAL NOT NULL,
                recommended_flow_duration_s INTEGER NOT NULL,
                selected_flow_duration_s INTEGER,
                readiness TEXT NOT NULL,
                trim_target_s REAL NOT NULL,
                model TEXT NOT NULL,
                resolution TEXT NOT NULL,
                aspect_ratio TEXT NOT NULL
            )
            """
        )
