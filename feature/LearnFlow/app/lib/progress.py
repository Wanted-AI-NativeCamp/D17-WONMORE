# -*- coding: utf-8 -*-
"""진행 상태·진행률 계산 (PRD §4 F06). Streamlit을 쓰지 않는 순수 함수만 둔다."""
import uuid
from datetime import datetime

STATUS_ICON = {"todo": "○ 시작 전", "doing": "◐ 진행 중", "done": "✓ 완료"}
LEVEL_LABEL = {"good": "🙂 잘 따라감", "struggling": "😵 조금 헤맴", "stuck": "⚠ 막힘"}
NOTE_LABEL = {"difficulty": "어려움", "solution": "해결", "discovery": "발견"}


def _iso(now: datetime) -> str:
    return now.isoformat(timespec="seconds")


def get_status(data: dict, lesson_id: str, section_id: str) -> str:
    return data["progress"].get(lesson_id, {}).get(section_id, {}).get("status", "todo")


def set_status(data: dict, lesson_id: str, section_id: str, status: str, now: datetime) -> None:
    sec = data["progress"].setdefault(lesson_id, {}).setdefault(
        section_id, {"status": "todo", "checked": [], "updated_at": _iso(now)}
    )
    sec["status"] = status
    sec["updated_at"] = _iso(now)


def mark_opened(data: dict, lesson_id: str, section_id: str, now: datetime) -> bool:
    """구간을 열면 '시작 전' → '진행 중'. 이어보기 위치도 갱신. 바뀐 게 있으면 True."""
    changed = False
    if get_status(data, lesson_id, section_id) == "todo":
        set_status(data, lesson_id, section_id, "doing", now)
        changed = True
    resume = data.get("resume") or {}
    if (resume.get("lesson_id"), resume.get("section_id")) != (lesson_id, section_id):
        data["resume"] = {"lesson_id": lesson_id, "section_id": section_id, "updated_at": _iso(now)}
        changed = True
    return changed


def add_checkin(data: dict, lesson_id: str, section_id: str, level: str, note: str, now: datetime) -> dict:
    if level not in LEVEL_LABEL:
        raise ValueError(f"알 수 없는 체크인 값: {level}")
    note = (note or "").strip()
    item = {
        "id": uuid.uuid4().hex,
        "lesson_id": lesson_id,
        "section_id": section_id,
        "level": level,
        "note": note if level != "good" and note else None,
        "created_at": _iso(now),
    }
    data["checkins"].append(item)
    # 잘 따라감·조금 헤맴 → 완료, 막힘 → 진행 중 유지
    set_status(data, lesson_id, section_id, "doing" if level == "stuck" else "done", now)
    return item


def latest_checkin(data: dict, lesson_id: str, section_id: str) -> dict | None:
    items = [c for c in data["checkins"] if c["lesson_id"] == lesson_id and c["section_id"] == section_id]
    return max(items, key=lambda c: c["created_at"]) if items else None


def add_note(data: dict, lesson_id: str, section_id: str, note_type: str, content: str, now: datetime) -> dict:
    """공백만 있는 기록은 ValueError (한국어 메시지)."""
    content = (content or "").strip()
    if not content:
        raise ValueError("내용을 입력해 주세요. 공백만 있는 기록은 저장하지 않습니다.")
    if note_type not in NOTE_LABEL:
        raise ValueError(f"알 수 없는 기록 유형: {note_type}")
    item = {
        "id": uuid.uuid4().hex,
        "lesson_id": lesson_id,
        "section_id": section_id,
        "type": note_type,
        "content": content,
        "created_at": _iso(now),
    }
    data["notes"].append(item)
    return item


def delete_item(data: dict, kind: str, item_id: str) -> bool:
    """체크인 또는 기록 한 건만 삭제. kind = 'checkins' | 'notes'."""
    before = len(data[kind])
    data[kind] = [x for x in data[kind] if x["id"] != item_id]
    return len(data[kind]) == before - 1


def progress_counts(data: dict, lesson: dict) -> tuple[int, int]:
    """(완료 구간 수, 전체 구간 수) — 정수로 센다."""
    total = len(lesson["sections"])
    done = sum(1 for s in lesson["sections"] if get_status(data, lesson["id"], s["id"]) == "done")
    return done, total


def percent(done: int, total: int) -> int:
    """표시용 진행률(%). 전체가 0이면 0."""
    if total <= 0:
        return 0
    return (done * 100 + total // 2) // total  # 정수 반올림
