# -*- coding: utf-8 -*-
"""WONMORE 학습 캘린더 — 수업 자료를 구간별로 따라가며 진행 상황과 어려움을 기록한다.
실행: streamlit run app.py   (먼저 python scripts/build_lessons.py)
"""
from datetime import date, datetime
from html import escape

import streamlit as st

from lib import lessons as lessons_lib
from lib import progress as pg
from lib import schedule as sch
from lib import storage, theme, upload

st.set_page_config(page_title="WONMORE", page_icon=":material/calendar_month:", layout="wide")

# 저장 값(beginner/advanced)은 기존 기록과 호환되도록 그대로 두고 화면 이름만 바꾼다
MODE_LABEL = {"beginner": "차근차근 학습", "advanced": "빠르게 둘러보기"}


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
NAV = [("home", "학습 캘린더"), ("lessons", "교육 모아보기"), ("records", "학습 기록")]


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
        # 오른쪽 끝: 관리자 페이지(조 편성·불참 관리)
        if st.button("", key=f"gnb{'on' if active == 'admin' else 'off'}_admin_btn", icon=":material/settings:",
                     type="tertiary", help="관리자 · 조 편성", width="content"):
            go(page="admin")


# ---------- 홈 ----------
def home(lessons: list[dict], data: dict) -> None:
    # 배너: 왼쪽 소개 글, 오른쪽 "교육 자료 추가하기" 버튼
    with st.container(key="lf_hero", horizontal=True, vertical_alignment="bottom", horizontal_alignment="distribute"):
        st.html(
            '<div class="lf-hero-text"><div class="lf-eyebrow">WONMORE</div>'
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
    st.caption("어느 날, 어느 구간에서의 기록인지 고른 뒤 남겨 주세요. 학습 기록 메뉴와 날짜 패널에서 다시 볼 수 있어요.")

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
        if c1.button(f"이어보기 · {r_lesson['id']} {r_sec['title']}", type="primary", use_container_width=True):
            go(r_lesson["id"], r_sec["id"])

    st.subheader("Day 흐름 한눈에 보기" if advanced else "Day 목록")
    if advanced:
        st.caption("Day를 펼치면 구간 흐름이, 구간을 펼치면 원본 소제목이 보여요. ○ 시작 전 · ◐ 진행 중 · ✓ 완료 · (막힘) 표시")
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


# ---------- 학습 기록 (GNB) ----------
# ---------- 기록 한 줄 (구간 카드 안에 쌓는다) ----------
def record_row(kind: str, it: dict) -> None:
    if kind == "checkins":
        cls = " warn" if it["level"] == "stuck" else ""
        tag = f'<span class="lf-tag{cls}">{escape(pg.LEVEL_LABEL[it["level"]])}</span>'
        text = it.get("note") or ""
    else:
        tag = f'<span class="lf-tag">{escape(pg.NOTE_LABEL[it["type"]])}</span>'
        text = it["content"]
    c1, c2 = st.columns([6, 1], vertical_alignment="center")
    c1.html(f'<div class="lf-recrow">{tag} <span class="lf-muted">{it["created_at"][5:16].replace("T", " ")}</span>'
            + (f'<span class="lf-recrow-text">{escape(text)}</span>' if text else "") + "</div>")
    if c2.button("삭제", key=f"del_{it['id']}", type="tertiary"):
        confirm_delete(kind, it["id"], text[:60] or pg.LEVEL_LABEL.get(it.get("level"), ""))


def records_page(lessons: list[dict], data: dict) -> None:
    """학습 기록: 체크인 기록 / 헤매거나 어려운 구간·해결한 정보 / 발견한 정보 세 갈래로 나눠 쌓는다."""
    checkins, notes = data["checkins"], data["notes"]
    hard = [x for x in notes if x["type"] in ("difficulty", "solution")]
    found = [x for x in notes if x["type"] == "discovery"]
    head, btn = st.columns([4, 1], vertical_alignment="bottom")
    head.html('<div class="lf-eyebrow">학습 기록</div><h1 style="margin:4px 0 4px">내 학습 기록</h1>'
              f'<p class="lf-muted" style="font-size:15px;line-height:22px">체크인 {len(checkins)}개 · '
              f'어려움·해결 {len(hard)}개 · 발견 {len(found)}개</p>')
    if btn.button("＋ 기록 추가하기", key="rec_add", use_container_width=True):
        note_dialog(lessons, data)

    by_id = {l["id"]: l for l in lessons}

    def sec_title(lid: str, sid: str) -> str:
        if sid == sch.PROJECT_SECTION:
            return "프로젝트 기간"
        lesson = by_id.get(lid)
        return next((s_["title"] for s_ in (lesson or {}).get("sections", []) if s_["id"] == sid), "구간")

    def day_key(lid: str) -> int:
        return int(lid[1:]) if lid[1:].isdigit() else 0

    def render(rows: list, kind: str, empty: str) -> None:
        if not rows:
            st.caption(empty)
            return
        rows = sorted(rows, key=lambda x: (day_key(x["lesson_id"]), x["created_at"]), reverse=True)
        # Day → 구간 순서로 묶는다. 구간마다 카드 하나, 그 안에 기록을 최신순으로 한 줄씩
        groups: dict[str, dict[str, list]] = {}
        for it in rows:
            groups.setdefault(it["lesson_id"], {}).setdefault(it["section_id"], []).append(it)
        for lid, secs in groups.items():
            n = day_key(lid)
            lesson = by_id.get(lid)
            t = "프로젝트 기간" if n in sch.PROJECT_DAYS else (lesson["title"] if lesson else "수업 자료 없음")
            st.html(f'<div class="lf-rec-day"><span class="lf-tag">{lid}</span> '
                    f'<span class="lf-muted">{sch.fmt_date(sch.date_for_day(n)) if n else ""}</span> '
                    f'<b>{escape(t)}</b></div>')
            for sid, items in secs.items():
                with st.container(border=True, key=f"lfrecsec_{kind}_{lid}_{sid}"):
                    st.html(f'<div class="lf-recsec-head">{escape(sec_title(lid, sid))}'
                            f'<span class="lf-muted">{len(items)}개</span></div>')
                    for it in items:
                        record_row(kind, it)

    t1, t2, t3 = st.tabs([f"체크인 기록 {len(checkins)}", f"헤매거나 어려운 구간 · 해결한 정보 {len(hard)}",
                          f"발견한 정보 {len(found)}"])
    with t1:
        render(checkins, "checkins", "아직 체크인 기록이 없어요. 수업 화면에서 '잘 따라가고 있나요?'에 답하면 쌓여요.")
    with t2:
        render(hard, "notes", "아직 어려움·해결 기록이 없어요. '＋ 기록 추가하기'에서 유형을 어려움이나 해결로 골라 남겨 보세요.")
    with t3:
        render(found, "notes", "아직 발견한 정보가 없어요. '＋ 기록 추가하기'에서 유형을 발견으로 골라 남겨 보세요.")


# ---------- 캠프 일정 ----------
def schedule_section(lessons: list[dict], data: dict, today: date | None = None) -> None:
    """캠프 일정. 월별 캘린더(기본) / 전체 일정 보기를 바꿔 쓸 수 있다. 고른 날짜는 sel_date 하나로 관리한다."""
    today = today or date.today()
    ss = st.session_state
    if "sel_date" not in ss:
        ss.sel_date = sch.default_date(today)
    if "cal_month" not in ss:
        ss.cal_month = sch.clamp_month(ss.sel_date.year, ss.sel_date.month)

    # 기간·제목·보기 스위치는 캘린더 카드 위에
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

    # 흰 카드는 캘린더 자체만 감싼다(각 보기의 lf_cal / lf_daily 상자).
    # "선택한 구간" 안내와 날짜 고르기 버튼·스위치는 카드 밖에 둔다.
    if view == "month":
        month_calendar_view(lessons, data, today)
    elif view == "day":
        daily_view(lessons, data, today)
    else:
        all_schedule_view(lessons, today)
    st.html(f'<p class="lf-muted">{sch.CAMP_NOTE}</p>')

    # 보기 모드 선택은 학습 캘린더에서 빼고 교육 모아보기 페이지에만 둔다
    # 그날 수업·기록 카드: 월별은 오른쪽 정보칸 아래, 일별은 캘린더 안에 같은 내용(완료율·학습 목록)이 있어 생략
    if view == "all":
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


def month_calendar_view(lessons: list[dict], data: dict, today: date) -> None:
    """왼쪽 반: 한 달 캘린더(< > 이동, 칸을 누르면 그 구간 선택), 오른쪽 반: 선택한 구간의 Day 일정 리스트."""
    ss = st.session_state
    y, m = ss.cal_month
    sel = ss.sel_date
    sel_unit = sch.unit_index_for(sel)
    mi = sch.CAL_MONTHS.index((y, m))

    # 캘린더 7 : 오른쪽 정보 3. 1100px 이하에서는 CSS로 오른쪽 정보를 캘린더 아래로 내린다(lf_msplit)
    left, right = st.container(key="lf_msplit").columns([7, 3], gap="medium")
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

        # 좁은 화면(767px 이하)에서만: 일별처럼 ‹ n월 › 아래에 선택한 구간 요약 (넓은 화면은 오른쪽 패널에 있으므로 숨김)
        if sel_unit is not None:
            u_start, u_end, u_tag, u_title, u_events = sch.UNITS[sel_unit]
            u_span = sch.fmt_date(u_start) if u_start == u_end else f"{sch.fmt_date(u_start)} – {sch.fmt_date(u_end)}"
            u_badges = "".join(f'<span class="lf-event{" past" if ed < today else ""}">{escape(e)}</span>' for ed, e in u_events)
            u_tag_html = f'<span class="lf-tag">{escape(u_tag)}</span>' if u_tag else ""
            st.html(
                f'<div class="lf-month-unit"><div class="lf-list-unit" style="justify-content:center">{u_tag_html}{u_badges}</div>'
                f'<div class="lf-month-unit-title">{escape(u_title)}</div>'
                f'<div class="lf-muted">{u_span} · 수업일 {len(sch.unit_dates(sch.UNITS[sel_unit]))}일</div></div>'
            )

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
        # 월별: 고른 날짜의 수업·내 기록 카드(수업 열기)는 오른쪽 정보칸 아래에
        day_panel(sel, lessons, data, stacked=True)


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
    # "선택한 구간 · [태그] · 제목"은 캘린더에서 이미 보이므로 중복으로 보여주지 않는다 (기간·수업일 줄만)
    st.html(
        f'<div class="lf-unit-when">{badges}<span class="lf-muted" style="font-size:14px;line-height:20px;margin:0">'
        f'{span} · 수업일 {len(dates)}일</span></div>'
    )
    if not dates:
        return

    def date_label(d: date) -> str:
        n = sch.day_for_date(d)
        return sch.fmt_date(d) + (f" · D{n}" if n else "")

    def date_buttons() -> None:
        # 회색 트랙 안의 날짜 버튼(CSS grid). 선택한 날·지나간 날은 바깥 컨테이너 key로 구분해 꾸민다
        with st.container(key="lf_datebtns", gap="small", width="content"):
            for d in dates:
                wrap_key = f"lfdsel_{d.isoformat()}" if d == sel else (f"lfdpast_{d.isoformat()}" if d < today else None)
                box = st.container(key=wrap_key) if wrap_key else st.container()
                box.button(date_label(d), key=f"lfdate_{d.isoformat()}", on_click=_select_date, args=(d,),
                           width="stretch")

    if as_buttons:
        date_buttons()
        return
    # 전체 일정: 넓은 화면은 날짜 토글, 좁은 화면(767px 이하)은 월별과 같은 날짜 버튼 (CSS가 하나만 보여준다)
    date_buttons()

    key = f"date_pick_{sel_unit}"

    def on_date() -> None:
        i = st.session_state.get(key)
        if i is not None:
            _select_date(dates[i])

    # 다른 곳(캘린더·오늘 버튼)에서 날짜가 바뀌면 토글 선택도 맞춘다
    want = dates.index(sel) if sel in dates else None
    if key in st.session_state and st.session_state[key] != want:
        st.session_state[key] = want
    with st.container(key="lf_alltoggle"):
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
            # [태그](+이벤트 태그) 한 줄 → 대주제(h2, 28px) → 그날 수업 제목 소제목(h3)
            day_lesson = next((l for l in lessons if n and l["id"] == f"D{n}"), None)
            if day_lesson:
                sub = f"D{n} · {day_lesson['title']}"
            elif n in sch.PROJECT_DAYS:
                sub = f"D{n} · 프로젝트 기간"
            else:
                sub = ""
            sub_html = f'<h3 class="lf-daily-sub">{escape(sub)}</h3>' if sub else ""
            st.html(f'<div class="lf-daily-unit"><div class="lf-list-unit" style="justify-content:center">{tag_html}{badges}</div>'
                    f'<h2 class="lf-daily-topic">{escape(title)}</h2>{sub_html}</div>')

        # 학습 목록 위: 그날 수업의 구간 완료율 바 + 표시 글자
        day_lesson_p = next((l for l in lessons if n and l["id"] == f"D{n}"), None)
        if day_lesson_p and day_lesson_p["sections"]:
            done, total = pg.progress_counts(data, day_lesson_p)
            with st.container(key="lf_dprogress"):
                st.progress(pg.percent(done, total) / 100, text=f"{done}/{total} 구간 완료 · {pg.percent(done, total)}%")
        st.html('<div class="lf-daylist-head">오늘의 학습 목록</div>' if d == today
                else '<div class="lf-daylist-head">이 날의 학습 목록</div>')
        daily_lesson_list(d, lessons, data)
        showcase_section(d, data)


# ---------- 과제 뽐내기 (그날 과제 결과물: 썸네일 타일 갤러리) ----------
@st.dialog("배포 링크 등록하기")
def showcase_dialog(d: date, data: dict) -> None:
    k = d.isoformat()
    st.caption(f"{sch.fmt_date(d)} 과제 결과물을 등록해요. 링크와 서비스 이름은 꼭 입력해 주세요.")
    url = st.text_input("링크 주소", placeholder="https://", key=f"show_url_{k}")
    name = st.text_input("서비스 이름", placeholder="예: 1/N 정산왕", key=f"show_name_{k}")
    members_text = st.text_input("참여자", placeholder="쉼표로 구분 · 예: 홍길동, 김철수", key=f"show_members_{k}")
    note = st.text_input("한 줄 설명 (선택)", placeholder="예: 모임 정산을 1분 만에", key=f"show_note_{k}")
    thumb = st.file_uploader("썸네일 이미지 (선택 · 서비스 로고 등 PNG/JPG/WEBP, 2MB 이하 · 없으면 WONMORE 로고)",
                             type=["png", "jpg", "jpeg", "webp"], key=f"show_thumb_{k}")
    c1, c2 = st.columns(2)
    if c1.button("등록하기", type="primary", use_container_width=True, key="show_save"):
        try:
            item = pg.add_showcase(data, k, url, name, pg.parse_members(members_text), note, datetime.now())
        except ValueError as e:
            st.warning(str(e))
            return
        if thumb is not None:
            try:
                item["thumb"] = storage.save_thumbnail(item["id"], thumb.getvalue(), thumb.type)
            except storage.StorageError as e:
                data["showcases"].remove(item)  # 이미지 저장에 실패하면 등록도 하지 않는다
                st.warning(str(e))
                return
        if persist("과제를 등록했어요."):
            st.rerun()
    if c2.button("취소", use_container_width=True, key="show_cancel"):
        st.rerun()


@st.dialog("과제 보기")
def showcase_detail(item_id: str, data: dict) -> None:
    it = next((x for x in data.get("showcases", []) if x["id"] == item_id), None)
    if not it:
        st.info("이미 삭제된 과제예요.")
        return
    img = storage.load_thumbnail(it.get("thumb"))
    st.html(f'<div class="lf-tile lf-tile-big">{_thumb_html(it)}</div>')
    st.markdown(f"**{escape(it.get('name') or '이름 없음')}**")
    if it.get("members"):
        st.caption("참여자 · " + ", ".join(it["members"]))
    if it.get("note"):
        st.write(it["note"])
    st.link_button("링크 열기", it["url"], use_container_width=True)
    ck = f"show_del_confirm_{item_id}"
    if not st.session_state.get(ck):
        if st.button("삭제", key=f"show_del_{item_id}", type="tertiary"):
            st.session_state[ck] = True
            st.rerun(scope="fragment")
    else:
        st.warning("이 과제를 삭제할까요? 삭제하면 되돌릴 수 없어요.")
        c1, c2 = st.columns(2)
        if c1.button("삭제하기", type="primary", use_container_width=True, key=f"show_del_yes_{item_id}"):
            if pg.delete_item(data, "showcases", item_id) and persist("과제를 삭제했어요."):
                st.session_state.pop(ck, None)
                st.rerun()
        if c2.button("취소", use_container_width=True, key=f"show_del_no_{item_id}"):
            st.session_state.pop(ck, None)
            st.rerun(scope="fragment")


@st.cache_data
def _default_logo_uri() -> str:
    import base64
    from pathlib import Path as _P

    f = _P(__file__).resolve().parent / "assets" / "wonmore_logo_thumb.png"
    return "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode()


def _thumb_html(it: dict) -> str:
    import base64

    img = storage.load_thumbnail(it.get("thumb"))
    if img:
        b64 = base64.b64encode(img[0]).decode()
        return f'<img class="lf-tile-img" src="data:{img[1]};base64,{b64}" alt="">'
    # 썸네일을 올리지 않았으면 WONMORE 로고를 기본 썸네일로
    return f'<img class="lf-tile-img lf-tile-logo" src="{_default_logo_uri()}" alt="">'


def showcase_section(d: date, data: dict) -> None:
    """일별 보기: '과제 뽐내기' 제목 + [링크 등록하기] + 정사각형 썸네일 타일(누르면 과제 보기) + 맨 끝 + 타일(새 등록)."""
    iso = d.isoformat()
    with st.container(key="lf_showhead", horizontal=True, vertical_alignment="center", horizontal_alignment="distribute"):
        st.html('<div class="lf-daylist-head" style="margin:0">과제 뽐내기</div>', width="content")
        if st.button("배포 링크 등록하기", key=f"show_add_{iso}", icon=":material/add_link:", width="content"):
            showcase_dialog(d, data)
    items = sorted((x for x in data.get("showcases", []) if x.get("date") == iso), key=lambda x: x["created_at"])
    with st.container(key="lf_showgrid", horizontal=True, wrap=True, gap="small"):
        for it in items:
            with st.container(key=f"lfshowtile_{it['id']}", width="content"):
                st.html(f'<div class="lf-tile">{_thumb_html(it)}</div>'
                        f'<div class="lf-tile-cap">{escape(it.get("name") or it["url"])}</div>')
                if st.button(f"{it.get('name') or '과제'} 보기", key=f"lfshowopen_{it['id']}"):
                    showcase_detail(it["id"], data)
        with st.container(key=f"lfshowadd_{iso}", width="content"):
            st.html('<div class="lf-tile lf-tile-add"><span>+</span></div><div class="lf-tile-cap">&nbsp;</div>')
            if st.button("과제 등록하기", key=f"lfshowaddbtn_{iso}"):
                showcase_dialog(d, data)


def daily_lesson_list(d: date, lessons: list[dict], data: dict) -> None:
    """그날 수업의 구간 목록(왼쪽)과 고른 구간 미리보기(오른쪽). 상세보기 버튼으로 구간을 연다."""
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
    ids = [sec["id"] for sec in sections]
    sel_key = f"dsel_{lid}"
    if st.session_state.get(sel_key) not in ids:
        resume = data.get("resume") or {}
        st.session_state[sel_key] = resume["section_id"] if resume.get("lesson_id") == lid and resume.get("section_id") in ids else ids[0]
    sel_id = st.session_state[sel_key]

    def pick(sid: str) -> None:
        st.session_state[sel_key] = sid

    # 왼쪽: 학습 목록(한 줄에 하나) / 오른쪽: 고른 구간 미리보기 + 학습 상세보기
    # 비율: 넓은 화면 1:2, 1100px 이하 1:1(CSS), 640px 이하는 위아래로 쌓이고 목록 대신 숫자 버튼만
    # 오른쪽 미리보기 카드 높이는 왼쪽 목록 높이에 맞춘다(CSS)
    with st.container(key="lf_dsplit"):
        left, right = st.columns([1, 2], gap="medium")  # 왼쪽 목록 : 오른쪽 미리보기 = 1 : 2
    with left:
        listbox = st.container(key="lf_dseclist")
        for i, sec in enumerate(sections):
            status = pg.get_status(data, lid, sec["id"])
            last = pg.latest_checkin(data, lid, sec["id"])
            stuck = '<span class="lf-tag warn">막힘</span>' if last and last["level"] == "stuck" else ""
            selcls = " sel" if sec["id"] == sel_id else ""
            with listbox, st.container(key=f"lfdsec_{lid}_{i}"):
                st.html(
                    f'<div class="lf-dsec {status}{selcls}"><span class="lf-flow-num">{i + 1}</span>'
                    f'<div class="lf-dsec-body"><b>{escape(sec["title"])}</b>'
                    f'<span class="lf-muted" style="margin:0">{pg.STATUS_ICON[status]}</span>{stuck}</div></div>'
                )
                st.button(f"{i + 1}. {sec['title']} 미리보기", key=f"lfdopen_{lid}_{i}",
                          on_click=pick, args=(sec["id"],), use_container_width=True)
        # 가장 좁은 화면용: 카드 없이 숫자만 (CSS가 640px 이하에서만 보여준다)
        with st.container(key="lf_dnums", horizontal=True, wrap=True, gap="small"):
            for i, sec in enumerate(sections):
                box = st.container(key=f"lfdnumsel_{lid}_{i}", width="content") if sec["id"] == sel_id \
                    else st.container(width="content")
                box.button(str(i + 1), key=f"lfdnum_{lid}_{i}", on_click=pick, args=(sec["id"],),
                           help=sec["title"], width="content")
    with right, st.container(key="lf_dpreview"):
        i = ids.index(sel_id)
        sec = sections[i]
        status = pg.get_status(data, lid, sel_id)
        outline = (sec.get("outline") or [])[:5]
        excerpt = lessons_lib.section_excerpt(sec)
        st.html(
            f'<div class="lf-dprev"><div class="lf-eyebrow">{i + 1} / {len(sections)} · {pg.STATUS_ICON[status]}</div>'
            f'<h3 class="lf-dprev-title">{escape(sec["title"])}</h3>'
            + ("<ul>" + "".join(f"<li>{escape(t)}</li>" for t in outline) + "</ul>" if outline else "")
            + (f'<p class="lf-dprev-text">{escape(excerpt)}</p>' if excerpt else "")
            + "</div>"
        )
        if st.button("학습하기", key=f"lfdgo_{lid}", type="primary", use_container_width=True):
            go(lid, sel_id)


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

    # 날짜 고르기: "선택한 구간" 안내 + 날짜 토글(좁은 화면은 날짜 버튼)
    with st.container(key="lf_allpanel"):
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


def day_panel(d: date, lessons: list[dict], data: dict, stacked: bool = False) -> None:
    """그날 수업·내 기록 카드. stacked=True(좁은 칸, 월별 오른쪽)면 버튼을 제목 아래 한 줄 전체로 쌓는다."""
    n = sch.day_for_date(d)
    lesson = next((l for l in lessons if n and l["id"] == f"D{n}"), None)
    with st.container(border=True):
        head = f"D{n} · {sch.fmt_date(d)}" if n else sch.fmt_date(d)
        st.html(f'<div class="lf-eyebrow">{head}</div>')
        if n in sch.PROJECT_DAYS:
            c1, c2 = (st.container(), st.container()) if stacked else st.columns([3, 1])
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
        c1, c2 = (st.container(), st.container()) if stacked else st.columns([3, 1])
        c1.markdown(f"**{escape(lesson['title'])}**")
        c1.progress(pct / 100, text=f"{done}/{total} 구간 완료 · {pct}%")
        if data["prefs"]["mode"] == "advanced":
            day_overview(lesson, data)
        elif c2.button("학습하기", key=f"panel_open_{lesson['id']}", use_container_width=True):
            go(lesson["id"])
        if stacked:  # 월별 오른쪽 카드: 내 체크인 기록은 접었다 펼치는 토글로
            n_rec = sum(1 for c in data["checkins"] if c["lesson_id"] == lesson["id"]) +                 sum(1 for x in data["notes"] if x["lesson_id"] == lesson["id"])
            with st.expander(f"내 체크인 기록 {n_rec}개", expanded=False):
                records_list(data, lesson)
        else:
            st.markdown("**내 체크인 기록**")
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
    stuck = " (막힘)" if last and last["level"] == "stuck" else ""
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

    # 왼쪽: 구간 목록(네비게이터) + 학습 기록 / 오른쪽: 교육 노트
    side, main = st.columns([3, 7], gap="large")

    role = data["prefs"].get("role", "student")
    with side:
        if role == "admin":
            # 관리자: 구간별 진행 현황(수강생 인원 숫자, 누르면 그 구간으로 이동)
            progress_overview(data, lesson, sec_id, admin=True)
        else:
            # 수강생: 구간별 진행 현황 → 체크인 → D? 체크인 기록 → 조별 편성(참석/불참)
            progress_overview(data, lesson, sec_id)
            st.divider()
            checkin_form(data, lid, sec_id, pg.get_status(data, lid, sec_id))
            st.divider()
            day_notes(data, lesson, sec_id)
            st.divider()
            team_section(data, sch.date_for_day(int(lid[1:])) if lid[1:].isdigit() else None)

    with main:
        # 오른쪽 위: 이전/다음 구간 · Day 제목
        with st.container(key="lf_lessonhead"):
            # 한 줄: [수강생 | 관리자] 모드 (왼쪽) ············ [← 이전 구간] [다음 구간 →] (오른쪽)
            has_prev, has_next = idx > 0, idx < len(ids) - 1
            with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center",
                              key="lf_secnav"):
                picked_role = st.segmented_control(
                    "보기", options=["student", "admin"], format_func={"student": "수강생", "admin": "관리자"}.get,
                    default=role, key="role_select", label_visibility="collapsed",
                )
                with st.container(horizontal=True, gap="small", width="content", key="lf_secnav_btns"):
                    if has_prev and st.button("← 이전 구간", key="sec_prev", width="content"):
                        go(lid, ids[idx - 1])
                    if has_next and st.button("다음 구간 →", key="sec_next", width="content"):
                        go(lid, ids[idx + 1])
            if picked_role and picked_role != role:
                data["prefs"]["role"] = picked_role
                if persist():
                    st.rerun()
            # 구간 완료율 바·글자는 교육 모아보기 등 다른 화면에 있으므로 여기서는 보여주지 않는다
            st.markdown(f"**{lid} · {escape(lesson['title'])}**")
        st.divider()
        status = pg.get_status(data, lid, sec_id)
        st.html(
            f'<div class="lf-eyebrow">{lid} · 구간 {idx + 1}/{len(sections)}</div>'
            f'<h2 style="margin:4px 0 8px">{escape(sec["title"])}</h2>'
            f'<span class="lf-tag">{pg.STATUS_ICON[status]}</span>'
        )
        body = "".join(b.get("html") or "" for b in sec["blocks"])
        parts = lessons_lib.split_steps(body)
        if parts:
            # 체크 단계 목록이 있으면: 목록 위에 단계 탭(1. 창업, 2. 기획 …)을 두고 탭마다 그 단계만 보여준다
            pre, steps, post = parts
            if pre.strip():
                st.html(f'<div class="lf-content">{pre}</div>')
            with st.container(key="lf_steptabs"):
                # 탭에는 번호만 (단계 제목은 탭 안 내용 맨 위에 그대로 있다)
                for tab, (i, (_, step_html)) in zip(st.tabs([str(n + 1) for n in range(len(steps))]), enumerate(steps)):
                    with tab:
                        st.html(f'<div class="lf-content"><ol class="steps" start="{i + 1}">{step_html}</ol></div>')
            if post.strip():
                st.html(f'<div class="lf-content">{post}</div>')
        else:
            st.html(f'<div class="lf-content">{body}</div>')

        if role != "admin":  # 학습 기록 남기기는 수강생 모드에서만
            st.divider()
            note_form(data, lid, sec_id)


