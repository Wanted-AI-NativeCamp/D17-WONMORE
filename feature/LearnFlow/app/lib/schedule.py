# -*- coding: utf-8 -*-
"""원티드 AI 네이티브 커리어 캠프 2기 일정 (schedule.png 기준) 과 Day 그룹.
Streamlit을 쓰지 않는 순수 데이터·함수만 둔다.
"""
from datetime import date, timedelta

CAMP_TITLE = "원티드 AI 네이티브 커리어 캠프 2기"
CAMP_PERIOD = "2026. 10. 6 화 – 2027. 1. 29 금 · AM 10 ~ PM 07"
CAMP_NOTE = "세부 커리큘럼은 운영 상황에 따라 일부 변경될 수 있음."

D1_DATE = date(2026, 10, 14)  # D1 = 10월 14일, 이후 수업일(평일, 휴일 제외)마다 Day가 1씩 늘어난다

HOLIDAYS = {
    date(2026, 10, 5): "대체휴일",
    date(2026, 10, 9): "한글날",
    date(2026, 12, 25): "성탄절",
    date(2026, 12, 31): "연말 휴강",
    date(2027, 1, 1): "신정",
}

# (시작, 끝, 태그, 제목, [(날짜, 이벤트)])  — 태그가 없으면 ""
UNITS = [
    (date(2026, 10, 6), date(2026, 10, 7), "", "OT · 입과", [(date(2026, 10, 6), "입과")]),
    (date(2026, 10, 8), date(2026, 10, 13), "", "직무별 AI 활용 가이드", []),
    (date(2026, 10, 14), date(2026, 10, 20), "AI 활용 기초", "설치부터 첫 대화까지", []),
    (date(2026, 10, 21), date(2026, 10, 27), "AI 활용 기초", "도구 선택과 안전한 활용", []),
    (date(2026, 10, 28), date(2026, 11, 3), "프롬프트 실전 활용", "반복 업무 프롬프트 설계",
     [(date(2026, 10, 28), "1차 프로젝트"), (date(2026, 11, 3), "1차 마감")]),
    (date(2026, 11, 4), date(2026, 11, 10), "프롬프트 실전 활용", "나만의 AI 업무 도구 제작", []),
    (date(2026, 11, 11), date(2026, 11, 17), "업무 환경에 AI 연동하기", "AI 워크스페이스 구축", []),
    (date(2026, 11, 18), date(2026, 11, 24), "업무 환경에 AI 연동하기", "외부 서비스·데이터 연동", []),
    (date(2026, 11, 25), date(2026, 11, 30), "데이터를 읽는 AI 활용법", "AI 데이터 분석·인사이트",
     [(date(2026, 11, 25), "2차 프로젝트")]),
    (date(2026, 12, 1), date(2026, 12, 1), "", "중간 점검 · 트랙 확정", [(date(2026, 12, 1), "2차 마감")]),
    (date(2026, 12, 2), date(2026, 12, 8), "포트폴리오 킥오프", "직군별 유형 브리핑", []),
    (date(2026, 12, 9), date(2026, 12, 14), "", "1:1 현직자 멘토링", []),
    (date(2026, 12, 15), date(2026, 12, 18), "포트폴리오 완성 스프린트", "실전 과제 선정·기획",
     [(date(2026, 12, 18), "3차 프로젝트")]),
    (date(2026, 12, 21), date(2026, 12, 30), "포트폴리오 완성 스프린트", "1차 스프린트 : 프로토타입",
     [(date(2026, 12, 24), "3차 마감")]),
    (date(2027, 1, 4), date(2027, 1, 4), "", "1차 결과 피드백", []),
    (date(2027, 1, 5), date(2027, 1, 14), "포트폴리오 완성 스프린트", "2차 스프린트 : 완성도",
     [(date(2027, 1, 5), "최종 프로젝트")]),
    (date(2027, 1, 15), date(2027, 1, 15), "", "최종 포트폴리오 발표회", [(date(2027, 1, 15), "최종 마감")]),
    (date(2027, 1, 18), date(2027, 1, 22), "포트폴리오 최종 리부트", "그룹별 데모데이",
     [(date(2027, 1, 22), "데모데이 심사")]),
    (date(2027, 1, 25), date(2027, 1, 26), "", "이력서 · 자소서", []),
    (date(2027, 1, 27), date(2027, 1, 27), "", "포트폴리오 최종 점검", []),
    (date(2027, 1, 28), date(2027, 1, 29), "", "모의 면접 · 기업 매칭", [(date(2027, 1, 29), "수료")]),
]

