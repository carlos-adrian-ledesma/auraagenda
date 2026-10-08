# Third-Party Notices

AuraAgenda 2.0.4 declares the following direct dependencies:

## Runtime

- PySide6 / Qt for Python — Qt Project / The Qt Company. Community packages are available under LGPLv3/GPLv3 terms, with commercial licensing also available from Qt. Binary distribution must be reviewed for the exact Qt modules shipped and the applicable license obligations.
- cryptography — Python cryptographic primitives used for AES-GCM and scrypt in encrypted recovery kits. Verify the package license for the exact pinned release used in a binary release.
- tzdata — IANA timezone data fallback used by Python `zoneinfo` on platforms that need it.

## Build / development

- PyInstaller — used only to build the Windows executable.
- Ruff — development linting/formatting tool.
- pip-audit — optional dependency vulnerability audit tool.

AuraAgenda itself is not relicensed as MIT/GPL/Apache by this notice. Before distributing a compiled installer, verify and bundle the required third-party license notices for the exact versions included in the artifact.
