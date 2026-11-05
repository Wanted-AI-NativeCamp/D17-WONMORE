# -*- coding: utf-8 -*-
import json
from datetime import datetime
from pathlib import Path

import pytest

from lib import progress as pg
from lib import storage

NOW = datetime(2026, 11, 5, 18, 0, 0)
LESSON = {"id": "D3", "sections": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}
LESSONS_JSON = Path(__file__).resolve().parents[1] / "data" / "lessons.generated.json"


def test_percent_is_exact_and_safe():
    assert pg.percent(0, 0) == 0
    assert pg.percent(1, 3) == 33
    assert pg.percent(2, 3) == 67
    assert pg.percent(3, 3) == 100


def test_status_rules():
    d = storage.default_data()
    assert pg.get_status(d, "D3", "a") == "todo"
    pg.mark_opened(d, "D3", "a", NOW)
    assert pg.get_status(d, "D3", "a") == "doing"
    assert d["resume"]["section_id"] == "a"
    pg.add_checkin(d, "D3", "a", "stuck", "모르겠음", NOW)
    assert pg.get_status(d, "D3", "a") == "doing"
    pg.add_checkin(d, "D3", "a", "struggling", "", NOW)
    assert pg.get_status(d, "D3", "a") == "done"
    assert pg.progress_counts(d, LESSON) == (1, 3)


def test_blank_note_rejected():
    d = storage.default_data()
    with pytest.raises(ValueError):
        pg.add_note(d, "D3", "a", "difficulty", "   \n ", NOW)
    assert d["notes"] == []


def test_delete_only_one():
    d = storage.default_data()
    a = pg.add_note(d, "D3", "a", "solution", "하나", NOW)
    pg.add_note(d, "D3", "a", "solution", "둘", NOW)
    assert pg.delete_item(d, "notes", a["id"])
    assert [n["content"] for n in d["notes"]] == ["둘"]


def test_storage_missing_file_starts_empty(tmp_path):
    data, warn = storage.load(tmp_path / "none.json")
    assert warn is None and data["notes"] == []


def test_storage_roundtrip_and_backups(tmp_path):
    path = tmp_path / "learnflow.v1.json"
    d = storage.default_data()
    for i in range(8):
        d["prefs"]["mode"] = "advanced"
        storage.save(d, path, datetime(2026, 11, 5, 18, 0, i))
    loaded, warn = storage.load(path)
    assert warn is None and loaded["prefs"]["mode"] == "advanced"
    assert len(list((tmp_path / "backups").glob("*.json"))) == 5


def test_storage_broken_file_is_kept(tmp_path):
    path = tmp_path / "learnflow.v1.json"
    path.write_text("{깨진", encoding="utf-8")
    data, warn = storage.load(path, NOW)
    assert warn and data["checkins"] == []
    assert (tmp_path / "learnflow.v1.json.broken-20261105-180000").exists()


@pytest.mark.skipif(not LESSONS_JSON.exists(), reason="빌드 결과물 없음")
def test_built_lessons_match_prd():
    lessons = json.loads(LESSONS_JSON.read_text(encoding="utf-8"))
    counts = {l["id"]: len(l["sections"]) for l in lessons}
    expected = {"D2": 6, "D3": 8, "D4": 11, "D5": 9, "D6": 6, "D7": 6, "D8": 6, "D9": 11, "D10": 8, "D17": 7}
    assert [l["id"] for l in lessons] == ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D17"]
    assert {k: counts[k] for k in expected} == expected
    assert counts["D1"] in (7, 11)
    blob = json.dumps(lessons, ensure_ascii=False)
    assert "<script" not in blob and "onclick" not in blob.lower()


