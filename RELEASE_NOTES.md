# AuraAgenda v2.0.3 — Security & Recovery Release Candidate

AuraAgenda 2.0.3 focuses on security hardening, owner-controlled recovery and repository readiness while preserving the V2.0.2 premium UI/UX.

Highlights:

- owner master recovery key unique per installation;
- encrypted recovery kits for rapid restoration after reinstall/device loss;
- optional trusted local network/IP restriction with master-key override;
- tray-lock bypass correction;
- progressive PIN retry delay and six-character policy for new PINs;
- sensitive notification privacy;
- hardened backup validation and SQLite integrity verification;
- minimal runtime dependencies and `.venv`-based Windows launcher;
- GitHub CI, Dependabot and security/legal documentation.

The application remains local-first. It does not query a public-IP service, add cloud tracking, or contain a universal developer backdoor.
