# -*- coding: utf-8 -*-
"""진행 상태·진행률 계산 (PRD §4 F06). Streamlit을 쓰지 않는 순수 함수만 둔다."""
import uuid
from datetime import datetime

STATUS_ICON = {"todo": "○ 시작 전", "doing": "◐ 진행 중", "done": "✓ 완료"}
# 체크인: "진행 중"(아직 하는 중) + 다 끝낸 뒤의 평가 3가지. 이모지 대신 글자 (막힘은 경고색 태그로 구분)
LEVEL_LABEL = {"doing": "진행 중", "watch": "관전", "good": "잘 따라감", "struggling": "조금 헤맴", "stuck": "막힘"}
# 관전: 직접 따라 하지 않고 보기만 함 → 구간은 완료로 친다
DONE_LEVELS = ("good", "struggling", "stuck")  # 완료 후에 고르는 평가
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
    # 진행 중·막힘 → 진행 중, 잘 따라감·조금 헤맴 → 완료
    set_status(data, lesson_id, section_id, "doing" if level in ("doing", "stuck") else "done", now)
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


def parse_members(text: str) -> list[str]:
    """'홍길동, 김철수 ,, 이영희' → ['홍길동', '김철수', '이영희'] (쉼표·줄바꿈 구분, 중복 제거)."""
    out: list[str] = []
    for part in (text or "").replace("\n", ",").split(","):
        name = part.strip()
        if name and name not in out:
            out.append(name)
    return out


def add_showcase(data: dict, day_iso: str, url: str, name: str, members: list[str], note: str,
                 now: datetime) -> dict:
    """과제 뽐내기 등록. 링크(http/https)와 서비스 이름은 필수 (잘못되면 ValueError, 한국어 메시지)."""
    name = (name or "").strip()
    if not name:
        raise ValueError("서비스 이름을 입력해 주세요.")
    url = (url or "").strip()
    if not url:
        raise ValueError("링크 주소를 입력해 주세요.")
    if not (url.startswith("http://") or url.startswith("https://")) or "." not in url.split("://", 1)[1].split("/")[0]:
        raise ValueError("링크는 https:// 로 시작하는 주소로 입력해 주세요. 예: https://github.com/내아이디/과제")
    item = {
        "id": uuid.uuid4().hex,
        "date": day_iso,
        "url": url,
        "name": name,
        "members": list(members or []),
        "note": (note or "").strip() or None,
        "thumb": None,  # 썸네일 파일 이름 (.userdata/thumbnails/)
        "created_at": _iso(now),
    }
    data.setdefault("showcases", []).append(item)
    return item


def add_team(data: dict, name: str, members: list[str], round_no: int) -> dict:
    """조 추가. 조 이름 필수, 같은 차수 안에서 같은 이름의 조는 만들지 않는다 (ValueError, 한국어)."""
    name = (name or "").strip()
    if not name:
        raise ValueError("조 이름을 입력해 주세요.")
    if any(t["name"] == name and t.get("round") == round_no for t in data.setdefault("teams", [])):
        raise ValueError(f"{round_no}차에 '{name}' 조가 이미 있어요. 다른 이름을 써 주세요.")
    team = {"id": uuid.uuid4().hex, "name": name, "members": list(members or []), "round": round_no}
    data["teams"].append(team)
    return team


def update_team(data: dict, team_id: str, name: str, members: list[str], round_no: int) -> dict:
    """조 수정 (이름·조원·차수). 같은 차수에 같은 이름의 다른 조가 있으면 ValueError (한국어)."""
    team = next((t for t in data.get("teams", []) if t["id"] == team_id), None)
    if team is None:
        raise ValueError("이미 삭제된 조예요. 목록을 새로고침해 주세요.")
    name = (name or "").strip()
    if not name:
        raise ValueError("조 이름을 입력해 주세요.")
    if any(t["id"] != team_id and t["name"] == name and t.get("round") == round_no for t in data["teams"]):
        raise ValueError(f"{round_no}차에 '{name}' 조가 이미 있어요. 다른 이름을 써 주세요.")
    team.update({"name": name, "members": list(members or []), "round": round_no})
    return team


def teams_for_round(data: dict, round_no: int | None) -> list[dict]:
    return [t for t in data.get("teams", []) if round_no is not None and t.get("round") == round_no]


def all_members(data: dict, round_no: int | None = None) -> list[str]:
    """조원 전체(중복 제거). round_no를 주면 그 차수의 조원만."""
    out: list[str] = []
    teams = data.get("teams", []) if round_no is None else teams_for_round(data, round_no)
    for t in teams:
        for m in t["members"]:
            if m not in out:
                out.append(m)
    return out


def set_absences(data: dict, day_iso: str, names: list[str]) -> None:
    """그날 불참자 목록을 통째로 바꾼다. 빈 목록이면 그날 기록을 지운다."""
    ab = data.setdefault("absences", {})
    if names:
        ab[day_iso] = list(dict.fromkeys(names))
    else:
        ab.pop(day_iso, None)


def set_attendance(data: dict, day_iso: str, name: str, present: bool) -> None:
    """한 사람의 그날 참석/불참을 바꾼다 (불참 목록에 넣거나 뺀다)."""
    cur = list(data.get("absences", {}).get(day_iso, []))
    if present:
        cur = [m for m in cur if m != name]
    elif name not in cur:
        cur.append(name)
    set_absences(data, day_iso, cur)


def lesson_started(data: dict, lesson_id: str) -> bool:
    """이 수강생이 그 Day에서 '학습하기'를 눌러 구간을 한 번이라도 열었는지."""
    return any(v.get("status") in ("doing", "done") for v in data.get("progress", {}).get(lesson_id, {}).values())


def section_counts(students: list[dict], lesson_id: str, section_id: str) -> dict:
    """관리자용 집계: 수강생들의 데이터 목록을 받아 그 구간의 진행 중·완료·막힘 인원과
    총 수강생(그 Day에서 학습하기를 누른 수강생) 수를 센다.
    지금 앱은 혼자 쓰는 구조라 students = [내 데이터] 하나뿐이다 (여러 수강생 집계는 추후)."""
    total = doing = done = stuck = 0
    for d in students:
        if not lesson_started(d, lesson_id):
            continue
        total += 1
        status = get_status(d, lesson_id, section_id)
        last = latest_checkin(d, lesson_id, section_id)
        if last and last["level"] == "stuck":
            stuck += 1
        elif status == "done":
            done += 1
        elif status == "doing":
            doing += 1
    return {"total": total, "doing": doing, "done": done, "stuck": stuck}


def delete_item(data: dict, kind: str, item_id: str) -> bool:
    """체크인·기록·과제 링크 한 건만 삭제. kind = 'checkins' | 'notes' | 'showcases'."""
    data.setdefault(kind, [])
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