def test_app_opens_with_no_records(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception


def test_day_view_checkin_and_note(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.query_params["day"] = "D3"
    at.run()
    assert not at.exception
    saved = json.loads((tmp_path / "learnflow.v1.json").read_text(encoding="utf-8"))
    assert saved["resume"]["lesson_id"] == "D3"
    radio = next(r for r in at.radio if r.key and r.key.startswith("lvl_"))
    radio.set_value("good").run()
    next(b for b in at.button if b.key and b.key.startswith("ck_")).click().run()
    assert not at.exception
    saved = json.loads((tmp_path / "learnflow.v1.json").read_text(encoding="utf-8"))
    assert saved["checkins"][0]["level"] == "good"
    assert saved["progress"]["D3"][saved["resume"]["section_id"]]["status"] == "done"


def test_advanced_mode_shows_overview(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    path = tmp_path / "learnflow.v1.json"
    d = storage.default_data()
    d["prefs"]["mode"] = "advanced"
    storage.save(d, path, NOW)
    monkeypatch.setattr(storage, "DEFAULT_PATH", path)
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.query_params["page"] = "lessons"
    at.run()
    assert not at.exception
    assert len(at.expander) == 11  # 교육 모아보기에서 Day 11개가 토글로
    # 수업 Day는 페이지 이동 버튼 없음 (프로젝트 기간 카드만 예외: 눌러서 기록하러 들어간다)
    assert not any(b.key and b.key.startswith(("open_D", "detail_")) for b in at.button)
    at.query_params["day"] = "D4"
    at.run()
    assert not at.exception
    assert len(at.expander) == 11  # ?day= 로 와도 같은 교육 모아보기 화면 (D4만 펼침)


def test_schedule_day_dates():
    from datetime import date
    from lib import schedule as sch

    assert sch.date_for_day(1) == date(2026, 10, 14)
    assert sch.date_for_day(10) == date(2026, 10, 27)
    assert sch.date_for_day(17) == date(2026, 11, 5)  # 원본 파일 D17_1105와 일치
    assert sch.day_for_date(date(2026, 10, 19)) == 4  # D04_1019
    assert sch.day_for_date(date(2026, 10, 13)) is None  # D1 이전
    assert sch.day_for_date(date(2026, 10, 17)) is None  # 토요일
    assert [d for _, _, ds in sch.DAY_GROUPS for d in ds] == list(range(1, 18))


def test_project_period_card_and_notes(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    path = tmp_path / "learnflow.v1.json"
    monkeypatch.setattr(storage, "DEFAULT_PATH", path)
    app = str(Path(__file__).resolve().parents[1] / "app.py")

    at = AppTest.from_file(app, default_timeout=30)
    at.query_params["page"] = "lessons"
    at.run()
    assert not at.exception
    keys = [b.key for b in at.button]
    assert "open_project" in keys  # 프로젝트 기간은 긴 카드 하나
    assert not any(k and k in {f"open_D{n}" for n in range(11, 17)} for k in keys)

    at = AppTest.from_file(app, default_timeout=30)
    at.query_params["project"] = "D12"
    at.run()
    assert not at.exception
    at.text_area[0].set_value("프로젝트 아이디어 정리")
    next(b for b in at.button if b.label == "기록 저장").click().run()
    assert not at.exception
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["notes"][0]["lesson_id"] == "D12"
    assert saved["notes"][0]["section_id"] == "project"


def test_default_unit_follows_today():
    from datetime import date
    from lib import schedule as sch

    assert sch.UNITS[sch.default_unit_index(date(2026, 11, 5))][3] == "나만의 AI 업무 도구 제작"  # 구간 안
    assert sch.default_unit_index(date(2026, 12, 19)) == sch.unit_index_for(date(2026, 12, 21))  # 주말 → 다음 구간
    assert sch.default_unit_index(date(2026, 1, 1)) == 0  # 캠프 시작 전 → 첫 구간
    assert sch.default_unit_index(date(2027, 3, 1)) == len(sch.UNITS) - 1  # 캠프 종료 후 → 마지막 구간


def test_month_weeks_are_weekdays_only():
    from datetime import date
    from lib import schedule as sch

    weeks = sch.month_weeks(2026, 10)
    assert all(len(w) == 5 for w in weeks)
    days = [d for w in weeks for d in w if d]
    assert days[0] == date(2026, 10, 1) and days[-1] == date(2026, 10, 30)
    assert all(d.weekday() < 5 for d in days)
    assert sch.units_in_month(2026, 11)[0] == sch.unit_index_for(date(2026, 10, 28))  # 10/28~11/3 구간 포함


def test_calendar_month_view_default_and_switch(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception
    keys = {b.key for b in at.button}
    assert "day_prev" in keys and "cal_prev" not in keys  # 기본은 일별 캘린더
    at.segmented_control(key="cal_view").set_value("month").run()  # 기본은 일별 → 월별로 전환
    keys = {b.key for b in at.button}
    assert {"cal_prev", "cal_next"} <= keys
    assert not any(k and k.startswith("lfpick_") for k in keys)

    # 오른쪽 날짜 버튼을 누르면 아래 패널이 그 날짜로 바뀐다
    btn = [b for b in at.button if b.key and b.key.startswith("lfdate_")][0]
    btn.click().run()
    assert not at.exception
    assert at.session_state.sel_date.isoformat() == btn.key.removeprefix("lfdate_")

    # < > 로 달 이동
    before = at.session_state.cal_month
    next(b for b in at.button if b.key == "cal_prev").click().run()
    assert at.session_state.cal_month != before

    # 전체 일정 보기로 전환
    next(s for s in at.segmented_control if s.key == "cal_view").set_value("all").run()
    assert not at.exception
    assert any(b.key and b.key.startswith("lfpick_") for b in at.button)


def test_calendar_cell_selects_unit(tmp_path, monkeypatch):
    from datetime import date
    from streamlit.testing.v1 import AppTest
    from lib import schedule as sch

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    at.segmented_control(key="cal_view").set_value("month").run()  # 기본은 일별 → 월별로 전환
    # 11/11 칸(AI 워크스페이스 구축 구간)을 누르면 그 구간이 선택되고, 오른쪽에는 그 구간 Day만 나온다
    next(b for b in at.button if b.key == "lfday_2026-11-11").click().run()  # 11/11~11/13 블록
    assert not at.exception
    unit = sch.UNITS[sch.unit_index_for(date(2026, 11, 11))]
    assert sch.unit_index_for(at.session_state.sel_date) == sch.unit_index_for(date(2026, 11, 11))
    btns = sorted(b.key.removeprefix("lfdate_") for b in at.button if b.key and b.key.startswith("lfdate_"))
    assert btns == [d.isoformat() for d in sch.unit_dates(unit)]


def test_week_segments_merge_units():
    from datetime import date
    from lib import schedule as sch

    # 10/12 주: 12~13 직무별 가이드 | 14~16 설치부터 첫 대화까지
    week = sch.month_weeks(2026, 10)[2]
    segs = sch.week_segments(week)
    assert [len(x[2]) for x in segs] == [2, 3]
    # 10/5 주: 5 대체휴일 | 6~7 OT | 8 가이드 | 9 한글날
    segs = sch.week_segments(sch.month_weeks(2026, 10)[1])
    assert [x[0] for x in segs] == ["holiday", "unit", "unit", "holiday"]
    assert sum(len(x[2]) for x in segs) == 5


def test_month_view_has_narrow_screen_unit_list(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from lib import schedule as sch

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    at.segmented_control(key="cal_view").set_value("month").run()  # 기본은 일별 → 월별로 전환
    y, m = at.session_state.cal_month
    picks = sorted(int(b.key.removeprefix("lfmpick_")) for b in at.button if b.key and b.key.startswith("lfmpick_"))
    assert picks == sch.units_in_month(y, m)  # 좁은 화면용 카드는 그 달 구간만
    target = picks[-1]
    next(b for b in at.button if b.key == f"lfmpick_{target}").click().run()
    assert not at.exception
    assert sch.unit_index_for(at.session_state.sel_date) == target


def test_gnb_pages_open(tmp_path, monkeypatch):
    """상단 메뉴의 세 화면(홈·교육 모아보기·기록 모아보기)이 기록 0개여도 에러 없이 열린다."""
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    app = str(Path(__file__).resolve().parents[1] / "app.py")
    for page, active in ((None, "home"), ("lessons", "lessons"), ("records", "records")):
        at = AppTest.from_file(app, default_timeout=30)
        if page:
            at.query_params["page"] = page
        at.run()
        assert not at.exception
        assert f"gnbon_{active}" in [b.key for b in at.button]
    assert any(m.value == "**아직 남긴 기록이 없어요.**" for m in at.markdown)


def test_records_page_lists_saved_records(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    path = tmp_path / "learnflow.v1.json"
    d = storage.default_data()
    pg.add_note(d, "D12", "project", "difficulty", "프로젝트 메모", NOW)
    pg.add_checkin(d, "D3", "s1", "stuck", "설치가 막힘", NOW)
    storage.save(d, path, NOW)
    monkeypatch.setattr(storage, "DEFAULT_PATH", path)
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.query_params["page"] = "records"
    at.run()
    assert not at.exception
    keys = [b.key for b in at.button]
    assert "rec_proj_12" in keys and "rec_open_D3" in keys


def test_daily_step_skips_weekends_and_holidays():
    from datetime import date
    from lib import schedule as sch

    assert sch.step_day(date(2026, 11, 6), 1) == date(2026, 11, 9)  # 금 → 다음 월
    assert sch.step_day(date(2026, 11, 9), -1) == date(2026, 11, 6)  # 월 → 이전 금
    assert sch.step_day(date(2026, 10, 8), 1) == date(2026, 10, 12)  # 10/9 한글날 건너뜀
    assert sch.step_day(date(2026, 11, 7), 1) == date(2026, 11, 9)  # 토요일에서도 가장 가까운 수업일
    assert sch.step_day(date(2026, 10, 6), -1) is None  # 캠프 첫날
    assert sch.step_day(date(2027, 1, 29), 1) is None  # 캠프 마지막 날
    assert sch.fmt_mmdd(date(2026, 11, 5)) == "11.05"


def test_daily_view_opens_section(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    at.session_state["sel_date"] = __import__("datetime").date(2026, 10, 14)  # D1
    at.segmented_control(key="cal_view").set_value("day").run()
    assert not at.exception
    keys = [b.key for b in at.button]
    assert "day_prev" in keys and "day_next" in keys
    assert "lfdopen_D1_0" in keys
    at.button(key="day_next").click().run()
    assert at.session_state["sel_date"] == __import__("datetime").date(2026, 10, 15)
    assert "lfdopen_D2_0" in [b.key for b in at.button]


# ---------- 교육 자료 추가 (업로드) ----------
LESSON_HTML = """<html><head><title>D18 워크북 · 테스트 수업 · 11월 6일</title></head><body>
<section id="s1"><h2>첫 구간</h2><h3>소제목</h3><p>본문</p></section>
<section id="s2"><h2>둘째 구간</h2><p>본문</p></section></body></html>"""


def test_upload_adds_new_day_and_rebuilds(tmp_path):
    pytest.importorskip("bs4")
    from datetime import date
    from lib import upload

    data_dir, out = tmp_path / "Data", tmp_path / "lessons.generated.json"
    data_dir.mkdir()
    lesson = upload.add_lesson_file(LESSON_HTML.encode("utf-8"), date(2026, 11, 6), data_dir, out)
    assert lesson["id"] == "D18" and len(lesson["sections"]) == 2
    assert (data_dir / "D18_1106.html").exists()
    built = json.loads(out.read_text(encoding="utf-8"))
    assert [l["id"] for l in built] == ["D18"]
    assert not list(data_dir.glob("*.tmp")) and not list(tmp_path.glob("*.tmp"))  # 임시 파일이 남지 않음


def test_upload_never_overwrites_existing_original(tmp_path):
    from datetime import date
    from lib import upload

    data_dir, out = tmp_path / "Data", tmp_path / "lessons.generated.json"
    data_dir.mkdir()
    original = data_dir / "D18_1106.html"
    original.write_text("원본", encoding="utf-8")
    with pytest.raises(upload.UploadError, match="덮어쓰지 않아요"):
        upload.add_lesson_file(LESSON_HTML.encode("utf-8"), date(2026, 11, 6), data_dir, out)
    assert original.read_text(encoding="utf-8") == "원본"
    assert not out.exists()


def test_upload_rejects_bad_files_without_saving(tmp_path):
    from datetime import date
    from lib import upload

    data_dir, out = tmp_path / "Data", tmp_path / "lessons.generated.json"
    data_dir.mkdir()
    d = date(2026, 11, 6)
    cases = [(b"", "비어"), (b"<section id='a'>x</section>\xff", "UTF-8")]
    try:
        import bs4  # noqa: F401  구간 검사는 HTML 분석 도구(bs4)가 있을 때만 확인할 수 있다
        cases.append(("<html>구간 없음</html>".encode("utf-8"), "구간"))
    except ImportError:
        pass
    for content, msg in cases:
        with pytest.raises(upload.UploadError, match=msg):
            upload.add_lesson_file(content, d, data_dir, out)
    assert list(data_dir.iterdir()) == []  # 아무것도 저장되지 않음


def test_uploadable_dates_skip_project_and_pre_day():
    from datetime import date
    from lib import schedule as sch
    from lib import upload

    assert upload.uploadable_dates(sch.UNITS[0]) == []  # OT · 입과: Day 시작 전
    project_unit = sch.unit_index_for(date(2026, 10, 29))
    assert all(sch.day_for_date(d) not in sch.PROJECT_DAYS for d in upload.uploadable_dates(sch.UNITS[project_unit]))
    assert upload.file_name_for(date(2026, 11, 6)) == "D18_1106.html"


def test_data_dir_matches_build_script():
    pytest.importorskip("bs4")
    from lib import lessons
    from scripts import build_lessons

    assert lessons.DATA_DIR == build_lessons.DATA_DIR


def test_home_has_upload_button(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception
    at.button(key="open_upload").click().run()
    assert not at.exception
    assert any(s.label == "어느 구간에 추가할까요?" for s in at.selectbox)


def test_add_note_button_under_upload(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    path = tmp_path / "learnflow.v1.json"
    monkeypatch.setattr(storage, "DEFAULT_PATH", path)
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    keys = [b.key for b in at.button]
    assert keys.index("open_upload") < keys.index("open_note")  # 교육 자료 추가하기 바로 아래
    next(b for b in at.button if b.key == "open_note").click().run()
    assert not at.exception
    # 창이 열리고 구간·날짜·구간 선택과 저장 버튼이 보인다
    # (AppTest는 창 안 입력 후 다시 그릴 때 창을 닫으므로 저장 동작은 pg.add_note 테스트로 확인)
    assert any(b.key == "note_save" for b in at.button)
    assert any(s.key == "note_unit" for s in at.selectbox)


def test_today_button_in_month_and_day_views(tmp_path, monkeypatch):
    from datetime import date
    from streamlit.testing.v1 import AppTest
    from lib import schedule as sch

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    at.segmented_control(key="cal_view").set_value("month").run()  # 기본은 일별 → 월별로 전환
    target = sch.default_date(date.today())
    # 월별: 다른 달로 갔다가 [오늘]을 누르면 오늘이 있는 달·날짜로 돌아온다
    next(b for b in at.button if b.key == "cal_prev").click().run()
    at.button(key="cal_today").click().run()
    assert not at.exception
    assert at.session_state.sel_date == target
    assert at.session_state.cal_month == sch.clamp_month(target.year, target.month)
    # 일별: 다음 날로 갔다가 [오늘]
    next(s for s in at.segmented_control if s.key == "cal_view").set_value("day").run()
    at.button(key="day_next").click().run()
    at.button(key="day_today").click().run()
    assert not at.exception
    assert at.session_state.sel_date == target


def test_unit_label_once_per_month():
    from datetime import date
    from lib import schedule as sch

    ui = sch.unit_index_for(date(2026, 10, 28))  # 10/28~11/3 반복 업무 프롬프트 설계
    assert sch.unit_first_day_in_month(ui, 2026, 10) == date(2026, 10, 28)
    assert sch.unit_first_day_in_month(ui, 2026, 11) == date(2026, 11, 2)  # 다음 달 첫 블록에 다시 표기
    ui = sch.unit_index_for(date(2026, 12, 21))  # 12/21~30, 12/25 휴일
    assert sch.unit_first_day_in_month(ui, 2026, 12) == date(2026, 12, 21)


def test_month_and_all_views_use_date_toggle(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from lib import schedule as sch

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    at.segmented_control(key="cal_view").set_value("all").run()
    assert not at.exception
    assert not any(b.key and b.key.startswith("lfrow_") for b in at.button)  # 날짜 버튼 목록 없음
    unit = sch.unit_index_for(at.session_state.sel_date)
    toggle = at.segmented_control(key=f"date_pick_{unit}")
    dates = sch.unit_dates(sch.UNITS[unit])
    toggle.set_value(len(dates) - 1).run()
    assert not at.exception
    assert at.session_state.sel_date == dates[-1]


def test_month_view_uses_date_buttons(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path / "learnflow.v1.json")
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    at.run()
    at.segmented_control(key="cal_view").set_value("month").run()
    assert not at.exception
    assert any(b.key and b.key.startswith("lfdate_") for b in at.button)  # 날짜마다 따로 버튼
    assert not any(s.key and s.key.startswith("date_pick_") for s in at.segmented_control)  # 토글 아님
