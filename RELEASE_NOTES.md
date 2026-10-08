# AuraAgenda v2.0.4 — Final Portfolio & Security Release

AuraAgenda 2.0.4 is the final portfolio-focused release of the current AuraAgenda desktop architecture.

This release consolidates application security, owner-controlled recovery, dependency modernization, repository protection, real application screenshots and GitHub presentation.

## Highlights

- Complete Windows desktop application built with Python, PySide6 and SQLite.
- Local-first architecture with no mandatory cloud account.
- Spanish / English interface structure.
- Owner-controlled master recovery.
- AES-256-GCM encrypted `.aurarecovery` kits.
- Hardened local backup and restore validation.
- Optional trusted local IPv4/CIDR guard.
- Real application screenshots included in the repository.
- Protected GitHub `main` branch and mandatory CI validation.
- Dependency monitoring with Dependabot and `pip-audit`.

## Security

AuraAgenda does not contain a universal developer password or hidden recovery backdoor.

The application does not expose an inbound remote-control server or network listener.

The trusted-network feature uses local network information only as a supplemental restriction and does not treat an IP address as an authentication credential.

Repository security was also reviewed before this release:

- no repository Deploy Keys;
- no repository Webhooks;
- no self-hosted GitHub Actions runners;
- protected `main`;
- blocked force pushes;
- blocked deletion of `main`;
- required Python 3.11 and Python 3.12 status checks.

## Dependency modernization

Runtime dependencies were updated to the current supported release ranges used by AuraAgenda:

- PySide6 6.11.x
- cryptography 50.x
- tzdata 2026.x

Development security tooling includes Ruff and pip-audit.

## Recovery model

Each installation can generate its own master recovery key.

Only a salted verifier is stored locally.

Encrypted recovery kits use AES-256-GCM with a key derived through scrypt.

The recovery workflow is intentionally owner-controlled and does not rely on a hidden developer credential.

## Repository and portfolio

Version 2.0.4 removes temporary patch artifacts and obsolete legacy migration components.

The repository now includes screenshots captured directly from the real AuraAgenda application using synthetic demo data.

Documentation, application identity, installer metadata and portfolio presentation were updated for the 2.0.4 release.

## Important limitations

The primary SQLite database is not claimed to be encrypted at rest.

The application PIN controls access through the AuraAgenda interface and should not be considered equivalent to full-disk encryption.

Compiled Windows binaries should be separately validated and reviewed for applicable third-party licensing obligations before commercial distribution.

## Validation

Final validation includes:

- Python compilation check;
- full unit/security test suite;
- Ruff safety lint;
- dependency vulnerability audit;
- Windows GitHub Actions on Python 3.11 and 3.12.

The final public release should only be published after all required CI checks pass.
