from __future__ import annotations

import base64
import json
import os
import shutil
import struct
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from .backup import BackupService
from .privacy import generate_master_key, make_master_hash, normalize_master_key, verify_master_key

MAGIC = b"AURA-RECOVERY-V1\n"
MAX_HEADER = 64 * 1024
MAX_PACKAGE = 2 * 1024 * 1024 * 1024 + 128 * 1024 * 1024


class RecoveryError(ValueError):
    pass


class RecoveryService:
    """Owner-controlled recovery without a universal developer backdoor.

    A master recovery key is unique to each AuraAgenda installation. Only its
    salted verifier is stored in SQLite. Recovery packages are encrypted with
    AES-256-GCM using a key derived from that master key with scrypt.
    """

    def __init__(self, db):
        self.db = db
        self.backups = BackupService(db)

    def ensure_installation_id(self) -> str:
        current = self.db.setting("installation_id", "").strip()
        if current:
            return current
        current = str(uuid.uuid4())
        self.db.set_setting("installation_id", current)
        self.db.audit("CREATE_INSTALLATION_ID", "security")
        return current

    def has_master_key(self) -> bool:
        return bool(self.db.setting("master_key_hash", "") and self.db.setting("master_key_salt", ""))

    def create_master_key(self) -> str:
        key = generate_master_key()
        digest, salt = make_master_hash(key)
        self.db.set_settings(
            {
                "master_key_hash": digest,
                "master_key_salt": salt,
                "master_key_created_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        self.ensure_installation_id()
        self.db.audit("CREATE_MASTER_RECOVERY_KEY", "security")
        return key

    def verify_master_key(self, key: str) -> bool:
        return verify_master_key(
            key,
            self.db.setting("master_key_hash", ""),
            self.db.setting("master_key_salt", ""),
        )

    @staticmethod
    def _crypto():
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
        except ImportError as exc:
            raise RecoveryError(
                "The 'cryptography' package is required for encrypted recovery kits"
            ) from exc
        return AESGCM, Scrypt

    @classmethod
    def _derive_key(cls, master_key: str, salt: bytes) -> bytes:
        _, Scrypt = cls._crypto()
        normalized = normalize_master_key(master_key)
        if len(normalized) < 32:
            raise RecoveryError("Master recovery key is invalid")
        kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
        return kdf.derive(normalized.encode("utf-8"))

    def create_recovery_kit(self, target: Path, master_key: str) -> Path:
        if not self.verify_master_key(master_key):
            raise RecoveryError("Master recovery key is incorrect")
        target = Path(target)
        if target.suffix.lower() != ".aurarecovery":
            target = target.with_suffix(".aurarecovery")
        target.parent.mkdir(parents=True, exist_ok=True)

        snapshot = self.backups.create("RecoverySnapshot")
        payload = snapshot.read_bytes()
        if len(payload) > MAX_PACKAGE:
            raise RecoveryError("Recovery package is too large")

        AESGCM, _ = self._crypto()
        salt = os.urandom(16)
        nonce = os.urandom(12)
        header = {
            "application": "AuraAgenda",
            "format": 1,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "installation_id": self.ensure_installation_id(),
            "cipher": "AES-256-GCM",
            "kdf": "scrypt",
            "salt": base64.b64encode(salt).decode("ascii"),
            "nonce": base64.b64encode(nonce).decode("ascii"),
        }
        header_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
        key = self._derive_key(master_key, salt)
        ciphertext = AESGCM(key).encrypt(nonce, payload, header_bytes)

        with target.open("wb") as handle:
            handle.write(MAGIC)
            handle.write(struct.pack(">I", len(header_bytes)))
            handle.write(header_bytes)
            handle.write(ciphertext)

        self.db.audit("CREATE_RECOVERY_KIT", "security", None, str(target))
        return target

    @classmethod
    def _read_package(cls, path: Path) -> tuple[dict, bytes, bytes]:
        path = Path(path)
        if not path.is_file():
            raise RecoveryError("Recovery kit was not found")
        if path.stat().st_size > MAX_PACKAGE:
            raise RecoveryError("Recovery kit exceeds the safety limit")
        with path.open("rb") as handle:
            if handle.read(len(MAGIC)) != MAGIC:
                raise RecoveryError("This is not an AuraAgenda recovery kit")
            length_data = handle.read(4)
            if len(length_data) != 4:
                raise RecoveryError("Recovery kit header is incomplete")
            header_length = struct.unpack(">I", length_data)[0]
            if header_length <= 0 or header_length > MAX_HEADER:
                raise RecoveryError("Recovery kit header is invalid")
            header_bytes = handle.read(header_length)
            ciphertext = handle.read()
        try:
            header = json.loads(header_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RecoveryError("Recovery kit header is invalid") from exc
        if header.get("application") != "AuraAgenda" or int(header.get("format", 0)) != 1:
            raise RecoveryError("Unsupported recovery kit")
        if header.get("cipher") != "AES-256-GCM" or header.get("kdf") != "scrypt":
            raise RecoveryError("Unsupported recovery encryption")
        return header, header_bytes, ciphertext

    def decrypt_to_backup(self, path: Path, master_key: str, destination: Path) -> dict:
        header, header_bytes, ciphertext = self._read_package(path)
        try:
            salt = base64.b64decode(header["salt"], validate=True)
            nonce = base64.b64decode(header["nonce"], validate=True)
        except Exception as exc:
            raise RecoveryError("Recovery kit cryptographic metadata is invalid") from exc
        if len(salt) != 16 or len(nonce) != 12:
            raise RecoveryError("Recovery kit cryptographic metadata is invalid")
        AESGCM, _ = self._crypto()
        key = self._derive_key(master_key, salt)
        try:
            plaintext = AESGCM(key).decrypt(nonce, ciphertext, header_bytes)
        except Exception as exc:
            raise RecoveryError("Recovery key is incorrect or the kit was modified") from exc
        Path(destination).write_bytes(plaintext)
        return header

    def restore_recovery_kit(self, path: Path, master_key: str):
        # The recovery kit authenticates the supplied key through AES-GCM. This
        # deliberately allows restoring an older kit after a reinstall or after
        # the local installation's master key was rotated.
        with tempfile.TemporaryDirectory(prefix="aura_recovery_") as temp_dir:
            backup_path = Path(temp_dir) / "recovery_payload.zip"
            header = self.decrypt_to_backup(path, master_key, backup_path)
            self.backups.validate_detailed(backup_path)
            safety = self.backups.restore(backup_path)
        self.db.audit("RESTORE_RECOVERY_KIT", "security", None, str(path))
        return header, safety

    def reset_pin_with_master_key(self, master_key: str, new_pin: str) -> bool:
        if not self.verify_master_key(master_key):
            return False
        from .privacy import make_pin_hash, validate_new_pin

        valid, message = validate_new_pin(new_pin)
        if not valid:
            raise RecoveryError(message)
        digest, salt = make_pin_hash(new_pin)
        self.db.set_settings({"pin_hash": digest, "pin_salt": salt})
        self.db.audit("RESET_PIN_WITH_MASTER_KEY", "security")
        return True
