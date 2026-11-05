# -*- coding: utf-8 -*-
"""수업 JSON 읽기. 파일이 없으면 None을 돌려주고 화면에서 안내한다."""
import json
from pathlib import Path

LESSONS_PATH = Path(__file__).resolve().parents[1] / "data" / "lessons.generated.json"
DATA_DIR = Path(__file__).resolve().parents[4] / "Data"  # 원본 수업 HTML 폴더 (scripts/build_lessons.py와 같은 위치)


def section_excerpt(sec: dict, limit: int = 180) -> str:
    """구간 원본 본문의 앞부분 글자(미리보기용). 새 문장을 만들지 않고 원본을 잘라서만 쓴다 (PRD 정책 2)."""
    import html as _html
    import re

    raw = " ".join(b.get("html") or "" for b in sec.get("blocks", []))
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def split_steps(html: str) -> tuple[str, list[tuple[str, str]], str] | None:
    """구간 본문에 단계 체크 목록(<ol class="steps"> 안의 <li class="step">)이 있으면
    (앞부분 HTML, [(단계 탭 이름, 단계 HTML)], 뒷부분 HTML)로 나눈다. 없으면 None.
    탭 이름은 원본 단계 제목(h3)에서 시간 표시(<small>)만 뺀 것 (PRD 정책 2: 새 문장을 만들지 않음)."""
    import re

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(f"<div id='lfroot'>{html}</div>", "lxml")
    root = soup.find(id="lfroot")
    ol = root.find("ol", class_="steps")
    if ol is None:
        return None
    items = ol.find_all("li", class_="step", recursive=False)
    if len(items) < 2:
        return None
    steps = []
    for i, li in enumerate(items):
        h3 = li.find("h3")
        title = ""
        if h3:
            h3c = BeautifulSoup(str(h3), "lxml").find("h3")
            for sm in h3c.find_all("small"):
                sm.decompose()
            title = re.sub(r"\s+", " ", h3c.get_text(" ", strip=True))
        steps.append((f"{i + 1}. {title or '단계'}", str(li)))
    marker = "<!--LF_STEPS-->"
    ol.replace_with(BeautifulSoup(marker, "lxml").find(string=lambda s: "LF_STEPS" in s) or marker)
    rest = root.decode_contents()
    pre, _, post = rest.partition(marker)
    return pre, steps, post


def load_lessons(path: Path = LESSONS_PATH) -> list[dict] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
