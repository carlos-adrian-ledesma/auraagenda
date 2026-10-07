# Historical migration from V1

This document is the only user-facing historical compatibility note for the previous product identity.

AuraAgenda checks for the legacy folder `Documents\DanicaDavis` and database `BaseDatos\danica_davis.db` only to offer a one-time, user-controlled import. The old folder is never deleted.

Before importing, AuraAgenda copies the legacy database into the new local backup directory. Data is imported table-by-table into the current schema rather than overwriting the new database. Compatible legacy settings are retained; the old personal display name is deliberately not copied as the new product identity.

If the user declines, the original data remains untouched and import can later be started manually from Settings.
