# AuraAgenda Privacy

AuraAgenda is designed as a **local-first** Windows desktop application.

## Data handling

Core AuraAgenda functions do not require an account and do not intentionally transmit the user's:

- diary;
- health/wellness records;
- cycle records;
- finances;
- tasks/calendar;
- personal contacts;
- attached files;
- recovery information;

to an AuraAgenda server.

AuraAgenda 2.0.3 does not include advertising, analytics tracking or telemetry.

## Local storage

Application data is normally stored under:

`Documents\AuraAgenda\`

This may include SQLite data, attachments, exports, local backups and logs.

## PIN limitation

The optional local PIN protects access through the AuraAgenda user interface. It **does not encrypt** `auraagenda.db` or all files stored on the disk. Anyone with sufficient access to the Windows account/storage may be able to access unencrypted local files outside AuraAgenda.

## Owner master recovery key

The owner may generate a unique master recovery key. AuraAgenda stores only a salted verifier of that key. There is no universal developer key.

The owner should store the master key separately from the computer and separately from encrypted recovery kits.

## Encrypted recovery kits

`.aurarecovery` packages are encrypted with authenticated encryption and are intended for off-device recovery. The user chooses where to save them. AuraAgenda does not automatically upload them to a cloud provider.

## IP/network information

AuraAgenda may display the computer's local IPv4 address for the optional trusted-network feature. It does not contact an external service to discover or track the public IP. IP/network information is not treated as a standalone password.

## Notifications

Sensitive system notifications can be hidden. While AuraAgenda is locked, the application uses generic reminder text rather than revealing protected content through its own tray notifications.

## Backups and exports

Manual backups and exports remain under the user's control. A copy placed on USB, email, cloud storage or another service is subject to that destination's security and privacy practices.

## Deleting data

Local data can be removed by the user from the application where supported, from the application's Trash, or by removing the local AuraAgenda data directory after creating any desired backup. Exercise care: deleting the data directory can permanently remove local information.

## No claim of absolute security

AuraAgenda reduces common application-level risks but does not claim absolute security. Windows account security, disk encryption, malware protection and physical control of the device remain important.
