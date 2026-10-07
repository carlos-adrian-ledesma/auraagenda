from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from dataclasses import dataclass

PIN_ITERATIONS = 350_000
MASTER_ITERATIONS = 450_000
MIN_NEW_PIN_LENGTH = 6


def _pbkdf2_hash(secret: str, salt_hex: str | None, iterations: int) -> tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, iterations)
    return digest.hex(), salt.hex()


def make_pin_hash(pin: str, salt_hex: str | None = None) -> tuple[str, str]:
    """Hash a PIN. Existing shorter legacy PINs remain verifiable; new UI saves >=6."""
    return _pbkdf2_hash(pin, salt_hex, PIN_ITERATIONS)


def verify_pin(pin: str, hash_hex: str, salt_hex: str) -> bool:
    if not hash_hex or not salt_hex:
        return False
    check, _ = make_pin_hash(pin, salt_hex)
    return hmac.compare_digest(check, hash_hex)


def make_master_hash(secret: str, salt_hex: str | None = None) -> tuple[str, str]:
    return _pbkdf2_hash(normalize_master_key(secret), salt_hex, MASTER_ITERATIONS)


def verify_master_key(secret: str, hash_hex: str, salt_hex: str) -> bool:
    if not hash_hex or not salt_hex:
        return False
    check, _ = make_master_hash(secret, salt_hex)
    return hmac.compare_digest(check, hash_hex)


def generate_master_key() -> str:
    # 256 bits of entropy represented in grouped hexadecimal for easy offline storage.
    raw = secrets.token_hex(32).upper()
    return "-".join(raw[index:index + 8] for index in range(0, len(raw), 8))


def normalize_master_key(value: str) -> str:
    return "".join(ch for ch in (value or "").upper() if ch.isalnum())


def validate_new_pin(pin: str) -> tuple[bool, str]:
    if len(pin) < MIN_NEW_PIN_LENGTH:
        return False, f"PIN must contain at least {MIN_NEW_PIN_LENGTH} characters"
    if len(pin) > 128:
        return False, "PIN is too long"
    return True, ""


@dataclass
class AttemptLimiter:
    """Small in-memory brute-force delay used by the unlock dialog.

    It is intentionally not presented as cryptographic protection of the SQLite
    file; it only slows repeated guesses through the application UI.
    """

    failures: int = 0
    blocked_until: float = 0.0

    def remaining_seconds(self, now: float | None = None) -> int:
        now = time.monotonic() if now is None else now
        return max(0, int(self.blocked_until - now + 0.999))

    def can_attempt(self, now: float | None = None) -> bool:
        return self.remaining_seconds(now) == 0

    def register_failure(self, now: float | None = None) -> int:
        now = time.monotonic() if now is None else now
        self.failures += 1
        # First two attempts are immediate; then 2, 4, 8 ... up to 60 seconds.
        if self.failures >= 3:
            delay = min(60, 2 ** min(self.failures - 2, 6))
            self.blocked_until = now + delay
            return delay
        return 0

    def register_success(self) -> None:
        self.failures = 0
        self.blocked_until = 0.0
