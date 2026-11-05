# -*- coding: utf-8 -*-
"""LearnFlow — 수업 자료를 구간별로 따라가며 진행 상황과 어려움을 기록한다.
실행: streamlit run app.py   (먼저 python scripts/build_lessons.py)
"""
from datetime import date, datetime
from html import escape

import streamlit as st

from lib import lessons as lessons_lib
from lib import progress as pg
from lib import schedule as sch
from lib import storage, theme, upload

st.set_page_config(page_title="LearnFlow", page_icon="📘", layout="wide")

# 저장 값(beginner/advanced)은 기존 기록과 호환되도록 그대로 두고 화면 이름만 바꾼다
MODE_LABEL = {"beginner": "🔵 차근차근 학습", "advanced": "🟣 빠르게 둘러보기"}


# ---------- 데이터 ----------
@st.cache_data
def get_lessons():
    return lessons_lib.load_lessons()


def state() -> dict:
    if "data" not in st.session_state:
        data, warning = storage.load()
        st.session_state.data = data
        st.session_state.load_warning = warning
    return st.session_state.data


def persist(success_msg: str | None = None) -> bool:
    try:
        storage.save(st.session_state.data)
    except storage.StorageError as e:
        st.error(str(e))
        return False
    if success_msg:
        st.toast(success_msg)
    return True


def go(day: str | None = None, sec: str | None = None, project: str | None = None, page: str | None = None) -> None:
    st.query_params.clear()
    if page:
        st.query_params["page"] = page
    if project:
        st.query_params["project"] = project
    if day:
        st.query_params["day"] = day
    if sec:
        st.query_params["sec"] = sec
    st.rerun()


# ---------- 삭제 확인 ----------
@st.dialog("기록 삭제")
def confirm_delete(kind: str, item_id: str, summary: str) -> None:
    st.write("이 기록을 삭제할까요? 삭제하면 되돌릴 수 없어요.")
    st.caption(summary)
    c1, c2 = st.columns(2)
    if c1.button("삭제하기", type="primary", use_container_width=True):
        if pg.delete_item(st.session_state.data, kind, item_id) and persist("기록을 삭제했어요."):
            st.rerun()
    if c2.button("취소", use_container_width=True):
        st.rerun()


# ---------- 상단 메뉴(GNB) ----------
NAV = [("home", "학습 캘린더"), ("lessons", "교육 모아보기"), ("records", "기록 모아보기")]