def progress_overview(data: dict, lesson: dict, current_sec: str, admin: bool = False) -> None:
    """구간별 진행 현황. 수강생: 내 상태·최근 체크인·기록 수. 관리자: 수강생 인원 숫자(진행 중·완료·막힘 / 총원)."""
    lid = lesson["id"]
    st.markdown("#### 구간별 진행 현황")
    if admin:
        students = [data]  # 지금은 이 컴퓨터의 기록 하나 (여러 수강생 집계는 추후 서버·이름 구분이 생기면)
        total = sum(1 for d_ in students if pg.lesson_started(d_, lid))
        st.caption(f"총 수강생 {total}명 · '학습하기'를 누른 수강생 기준 (지금은 이 컴퓨터의 기록만 세요)")
    rowbox = st.container(key="lf_prowlist")  # 카드 사이 간격을 좁게 (CSS)
    for i, sec in enumerate(lesson["sections"]):
        status = pg.get_status(data, lid, sec["id"])
        last = pg.latest_checkin(data, lid, sec["id"])
        n_rec = sum(1 for c in data["checkins"] if c["lesson_id"] == lid and c["section_id"] == sec["id"]) +             sum(1 for x in data["notes"] if x["lesson_id"] == lid and x["section_id"] == sec["id"])
        lv = ""
        if admin:
            c = pg.section_counts(students, lid, sec["id"])
            sub = f'진행 중 {c["doing"]} · 완료 {c["done"]} · 막힘 {c["stuck"]} / 총 {c["total"]}명'
            if c["stuck"]:
                lv = f'<span class="lf-tag warn">막힘 {c["stuck"]}</span>'
        else:
            sub = f'{pg.STATUS_ICON[status]} · 기록 {n_rec}개'
            if last:
                cls = " warn" if last["level"] == "stuck" else ""
                lv = f'<span class="lf-tag{cls}">{escape(pg.LEVEL_LABEL[last["level"]])}</span>'
        cur = " cur" if sec["id"] == current_sec else ""
        # 줄 전체를 누르면 그 구간 학습 페이지로 (투명 버튼을 줄 위에 겹친다)
        with rowbox, st.container(key=f"lfprow_{i}"):
            st.html(f'<div class="lf-prow{cur}"><span class="lf-flow-num">{i + 1}</span>'
                    f'<div class="lf-prow-body"><b>{escape(sec["title"])}</b>'
                    f'<span class="lf-muted" style="margin:0">{sub}</span></div>{lv}</div>')
            if st.button(f"{i + 1}. {sec['title']} 학습 페이지로", key=f"lfprowgo_{i}"):
                go(lid, sec["id"])