# Day 목록 그룹 (사용자 지정). 수업 자료가 없는 Day는 프로젝트 기간이다.
DAY_GROUPS = [
    ("AI 활용 기초", "Step 01. 설치부터 첫 대화까지", list(range(1, 6))),
    ("AI 활용 기초", "Step 02. 도구 선택과 안전한 활용", list(range(6, 11))),
    ("프롬프트 실전 활용", "Step 3. 반복 업무 프롬프트 설계", list(range(11, 16))),
    ("프롬프트 실전 활용", "Step 4. 나만의 AI 업무 도구 제작", [16, 17]),
]

# 프로젝트 기간(1차 프로젝트 10/28 ~ 1차 마감 11/3): 교육 진행 없음.
# Day별 개인 학습 기록만 남긴다 (section_id = PROJECT_SECTION)
PROJECT_DAYS = list(range(11, 16))
PROJECT_SECTION = "project"

WEEKDAY = "월화수목금토일"


def is_class_day(d: date) -> bool:
    return d.weekday() < 5 and d not in HOLIDAYS


def date_for_day(n: int) -> date:
    """Day 번호 → 날짜. D1 = 10/14."""
    if n < 1:
        raise ValueError("Day 번호는 1 이상이어야 합니다")
    d, count = D1_DATE, 1
    while count < n:
        d += timedelta(days=1)
        if is_class_day(d):
            count += 1
    return d


def day_for_date(d: date) -> int | None:
    """날짜 → Day 번호. D1 이전이거나 수업일이 아니면 None."""
    if d < D1_DATE or not is_class_day(d):
        return None
    n, cur = 1, D1_DATE
    while cur < d:
        cur += timedelta(days=1)
        if is_class_day(cur):
            n += 1
    return n


def unit_dates(unit) -> list[date]:
    """구간(일정 블록) 안의 수업일 목록."""
    start, end = unit[0], unit[1]
    out, d = [], start
    while d <= end:
        if is_class_day(d):
            out.append(d)
        d += timedelta(days=1)
    return out


def unit_label(unit) -> str:
    start, end, tag, title, _ = unit
    span = f"{start.month}/{start.day}" if start == end else f"{start.month}/{start.day}–{end.month}/{end.day}"
    return f"{span} {title}"


def unit_index_for(d: date) -> int | None:
    for i, u in enumerate(UNITS):
        if u[0] <= d <= u[1]:
            return i
    return None


def default_unit_index(d: date) -> int:
    """오늘 날짜로 처음 선택할 구간을 고른다.
    오늘이 속한 구간 → 없으면(주말·휴강 사이) 다음 구간 → 캠프가 끝났으면 마지막 구간."""
    for i, u in enumerate(UNITS):
        if d <= u[1]:
            return i
    return len(UNITS) - 1


CAL_MONTHS = [(2026, 10), (2026, 11), (2026, 12), (2027, 1)]  # 캘린더로 보여줄 달


def default_date(today: date) -> date:
    """처음 선택할 날짜: 오늘이 수업일이면 오늘, 아니면 기본 구간의 첫 수업일."""
    if unit_index_for(today) is not None and is_class_day(today):
        return today
    dates = unit_dates(UNITS[default_unit_index(today)])
    later = [d for d in dates if d >= today]
    return (later or dates)[0]


