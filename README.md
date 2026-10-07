# AuraAgenda

**Personal Life Planner — Windows desktop / local-first**

AuraAgenda 2.0.3 is a complete, runnable Windows desktop application built with Python, PySide6 and SQLite. This repository contains the application source, launch scripts, assets, tests, security/recovery services, documentation and GitHub automation needed to install and run the program from source.

## Run AuraAgenda on Windows

### Recommended

1. Install Python 3.11 or 3.12.
2. Download or clone this repository.
3. Open the `AuraAgenda` folder.
4. Double-click `INICIAR_AURAAGENDA.bat`.

The launcher creates a local `.venv`, installs the runtime dependencies from `requirements.txt` and starts AuraAgenda.

After the first installation, `run_windows.bat` can be used for normal startup.

### Recovery launcher

`RECUPERAR_AURAAGENDA.bat` opens the recovery workflow for encrypted `.aurarecovery` kits.

## Main capabilities

- dashboard and quick actions;
- calendar with day/week/month/list workflows;
- tasks, alarms, habits and checklists;
- diary, writing, goals and important people;
- wellness, cycle, water, sleep, mood and self-care modules;
- beauty and personal style modules;
- finances, travel, library and multimedia projects;
- statistics, backups, trash/recovery and configuration;
- Spanish / English internationalization;
- multiple dark pink/violet themes;
- local PIN lock and owner-controlled recovery;
- encrypted recovery kits using AES-256-GCM with scrypt-derived keys;
- optional trusted local IPv4/CIDR guard as a supplemental control;
- hardened backup validation with SHA-256 manifests and SQLite integrity checks.

## Security model

AuraAgenda does **not** use an IP address as a password. The optional trusted-network guard is only an additional restriction.

Each installation can create its own owner recovery key. There is no universal developer password or hidden backdoor.

The normal SQLite database is **not claimed to be encrypted at rest**. The local PIN protects access through the AuraAgenda interface. Encrypted recovery kits are encrypted separately. Read `SECURITY_RECOVERY.md`, `SECURITY.md` and `PRIVACY.md` for the exact model and limitations.

## Data location

By default, user data is stored outside the repository under the Windows user profile, in the AuraAgenda data directory. Do not commit personal databases, logs, backups, recovery kits or credentials.

The repository `.gitignore` excludes the common runtime artifacts.

## Technologies

- Python 3.11 / 3.12 target
- PySide6 / Qt
- SQLite
- `cryptography`
- `zoneinfo` + `tzdata`
- standard-library `unittest`

## Development checks

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

For QA tooling:

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check app tests --select F,E9
```

GitHub Actions runs compile checks, Ruff safety checks and the unit/security suite on Windows with Python 3.11 and 3.12.

## Build

`build_exe.bat` is provided for the Windows build workflow. Building a standalone executable requires the build dependencies in `requirements-build.txt` and should be validated on Windows before distributing binaries.

## Repository structure

- `app/` — complete application source;
- `app/pages/` — application modules/pages;
- `app/services/` — backup, privacy, network guard, migration and recovery services;
- `app/i18n/` — ES/EN translation catalogue;
- `tests/` — unit, migration, security and design-system tests;
- `assets/` — AuraAgenda visual assets;
- `docs/` — project documentation and screenshot location;
- `.github/` — CI and Dependabot configuration;
- `INICIAR_AURAAGENDA.bat` — first-run/install-and-start launcher;
- `run_windows.bat` — normal source launcher;
- `RECUPERAR_AURAAGENDA.bat` — recovery launcher.

## Screenshots

Only screenshots captured from the real application should be committed. Do not upload screenshots containing personal information. See `docs/screenshots/README.md`.

## Medical and financial scope

Wellness, cycle, sleep, symptoms and medication features are personal organization tools. AuraAgenda does not diagnose, prescribe or replace professional medical care.

Financial features are for personal organization and are not banking, investment advice or certified accounting software.

## Copyright

Copyright © 2026 Carlos Adrián Ledesma. All rights reserved.

AuraAgenda source code is published for portfolio, technical evaluation and demonstration purposes. No open-source license is granted unless a separate license file expressly states otherwise.

Third-party software retains its own licenses and copyrights. See `COPYRIGHT.md` and `THIRD_PARTY_NOTICES.md`.
