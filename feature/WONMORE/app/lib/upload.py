# -*- coding: utf-8 -*-
"""수업 자료(HTML) 업로드: 검사 → Data/에 새 파일로 저장 → 수업 데이터 다시 만들기.
Streamlit 화면 함수는 쓰지 않는다. 폴더 위치는 값으로 넘겨받는다(테스트에서 임시 폴더 사용).

원본 보호: 이미 그날 자료가 있으면 덮어쓰지 않고 거절한다. 기존 원본 파일은 읽기만 한다.
"""
import os
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

from lib import schedule as sch

MAX_BYTES = 20 * 1024 * 1024  # 20MB. 수업 HTML 한 개로는 넉넉한 크기


class UploadError(Exception):
    """사용자에게 그대로 보여줄 한국어 메시지를 담는다."""


def file_name_for(d: date) -> str:
    """날짜 → 원본과 같은 규칙의 파일 이름. 11/6(D18) → 'D18_1106.html'"""
    n = sch.day_for_date(d)
    if not n:
        raise UploadError("이 날은 Day 번호가 없는 날이라 수업 자료를 추가할 수 없어요.")
    return f"D{n:02d}_{d.month:02d}{d.day:02d}.html"


def existing_file(data_dir: Path, d: date) -> Path | None:
    """그날(Day)의 원본 파일이 이미 있으면 그 경로. 날짜 부분이 달라도 같은 Day면 있는 것으로 본다."""
    n = sch.day_for_date(d)
    if not n or not data_dir.exists():
        return None
    for p in data_dir.glob(f"D{n:02d}_*.html"):
        if not p.name.endswith(".rendered.html"):
            return p
    return None


def uploadable_dates(unit) -> list[date]:
    """구간 안에서 자료를 올릴 수 있는 날: Day 번호가 있고 프로젝트 기간(교육 없음)이 아닌 수업일."""
    return [d for d in sch.unit_dates(unit) if sch.day_for_date(d) and sch.day_for_date(d) not in sch.PROJECT_DAYS]


def add_lesson_file(content: bytes, d: date, data_dir: Path, out_path: Path) -> dict:
    """업로드한 HTML을 그날의 수업 자료로 추가하고 수업 데이터를 다시 만든다. 추가된 Day 정보를 돌려준다.
    실패하면 UploadError(한국어 메시지). 중간에 실패해도 기존 원본·수업 데이터는 그대로 남는다."""
    if not content:
        raise UploadError("파일이 비어 있어요. 다른 파일을 골라 주세요.")
    if len(content) > MAX_BYTES:
        raise UploadError("파일이 너무 커요(20MB 초과). 수업 HTML 파일이 맞는지 확인해 주세요.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise UploadError("파일을 읽을 수 없어요. UTF-8로 저장된 HTML 파일인지 확인해 주세요.") from None

    name = file_name_for(d)
    if (old := existing_file(data_dir, d)) is not None:
        raise UploadError(f"이 날에는 이미 수업 자료({old.name})가 있어요. 원본 보호를 위해 덮어쓰지 않아요.")

    try:  # HTML 분석 도구(bs4)는 업로드할 때만 불러온다 → 없어도 앱 자체는 열린다
        from scripts import build_lessons
    except ImportError as e:
        print(f"[upload] build_lessons 불러오기 실패: {e!r}")
        raise UploadError("수업 자료를 읽는 도구가 설치되어 있지 않아요. 터미널에서 `pip install -r requirements.txt` 후 다시 시도해 주세요.") from e

    # 1) 저장하기 전에 임시 폴더에서 구간이 나오는지 먼저 확인한다
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / name
        probe.write_text(text, encoding="utf-8")
        try:
            lesson = build_lessons.parse_lesson(probe, Counter())
        except Exception as e:
            print(f"[upload] HTML 분석 실패: {e!r}")
            raise UploadError("수업 자료를 읽지 못했어요. 기존 수업 자료와 같은 형식의 HTML 파일인지 확인해 주세요.") from e
    if not lesson["sections"]:
        raise UploadError("이 파일에서 수업 구간(<section id>)을 찾지 못했어요. 기존 수업 자료와 같은 형식인지 확인해 주세요.")

    # 2) 새 파일로 저장 (임시 파일에 쓴 뒤 이름 바꾸기 → 도중에 꺼져도 반쪽 파일이 남지 않음)
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / name
    fd, tmp_path = tempfile.mkstemp(dir=data_dir, prefix=".upload-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp_path, target)
    except OSError as e:
        Path(tmp_path).unlink(missing_ok=True)
        print(f"[upload] 파일 저장 실패: {e!r}")
        raise UploadError("수업 자료를 저장하지 못했어요. 폴더 권한이나 남은 용량을 확인해 주세요.") from e

    # 3) 수업 데이터 다시 만들기. 실패하면 방금 추가한 파일만 되돌린다 (기존 원본은 건드리지 않음)
    try:
        build_lessons.build(data_dir, out_path)
    except Exception as e:
        target.unlink(missing_ok=True)
        print(f"[upload] 수업 데이터 다시 만들기 실패: {e!r}")
        raise UploadError("수업 데이터를 다시 만들지 못해 추가를 취소했어요. 터미널 로그를 확인해 주세요.") from e
    return lesson
