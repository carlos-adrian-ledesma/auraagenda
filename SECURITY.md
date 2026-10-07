# Security Policy

AuraAgenda is a local-first Windows desktop application. Security-sensitive changes are reviewed through tests and release checklists.

## Supported version

Security work in this repository targets AuraAgenda 2.0.3 and later release candidates.

## Reporting a vulnerability

Do not post active exploits, recovery keys, personal databases, logs, or private information in a public Issue. If GitHub Private Vulnerability Reporting / Security Advisories are enabled for the repository, use that private channel.

If no private reporting channel is configured, open a minimal Issue that contains no exploit details or sensitive data and ask the maintainer for a private contact method.

## Security boundaries

- The local PIN protects access through the AuraAgenda interface; it does not encrypt `auraagenda.db` at rest.
- Owner recovery keys are unique per installation. AuraAgenda contains no universal developer password or backdoor.
- Trusted-network/IP restrictions are supplemental controls, not authentication by themselves.
- Encrypted recovery kits use authenticated encryption and must be stored separately from the computer they protect.