def checkin_form(data: dict, lid: str, sec_id: str, status: str) -> None:
    st.markdown("#### 잘 따라가고 있나요?")
    last = pg.latest_checkin(data, lid, sec_id)
    if last:
        st.caption(f"최근 체크인: {pg.LEVEL_LABEL[last['level']]} · {last['created_at'][5:16].replace('T', ' ')}")
    level = st.radio(
        "체크인", options=list(pg.LEVEL_LABEL), format_func=pg.LEVEL_LABEL.get,
        horizontal=True, index=None, key=f"lvl_{lid}_{sec_id}", label_visibility="collapsed",
    )
    st.caption("하는 중이면 '진행 중', 직접 따라 하지 않고 보기만 했으면 '관전', "
               "다 끝냈으면 잘 따라감 · 조금 헤맴 · 막힘 중에서 골라 주세요.")
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
    st.markdown(f"#### {lid} 체크인 기록")
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
        # 구간 이름(누르면 그 구간으로 이동)도 카드 안 맨 위에
        with st.container(border=True, key=f"lfdaysec_{lid}_{sec['id']}"):
            h1, h2 = st.columns([5, 1], vertical_alignment="center")
            if h1.button(f"{sec['title']}{here}", key=f"jump_{sec['id']}", type="tertiary"):
                go(lid, sec["id"])
            h2.html(f'<div class="lf-muted" style="margin:0;text-align:right">{len(sec_items)}개</div>')
            for kind, it in sec_items:
                record_row(kind, it)


