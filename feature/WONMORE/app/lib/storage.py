# -*- coding: utf-8 -*-
"""사용자 데이터(.userdata/learnflow.v1.json) 읽기·쓰기. 이 파일만 사용자 데이터에 접근한다.

- 파일이 없으면 기본값으로 시작한다.
- 깨진 파일은 덮어쓰지 않고 .broken-<시각> 으로 옮겨 둔다.
- 저장은 임시 파일 → os.replace 로 교체하고, 직전 파일을 backups/ 에 최근 5개까지 남긴다.
"""
import copy
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / ".userdata" / "learnflow.v1.json"
BACKUP_KEEP = 5

DEFAULT_DATA = {
    "version": 1,
    "progress": {},
    "checkins": [],
    "notes": [],
    "resume": None,
    "prefs": {"mode": "beginner", "job": "common", "os": "win", "role": "student"},  # role: 수업 화면 수강생/관리자 모드
    "showcases": [],
    "teams": [],      # 조 편성: {id, name, members:[이름]}
    "absences": {},   # 불참: {"YYYY-MM-DD": [이름]}  # 과제 뽐내기 링크: {id, date(YYYY-MM-DD), url, note, created_at}
}


class StorageError(Exception):
    """저장 실패. 메시지는 사용자에게 보여줄 한국어 문장이다."""


def default_data() -> dict:
    return copy.deepcopy(DEFAULT_DATA)


def _stamp(now: datetime) -> str:
    return now.strftime("%Y%m%d-%H%M%S")


def load(path: Path | None = None, now: datetime | None = None) -> tuple[dict, str | None]:
    """(데이터, 안내 문구). 안내 문구는 문제가 있었을 때만 채워진다."""
    path = path or DEFAULT_PATH
    now = now or datetime.now()
    if not path.exists():
        return default_data(), None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("최상위 값이 객체가 아님")
    except (ValueError, OSError) as e:
        broken = path.with_name(f"{path.name}.broken-{_stamp(now)}")
        try:
            path.replace(broken)
        except OSError:
            pass
        print(f"[storage] 사용자 데이터 파일 읽기 실패: {e!r} → {broken}")
        return default_data(), (
            "저장된 기록 파일이 손상되어 새로 시작합니다. "
            f"기존 파일은 {broken.name} 이름으로 보관해 두었습니다."
        )
    data = default_data()
    data.update(raw)
    data["prefs"] = {**DEFAULT_DATA["prefs"], **(raw.get("prefs") or {})}
    return data, None


def _rotate_backup(path: Path, now: datetime) -> None:
    if not path.exists():
        return
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_dir / f"{path.stem}-{_stamp(now)}.json")
    backups = sorted(backup_dir.glob(f"{path.stem}-*.json"))
    for old in backups[:-BACKUP_KEEP]:
        old.unlink()


def save(data: dict, path: Path | None = None, now: datetime | None = None) -> None:
    """실패하면 StorageError를 던진다 (성공으로 표시하면 안 됨)."""
    path = path or DEFAULT_PATH
    now = now or datetime.now()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _rotate_backup(path, now)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)
    except OSError as e:
        print(f"[storage] 저장 실패: {e!r}")
        raise StorageError("기록을 저장하지 못했습니다. 디스크 공간이나 폴더 권한을 확인한 뒤 다시 시도해 주세요.") from e


# ---------- 과제 뽐내기 썸네일 이미지 ----------
THUMB_TYPES = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}
THUMB_MAX_BYTES = 2 * 1024 * 1024  # 2MB


def thumb_dir(path: Path | None = None) -> Path:
    return (path or DEFAULT_PATH).parent / "thumbnails"


def save_thumbnail(item_id: str, content: bytes, mime: str, path: Path | None = None) -> str:
    """썸네일을 .userdata/thumbnails/<id>.<확장자> 로 저장하고 파일 이름을 돌려준다. 실패하면 StorageError(한국어)."""
    ext = THUMB_TYPES.get(mime)
    if not ext:
        raise StorageError("썸네일은 PNG, JPG, WEBP 이미지만 올릴 수 있어요.")
    if len(content) > THUMB_MAX_BYTES:
        raise StorageError("썸네일 이미지는 2MB 이하로 올려 주세요.")
    folder = thumb_dir(path)
    try:
        folder.mkdir(parents=True, exist_ok=True)
        name = f"{item_id}.{ext}"
        tmp = folder / (name + ".tmp")
        tmp.write_bytes(content)
        os.replace(tmp, folder / name)
    except OSError as e:
        print(f"[storage] 썸네일 저장 실패: {e!r}")
        raise StorageError("썸네일을 저장하지 못했어요. 디스크 공간이나 폴더 권한을 확인해 주세요.") from e
    return name


def load_thumbnail(name: str | None, path: Path | None = None) -> tuple[bytes, str] | None:
    """(이미지 바이트, MIME). 파일이 없으면 None (화면에는 빈 썸네일)."""
    if not name or "/" in name or "\\" in name or ".." in name:
        return None
    f = thumb_dir(path) / name
    if not f.exists():
        return None
    mime = next((m for m, e in THUMB_TYPES.items() if f.suffix == "." + e), "image/png")
    return f.read_bytes(), mime
