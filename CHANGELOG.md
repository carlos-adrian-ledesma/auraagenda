# Changelog

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
