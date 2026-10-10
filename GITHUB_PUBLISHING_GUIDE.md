# AuraAgenda v2.0.4 — GitHub Publishing Guide

**Project:** AuraAgenda — Personal Life Planner  
**Version:** 2.0.4  
**Repository:** `carlos-adrian-ledesma/auraagenda`  
**Distribution:** Public Portfolio / Runnable Source  
**Target platform:** Windows 10/11  
**Status:** Published

## 1. Repository Overview

AuraAgenda is a desktop personal management application developed with Python, PySide6 and SQLite.

The public repository includes the application source code, Windows launchers, automated tests, technical documentation and screenshots generated with synthetic data.

The application uses a local-first architecture and does not require a permanent cloud account.

Official repository:

https://github.com/carlos-adrian-ledesma/auraagenda

## 2. Current Public Release

**Version:** v2.0.4

**Release title:** AuraAgenda v2.0.4 — Final Portfolio & Security Release

Official release:

https://github.com/carlos-adrian-ledesma/auraagenda/releases/tag/v2.0.4

### Published assets

- `AuraAgenda_V2.0.4_GitHub_Final_Runnable.zip`
- `AuraAgenda_V2.0.4_GitHub_Final_Runnable_SHA256.txt`

The published ZIP contains runnable application source code.

It is not a standalone compiled Windows executable or installer.

## 3. Running the Application

### Requirements

- Windows 10/11.
- Python 3.11 or Python 3.12.
- Internet access for initial dependency installation.

### Installation

1. Download or clone the repository.
2. Extract the downloaded ZIP if applicable.
3. Open the project directory.
4. Run `INICIAR_AURAAGENDA.bat`.
5. Allow the launcher to create its local virtual environment and install dependencies.
6. Start the application.

For subsequent launches, use `run_windows.bat`.

Additional instructions are available in `COMO_INICIAR.md`.

## 4. Repository Structure

The public repository includes:

- `app/` — application modules and user interface.
- `tests/` — automated tests.
- `assets/` — application icons and visual resources.
- `docs/screenshots/` — screenshots with synthetic data.
- `.github/workflows/` — continuous integration configuration.
- `.github/dependabot.yml` — dependency update monitoring.
- `requirements.txt` — runtime dependencies.
- `requirements-dev.txt` — development and testing dependencies.
- `README.md` — project presentation.
- `ARCHITECTURE.md` — architecture documentation.
- `SECURITY.md` — security model and limitations.
- `PRIVACY.md` — privacy documentation.
- `TESTING.md` — testing strategy.
- `RELEASE_CHECKLIST.md` — release validation status.

## 5. Continuous Integration

AuraAgenda uses GitHub Actions to evaluate changes automatically.

The CI workflow includes:

- Python source compilation.
- Automated unit and regression tests.
- Ruff static analysis.
- Dependency security auditing.

The workflow runs on Windows with Python 3.11 and Python 3.12.

GitHub Actions:

https://github.com/carlos-adrian-ledesma/auraagenda/actions

Successful CI runs have been recorded.

Future releases should be published only after their required validation checks pass.

## 6. Branch Protection and Pull Requests

The primary branch is `main`.

Direct modifications are restricted by branch protection.

Recommended contribution workflow:

1. Create a dedicated branch.
2. Commit the intended change.
3. Open a Pull Request targeting `main`.
4. Review the modified files.
5. Wait for the required CI checks.
6. Merge after successful validation.
7. Delete the temporary branch when it is no longer needed.

Documentation-only changes should not be presented as functional software upgrades.

## 7. Security and Privacy

The repository must not include:

- Personal databases.
- Real user information.
- Passwords or access tokens.
- Private cryptographic keys.
- Recovery credentials.
- Sensitive logs.
- Runtime backups.
- Development virtual environments.
- Signing certificates.

AuraAgenda includes local privacy and recovery controls.

The main SQLite database is not claimed to be fully encrypted at rest.

Encrypted recovery kits provide a separate protection mechanism for recovery packages.

Security claims must correspond to implemented and tested behavior.

## 8. Release Verification

Before preparing any future release:

1. Verify the application version.
2. Review source changes.
3. Confirm automated test results.
4. Perform the required manual Windows tests.
5. Review dependencies and licenses.
6. Check release files for secrets and unnecessary artifacts.
7. Generate the SHA-256 checksum for the final distribution.
8. Review the README and release documentation.
9. Publish the new version with accurate release notes.

Historical releases and their documentation should be preserved for traceability.

## 9. Windows Executable Distribution

The current release provides runnable source code.

For a future compiled executable or installer:

- Validate the actual Windows build.
- Verify all bundled dependencies.
- Check applicable third-party redistribution licenses.
- Scan the final executable.
- Test installation and removal on a clean system.
- Consider Authenticode code signing.
- Publish a verified SHA-256 checksum.
- Document the minimum system requirements.

A Windows source launcher should not be described as a standalone executable.

## 10. Portfolio and Recruitment

The repository is designed to demonstrate:

- Python desktop application development.
- PySide6 graphical interface implementation.
- SQLite persistence.
- Modular architecture.
- Local-first application design.
- Authentication and recovery workflows.
- Security-conscious development.
- Automated regression testing.
- GitHub Actions and dependency management.
- Professional technical documentation.

Recruiters and technical reviewers can inspect the application source, automated tests, architecture documents and release history.

## 11. Maintenance

Keep release documentation synchronized with the current published version.

Older technical reports may be retained as historical evidence when clearly identified.

Do not overwrite previous release records merely to make them appear current.

---

**Copyright © 2026 Carlos Adrián Ledesma. All rights reserved.**

Third-party components remain subject to their respective licenses.