# ---------- 조별 편성 (수업 화면) ----------
def team_section(data: dict, d: date | None) -> None:
    """그날 조별 편성 목록. 불참한 사람은 '불참' 표시. 편성·불참은 관리자 페이지(톱니바퀴)에서 바꾼다."""
    st.markdown("#### 조별 편성")
    rno = sch.round_for_date(d) if d else None
    if rno is None:
        periods = " · ".join(sch.round_label(no) for no, _, _ in sch.TEAM_ROUNDS)
        st.caption(f"이 날은 조 편성 기간이 아니에요. ({periods})")
        return
    teams = pg.teams_for_round(data, rno)
    st.caption(sch.round_label(rno))
    if not teams:
        st.caption(f"아직 {rno}차 조 편성이 없어요. 오른쪽 위 톱니바퀴(관리자)에서 조를 만들 수 있어요.")
        return
    absent = set(data.get("absences", {}).get(d.isoformat(), [])) if d else set()
    members_all = [m for t in teams for m in t["members"]]
    n_absent = sum(1 for m in members_all if m in absent)
    if d:
        st.caption(f"{sch.fmt_date(d)} 기준 · 참석 {len(members_all) - n_absent}명 · 불참 {n_absent}명 "
                   "· 이름 옆 버튼으로 참석/불참을 바꿀 수 있어요")

    def on_change(key: str, name: str) -> None:
        val = st.session_state.get(key)
        if val is None:  # 이미 고른 칸을 다시 눌러 선택이 풀리면 그대로 둔다
            return
        pg.set_attendance(data, d.isoformat(), name, present=(val == "present"))
        persist(f"{name} · {'참석' if val == 'present' else '불참'}으로 바꿨어요.")

    for t in teams:
        with st.container(border=True, key=f"lfteam_{t['id']}"):
            here = sum(1 for m in t["members"] if m not in absent)
            st.html(f'<div class="lf-team-name">{escape(t["name"])} '
                    f'<span class="lf-muted" style="margin:0;font-weight:400">참석 {here} · 불참 {len(t["members"]) - here}</span></div>')
            if not t["members"]:
                st.caption("조원 없음")
            for m in t["members"]:
                key = f"att_{d.isoformat()}_{t['id']}_{m}"
                want = "absent" if m in absent else "present"
                if st.session_state.get(key) != want:
                    st.session_state[key] = want  # 관리자 페이지 등에서 바뀐 값과 맞춘다
                with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="distribute",
                                  key=f"lfatt_{t['id']}_{m}"):
                    st.html(f'<span class="lf-member{" absent" if m in absent else ""}">{escape(m)}</span>', width="content")
                    st.segmented_control(
                        f"{m} 참석 여부", options=["present", "absent"], format_func={"present": "참석", "absent": "불참"}.get,
                        key=key, on_change=on_change, args=(key, m), label_visibility="collapsed",
                    )