def clamp_month(y: int, m: int) -> tuple[int, int]:
    if (y, m) < CAL_MONTHS[0]:
        return CAL_MONTHS[0]
    if (y, m) > CAL_MONTHS[-1]:
        return CAL_MONTHS[-1]
    return (y, m)


def month_weeks(y: int, m: int) -> list[list[date | None]]:
    """그 달의 주 목록. 한 주는 월~금 5칸, 다른 달 날짜는 None."""
    first = date(y, m, 1)
    d = first - timedelta(days=first.weekday())  # 그 주 월요일
    weeks = []
    while d.month == m or d < first:
        week = [d + timedelta(days=i) for i in range(5)]
        week = [x if x.month == m else None for x in week]
        if any(week):
            weeks.append(week)
        d += timedelta(days=7)
    return weeks


def week_segments(week: list) -> list[tuple[str, int | None, list]]:
    """한 주(월~금 5칸)를 같은 구간끼리 합친 블록 목록으로 나눈다.
    블록 = (종류, 구간 번호, 날짜 목록). 종류: 'unit' | 'holiday' | 'off'(일정 없음) | 'empty'(다른 달)."""
    segs: list[tuple[str, int | None, list]] = []
    for d in week:
        if d is None:
            kind, ui = "empty", None
        elif d in HOLIDAYS:
            kind, ui = "holiday", None
        else:
            ui = unit_index_for(d)
            kind = "off" if ui is None else "unit"
        if segs and kind != "holiday" and segs[-1][0] == kind and segs[-1][1] == ui:
            segs[-1][2].append(d)
        else:
            segs.append((kind, ui, [d]))
    return segs


def unit_first_day_in_month(ui: int, y: int, m: int) -> date | None:
    """그 달 캘린더에서 이 구간이 처음 나오는 날 (월~금, 휴일 제외)."""
    start, end = UNITS[ui][0], UNITS[ui][1]
    d = max(start, date(y, m, 1))
    while d <= end and d.month == m:
        if d.weekday() < 5 and d not in HOLIDAYS:
            return d
        d += timedelta(days=1)
    return None


def units_in_month(y: int, m: int) -> list[int]:
    start = date(y, m, 1)
    end = (date(y + (m == 12), m % 12 + 1, 1)) - timedelta(days=1)
    return [i for i, u in enumerate(UNITS) if u[0] <= end and u[1] >= start]


def events_on(d: date) -> list[str]:
    return [e for u in UNITS for (ed, e) in u[4] if ed == d]


# 조 편성 차수: (차수, 시작일, 종료일)
TEAM_ROUNDS = [
    (1, date(2026, 10, 6), date(2026, 10, 27)),
    (2, date(2026, 11, 4), date(2026, 11, 24)),
]


def round_for_date(d: date) -> int | None:
    """그 날짜가 속한 조 편성 차수. 어느 차수에도 속하지 않으면 None."""
    for no, start, end in TEAM_ROUNDS:
        if start <= d <= end:
            return no
    return None


def round_label(no: int) -> str:
    _, start, end = next(r for r in TEAM_ROUNDS if r[0] == no)
    return f"{no}차 ({start.month}/{start.day} – {end.month}/{end.day})"


def camp_days() -> list[date]:
    """캠프 기간 안의 수업일 전체 (일별 캘린더의 ‹ › 이동 순서). 주말·휴강일은 빠진다."""
    return sorted({d for u in UNITS for d in unit_dates(u)})


def step_day(d: date, step: int) -> date | None:
    """d 기준 이전(-1)/다음(+1) 수업일. 캠프 범위를 벗어나면 None.
    d가 수업일이 아니어도(주말 등) 그 앞뒤의 가장 가까운 수업일을 돌려준다."""
    days = camp_days()
    if step < 0:
        before = [x for x in days if x < d]
        return before[-1] if before else None
    after = [x for x in days if x > d]
    return after[0] if after else None


def fmt_mmdd(d: date) -> str:
    return f"{d.month:02d}.{d.day:02d}"


def fmt_date(d: date) -> str:
    return f"{d.month}/{d.day} ({WEEKDAY[d.weekday()]})"
