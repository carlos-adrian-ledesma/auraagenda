# AuraAgenda Owner Security & Recovery

## Why AuraAgenda does not use an IP address as a password

An IP address can change, can be shared by many devices behind a router, and can be reassigned by an ISP or DHCP server. AuraAgenda therefore treats IP/network information only as an optional second restriction. It is never the sole authentication factor.

AuraAgenda 2.0.3 remains local-first and does **not** call an external service to discover or track the user's public IP.

## Owner / master model

Each installation gets a unique **Installation ID** and can create a unique **Owner Master Recovery Key**. This key is the highest recovery credential for that installation.

There is deliberately **no universal developer master password**. A universal backdoor would weaken every copy of AuraAgenda if it leaked.

AuraAgenda stores only a salted verifier of the master key. The original key is shown to the owner and must be saved offline.

## Encrypted recovery kit

The owner can create a `.aurarecovery` file from Settings → Privacy. The kit contains a verified AuraAgenda backup encrypted with AES-256-GCM. The encryption key is derived from the owner recovery key with scrypt.

Recommended storage:

- one copy on an external USB drive, and/or
- one copy in a private cloud folder controlled by the owner, and
- the master key stored separately from the recovery kit.

If the computer or program is lost:

1. Reinstall/extract AuraAgenda.
2. Prepare its `.venv` using `INICIAR_AURAAGENDA.bat`.
3. Run `RECUPERAR_AURAAGENDA.bat`.
4. Select the `.aurarecovery` file.
5. Enter the owner master recovery key.
6. AuraAgenda validates and decrypts the kit, verifies the database, creates a safety backup of the current installation, and restores the data.
7. Start AuraAgenda normally.

## Forgotten PIN

If the local PIN is forgotten, canceling the PIN dialog does not unlock the app. The owner may choose master recovery, authenticate with the master key, and set a new PIN.

## Trusted local network

The optional network guard accepts an exact IPv4 address (`192.168.1.10/32`) or CIDR (`192.168.1.0/24`). If the current local IP is outside the configured network, AuraAgenda stays locked until the owner master key is supplied.

Because network addresses can change, this control should be used only when the owner understands the local network configuration. A master key is required before the network lock can be enabled.
