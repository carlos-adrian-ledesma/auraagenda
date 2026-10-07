# AuraAgenda Architecture — 2.0.3

AuraAgenda is a local-first Windows desktop application built with PySide6 and SQLite.

## Layers

- `app/main.py` — application bootstrap, logging, onboarding, lock initialization.
- `app/main_window.py` — desktop shell, navigation, tray, alarms and notification routing.
- `app/pages/` — feature pages and settings UI.
- `app/widgets/` — reusable UI components.
- `app/services/` — backup, recovery, privacy, auto-lock, migration, network and formatting services.
- `app/i18n/` — centralized ES/EN strings.
- `app/database.py` — SQLite schema, incremental compatibility and DB helpers.

## Security architecture

`AutoLockController` is the visibility gate for protected UI. `MainWindow.show_normal()` delegates to it so tray actions do not bypass a locked session.

`RecoveryService` owns per-installation master-recovery operations. It does not contain a universal master password.

`NetworkGuard` handles optional local IPv4/CIDR checks without querying a public-IP service.

`BackupService` creates verified snapshots and validates archive structure, size, hashes and SQLite integrity before restore.

## Recovery trust model

The owner/master recovery key is the highest recovery credential for one installation. It should be retained offline by the legitimate owner or organization responsible for that installation. IP/network configuration is only a supplemental restriction.

## Data model

The main database is SQLite. Schema version for 2.0.3 is 4. New security settings are stored as key/value preferences; no plaintext PIN or master key is stored.
