# -*- coding: utf-8 -*-
"""수업 JSON 읽기. 파일이 없으면 None을 돌려주고 화면에서 안내한다."""
import json
from pathlib import Path

LESSONS_PATH = Path(__file__).resolve().parents[1] / "data" / "lessons.generated.json"
DATA_DIR = Path(__file__).resolve().parents[4] / "Data"  # 원본 수업 HTML 폴더 (scripts/build_lessons.py와 같은 위치)


def load_lessons(path: Path = LESSONS_PATH) -> list[dict] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
