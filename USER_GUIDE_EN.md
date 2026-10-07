# User Guide — AuraAgenda 2.0.3

On first launch, the setup wizard lets you choose language, name, country, timezone, currency, date format, optional modules, water goal, theme and an optional local PIN. Health information is never mandatory.

The sidebar groups Organization, Personal, Wellness, Style, Life and System. Optional modules can be hidden from Settings. Global search covers events, tasks, diary, people, goals, lists, library, multimedia, products and wardrobe items.

The Dashboard summarizes events, tasks, water, balance, habits, sleep, mood and birthdays. Quick actions create records in key modules.

Trash can restore deleted records or permanently remove them after confirmation. Backup creates local ZIP archives; Restore validates the ZIP and creates a safety backup first.

Cycle, health, sleep and wellness modules are for personal organization only. They do not diagnose or replace medical advice.

## Owner security and recovery — V2.0.3

Under **Settings → Privacy**, you can generate a master recovery key unique to that installation. Store it away from the PC. There is no universal developer password.

For fast recovery after program/device loss:

1. Generate the master key.
2. Create an encrypted `.aurarecovery` recovery kit.
3. Store the kit and key separately.
4. On a fresh installation, run `RECUPERAR_AURAAGENDA.bat`.
5. Select the kit and enter the master key.

The IP/network restriction is optional. AuraAgenda only uses local IPv4/CIDR values and does not query your public IP. An IP address does not replace the PIN or master recovery key.
