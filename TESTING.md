# Testing AuraAgenda 2.0.3

## Automated source/data tests

Run:

```text
python -m compileall -q .
python -m unittest discover -s tests -v
```

Security tests include PIN/master hashing, retry delay, backup hardening, recovery-kit encryption round-trip, network parsing, SQL table allowlist, repository secret/data hygiene and tray-lock source guards.

## Development quality checks

Install `requirements-dev.txt`, then run:

```text
ruff check .
ruff format --check .
pip-audit
```

`pip-audit` requires current package/index information and should be run shortly before release.

## Windows/Qt manual smoke test

The release is not approved solely by unit tests. On Windows, verify:

- first-run onboarding;
- every navigation page;
- ES → EN → ES;
- all themes;
- PIN lock and inactivity lock;
- tray double-click while locked;
- cancel PIN and verify application remains locked;
- master-key PIN reset;
- trusted-network restriction using a disposable profile;
- create/restore normal backup;
- create/restore encrypted recovery kit on a clean profile;
- 1366×768, 1600×900, 1920×1080;
- Windows scaling 100%, 125%, 150%.

Never test recovery against the only copy of valuable user data.
