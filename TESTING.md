# AuraAgenda v2.0.4 — Testing and Quality Assurance

**Project:** AuraAgenda — Personal Life Planner  
**Version:** 2.0.4  
**Distribution:** Public Portfolio / Runnable Source  
**Target:** Windows 10/11 · Python 3.11 / 3.12

## 1. Testing Strategy

AuraAgenda uses automated checks and manual functional validation to evaluate application quality, stability, security and compatibility.

Automated checks provide regression coverage but do not replace real graphical testing on Windows.

## 2. Continuous Integration

GitHub Actions runs the quality workflow on Windows using Python 3.11 and Python 3.12.

The workflow performs:

- Python source compilation.
- Ruff static analysis.
- Dependency vulnerability auditing.
- Unit and regression tests.

Workflow:

https://github.com/carlos-adrian-ledesma/auraagenda/actions/workflows/ci.yml

Successful workflow executions have been recorded for the project.

## 3. Local Automated Validation

Install the development dependencies before executing the quality checks.

Run these commands from the repository root:

**Source compilation:**

`python -m compileall -q .`

**Automated tests:**

`python -m unittest discover -s tests -v`

**Static analysis:**

`python -m ruff check app tests --select F,E9`

**Dependency vulnerability audit:**

`python -m pip_audit -r requirements.txt`

The dependency audit requires access to current vulnerability information.

## 4. Functional Testing

Manual Windows verification should cover:

- First-run onboarding.
- Dashboard and navigation.
- Calendar, tasks and reminders.
- Financial management.
- Personal organization and wellness.
- Spanish and English translations.
- Theme selection.
- PIN locking and unlocking.
- Inactivity locking.
- Application reopening from the system tray.
- Owner-controlled recovery.
- Normal backup and restoration.
- Encrypted recovery kit creation and restoration.
- Application shutdown and restart.

Perform tests using disposable profiles and synthetic data.

## 5. Display Compatibility

Recommended verification resolutions:

- 1366 × 768.
- 1600 × 900.
- 1920 × 1080.

Recommended Windows scaling:

- 100%.
- 125%.
- 150%.

Check for clipped controls, overlapping elements, inaccessible buttons and broken scrolling.

## 6. Security Testing

The automated and manual validation strategy includes:

- PIN and owner recovery behavior.
- Failed authentication attempt handling.
- Backup validation.
- Recovery kit encryption and integrity.
- SQL table allowlists.
- Repository hygiene.
- Sensitive file exclusion.
- Trusted local network restriction.
- Application lock state consistency.

The main SQLite database is not fully encrypted at rest.

Recovery kit encryption must not be represented as full database encryption.

## 7. Backup and Recovery Safety

Never test restoration using the only available copy of valuable user data.

Before restoration testing:

1. Create a disposable application profile.
2. Generate synthetic data.
3. Produce a backup or encrypted recovery kit.
4. Validate its integrity.
5. Restore into an isolated test profile.
6. Confirm the recovered data and application behavior.

## 8. Release Validation

**Current public release:** v2.0.4

https://github.com/carlos-adrian-ledesma/auraagenda/releases/tag/v2.0.4

The current distribution provides runnable Python source code and Windows launchers.

It does not include a validated standalone Windows executable.

Automated CI results and manual acceptance results must be recorded separately.

For current release acceptance status, see `RELEASE_CHECKLIST.md`.

## 9. Known Validation Limits

Automated tests cannot independently certify:

- Complete Windows GUI behavior.
- Compatibility with every target computer.
- Absence of all security vulnerabilities.
- Correctness of every business workflow.
- Reliability of recovery on all environments.

These areas require additional targeted testing.

---

Copyright © 2026 Carlos Adrián Ledesma. All rights reserved.