def gnb(active: str) -> None:
    """모든 화면 맨 위의 메뉴바. 로고를 누르면 홈으로 간다."""
    with st.container(key="lf_gnb", horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
        with st.container(key="lf_logo"):
            st.html('<div class="lf-logo">WONMORE</div>')  # 상위 브랜드 글자 로고 (그림 없음)
            if st.button("WONMORE · 학습 캘린더로 이동", key="gnb_logo"):
                go()
        with st.container(key="lf_nav", horizontal=True, horizontal_alignment="center", gap="small"):
            for page, label in NAV:
                on = "on" if page == active else "off"
                if st.button(label, key=f"gnb{on}_{page}", type="tertiary", width="content"):
                    go(page=None if page == "home" else page)
        st.html('<div class="lf-gnb-end"></div>')  # 메뉴를 가운데 두기 위한 오른쪽 빈 칸 (로고와 같은 너비)


# ---------- 홈 ----------
def home(lessons: list[dict], data: dict) -> None:
    # 배너: 왼쪽 소개 글, 오른쪽 "교육 자료 추가하기" 버튼
    with st.container(key="lf_hero", horizontal=True, vertical_alignment="bottom", horizontal_alignment="distribute"):
        st.html(
            '<div class="lf-hero-text"><div class="lf-eyebrow">WONMORE · LearnFlow</div>'
            "<h1>수업 자료를 구간별로, 내 속도대로</h1>"
            "<p>수업 자료를 일별로 확인하고, 다시 봐야 할 땐 북마크로 남겨요.</p></div>"
        )
        # 오른쪽 버튼 두 개를 세로로 (교육 자료 추가 → 그 아래 내 기록 추가)
        with st.container(key="lf_hero_actions", width=220, gap="small"):
            if st.button("＋ 교육 자료 추가하기", key="open_upload", width="stretch"):
                upload_dialog(lessons)
            if st.button("＋ 내 기록 추가하기", key="open_note", width="stretch"):
                note_dialog(lessons, data)
    schedule_section(lessons, data)


# ---------- 내 기록 추가 ----------
@st.dialog("내 기록 추가하기", width="medium")
def note_dialog(lessons: list[dict], data: dict, today: date | None = None) -> None:
    """구간 → 날짜 → (수업이 있으면) 수업 구간을 고르고 어려움/해결/발견 기록을 남긴다."""
    today = today or date.today()
    by_id = {l["id"]: l for l in lessons}
    st.caption("어느 날, 어느 구간에서의 기록인지 고른 뒤 남겨 주세요. 기록 모아보기와 날짜 패널에서 다시 볼 수 있어요.")

    def recordable(d: date) -> bool:
        n = sch.day_for_date(d)
        return bool(n) and (n in sch.PROJECT_DAYS or f"D{n}" in by_id)

    units = [i for i, u in enumerate(sch.UNITS) if any(recordable(d) for d in sch.unit_dates(u))]
    if not units:
        st.info("기록을 남길 수 있는 날이 아직 없어요. 수업 자료를 먼저 추가해 주세요.")
        return
    base = st.session_state.get("sel_date", today)
    start_ui = sch.unit_index_for(base)
    ui = st.selectbox("어느 구간인가요?", options=units, index=units.index(start_ui) if start_ui in units else 0,
                      format_func=lambda i: sch.unit_label(sch.UNITS[i]), key="note_unit")
    dates = [d for d in sch.unit_dates(sch.UNITS[ui]) if recordable(d)]
    d = st.selectbox("어느 날인가요?", options=dates, index=dates.index(base) if base in dates else 0,
                     format_func=lambda x: f"{sch.fmt_date(x)} · D{sch.day_for_date(x)}", key=f"note_date_{ui}")
    n = sch.day_for_date(d)
    lid = f"D{n}"
    if n in sch.PROJECT_DAYS:
        sec_id = sch.PROJECT_SECTION
        st.caption("프로젝트 기간 기록으로 저장돼요.")
    else:
        secs = by_id[lid]["sections"]
        sec_id = st.selectbox("수업의 어느 부분인가요?", options=[s["id"] for s in secs],
                              format_func=lambda sid: next(s["title"] for s in secs if s["id"] == sid),
                              key=f"note_sec_{lid}")
    ntype = st.segmented_control("유형", options=list(pg.NOTE_LABEL), format_func=pg.NOTE_LABEL.get,
                                 default="difficulty", key="note_type")
    content = st.text_area("내용", placeholder="막힌 점, 해결 방법, 새로 알게 된 것", key="note_content")
    c1, c2 = st.columns(2)
    if c1.button("기록 저장", type="primary", use_container_width=True, key="note_save"):
        try:
            pg.add_note(data, lid, sec_id, ntype or "difficulty", content, datetime.now())
        except ValueError as e:
            st.warning(str(e))
            return
        if persist("기록을 저장했어요."):
            st.session_state.sel_date = d  # 홈 날짜 패널이 방금 기록한 날을 보여주도록
            st.session_state.cal_month = sch.clamp_month(d.year, d.month)
            st.session_state.pop("note_content", None)
            st.rerun()
    if c2.button("취소", use_container_width=True, key="note_cancel"):
        st.rerun()


# ---------- 교육 자료 추가 (업로드) ----------
@st.dialog("교육 자료 추가하기", width="medium")
def upload_dialog(lessons: list[dict], today: date | None = None) -> None:
    """어느 구간·어느 날에 붙일지 고르고, 그날 전달받은 수업 HTML을 올린다."""
    today = today or date.today()
    have = {l["id"] for l in lessons}
    st.caption("그날 전달받은 수업 자료(HTML)를 올리면 해당 Day 수업으로 추가돼요. 이미 자료가 있는 날은 덮어쓰지 않아요.")

    ui = st.selectbox(
        "어느 구간에 추가할까요?", options=list(range(len(sch.UNITS))),
        index=sch.default_unit_index(today), format_func=lambda i: sch.unit_label(sch.UNITS[i]), key="up_unit",
    )
    dates = upload.uploadable_dates(sch.UNITS[ui])
    if not dates:
        st.info("이 구간에는 수업 자료를 올릴 날이 없어요. (Day 시작 전이거나 프로젝트 기간이에요) 다른 구간을 골라 주세요.")
        return

    def date_label(d: date) -> str:
        n = sch.day_for_date(d)
        return f"{sch.fmt_date(d)} · D{n}" + (" · 이미 자료 있음" if f"D{n}" in have else "")

    # 기본 날짜: 오늘 이후 중 자료가 아직 없는 첫날 (자료는 그날그날 받으므로) → 없으면 지난 빈 날 → 첫날
    empty = [d for d in dates if f"D{sch.day_for_date(d)}" not in have]
    first = next((x for x in empty if x >= today), empty[0] if empty else dates[0])
    d = st.selectbox("어느 날의 수업인가요?", options=dates, index=dates.index(first),
                     format_func=date_label, key=f"up_date_{ui}")
    taken = f"D{sch.day_for_date(d)}" in have
    if taken:
        st.warning("이 날에는 이미 수업 자료가 있어요. 원본 보호를 위해 덮어쓰지 않아요. 다른 날을 골라 주세요.")

    file = st.file_uploader("수업 자료 파일 (HTML)", type=["html", "htm"], key="up_file")
    c1, c2 = st.columns(2)
    if c1.button("추가하기", type="primary", use_container_width=True, disabled=taken or file is None):
        with st.spinner("수업 자료를 읽고 구간을 나누는 중이에요…"):
            try:
                lesson = upload.add_lesson_file(file.getvalue(), d, lessons_lib.DATA_DIR, lessons_lib.LESSONS_PATH)
            except upload.UploadError as e:
                st.error(str(e))
                return
        get_lessons.clear()
        st.session_state.sel_date = d  # 홈 날짜 패널이 방금 추가한 날을 보여주도록
        st.session_state.cal_month = sch.clamp_month(d.year, d.month)
        st.toast(f"{lesson['id']} 수업 자료를 추가했어요. 구간 {len(lesson['sections'])}개")
        st.rerun()
    if c2.button("취소", use_container_width=True):
        st.rerun()


# ---------- 교육 모아보기 ----------
def lessons_page(lessons: list[dict], data: dict) -> None:
    st.html(
        '<div class="lf-eyebrow">교육 모아보기</div><h1 style="margin:4px 0 4px">Day별 수업</h1>'
        '<p class="lf-muted" style="font-size:15px;line-height:22px">Day를 골라 수업을 열고, 구간마다 진행 상황을 남겨 보세요.</p>'
    )
    mode_selector(data)
    advanced = data["prefs"]["mode"] == "advanced"
    resume = data.get("resume")
    r_lesson = next((l for l in lessons if resume and l["id"] == resume["lesson_id"]), None)
    r_sec = next((s for s in r_lesson["sections"] if s["id"] == resume["section_id"]), None) if r_lesson else None
    if r_lesson and r_sec and not advanced:
        c1, _ = st.columns([1, 1])
        c1.caption("마지막으로 보던 곳")
        if c1.button(f"▶ 이어보기 · {r_lesson['id']} {r_sec['title']}", type="primary", use_container_width=True):
            go(r_lesson["id"], r_sec["id"])

    st.subheader("Day 흐름 한눈에 보기" if advanced else "Day 목록")
    if advanced:
        st.caption("Day를 펼치면 구간 흐름이, 구간을 펼치면 원본 소제목이 보여요. ○ 시작 전 · ◐ 진행 중 · ✓ 완료 · ⚠ 막힘")
    open_id = st.query_params.get("day") or (r_lesson["id"] if r_lesson else None)
    by_id = {l["id"]: l for l in lessons}

    for tag, title, days in sch.DAY_GROUPS:
        st.html(f'<div class="lf-group"><span class="lf-tag">{escape(tag)}</span><b>{escape(title)}</b></div>')
        project_days = [n for n in days if n in sch.PROJECT_DAYS]
        if project_days:
            project_card(data, project_days)
        days = [n for n in days if n not in sch.PROJECT_DAYS]
        cols = None if advanced or not days else st.columns(3)
        for i, n in enumerate(days):
            lesson = by_id.get(f"D{n}")
            when = sch.fmt_date(sch.date_for_day(n))
            if advanced:
                if lesson:
                    done, total = pg.progress_counts(data, lesson)
                    label = f"D{n} · {when} · {lesson['title']}  —  {done}/{total} 구간 완료 · {pg.percent(done, total)}%"
                    with st.expander(label, expanded=lesson["id"] == open_id):
                        day_overview(lesson, data)
                else:
                    st.caption(f"D{n} · {when} · 프로젝트 기간 (수업 자료 없음)")
                continue
            with cols[i % 3].container(border=True):
                st.html(f'<span class="lf-tag">D{n}</span> <span class="lf-muted">{when}</span>')
                if lesson:
                    done, total = pg.progress_counts(data, lesson)
                    pct = pg.percent(done, total)
                    st.markdown(f"**{escape(lesson['title'])}**")
                    st.progress(pct / 100, text=f"{done}/{total} 구간 완료 · {pct}%")
                    if st.button("학습하기", key=f"open_{lesson['id']}", use_container_width=True):
                        go(lesson["id"])
                else:
                    st.markdown("**프로젝트 기간**")
                    st.caption("이 날은 수업 자료가 없어요.")


# ---------- 프로젝트 기간 ----------
def project_card(data: dict, days: list[int]) -> None:
    """D11~D16을 하나의 긴 카드로. 누르면 프로젝트 기록 화면으로 들어간다."""
    first, last = sch.date_for_day(days[0]), sch.date_for_day(days[-1])
    count = sum(
        1 for x in data["notes"] if x["section_id"] == sch.PROJECT_SECTION and x["lesson_id"] in {f"D{n}" for n in days}
    )
    with st.container(border=True):
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
        c1.html(
            f'<span class="lf-tag">D{days[0]} – D{days[-1]}</span> '
            f'<span class="lf-muted">{sch.fmt_date(first)} – {sch.fmt_date(last)}</span>'
            f'<div style="margin-top:6px;font-weight:700;color:var(--text-strong)">프로젝트 기간</div>'
            f'<div class="lf-muted" style="font-size:14px;line-height:20px">수업 자료 없음 · Day별 개인 학습 기록 {count}개</div>'
        )
        if c2.button("기록하러 가기", key="open_project", type="primary", use_container_width=True):
            go(project=f"D{days[0]}")


def project_view(data: dict) -> None:
    days = sch.PROJECT_DAYS
    if st.button("← 교육 모아보기"):
        go(page="lessons")
    first, last = sch.date_for_day(days[0]), sch.date_for_day(days[-1])
    st.html(
        f'<div class="lf-eyebrow">D{days[0]} – D{days[-1]} · {sch.fmt_date(first)} – {sch.fmt_date(last)}</div>'
        '<h1 style="margin:4px 0 8px">프로젝트 기간</h1>'
        '<p class="lf-muted" style="font-size:15px;line-height:22px">이 기간에는 수업 자료가 없어요. '
        "Day별로 개인 학습 기록을 남겨 두세요.</p>"
    )
    cur = st.query_params.get("project")
    cur_n = int(cur[1:]) if cur and cur[1:].isdigit() and int(cur[1:]) in days else days[0]

    def label(n: int) -> str:
        c = sum(1 for x in data["notes"] if x["lesson_id"] == f"D{n}" and x["section_id"] == sch.PROJECT_SECTION)
        return f"D{n} · {sch.fmt_date(sch.date_for_day(n))}" + (f" · {c}" if c else "")

    n = st.segmented_control("Day", options=days, format_func=label, default=cur_n, key="proj_day") or cur_n
    lid = f"D{n}"
    if cur != lid:
        st.query_params["project"] = lid

    main, side = st.columns([7, 3], gap="large")
    with main:
        st.markdown(f"#### {lid} · {sch.fmt_date(sch.date_for_day(n))} 기록")
        note_form(data, lid, sch.PROJECT_SECTION)
    with side:
        st.markdown(f"#### {lid} 기록 목록")
        project_notes(data, lid, deletable=True)


def project_notes(data: dict, lid: str, deletable: bool) -> None:
    notes = sorted(
        (x for x in data["notes"] if x["lesson_id"] == lid and x["section_id"] == sch.PROJECT_SECTION),
        key=lambda x: x["created_at"], reverse=True,
    )
    if not notes:
        st.caption("이 날 남긴 기록이 없어요.")
        return
    for it in notes:
        with st.container(border=True):
            st.html(f'<span class="lf-tag">{escape(pg.NOTE_LABEL[it["type"]])}</span>')
            st.text(it["content"])
            c1, c2 = st.columns([2, 1])
            c1.caption(it["created_at"][5:16].replace("T", " "))
            if deletable and c2.button("삭제", key=f"del_{it['id']}", type="tertiary"):
                confirm_delete("notes", it["id"], it["content"][:60])


# ---------- 기록 모아보기 ----------
def records_page(lessons: list[dict], data: dict) -> None:
    """모든 Day의 체크인·학습 기록을 최근 Day부터 읽기 전용으로 모아 보여준다."""
    checkins, notes = data["checkins"], data["notes"]
    stuck = sum(1 for c in checkins if c["level"] == "stuck")
    st.html(
        '<div class="lf-eyebrow">기록 모아보기</div><h1 style="margin:4px 0 4px">내 학습 기록</h1>'
        f'<p class="lf-muted" style="font-size:15px;line-height:22px">체크인 {len(checkins)}개 · 학습 기록 {len(notes)}개'
        + (f" · 막힘 {stuck}개" if stuck else "") + "</p>"
    )
    used = {x["lesson_id"] for x in checkins} | {x["lesson_id"] for x in notes}
    if not used:
        with st.container(border=True):
            st.markdown("**아직 남긴 기록이 없어요.**")
            st.caption("수업을 열고 구간 끝에서 체크인하거나 학습 기록을 남기면 여기에 모여요.")
            if st.button("교육 모아보기로 가기", type="primary"):
                go(page="lessons")
        return

    by_id = {l["id"]: l for l in lessons}
    days = sorted((int(lid[1:]) for lid in used if lid[1:].isdigit()), reverse=True)
    for n in days:
        lid = f"D{n}"
        with st.container(border=True):
            c1, c2 = st.columns([3, 1], vertical_alignment="center")
            if n in sch.PROJECT_DAYS:
                c1.html(f'<span class="lf-tag">{lid}</span> <span class="lf-muted">{sch.fmt_date(sch.date_for_day(n))}</span>'
                        '<div style="margin-top:4px;font-weight:700;color:var(--text-strong)">프로젝트 기간</div>')
                if c2.button("기록 남기기", key=f"rec_proj_{n}", use_container_width=True):
                    go(project=lid)
                project_notes(data, lid, deletable=False)
                continue
            lesson = by_id.get(lid)
            title = escape(lesson["title"]) if lesson else "수업 자료 없음"
            c1.html(f'<span class="lf-tag">{lid}</span> <span class="lf-muted">{sch.fmt_date(sch.date_for_day(n))}</span>'
                    f'<div style="margin-top:4px;font-weight:700;color:var(--text-strong)">{title}</div>')
            if lesson:
                if c2.button("수업 열기", key=f"rec_open_{lid}", use_container_width=True):
                    go(lid)
                records_list(data, lesson)


# ---------- 캠프 일정 ----------
def schedule_section(lessons: list[dict], data: dict, today: date | None = None) -> None:
    """캠프 일정. 월별 캘린더(기본) / 전체 일정 보기를 바꿔 쓸 수 있다. 고른 날짜는 sel_date 하나로 관리한다."""
    today = today or date.today()
    ss = st.session_state
    if "sel_date" not in ss:
        ss.sel_date = sch.default_date(today)
    if "cal_month" not in ss:
        ss.cal_month = sch.clamp_month(ss.sel_date.year, ss.sel_date.month)

    head, toggle = st.container(key="lf_schedhead").columns([3, 2], vertical_alignment="bottom")
    head.html(
        f'<div class="lf-eyebrow">{sch.CAMP_PERIOD}</div>'
        f'<h2 style="margin:4px 0 0">{sch.CAMP_TITLE}</h2>'
    )
    with toggle, st.container(key="lf_viewtoggle", horizontal=True, horizontal_alignment="right"):
        view = st.segmented_control(
            "일정 보기", options=["day", "month", "all"],
            format_func={"day": "일별", "month": "월별", "all": "전체 일정"}.get,
            default="day", key="cal_view", label_visibility="collapsed",
        ) or "day"

    if view == "month":
        month_calendar_view(lessons, today)
    elif view == "day":
        daily_view(lessons, data, today)
    else:
        all_schedule_view(lessons, today)
    st.html(f'<p class="lf-muted">{sch.CAMP_NOTE}</p>')

    mode_selector(data)  # 보기 모드는 날짜 패널 바로 위 (아래 패널 모양이 모드에 따라 바뀐다)
    day_panel(ss.sel_date, lessons, data)


def _select_date(d: date) -> None:
    st.session_state.sel_date = d


def _select_unit(ui: int, today: date) -> None:
    """구간 선택: 그 구간의 오늘(있으면) 또는 첫 수업일을 고른다. 캘린더 달은 그대로 둔다."""
    dates = sch.unit_dates(sch.UNITS[ui])
    if dates:
        st.session_state.sel_date = today if today in dates else dates[0]


def _move_month(step: int) -> None:
    i = sch.CAL_MONTHS.index(st.session_state.cal_month) + step
    st.session_state.cal_month = sch.CAL_MONTHS[max(0, min(i, len(sch.CAL_MONTHS) - 1))]


def day_row_name(d: date, lessons: list[dict]) -> str:
    n = sch.day_for_date(d)
    if n in sch.PROJECT_DAYS:
        return "프로젝트 기간 · 수업 자료 없음"
    lesson = next((l for l in lessons if n and l["id"] == f"D{n}"), None)
    if lesson:
        return lesson["title"]
    ui = sch.unit_index_for(d)
    if n and n <= 17:
        return "수업 자료 없음"
    return sch.UNITS[ui][3] if ui is not None else ""


def calendar_block(kind: str, ui: int | None, days: list, today: date, sel_unit: int | None) -> None:
    """캘린더 한 주 안에서 같은 구간에 속한 날짜를 합친 블록. 누르면 그 구간을 선택한다."""
    nums = "".join(
        f'<span class="lf-blk-day{" past" if d < today else ""}">{d.day}'
        + ('<span class="lf-today">오늘</span>' if d == today else "") + "</span>"
        if d else '<span class="lf-blk-day"></span>'
        for d in days
    )
    if kind == "empty":
        st.html('<div class="lf-blk empty"></div>')
        return
    if kind == "holiday":
        st.html(f'<div class="lf-blk holiday"><div class="lf-blk-days">{nums}</div>'
                f'<div class="lf-blk-title">{escape(sch.HOLIDAYS[days[0]])}</div></div>')
        return
    if kind == "off":
        st.html(f'<div class="lf-blk off"><div class="lf-blk-days">{nums}</div></div>')
        return
    start, end, tag, title, events = sch.UNITS[ui]
    ns = [sch.day_for_date(d) for d in days if sch.day_for_date(d)]
    dn = (f"D{ns[0]}" if len(ns) == 1 else f"D{ns[0]}–D{ns[-1]}") if ns else ""
    badges = "".join(f'<span class="lf-event{" past" if d < today else ""}">{escape(e)}</span>'
                     for d in days for e in sch.events_on(d))
    tag_html = f'<span class="lf-blk-tag">[{escape(tag)}]</span>' if tag else ""
    # [태그]·주제는 그 달에서 이 구간의 첫 블록에만 (다음 달로 넘어가면 그 달 첫 블록에 다시 표시)
    first = days[0] == sch.unit_first_day_in_month(ui, days[0].year, days[0].month)
    label_html = f'{tag_html}<span class="lf-blk-title">{escape(title)}</span>' if first else ""
    sel = " sel" if ui == sel_unit else ""
    past = " past" if all(d < today for d in days if d) else ""
    with st.container(key=f"lfcell_{days[0].isoformat()}"):
        st.html(
            f'<div class="lf-blk in{sel}{past}"><div class="lf-blk-days">{nums}</div>'
            f'<div class="lf-blk-body">{badges}{label_html}'
            + (f'<span class="lf-cell-dn">{dn}</span>' if dn else "") + "</div></div>"
        )
        st.button(f"{title} 구간 선택", key=f"lfday_{days[0].isoformat()}",
                  on_click=_select_unit, args=(ui, today))


def month_unit_cards(y: int, m: int, today: date, sel_unit: int | None) -> None:
    """좁은 화면용: 그 달에 걸친 구간을 전체 일정 보기처럼 카드로 보여준다. 누르면 그 구간 선택."""
    cur = sch.unit_index_for(today)
    for i in sch.units_in_month(y, m):
        start, end, tag, title, events = sch.UNITS[i]
        span = f"{start.month}/{start.day}" if start == end else f"{start.month}/{start.day}–{end.month}/{end.day}"
        badges = "".join(f'<span class="lf-event{" past" if ed < today else ""}">{escape(e)}</span>' for ed, e in events)
        tag_html = f'<span class="lf-unit-tag">[{escape(tag)}]</span>' if tag else ""
        today_html = '<span class="lf-today">오늘</span>' if i == cur else ""
        sel = " sel" if i == sel_unit else ""
        sel += " past" if end < today else ""
        with st.container(key=f"lfmunit_{i}"):
            st.html(
                f'<div class="lf-unit{sel}"><span class="lf-unit-date">{span}{today_html}</span>{tag_html}'
                f'<span class="lf-unit-title">{escape(title)}</span>{badges}</div>'
            )
            st.button(f"{title} 구간 선택", key=f"lfmpick_{i}", on_click=_select_unit, args=(i, today),
                      use_container_width=True)


def month_calendar_view(lessons: list[dict], today: date) -> None:
    """왼쪽 반: 한 달 캘린더(< > 이동, 칸을 누르면 그 구간 선택), 오른쪽 반: 선택한 구간의 Day 일정 리스트."""
    ss = st.session_state
    y, m = ss.cal_month
    sel = ss.sel_date
    sel_unit = sch.unit_index_for(sel)
    mi = sch.CAL_MONTHS.index((y, m))

    left, right = st.columns([7, 3], gap="medium")  # 캘린더를 넓히고 사이 간격을 줄인다 (오른쪽은 날짜 버튼 2칸이 들어가는 폭)
    with left, st.container(key="lf_cal"):
        # ‹ n월 › 를 좁은 화면에서도 한 줄에 (st.columns는 좁으면 세로로 쌓이므로 가로 컨테이너 사용)
        with st.container(key="lf_calnav", horizontal=True, wrap=False,
                          horizontal_alignment="center", vertical_alignment="center", gap="medium"):
            st.button("‹", key="cal_prev", on_click=_move_month, args=(-1,), disabled=mi == 0,
                      help="이전 달", width="content")
            st.html(f'<div class="lf-cal-title">{m}월 <span>{y}</span></div>', width="content")
            st.button("›", key="cal_next", on_click=_move_month, args=(1,), disabled=mi == len(sch.CAL_MONTHS) - 1,
                      help="다음 달", width="content")
            today_target = sch.default_date(today)
            st.button("오늘", key="cal_today", icon=":material/undo:", icon_position="right", on_click=_go_today, args=(today,),
                      disabled=(y, m) == sch.clamp_month(today_target.year, today_target.month) and sel == today_target,
                      help="오늘로 돌아가기", width="content")

        # 넓은 화면: 구간별로 합친 캘린더 / 좁은 화면(767px 이하): 그 달 구간 카드 목록. CSS가 둘 중 하나만 보여준다.
        with st.container(key="lf_calgrid"):
            st.html('<div class="lf-cal-head">' + "".join(f"<span>{w}</span>" for w in "월화수목금") + "</div>")
            for week in sch.month_weeks(y, m):
                segs = sch.week_segments(week)
                for col, (kind, ui, days) in zip(st.columns([len(x[2]) for x in segs], gap="small"), segs):
                    with col:
                        calendar_block(kind, ui, days, today, sel_unit)
        with st.container(key="lf_callist"):
            month_unit_cards(y, m, today, sel_unit)

    with right:
        with st.container(key="lf_monthpanel", horizontal_alignment="right"):  # 선택한 구간: 오른쪽 정렬
            unit_day_list(lessons, sel_unit, sel, today, as_buttons=True)


def unit_day_list(lessons: list[dict], sel_unit: int | None, sel: date, today: date, as_buttons: bool = False) -> None:
    """선택한 구간 안내(태그·주제·기간·수업일 수) + 그 구간의 날짜 고르기.
    월별 보기(as_buttons=True)는 날짜마다 따로 떨어진 버튼, 전체 일정 보기는 날짜 선택 토글."""
    if sel_unit is None:
        st.caption("캘린더에서 구간을 눌러 주세요.")
        return
    start, end, tag, title, events = sch.UNITS[sel_unit]
    dates = sch.unit_dates(sch.UNITS[sel_unit])
    span = f"{sch.fmt_date(start)}" if start == end else f"{sch.fmt_date(start)} – {sch.fmt_date(end)}"
    tag_html = f'<span class="lf-tag">{escape(tag)}</span> ' if tag else ""
    badges = "".join(f'<span class="lf-event{" past" if ed < today else ""}">{escape(e)}</span>' for ed, e in events)
    st.html(
        '<div class="lf-eyebrow">선택한 구간</div>'
        f'<div class="lf-list-unit">{tag_html}<b style="font-size:18px">{escape(title)}</b></div>'
        f'<div class="lf-unit-when">{badges}<span class="lf-muted" style="font-size:14px;line-height:20px;margin:0">'
        f'{span} · 수업일 {len(dates)}일</span></div>'
    )
    if not dates:
        return

    def date_label(d: date) -> str:
        n = sch.day_for_date(d)
        return sch.fmt_date(d) + (f" · D{n}" if n else "")

    if as_buttons:
        # 한 줄에 3개씩(CSS grid). 모든 버튼 폭은 가장 넓은 버튼에 맞추고, 회색 영역은 그 격자 너비에 맞춘다
        with st.container(key="lf_datebtns", gap="small", width="content"):
            for d in dates:
                # 선택한 날·지나간 날은 바깥 컨테이너 key로 구분해 CSS로 꾸민다
                wrap_key = f"lfdsel_{d.isoformat()}" if d == sel else (f"lfdpast_{d.isoformat()}" if d < today else None)
                box = st.container(key=wrap_key) if wrap_key else st.container()
                box.button(date_label(d), key=f"lfdate_{d.isoformat()}", on_click=_select_date, args=(d,),
                           width="stretch")
        return

    key = f"date_pick_{sel_unit}"

    def on_date() -> None:
        i = st.session_state.get(key)
        if i is not None:
            _select_date(dates[i])

    # 다른 곳(캘린더·오늘 버튼)에서 날짜가 바뀌면 토글 선택도 맞춘다
    want = dates.index(sel) if sel in dates else None
    if key in st.session_state and st.session_state[key] != want:
        st.session_state[key] = want
    st.segmented_control(
        "날짜", options=list(range(len(dates))),
        format_func=lambda i: date_label(dates[i]),
        default=want, key=key, on_change=on_date, label_visibility="collapsed",
    )


def _go_today(today: date) -> None:
    """오늘로 돌아가기: 오늘(수업일이 아니면 가장 가까운 수업일)을 고르고 캘린더 달도 맞춘다."""
    d = sch.default_date(today)
    st.session_state.sel_date = d
    st.session_state.cal_month = sch.clamp_month(d.year, d.month)


def _step_date(step: int) -> None:
    d = sch.step_day(st.session_state.sel_date, step)
    if d:
        st.session_state.sel_date = d


def daily_view(lessons: list[dict], data: dict, today: date) -> None:
    """일별 캘린더: ‹ mm.dd › 로 수업일을 하루씩 옮기고, 그 아래에 그날의 학습 목록(구간)을 보여준다."""
    d = st.session_state.sel_date
    n = sch.day_for_date(d)
    ui = sch.unit_index_for(d)
    with st.container(key="lf_daily"):
        with st.container(key="lf_daynav", horizontal=True, wrap=False,
                          horizontal_alignment="center", vertical_alignment="center", gap="medium"):
            # ‹ mm.dd › 묶음만 가운데 정렬 기준에 들어가고, [오늘] 버튼은 그 묶음 오른쪽 바깥에 붙는다(CSS absolute)
            with st.container(key="lf_daycore", horizontal=True, wrap=False, width="content",
                              vertical_alignment="center", gap="medium"):
                st.button("‹", key="day_prev", on_click=_step_date, args=(-1,), disabled=sch.step_day(d, -1) is None,
                          help="이전 수업일", width="content")
                today_html = '<span class="lf-today">오늘</span>' if d == today else ""
                st.html(
                    f'<div class="lf-day-title">{sch.fmt_mmdd(d)}'
                    f'<span class="lf-day-sub">{sch.WEEKDAY[d.weekday()]}요일' + (f" · D{n}" if n else "")
                    + f"{today_html}</span></div>",  # [오늘] 태그는 요일·D번호 옆 한 줄에
                    width="content",
                )
                st.button("›", key="day_next", on_click=_step_date, args=(1,), disabled=sch.step_day(d, 1) is None,
                          help="다음 수업일", width="content")
                st.button("오늘", key="day_today", icon=":material/undo:", icon_position="right", on_click=_go_today, args=(today,),
                          disabled=d == sch.default_date(today), help="오늘로 돌아가기", width="content")

        if ui is not None:
            tag, title = sch.UNITS[ui][2], sch.UNITS[ui][3]
            badges = "".join(f'<span class="lf-event{" past" if d < today else ""}">{escape(e)}</span>' for e in sch.events_on(d))
            tag_html = f'<span class="lf-tag">{escape(tag)}</span> ' if tag else ""
            # [태그](+이벤트 태그) 한 줄 → 그 아래 대주제를 h1로
            st.html(f'<div class="lf-daily-unit"><div class="lf-list-unit" style="justify-content:center">{tag_html}{badges}</div>'
                    f'<h1 class="lf-daily-topic">{escape(title)}</h1></div>')

        st.html('<div class="lf-daylist-head">오늘의 학습 목록</div>' if d == today
                else '<div class="lf-daylist-head">이 날의 학습 목록</div>')
        daily_lesson_list(d, lessons, data)


def daily_lesson_list(d: date, lessons: list[dict], data: dict) -> None:
    """그날 수업의 구간을 카드로. 카드를 누르면 그 구간을 바로 연다."""
    n = sch.day_for_date(d)
    if n in sch.PROJECT_DAYS:
        st.caption("프로젝트 기간이라 수업 자료가 없어요. 아래에서 그날의 개인 학습 기록을 남길 수 있어요.")
        return
    lesson = next((l for l in lessons if n and l["id"] == f"D{n}"), None)
    if not lesson:
        st.caption("이 날은 수업 자료가 없어요." if n else "Day 수업이 시작되기 전 일정이라 수업 자료가 없어요.")
        return
    sections = lesson["sections"]
    if not sections:
        st.caption("이 Day에는 표시할 구간이 없어요.")
        return
    lid = lesson["id"]
    # 카드 격자: 넓은 화면 3개, 중간 2개, 좁은 화면 1개씩 (CSS grid, 1, 2, 3… 순서 유지)
    grid = st.container(key="lf_dseclist")
    for i, sec in enumerate(sections):
        status = pg.get_status(data, lid, sec["id"])
        last = pg.latest_checkin(data, lid, sec["id"])
        stuck = '<span class="lf-tag warn">막힘</span>' if last and last["level"] == "stuck" else ""
        with grid, st.container(key=f"lfdsec_{lid}_{i}"):
            st.html(
                f'<div class="lf-dsec {status}"><span class="lf-flow-num">{i + 1}</span>'
                f'<div class="lf-dsec-body"><b>{escape(sec["title"])}</b>'
                f'<span class="lf-muted" style="margin:0">{pg.STATUS_ICON[status]}</span>{stuck}</div></div>'
            )
            if st.button(f"{sec['title']} 열기", key=f"lfdopen_{lid}_{i}", use_container_width=True):
                go(lid, sec["id"])


def all_schedule_view(lessons: list[dict], today: date) -> None:
    """10월~1월 전체 일정. 구간을 누르면 그 구간의 날짜를 고를 수 있다."""
    ss = st.session_state
    cur = sch.unit_index_for(today)
    sel_unit = sch.unit_index_for(ss.sel_date)

    def pick(i: int) -> None:
        dates = sch.unit_dates(sch.UNITS[i])
        if dates:
            _select_date(today if today in dates else dates[0])

    with st.container(key="lf_cal"):
        for col, (y, m) in zip(st.columns(len(sch.CAL_MONTHS)), sch.CAL_MONTHS):
            with col:
                st.html(f'<div class="lf-month-head">{m}월 <span>{y}</span></div>')
                for i, (start, end, tag, title, events) in enumerate(sch.UNITS):
                    if (start.year, start.month) != (y, m):
                        continue
                    span = f"{start.month}/{start.day}" if start == end else f"{start.month}/{start.day}–{end.month}/{end.day}"
                    badges = "".join(f'<span class="lf-event{" past" if ed < today else ""}">{escape(e)}</span>' for ed, e in events)
                    tag_html = f'<span class="lf-unit-tag">[{escape(tag)}]</span>' if tag else ""
                    today_html = '<span class="lf-today">오늘</span>' if i == cur else ""
                    sel = " sel" if i == sel_unit else ""
                    sel += " past" if end < today else ""
                    with st.container(key=f"lfunit_{i}"):
                        st.html(
                            f'<div class="lf-unit{sel}"><span class="lf-unit-date">{span}{today_html}</span>{tag_html}'
                            f'<span class="lf-unit-title">{escape(title)}</span>{badges}</div>'
                        )
                        st.button(sch.unit_label(sch.UNITS[i]), key=f"lfpick_{i}", on_click=pick, args=(i,),
                                  use_container_width=True)

    # 날짜 고르기: 월별 보기 오른쪽과 같은 "선택한 구간" 안내 + 날짜 버튼 목록
    unit_day_list(lessons, sel_unit, ss.sel_date, today)


def mode_selector(data: dict) -> None:
    mode = st.segmented_control(
        "보기 모드", options=list(MODE_LABEL), format_func=MODE_LABEL.get,
        default=data["prefs"]["mode"], key="mode_select",
    )
    if mode and mode != data["prefs"]["mode"]:
        data["prefs"]["mode"] = mode
        if persist():
            st.rerun()


def day_panel(d: date, lessons: list[dict], data: dict) -> None:
    n = sch.day_for_date(d)
    lesson = next((l for l in lessons if n and l["id"] == f"D{n}"), None)
    with st.container(border=True):
        head = f"D{n} · {sch.fmt_date(d)}" if n else sch.fmt_date(d)
        st.html(f'<div class="lf-eyebrow">{head}</div>')
        if n in sch.PROJECT_DAYS:
            c1, c2 = st.columns([3, 1])
            c1.markdown("**프로젝트 기간** · 수업 자료 없음")
            if c2.button("기록 남기기", key=f"panel_proj_{n}", type="primary", use_container_width=True):
                go(project=f"D{n}")
            st.markdown("**내 기록**")
            project_notes(data, f"D{n}", deletable=False)
            return
        if not lesson:
            if n:
                st.caption("이 날의 수업 자료가 아직 없어요.")
            else:
                st.caption("Day 수업이 시작되기 전 일정이에요.")
            return
        done, total = pg.progress_counts(data, lesson)
        pct = pg.percent(done, total)
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**{escape(lesson['title'])}**")
        c1.progress(pct / 100, text=f"{done}/{total} 구간 완료 · {pct}%")
        if data["prefs"]["mode"] == "advanced":
            day_overview(lesson, data)
        elif c2.button("수업 열기", key=f"panel_open_{lesson['id']}", use_container_width=True):
            go(lesson["id"])
        st.markdown("**내 기록**")
        records_list(data, lesson)


def records_list(data: dict, lesson: dict) -> None:
    """그날의 체크인·기록을 구간별로 읽기 전용으로 보여준다."""
    lid = lesson["id"]
    rows = [("checkins", c) for c in data["checkins"] if c["lesson_id"] == lid]
    rows += [("notes", x) for x in data["notes"] if x["lesson_id"] == lid]
    if not rows:
        st.caption("이 날 남긴 기록이 없어요.")
        return
    html = []
    groups = [(s["id"], s["title"]) for s in lesson["sections"]]
    known = {sid for sid, _ in groups}
    # 수업 자료를 다시 빌드해 구간이 바뀌어도 기록은 숨기지 않고 따로 묶어 보여준다
    groups += [(sid, "현재 수업 자료에 없는 구간") for sid in dict.fromkeys(r[1]["section_id"] for r in rows) if sid not in known]
    for sid, sec_title in groups:
        items = sorted((r for r in rows if r[1]["section_id"] == sid),
                       key=lambda r: r[1]["created_at"], reverse=True)
        if not items:
            continue
        html.append(f'<div class="lf-rec-sec">{escape(sec_title)}</div>')
        for kind, it in items:
            when = it["created_at"][5:16].replace("T", " ")
            if kind == "checkins":
                cls = " warn" if it["level"] == "stuck" else ""
                tag = f'<span class="lf-tag{cls}">{escape(pg.LEVEL_LABEL[it["level"]])}</span>'
                text = it.get("note") or ""
            else:
                tag = f'<span class="lf-tag">{escape(pg.NOTE_LABEL[it["type"]])}</span>'
                text = it["content"]
            body = f'<div class="lf-rec-text">{escape(text)}</div>' if text else ""
            html.append(f'<div class="lf-rec">{tag} <span class="lf-muted">{when}</span>{body}</div>')
    st.html("".join(html))


# ---------- 빠르게 둘러보기 (F13) ----------
def day_overview(lesson: dict, data: dict) -> None:
    """Day 토글 안에 들어가는 내용: 구간 흐름 + 구간별 접기 목록 (원본 제목·소제목만)."""
    lid = lesson["id"]
    sections = lesson["sections"]
    if not sections:
        st.caption("이 Day에는 표시할 구간이 없어요.")
        return
    steps = "".join(
        f'<li class="lf-flow-step"><span class="lf-flow-num">{i + 1}</span>'
        f"<span>{escape(section_label(data, lid, s))}</span></li>"
        for i, s in enumerate(sections)
    )
    items = []
    for i, sec in enumerate(sections):
        outline = sec.get("outline") or []
        inner = (
            "<ul>" + "".join(f"<li>{escape(t)}</li>" for t in outline) + "</ul>"
            if outline else '<p class="lf-muted">소제목이 없는 구간이에요.</p>'
        )
        last = pg.latest_checkin(data, lid, sec["id"])
        if last:
            inner += f'<p class="lf-muted">최근 체크인: {escape(pg.LEVEL_LABEL[last["level"]])}</p>'
        items.append(
            f'<details class="lf-sec"><summary>{i + 1}. {escape(section_label(data, lid, sec))}</summary>{inner}</details>'
        )
    st.html(f'<ol class="lf-flow">{steps}</ol><div class="lf-secs">{"".join(items)}</div>')


# ---------- Day 상세 ----------
def section_label(data: dict, lesson_id: str, sec: dict) -> str:
    icon = pg.STATUS_ICON[pg.get_status(data, lesson_id, sec["id"])].split()[0]
    last = pg.latest_checkin(data, lesson_id, sec["id"])
    stuck = " ⚠" if last and last["level"] == "stuck" else ""
    return f"{icon} {sec['title']}{stuck}"


def day_view(lesson: dict, data: dict) -> None:
    sections = lesson["sections"]
    if not sections:
        st.warning("이 Day에는 표시할 구간이 없어요. 빌드 스크립트 로그를 확인해 주세요.")
        if st.button("← 교육 모아보기"):
            go(page="lessons")
        return
    ids = [s["id"] for s in sections]
    sec_id = st.query_params.get("sec")
    if sec_id not in ids:
        sec_id = ids[0]
    idx = ids.index(sec_id)
    sec = sections[idx]
    lid = lesson["id"]

    if pg.mark_opened(data, lid, sec_id, datetime.now()):
        persist()

    # 사이드바: 구간 목록
    with st.sidebar:
        if st.button("← 교육 모아보기", use_container_width=True):
            go(page="lessons")
        done, total = pg.progress_counts(data, lesson)
        st.markdown(f"**{lid} · {escape(lesson['title'])}**")
        st.progress(pg.percent(done, total) / 100, text=f"{done}/{total} 구간 완료")
        picked = st.radio(
            "구간", options=ids, index=idx, key=f"nav_{lid}_{sec_id}",
            format_func=lambda i: section_label(data, lid, sections[ids.index(i)]),
        )
        if picked != sec_id:
            go(lid, picked)
        st.caption("○ 시작 전 · ◐ 진행 중 · ✓ 완료 · ⚠ 막힘")

    main, side = st.columns([7, 3], gap="large")

    with main:
        status = pg.get_status(data, lid, sec_id)
        st.html(
            f'<div class="lf-eyebrow">{lid} · 구간 {idx + 1}/{len(sections)}</div>'
            f'<h2 style="margin:4px 0 8px">{escape(sec["title"])}</h2>'
            f'<span class="lf-tag">{pg.STATUS_ICON[status]}</span>'
        )
        body = "".join(b.get("html") or "" for b in sec["blocks"])
        st.html(f'<div class="lf-content">{body}</div>')

        st.divider()
        checkin_form(data, lid, sec_id, status)
        note_form(data, lid, sec_id)

        st.divider()
        p, _, n = st.columns([1, 1, 1])
        if idx > 0 and p.button("← 이전 구간", use_container_width=True):
            go(lid, ids[idx - 1])
        if idx < len(ids) - 1 and n.button("다음 구간 →", type="primary", use_container_width=True):
            go(lid, ids[idx + 1])

    with side:
        day_notes(data, lesson, sec_id)


def checkin_form(data: dict, lid: str, sec_id: str, status: str) -> None:
    st.markdown("#### 잘 따라가고 있나요?")
    last = pg.latest_checkin(data, lid, sec_id)
    if last:
        st.caption(f"최근 체크인: {pg.LEVEL_LABEL[last['level']]} · {last['created_at'][5:16].replace('T', ' ')}")
    level = st.radio(
        "체크인", options=list(pg.LEVEL_LABEL), format_func=pg.LEVEL_LABEL.get,
        horizontal=True, index=None, key=f"lvl_{lid}_{sec_id}", label_visibility="collapsed",
    )
    note = ""
    if level in ("struggling", "stuck"):
        note = st.text_area("어려웠던 점", key=f"ckn_{lid}_{sec_id}", placeholder="예: 3단계에서 명령어가 실행되지 않음")
    c1, c2 = st.columns([1, 1])
    if c1.button("체크인 남기기", key=f"ck_{lid}_{sec_id}", disabled=level is None, use_container_width=True):
        pg.add_checkin(data, lid, sec_id, level, note, datetime.now())
        if persist("체크인을 저장했어요."):
            for k in (f"lvl_{lid}_{sec_id}", f"ckn_{lid}_{sec_id}"):
                st.session_state.pop(k, None)
            st.rerun()
    if status == "done" and c2.button("다시 진행 중으로", key=f"redo_{lid}_{sec_id}", use_container_width=True):
        pg.set_status(data, lid, sec_id, "doing", datetime.now())
        if persist():
            st.rerun()


def note_form(data: dict, lid: str, sec_id: str) -> None:
    with st.form(f"note_{lid}_{sec_id}", clear_on_submit=True, border=True):
        st.markdown("**학습 기록 남기기**")
        ntype = st.segmented_control(
            "유형", options=list(pg.NOTE_LABEL), format_func=pg.NOTE_LABEL.get, default="difficulty",
        )
        content = st.text_area("내용", placeholder="막힌 점, 해결 방법, 새로 알게 된 것")
        if st.form_submit_button("기록 저장", type="primary"):
            try:
                pg.add_note(data, lid, sec_id, ntype or "difficulty", content, datetime.now())
            except ValueError as e:
                st.warning(str(e))
            else:
                if persist("기록을 저장했어요."):
                    st.rerun()


def day_notes(data: dict, lesson: dict, current_sec: str) -> None:
    lid = lesson["id"]
    st.markdown(f"#### {lid} 기록")
    items = [("checkins", c) for c in data["checkins"] if c["lesson_id"] == lid]
    items += [("notes", n) for n in data["notes"] if n["lesson_id"] == lid]
    if not items:
        st.caption("아직 기록이 없어요. 구간 끝에서 체크인하거나 학습 기록을 남겨 보세요.")
        return
    for sec in lesson["sections"]:
        sec_items = sorted((x for x in items if x[1]["section_id"] == sec["id"]),
                           key=lambda x: x[1]["created_at"], reverse=True)
        if not sec_items:
            continue
        here = " (지금 구간)" if sec["id"] == current_sec else ""
        if st.button(f"{sec['title']}{here}", key=f"jump_{sec['id']}", type="tertiary"):
            go(lid, sec["id"])
        for kind, it in sec_items:
            with st.container(border=True):
                when = it["created_at"][5:16].replace("T", " ")
                if kind == "checkins":
                    cls = " warn" if it["level"] == "stuck" else ""
                    st.html(f'<span class="lf-tag{cls}">체크인 · {pg.LEVEL_LABEL[it["level"]]}</span>')
                    text = it.get("note") or ""
                else:
                    st.html(f'<span class="lf-tag">{pg.NOTE_LABEL[it["type"]]}</span>')
                    text = it["content"]
                if text:
                    st.text(text)
                c1, c2 = st.columns([2, 1])
                c1.caption(when)
                if c2.button("삭제", key=f"del_{it['id']}", type="tertiary"):
                    confirm_delete(kind, it["id"], text[:60] or pg.LEVEL_LABEL.get(it.get("level"), ""))


# ---------- 시작 ----------
def main() -> None:
    lessons = get_lessons()
    data = state()
    theme.inject(data["prefs"]["mode"])
    if st.session_state.get("load_warning"):
        st.warning(st.session_state.load_warning)

    if not lessons:
        st.error(
            "수업 데이터가 아직 없어요. 터미널에서 `python scripts/build_lessons.py`를 먼저 실행한 뒤 새로고침해 주세요."
        )
        st.stop()

    qp = st.query_params
    day = qp.get("day")
    lesson = next((l for l in lessons if l["id"] == day), None)
    if qp.get("project"):
        gnb("lessons")
        project_view(data)
    elif lesson and not (data["prefs"]["mode"] == "advanced" and not qp.get("sec")):
        gnb("lessons")
        day_view(lesson, data)
    elif lesson or qp.get("page") == "lessons":
        gnb("lessons")  # 빠르게 둘러보기는 교육 모아보기에서 해당 Day 토글을 펼친 채로 보여준다
        lessons_page(lessons, data)
    elif qp.get("page") == "records":
        gnb("records")
        records_page(lessons, data)
    else:
        gnb("home")
        home(lessons, data)


main()
