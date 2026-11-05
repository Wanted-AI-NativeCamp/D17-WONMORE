# -*- coding: utf-8 -*-
"""원본 수업 HTML(Data/*.html)을 분석해 data/lessons.generated.json을 만든다.

원본 파일은 읽기만 한다. D1은 Data/D01_1014.rendered.html(브라우저 스냅샷)이 있으면 그것을 쓴다.
실행: python scripts/build_lessons.py
"""
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR.parents[2] / "Data"
OUT_PATH = APP_DIR / "data" / "lessons.generated.json"

# 화면에 쓰지 않는 원본 요소 (스크립트, 원본 메뉴, 원본 스타일, 동작하지 않는 복사 버튼)
REMOVE_SELECTORS = ["script", "style", "noscript", "link", "nav", "button.copy"]


def day_from_filename(name: str) -> int:
    """'D01_1014.html' → 1"""
    m = re.match(r"D(\d+)_", name)
    if not m:
        raise ValueError(f"파일 이름에서 Day를 찾을 수 없습니다: {name}")
    return int(m.group(1))


def clean_title(raw: str) -> str:
    """'D2 워크북 · 제목' → '제목', '제목 워크북 · 10월 14일' → '제목 워크북'"""
    title = re.sub(r"^D\d+\s*워크북\s*·\s*", "", raw.strip())
    title = re.sub(r"\s*·\s*\d+월\s*\d+일$", "", title)
    return title.strip()


def sanitize(node) -> None:
    """스크립트·이벤트 속성 제거, 외부 링크는 새 탭으로."""
    for sel in REMOVE_SELECTORS:
        for el in node.select(sel):
            el.decompose()
    for el in node.find_all(True):
        for attr in list(el.attrs):
            if attr.lower().startswith("on"):
                del el.attrs[attr]
        if el.name == "a" and str(el.get("href", "")).startswith("http"):
            el["target"] = "_blank"
            el["rel"] = "noopener"


def top_level_sections(soup):
    """다른 section 안에 들어 있지 않은 <section id> 목록."""
    return [s for s in soup.select("section[id]") if s.find_parent("section") is None]


def parse_lesson(path: Path, unknown_classes: Counter) -> dict:
    source = path
    day = day_from_filename(path.name)
    if day == 1:
        snapshot = path.with_name("D01_1014.rendered.html")
        if snapshot.exists():
            source = snapshot
        else:
            print("  ⚠ D1 스냅샷이 없어 정적 구간만 만듭니다 (DEVELOPMENT_GUIDE §4 참고)")

    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "lxml")
    title = clean_title(soup.title.get_text() if soup.title else f"D{day}")

    sections = []
    for order, sec in enumerate(top_level_sections(soup)):
        sec_id = sec.get("id", "")
        if "${" in sec_id:  # 스크립트 템플릿 안의 가짜 section
            continue
        h2 = sec.find("h2")
        sec_title = h2.get_text(" ", strip=True) if h2 else sec_id
        if h2:
            h2.decompose()  # 제목은 화면에서 따로 보여준다
        sanitize(sec)
        outline = [h.get_text(" ", strip=True) for h in sec.find_all("h3")]
        check_keys = [
            el.get("data-k") or el.get("data-key")
            for el in sec.select("[data-k], [data-key]")
        ]
        for el in sec.find_all(True):
            unknown_classes.update(el.get("class", []))
        sections.append(
            {
                "id": sec_id,
                "title": sec_title,
                "order": order,
                "outline": [t for t in outline if t],
                "blocks": [{"kind": "html", "html": sec.decode_contents()}],
                "check_keys": [k for k in check_keys if k],
            }
        )

    return {
        "id": f"D{day}",
        "day": day,
        "title": title,
        "source_file": path.name,
        "sections": sections,
    }


def build(data_dir: Path = DATA_DIR, out_path: Path = OUT_PATH) -> list[dict]:
    files = sorted(p for p in data_dir.glob("D*_*.html") if not p.name.endswith(".rendered.html"))
    if not files:
        raise FileNotFoundError(f"수업 HTML이 없습니다: {data_dir}")
    classes: Counter = Counter()
    lessons = []
    for f in files:
        lesson = parse_lesson(f, classes)
        print(f"  {lesson['id']:>4}  구간 {len(lesson['sections']):>2}개  {lesson['title']}")
        lessons.append(lesson)
    lessons.sort(key=lambda l: l["day"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # 임시 파일에 쓴 뒤 바꿔 끼운다 → 앱 화면에서 업로드 중에 꺼져도 기존 수업 데이터가 깨지지 않는다
    tmp = out_path.with_name(out_path.name + ".tmp")
    tmp.write_text(json.dumps(lessons, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, out_path)
    print(f"저장: {out_path} ({len(lessons)}개 Day)")
    print("자주 쓰인 class (화면 스타일 참고):", ", ".join(c for c, _ in classes.most_common(15)))
    return lessons


if __name__ == "__main__":
    try:
        build()
    except Exception as e:  # 사용자에게는 한국어로 알린다
        print(f"수업 데이터 만들기에 실패했습니다: {e}", file=sys.stderr)
        sys.exit(1)
