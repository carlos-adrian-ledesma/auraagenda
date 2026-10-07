from __future__ import annotations

import hashlib
import hmac
import json
import os
import shutil
import sqlite3
import stat
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath

from ..paths import APP_NAME, BACKUP_DIR, DATA_ROOT, DB_PATH, VERSION

MAX_FILES = 20_000
MAX_TOTAL_UNCOMPRESSED = 2 * 1024 * 1024 * 1024  # 2 GiB
MAX_SINGLE_FILE = 512 * 1024 * 1024  # 512 MiB
MAX_COMPRESSION_RATIO = 200
DATABASE_ARCHIVE_PATH = "Database/auraagenda.db"


class BackupValidationError(ValueError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_stream(stream) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


class BackupService:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def _excluded(path: Path) -> bool:
        try:
            rel = path.relative_to(DATA_ROOT)
        except ValueError:
            return True
        if not rel.parts:
            return True
        return rel.parts[0] in {"Backups", "Logs"}

    def _database_snapshot(self, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        source = sqlite3.connect(DB_PATH)
        destination = sqlite3.connect(target)
        try:
            source.backup(destination)
            result = destination.execute("PRAGMA integrity_check").fetchone()
            if not result or str(result[0]).lower() != "ok":
                raise BackupValidationError("SQLite integrity check failed while creating backup")
        finally:
            destination.close()
            source.close()

    def create(self, kind: str = "Manual") -> Path:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        target = BACKUP_DIR / f"AuraAgenda_{kind}_{stamp}.zip"

        with tempfile.TemporaryDirectory(prefix="aura_backup_") as temp_dir:
            snapshot = Path(temp_dir) / "auraagenda.db"
            self._database_snapshot(snapshot)

            archive_sources: list[tuple[Path, str]] = [(snapshot, DATABASE_ARCHIVE_PATH)]
            for item in DATA_ROOT.rglob("*"):
                if item.is_dir() or self._excluded(item):
                    continue
                if item in {DB_PATH, DB_PATH.with_suffix(".db-wal"), DB_PATH.with_suffix(".db-shm")}:
                    continue
                rel = item.relative_to(DATA_ROOT).as_posix()
                if rel in {"backup_manifest.json", DATABASE_ARCHIVE_PATH}:
                    continue
                archive_sources.append((item, rel))

            hashes: dict[str, str] = {}
            total = 0
            for source_path, arcname in archive_sources:
                size = source_path.stat().st_size
                if size > MAX_SINGLE_FILE:
                    raise BackupValidationError(f"File too large for backup: {arcname}")
                total += size
                if total > MAX_TOTAL_UNCOMPRESSED:
                    raise BackupValidationError("Backup exceeds the maximum allowed uncompressed size")
                hashes[arcname] = _sha256_file(source_path)

            manifest = {
                "application": APP_NAME,
                "version": VERSION,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "database": DATABASE_ARCHIVE_PATH,
                "kind": kind,
                "file_count": len(archive_sources),
                "total_uncompressed_size": total,
                "hash_algorithm": "SHA-256",
                "hashes": hashes,
            }

            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
                for source_path, arcname in archive_sources:
                    archive.write(source_path, arcname)
                archive.writestr(
                    "backup_manifest.json",
                    json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"),
                )

        self.db.execute(
            "INSERT INTO backups(path,kind,size_bytes,created_at,status) VALUES(?,?,?,?,?)",
            (str(target), kind, target.stat().st_size, self.db.now(), "OK"),
        )
        self.db.audit("CREATE_BACKUP", "backup", None, str(target))
        self.prune()
        return target

    @staticmethod
    def _safe_member_name(name: str) -> str:
        normalized = name.replace("\\", "/")
        pure = PurePosixPath(normalized)
        if not normalized or normalized.startswith("/") or pure.is_absolute():
            raise BackupValidationError("Unsafe absolute path in backup")
        if any(part in {"", ".", ".."} for part in pure.parts):
            raise BackupValidationError("Unsafe relative path in backup")
        if len(pure.parts) and ":" in pure.parts[0]:
            raise BackupValidationError("Unsafe drive path in backup")
        return pure.as_posix()

    @staticmethod
    def _is_symlink(info: zipfile.ZipInfo) -> bool:
        mode = (info.external_attr >> 16) & 0xFFFF
        return stat.S_ISLNK(mode)

    @staticmethod
    def safe_target(base: Path, name: str) -> Path:
        safe_name = BackupService._safe_member_name(name)
        destination = (base / safe_name).resolve()
        root = base.resolve()
        if destination != root and root not in destination.parents:
            raise BackupValidationError("Unsafe backup path")
        return destination

    def validate_detailed(self, path: Path) -> dict:
        path = Path(path)
        if not path.is_file() or not zipfile.is_zipfile(path):
            raise BackupValidationError("Invalid AuraAgenda backup")

        with zipfile.ZipFile(path) as archive:
            infos = [info for info in archive.infolist() if not info.is_dir()]
            if len(infos) > MAX_FILES:
                raise BackupValidationError("Backup contains too many files")

            total = 0
            names: set[str] = set()
            for info in infos:
                safe_name = self._safe_member_name(info.filename)
                if self._is_symlink(info):
                    raise BackupValidationError("Symbolic links are not allowed in backups")
                if safe_name in names:
                    raise BackupValidationError("Duplicate file name in backup")
                names.add(safe_name)
                if info.file_size > MAX_SINGLE_FILE:
                    raise BackupValidationError(f"Backup member is too large: {safe_name}")
                total += info.file_size
                if total > MAX_TOTAL_UNCOMPRESSED:
                    raise BackupValidationError("Backup expands beyond the safety limit")
                if info.file_size > 1024 * 1024:
                    compressed = max(1, info.compress_size)
                    if info.file_size / compressed > MAX_COMPRESSION_RATIO:
                        raise BackupValidationError("Suspicious compression ratio detected")

            if DATABASE_ARCHIVE_PATH not in names:
                raise BackupValidationError("Backup database is missing")
            if "backup_manifest.json" not in names:
                raise BackupValidationError("Backup manifest is missing")

            try:
                manifest = json.loads(archive.read("backup_manifest.json").decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise BackupValidationError("Backup manifest is invalid") from exc

            if manifest.get("application") != APP_NAME:
                raise BackupValidationError("Backup belongs to another application")
            if manifest.get("database") != DATABASE_ARCHIVE_PATH:
                raise BackupValidationError("Backup database path is invalid")

            payload_infos = [info for info in infos if self._safe_member_name(info.filename) != "backup_manifest.json"]
            if "file_count" in manifest and int(manifest.get("file_count", -1)) != len(payload_infos):
                raise BackupValidationError("Backup manifest file count does not match the archive")
            payload_total = sum(info.file_size for info in payload_infos)
            if (
                "total_uncompressed_size" in manifest
                and int(manifest.get("total_uncompressed_size", -1)) != payload_total
            ):
                raise BackupValidationError("Backup manifest size does not match the archive")

            # V2.0.2 backups are accepted for migration even if they predate hashes.
            hashes = manifest.get("hashes") or {}
            if hashes:
                for member, expected in hashes.items():
                    safe_member = self._safe_member_name(str(member))
                    if safe_member not in names:
                        raise BackupValidationError(f"Manifest references a missing file: {safe_member}")
                    with archive.open(safe_member) as stream:
                        actual = _sha256_stream(stream)
                    if not hmac.compare_digest(actual, str(expected).lower()):
                        raise BackupValidationError(f"Hash mismatch: {safe_member}")

            with tempfile.TemporaryDirectory(prefix="aura_validate_") as temp_dir:
                db_copy = Path(temp_dir) / "auraagenda.db"
                with archive.open(DATABASE_ARCHIVE_PATH) as source, db_copy.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
                con = sqlite3.connect(db_copy)
                try:
                    result = con.execute("PRAGMA integrity_check").fetchone()
                finally:
                    con.close()
                if not result or str(result[0]).lower() != "ok":
                    raise BackupValidationError("Backup database failed SQLite integrity_check")

            return {
                "manifest": manifest,
                "file_count": len(infos),
                "total_uncompressed_size": total,
                "legacy_manifest": not bool(hashes),
            }

    def validate(self, path: Path) -> bool:
        try:
            self.validate_detailed(path)
            return True
        except (OSError, zipfile.BadZipFile, BackupValidationError):
            return False

    def _extract_to_staging(self, path: Path, staging: Path) -> None:
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.is_dir() or info.filename == "backup_manifest.json":
                    continue
                target = self.safe_target(staging, info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

    def restore(self, path: Path):
        path = Path(path)
        # Validate fully before touching live data.
        self.validate_detailed(path)
        safety = self.create("BeforeRestore")
        temp = DATA_ROOT / "_restore_staging"
        shutil.rmtree(temp, ignore_errors=True)
        temp.mkdir(parents=True, exist_ok=True)
        try:
            self._extract_to_staging(path, temp)
            staged_db = temp / DATABASE_ARCHIVE_PATH
            if not staged_db.exists():
                raise BackupValidationError("Staged database is missing")

            for item in temp.rglob("*"):
                if item.is_dir():
                    continue
                rel = item.relative_to(temp)
                destination = DATA_ROOT / rel
                destination.parent.mkdir(parents=True, exist_ok=True)
                replacement = destination.with_name(destination.name + ".restore_tmp")
                shutil.copy2(item, replacement)
                os.replace(replacement, destination)
        finally:
            shutil.rmtree(temp, ignore_errors=True)

        self.db.audit("RESTORE_BACKUP", "backup", None, str(path))
        return safety

    def prune(self):
        try:
            keep = max(1, int(self.db.setting("backup_retention", "30")))
        except ValueError:
            keep = 30
        files = sorted(BACKUP_DIR.glob("AuraAgenda_*.zip"), key=lambda item: item.stat().st_mtime, reverse=True)
        for old in files[keep:]:
            old.unlink(missing_ok=True)
