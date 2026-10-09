"""SQLite persistence for one imported project workspace."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from flow_otomatis.application.ports.workspace_repository import (
    WorkspaceReadIssue,
    WorkspaceScanResult,
)
from flow_otomatis.domain.errors import (
    StorageError,
    WorkspaceAlreadyExistsError,
    WorkspaceCorruptError,
)
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene


class SqliteWorkspaceRepository:
    """Persist each episode in its own project.sqlite3 database."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def create(self, workspace: WorkspaceState) -> None:
        """Create a workspace atomically; never replace an existing episode."""

        db_path = self._db_path(workspace.episode_id)
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(db_path, timeout=10.0) as connection:
                connection.execute("BEGIN IMMEDIATE")
                self._create_schema(connection)
                existing = connection.execute(
                    "SELECT episode_id FROM project WHERE singleton = 1"
                ).fetchone()
                if existing is not None:
                    raise WorkspaceAlreadyExistsError(workspace.episode_id)
                connection.execute(
                    """
                    INSERT INTO project (
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
                connection.executemany(
                    """
                    INSERT INTO scenes (
                        scene_order, scene_id, image_file, image_exists,
                        motion_prompt, target_duration_s,
                        recommended_flow_duration_s, selected_flow_duration_s,
                        readiness, trim_target_s, model, resolution, aspect_ratio,
                        image_sha256_imported
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                            scene.image_sha256_imported,
                        )
                        for index, scene in enumerate(workspace.scenes)
                    ],
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not create workspace: {exc}") from exc

    def update(self, workspace: WorkspaceState) -> None:
        """Update an existing workspace without creating a missing project."""

        if self.load(workspace.episode_id) is None:
            raise StorageError(f"Workspace not found for update: {workspace.episode_id}")
        self.save(workspace)

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
                        readiness, trim_target_s, model, resolution, aspect_ratio,
                        image_sha256_imported
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                            scene.image_sha256_imported,
                        )
                        for index, scene in enumerate(workspace.scenes)
                    ],
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save workspace: {exc}") from exc

    def load(self, episode_id: str) -> WorkspaceState | None:
        """Read one project without mutating its SQLite source."""

        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            return None
        try:
            with self._connect_readonly(db_path) as connection:
                connection.row_factory = sqlite3.Row
                project = connection.execute("SELECT * FROM project WHERE singleton = 1").fetchone()
                if project is None:
                    return None
                scene_rows = connection.execute(
                    "SELECT * FROM scenes ORDER BY scene_order"
                ).fetchall()
                return self._decode_workspace(episode_id, project, scene_rows)
        except sqlite3.OperationalError as exc:
            raise StorageError(f"Could not load workspace: {episode_id}") from exc
        except sqlite3.DatabaseError as exc:
            raise WorkspaceCorruptError(episode_id) from exc
        except sqlite3.Error as exc:
            raise StorageError(f"Could not load workspace: {episode_id}") from exc
        except (ValueError, TypeError, IndexError, OverflowError) as exc:
            raise WorkspaceCorruptError(episode_id) from exc

    def list_recent(self, limit: int = 10) -> tuple[WorkspaceState, ...]:
        """Read healthy project databases and isolate failures."""

        return self.scan_recent(limit).workspaces

    def scan_recent(self, limit: int = 10) -> WorkspaceScanResult:
        """Return healthy projects plus corrupt/unavailable local entries."""

        if limit < 1 or not self._projects_root.is_dir():
            return WorkspaceScanResult(workspaces=(), issues=())

        workspaces: list[WorkspaceState] = []
        issues: list[WorkspaceReadIssue] = []
        for db_path in self._projects_root.glob("*/project.sqlite3"):
            episode_id = db_path.parent.name
            try:
                workspace = self.load(episode_id)
            except WorkspaceCorruptError:
                issues.append(WorkspaceReadIssue(episode_id=episode_id, kind="CORRUPT"))
                continue
            except StorageError:
                issues.append(WorkspaceReadIssue(episode_id=episode_id, kind="UNAVAILABLE"))
                continue
            if workspace is not None:
                workspaces.append(workspace)

        workspaces.sort(key=lambda item: item.imported_at, reverse=True)
        issues.sort(key=lambda item: item.episode_id)
        return WorkspaceScanResult(
            workspaces=tuple(workspaces[:limit]),
            issues=tuple(issues),
        )

    def _connect_readonly(self, db_path: Path) -> sqlite3.Connection:
        uri = f"{db_path.resolve().as_uri()}?mode=ro"
        return sqlite3.connect(uri, uri=True)

    def _decode_workspace(
        self,
        requested_episode_id: str,
        project: sqlite3.Row,
        scene_rows: list[sqlite3.Row],
    ) -> WorkspaceState:
        stored_episode_id = str(project["episode_id"])
        if stored_episode_id != requested_episode_id:
            raise ValueError("Stored episode identity does not match its project directory")

        scenes = tuple(self._decode_scene(row) for row in scene_rows)
        created_at = self._decode_aware_timestamp(project["created_at"])
        imported_at = self._decode_aware_timestamp(project["imported_at"])
        return WorkspaceState(
            schema_version=str(project["schema_version"]),
            episode_id=stored_episode_id,
            project_name=str(project["project_name"]),
            source_package_path=str(project["source_package_path"]),
            created_at=created_at,
            imported_at=imported_at,
            model=str(project["model"]),
            resolution=str(project["resolution"]),
            aspect_ratio=str(project["aspect_ratio"]),
            scenes=scenes,
        )

    @staticmethod
    def _decode_aware_timestamp(value: object) -> datetime:
        """Require timezone-aware stored timestamps without guessing or repairing."""

        if not isinstance(value, str) or not value.strip():
            raise ValueError("Workspace timestamp must be nonempty text")
        parsed = datetime.fromisoformat(value)
        if parsed.utcoffset() is None:
            raise ValueError("Workspace timestamp lacks timezone offset")
        return parsed

    def _decode_scene(self, row: sqlite3.Row) -> WorkspaceScene:
        image_exists = int(row["image_exists"])
        if image_exists not in {0, 1}:
            raise ValueError("image_exists must be stored as 0 or 1")
        return WorkspaceScene(
            scene_id=str(row["scene_id"]),
            image_file=str(row["image_file"]),
            image_exists=bool(image_exists),
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
            image_sha256_imported=(
                str(row["image_sha256_imported"])
                if "image_sha256_imported" in row.keys()
                and row["image_sha256_imported"] is not None
                else None
            ),
        )

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
                aspect_ratio TEXT NOT NULL,
                image_sha256_imported TEXT
            )
            """
        )
        columns = {
            str(row[1]) for row in connection.execute("PRAGMA table_info(scenes)").fetchall()
        }
        if "image_sha256_imported" not in columns:
            # Write-side migration only; read-only loads of legacy databases never
            # alter or rewrite user projects.
            connection.execute("ALTER TABLE scenes ADD COLUMN image_sha256_imported TEXT")
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
