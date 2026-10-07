# GitHub Publishing Guide — AuraAgenda 2.0.3

## Repository package

Use `AuraAgenda_V2.0.3_GitHub_Final_Runnable.zip` for the public repository if the goal is for visitors to be able to inspect **and run** the application from source.

Suggested repository name: `auraagenda-desktop`.

Suggested topics: `python`, `pyside6`, `qt`, `sqlite`, `desktop-application`, `local-first`, `i18n`, `security`, `windows`, `portfolio`.

## Before first push

1. Review `COPYRIGHT.md` and `THIRD_PARTY_NOTICES.md`.
2. Run the release checklist on Windows.
3. Launch the real application with `INICIAR_AURAAGENDA.bat`.
4. Add real screenshots to `docs/screenshots/` only after checking that they contain no personal data.
5. Confirm `.gitignore` excludes databases, logs, backups, recovery kits, virtual environments and signing credentials.
6. Enable GitHub Private Vulnerability Reporting when appropriate.
7. Do not add an open-source `LICENSE` unless that is an intentional licensing decision.

## Release

Tag: `v2.0.3`

Title: `AuraAgenda v2.0.3 — Security & Recovery Release Candidate`

For a source-only GitHub release, attach only reviewed source artifacts. If a compiled Windows binary is later attached, validate Qt/PySide6 redistribution requirements, scan the exact binary artifact and generate fresh SHA-256 checksums.
