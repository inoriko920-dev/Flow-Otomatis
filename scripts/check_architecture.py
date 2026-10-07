"""Static architecture guard for Flow-Otomatis.

This checker is intentionally dependency-free so it can run before the full
application imports. It guards the STEP 07 package boundaries and portable path
rules. More rules can be added only when their canonical owner is clear.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SRC_PACKAGE = Path("src/flow_otomatis")
FORBIDDEN_DRIVE_LITERAL = re.compile(r"(?i)(?:^|[^A-Za-z])(?:C|D):[\\/]")


@dataclass(frozen=True, slots=True)
class Violation:
    path: Path
    line: int
    rule: str
    detail: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.detail}"


def _module_parts(path: Path, root: Path) -> tuple[str, ...]:
    relative = path.relative_to(root)
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return tuple(parts)


def _imports(tree: ast.AST) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.append((node.lineno, node.module))
    return result


def _matches(module: str, prefixes: tuple[str, ...]) -> bool:
    return any(module == prefix or module.startswith(prefix + ".") for prefix in prefixes)


def check_file(path: Path, root: Path) -> list[Violation]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    module = _module_parts(path, root)
    top = module[0] if module else ""
    violations: list[Violation] = []

    if FORBIDDEN_DRIVE_LITERAL.search(text):
        violations.append(Violation(path, 1, "PATH001", "hard-coded C:/D: drive path"))

    for line, imported in _imports(tree):
        if top == "domain" and _matches(
            imported,
            ("PySide6", "playwright", "sqlite3", "keyring", "flow_otomatis.infrastructure"),
        ):
            violations.append(Violation(path, line, "DEP001", f"domain imports {imported}"))

        if top == "application" and _matches(
            imported,
            ("PySide6", "playwright", "sqlite3", "keyring", "flow_otomatis.infrastructure"),
        ):
            violations.append(Violation(path, line, "DEP002", f"application imports {imported}"))

        if top == "presentation" and _matches(
            imported,
            (
                "playwright",
                "sqlite3",
                "keyring",
                "flow_otomatis.infrastructure",
                "flow_otomatis.workers",
            ),
        ):
            violations.append(Violation(path, line, "DEP003", f"presentation imports {imported}"))

        if imported == "playwright" or imported.startswith("playwright."):
            allowed = module[:2] == ("workers", "browser") or module[:3] == (
                "infrastructure",
                "browser",
                "flow_web",
            )
            if not allowed:
                violations.append(
                    Violation(path, line, "DEP004", "Playwright outside browser boundary")
                )

        if imported == "sqlite3" and module[:2] != ("infrastructure", "persistence"):
            violations.append(
                Violation(path, line, "DEP005", "sqlite3 outside persistence boundary")
            )

        if imported == "keyring" and module[:2] != ("infrastructure", "secrets"):
            violations.append(
                Violation(path, line, "DEP006", "keyring outside secret-store boundary")
            )

    return violations


def check_repository(repo_root: Path) -> list[Violation]:
    src_root = repo_root / SRC_PACKAGE
    if not src_root.exists():
        return [Violation(src_root, 1, "REPO001", "source package does not exist")]
    violations: list[Violation] = []
    for path in sorted(src_root.rglob("*.py")):
        violations.extend(check_file(path, src_root))
    return violations


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    repo_root = Path(args[0]).resolve() if args else Path.cwd().resolve()
    violations = check_repository(repo_root)
    for violation in violations:
        print(violation.render())
    if violations:
        print(f"Architecture check failed: {len(violations)} violation(s).")
        return 1
    print("Architecture check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