# ---------- 관리자 (조 편성 · 불참 관리) ----------
def admin_page(lessons: list[dict], data: dict) -> None:
    st.html('<div class="lf-eyebrow">관리자</div><h1 style="margin:4px 0 4px">조 편성 · 불참 관리</h1>'
            '<p class="lf-muted" style="font-size:15px;line-height:22px">여기서 정한 조 편성과 불참 표시는 교육 모아보기의 수업 화면에 보여요.</p>')
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("#### 조 편성")
        with st.form("team_add", clear_on_submit=True, border=True):
            rnos = [no for no, _, _ in sch.TEAM_ROUNDS]
            round_no = st.segmented_control("차수", options=rnos, format_func=sch.round_label, default=rnos[0])
            name = st.text_input("조 이름", placeholder="예: 1조")
            members = st.text_input("조원", placeholder="쉼표로 구분 · 예: 홍길동, 김철수")
            if st.form_submit_button("조 추가하기", type="primary"):
                try:
                    pg.add_team(data, name, pg.parse_members(members), round_no or rnos[0])
                except ValueError as e:
                    st.warning(str(e))
                else:
                    if persist("조를 추가했어요."):
                        st.rerun()
        teams = data.get("teams", [])
        if not teams:
            st.caption("아직 만든 조가 없어요.")
        for no, _, _ in sch.TEAM_ROUNDS:
            r_teams = pg.teams_for_round(data, no)
            if r_teams:
                st.html(f'<div class="lf-rec-day"><b>{sch.round_label(no)}</b> <span class="lf-muted">{len(r_teams)}개 조</span></div>')
            for t in r_teams:
                team_admin_card(t, data)
        legacy = [t for t in teams if t.get("round") not in [no for no, _, _ in sch.TEAM_ROUNDS]]
        if legacy:
            st.html('<div class="lf-rec-day"><b>차수 없음</b> <span class="lf-muted">(차수를 정하기 전에 만든 조 · 다시 만들어 주세요)</span></div>')
        for t in legacy:
            team_admin_card(t, data)
    with right:
        st.markdown("#### 불참 관리")
        members = pg.all_members(data)
        if not members:
            st.caption("조를 먼저 만들면 날짜별로 불참자를 표시할 수 있어요.")
            return
        _absence_editor(data, members)


