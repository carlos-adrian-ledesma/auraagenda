# AuraAgenda v2.0.4 — Release Validation Checklist

**Project:** AuraAgenda — Personal Life Planner  
**Version:** 2.0.4  
**Release type:** Public Portfolio / Runnable Source  
**Target platform:** Windows 10/11  
**Supported Python:** 3.11 / 3.12  
**Status:** Published — additional manual validation recommended

## 1. Source and Repository Validation

- [x] Complete application source available in the public repository.
- [x] Documentation and application screenshots included.
- [x] Windows source launchers provided.
- [x] GitHub Actions CI workflow configured.
- [x] Dependabot configuration included.
- [x] Runtime dependency requirements documented.
- [x] Current version identified as 2.0.4.

## 2. Automated Quality and Security Checks

The GitHub Actions workflow executes:

- Python source compilation.
- Automated unit and regression tests.
- Ruff static analysis.
- Dependency vulnerability auditing with pip-audit.

Successful CI executions have been recorded for the published project.

Before approving future releases, verify that all required checks pass for the exact release commit.

## 3. Windows Functional Validation

The following checks require documented execution on Windows:

- [ ] Confirm clean installation using Python 3.11.
- [ ] Confirm clean installation using Python 3.12.
- [ ] Launch AuraAgenda using INICIAR_AURAAGENDA.bat.
- [ ] Verify dashboard and navigation.
- [ ] Verify calendar, tasks and financial modules.
- [ ] Verify Spanish and English translations.
- [ ] Test all available visual themes.
- [ ] Test Windows display scaling at 100%, 125% and 150%.
- [ ] Test resolutions 1366×768, 1600×900 and 1920×1080.
- [ ] Verify PIN locking and unlocking.
- [ ] Verify inactivity locking.
- [ ] Verify owner-controlled recovery.
- [ ] Test encrypted recovery kit creation and restoration.
- [ ] Verify backup and restore using disposable test data.
- [ ] Confirm normal application shutdown.

Unchecked items must not be represented as completed validations.

## 4. Security and Privacy Review

- [ ] Confirm no personal databases, credentials or recovery keys are included in release assets.
- [ ] Review runtime logs for accidental disclosure of sensitive information.
- [ ] Verify third-party license notices.
- [ ] Validate recovery and backup procedures on disposable test profiles.
- [ ] Confirm that the Windows launcher does not require unnecessary privileges.

The local application PIN does not provide full-database encryption.

Encrypted recovery kits protect the recovery package separately from the primary SQLite database.

## 5. Release Distribution

**Published release:** v2.0.4

https://github.com/carlos-adrian-ledesma/auraagenda/releases/tag/v2.0.4

The distributed package contains runnable Python source code and Windows launchers.

A compiled standalone executable is not included in this release.

Before future binary distribution:

- [ ] Build the executable in a controlled Windows environment.
- [ ] Verify bundled dependencies and licenses.
- [ ] Scan the final binary with security tools.
- [ ] Validate installation on a clean Windows machine.
- [ ] Generate SHA-256 checksums.
- [ ] Consider code signing for the public installer.

## 6. Release Decision

**Portfolio publication:** Completed.

**Automated CI validation:** Successful executions recorded.

**Runnable source distribution:** Published.

**Complete manual Windows acceptance:** Not yet documented in this checklist.

**Standalone commercial installer:** Not included.

## 7. Maintenance Policy

Preserve previous releases and their historical reports.

Update this checklist when new validation evidence becomes available.

Do not mark a test as passed without an actual execution result.

---

Copyright © 2026 Carlos Adrián Ledesma. All rights reserved.
