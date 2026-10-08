# Changelog

## 2.0.4 — Final Portfolio & Security Release

### Security
- Updated `cryptography` to the current supported 50.x release range.
- Added dependency vulnerability auditing with `pip-audit` to the CI workflow.
- Confirmed that AuraAgenda does not expose a remote-control server or inbound network listener.
- Confirmed repository Deploy Keys: none.
- Confirmed repository Webhooks: none.
- Confirmed self-hosted GitHub Actions runners: none.
- Preserved owner-controlled recovery without a universal developer backdoor.
- Preserved AES-256-GCM encrypted recovery kits with scrypt-derived keys.
- Preserved hardened backup validation and SQLite integrity checking.

### Dependencies
- Updated PySide6 to the supported 6.11.x release range.
- Updated `cryptography` to the supported 50.x release range.
- Updated `tzdata`.
- Updated `pip-audit`.
- Updated GitHub Actions dependencies.

### Repository hardening
- Protected `main` branch.
- Pull Request workflow required for changes to `main`.
- Force pushes and branch deletion blocked.
- Python 3.11 and Python 3.12 CI checks required.
- Squash-only merge policy.
- Dependabot monitoring enabled.

### Project cleanup
- Removed temporary Ruff patch artifacts.
- Removed obsolete source checksum manifest.
- Removed obsolete legacy migration code and associated tests.
- Removed residual legacy product identity references.
- Strengthened automated branding regression checks.

### Portfolio
- Added real AuraAgenda screenshots captured from the application.
- Updated README for portfolio presentation.
- Updated Spanish and English user guides.
- Updated visual-system, roadmap and third-party documentation.
- Updated application, installer and About version identity to 2.0.4.


## 2.0.3 — Security & Recovery Release Candidate

### Security
- Centralized locked state; system tray/open-window actions must pass the security controller.
- Canceling PIN authentication no longer clears the locked state.
- New PIN policy: minimum six characters for newly configured PINs; legacy PIN verification remains compatible.
- Progressive delay after repeated failed PIN attempts.
- Sensitive tray notification privacy.
- Explicit allowlist for soft-delete/restore table identifiers.
- Rotating error log.

### Owner / master recovery
- Unique Installation ID.
- Unique Owner Master Recovery Key; only a salted verifier is stored locally.
- No universal developer password/backdoor.
- PIN reset using the owner master key.
- Encrypted `.aurarecovery` package using AES-256-GCM and scrypt.
- Standalone `RECUPERAR_AURAAGENDA.bat` recovery workflow.
- Optional trusted local IPv4/CIDR guard with master-key recovery.

### Backup hardening
- Consistent SQLite snapshot via SQLite backup API.
- SHA-256 manifest.
- File count, individual-size and total-size safety limits.
- Compression-ratio guard.
- Absolute/path-traversal and symlink rejection.
- `PRAGMA integrity_check` before restore.
- Logs excluded from normal backups.

### Engineering / GitHub
- Runtime/build/dev requirements separated.
- `.venv`-based Windows source launcher.
- Per-user installer configuration prepared.
- GitHub Actions and Dependabot configuration.
- Security, copyright, third-party, signing and release documentation.

## 2.0.2 — Premium UI/UX Redesign
- Centralized visual design system and eight themes.
- Settings redesigned around vertical navigation and cards.
- Sidebar grouping/collapsing and dark-surface consistency.
- Responsive sizing improvements and UI regression tests.