def team_admin_card(t: dict, data: dict) -> None:
    """관리자 페이지의 조 카드: 조 이름·인원·조원, 수정 · 확인 후 삭제."""
    with st.container(border=True):
        c1, c2 = st.columns([4, 1], vertical_alignment="center")
        c1.markdown(f"**{escape(t['name'])}** · {len(t['members'])}명")
        c1.caption(", ".join(t["members"]) or "조원 없음")
        with c2:
            if st.button("수정", key=f"edit_{t['id']}", type="tertiary"):
                team_edit_dialog(t["id"], data)
            if st.button("삭제", key=f"del_{t['id']}", type="tertiary"):
                confirm_delete("teams", t["id"], t["name"])


@st.dialog("조 편성 수정")
def team_edit_dialog(team_id: str, data: dict) -> None:
    team = next((x for x in data.get("teams", []) if x["id"] == team_id), None)
    if team is None:
        st.info("이미 삭제된 조예요.")
        return
    rnos = [no for no, _, _ in sch.TEAM_ROUNDS]
    cur_round = team.get("round") if team.get("round") in rnos else rnos[0]
    round_no = st.segmented_control("차수", options=rnos, format_func=sch.round_label, default=cur_round,
                                    key=f"te_round_{team_id}")
    name = st.text_input("조 이름", value=team["name"], key=f"te_name_{team_id}")
    members = st.text_area("조원", value=", ".join(team["members"]), key=f"te_members_{team_id}",
                           help="쉼표나 줄바꿈으로 구분해요")
    st.caption("조원 이름을 바꾸거나 빼도, 이미 저장된 날짜별 불참 표시는 그대로 남아요.")
    c1, c2 = st.columns(2)
    if c1.button("저장하기", type="primary", use_container_width=True, key=f"te_save_{team_id}"):
        try:
            pg.update_team(data, team_id, name, pg.parse_members(members), round_no or cur_round)
        except ValueError as e:
            st.warning(str(e))
            return
        if persist("조 편성을 수정했어요."):
            st.rerun()
    if c2.button("취소", use_container_width=True, key=f"te_cancel_{team_id}"):
        st.rerun()


