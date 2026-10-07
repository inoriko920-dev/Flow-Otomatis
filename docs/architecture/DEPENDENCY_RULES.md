# DEPENDENCY RULES

- presentation may depend on application/domain read types/contracts; MUST NOT import infrastructure/workers/Playwright/sqlite3/keyring/provider SDK.
- application may depend on domain/contracts/application-owned ports/events; MUST NOT import PySide6 widgets or concrete infrastructure.
- domain may depend on stdlib/domain internals only; MUST NOT import PySide6/Playwright/sqlite3/filesystem/network/keyring.
- contracts may depend on Pydantic + stdlib; MUST NOT import PySide6 or concrete provider/infrastructure.
- infrastructure implements application ports and may use vendor/stdlib libraries; MUST NOT depend on presentation.
- workers/browser may depend on contracts + browser adapter internals; MUST NOT own presentation or project repositories.
- bootstrap may wire all concrete packages but must not contain business/use-case logic.
