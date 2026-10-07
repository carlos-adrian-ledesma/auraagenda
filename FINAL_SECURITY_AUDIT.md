# Final Security Audit — AuraAgenda 2.0.3

## Implemented in this release

- Fixed the tray/window visibility path so a locked application must pass through the central security controller.
- Cancellation of the PIN dialog no longer clears the locked state.
- New PINs require at least six characters; legacy PINs remain verifiable for compatibility.
- Repeated failed unlock attempts receive progressive in-app delays.
- Added per-installation Installation ID.
- Added unique owner master recovery key with salted PBKDF2-HMAC-SHA256 verifier.
- Added master-key PIN reset without a universal developer password.
- Added encrypted `.aurarecovery` kits using AES-256-GCM + scrypt.
- Added optional trusted local IPv4/CIDR guard. IP is supplemental, not primary authentication.
- Added privacy mode for sensitive system-tray notifications.
- Backup creation now uses a consistent SQLite snapshot, SHA-256 manifest, file/size limits, compression-ratio guard, path traversal checks, symlink rejection, and SQLite `PRAGMA integrity_check` before restore.
- Restore table names now use an explicit application allowlist.
- Logs use rotation and are excluded from normal backups.
- Runtime dependencies reduced and separated from build/development dependencies.
- Windows source launch now uses a project-local `.venv`.
- Added GitHub CI, Dependabot, security policy, copyright notice and third-party notices.

## Important security boundary

The normal SQLite database and ordinary local files are **not encrypted at rest**. The local PIN protects access through AuraAgenda's user interface. The encrypted recovery kit is encrypted separately.

Full database encryption is intentionally not improvised in this release; it would require a separate migration/key-management design and Windows validation.

## IP/network boundary

AuraAgenda does not query, track or depend on public IP addresses. Local network restriction is optional because IP addresses are not stable identities.

## Environment limitation

The build environment used to prepare this source did not include PySide6, so a real visual Windows/Qt smoke test was not executed here. Source compilation and unit/security tests were executed. The Windows release checklist must be completed on the target environment before public binary distribution.