def _absence_editor(data: dict, members_all: list[str]) -> None:
    """날짜를 고르면 그 날짜 차수의 조원만 불참자로 고를 수 있다."""
    days = [d for d in sch.camp_days() if sch.round_for_date(d)]
    default = st.session_state.get("sel_date", date.today())
    idx = days.index(default) if default in days else 0
    d = st.selectbox("날짜 (조 편성 기간만)", options=days, index=idx,
                     format_func=lambda x: f"{sch.fmt_date(x)} · {sch.round_for_date(x)}차"
                     + (f" · D{sch.day_for_date(x)}" if sch.day_for_date(x) else ""), key="admin_absent_day")
    members = pg.all_members(data, sch.round_for_date(d))
    if not members:
        st.caption(f"{sch.round_for_date(d)}차 조가 아직 없어요. 왼쪽에서 먼저 만들어 주세요.")
        return
    current = data.get("absences", {}).get(d.isoformat(), [])
    picked = st.multiselect("불참자", options=members, default=[m for m in current if m in members],
                            key=f"admin_absent_{d.isoformat()}", placeholder="불참하는 사람을 고르세요")
    if st.button("불참 저장", type="primary", key="admin_absent_save"):
        pg.set_absences(data, d.isoformat(), picked)
        if persist("불참 표시를 저장했어요."):
            st.rerun()


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
    elif qp.get("page") == "admin":
        gnb("admin")
        admin_page(lessons, data)
    else:
        gnb("home")
        home(lessons, data)


main()
