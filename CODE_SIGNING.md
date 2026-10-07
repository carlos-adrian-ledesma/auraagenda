# Windows Code Signing

AuraAgenda can be built unsigned for local development. Public Windows distribution should preferably use Authenticode signing from a certificate controlled by the publisher.

Never commit `.pfx`, `.p12`, private-key files, certificate passwords, CI signing secrets, or hardware-token credentials to GitHub.

Recommended release flow:

1. Build `AuraAgenda.exe` in a clean environment.
2. Calculate and archive SHA-256 before/after signing as appropriate for the release process.
3. Sign the executable using the publisher's protected signing credential.
4. Build `AuraAgenda_Setup_2.0.3.exe`.
5. Sign the installer.
6. Verify signatures on a clean Windows machine.
7. Generate `SHA256SUMS.txt` for the files actually published.

This repository does not contain a signing certificate or private key.
