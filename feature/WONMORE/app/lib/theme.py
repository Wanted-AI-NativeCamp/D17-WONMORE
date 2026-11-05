# -*- coding: utf-8 -*-
"""디자인 토큰과 CSS 주입 (colorsystem.md / WONMORE Designsystem.md). 커스텀 CSS는 이 파일에만 둔다."""
import streamlit as st

# 강조색은 보기 모드와 상관없이 하나: 원티드 Blue → Violet 그라데이션
#  --grad        #0066FF → #8364FF  장식·테두리·진행 막대
#  --grad-strong #0057D9 → #6541F2  흰 글자가 올라가는 CTA·배지 (양 끝 모두 흰 글자 대비 5.9:1 이상)
#  --grad-soft   #EBF3FF → #F3F0FF  선택 배경 (메인 배너와 같은 그라데이션, 불투명)
#  --accent        #4165FF 두 색의 중간값, 단색이 필요한 곳(포커스 링 등)
#  --accent-strong #3D4FE6 중간값의 진한 버전, 글자 (흰 배경 6.1:1, 연한 배경 5.4:1)
#  --accent-soft   #EEF0FF 연한 배경 단색
#  --accent-border #8364FF 강조 테두리(선택·hover·포커스)는 보라 하나
ACCENT_VARS = (
    "--grad:linear-gradient(120deg,#0066FF,#8364FF);"
    "--grad-strong:linear-gradient(120deg,#0057D9,#6541F2);"
    "--grad-soft:linear-gradient(120deg,#EBF3FF,#F3F0FF);"
    "--accent:#4165FF;--accent-strong:#3D4FE6;--accent-soft:#EEF0FF;"
    "--accent-border:#8364FF;"  # 강조 테두리는 원티드 Violet 하나만
)

BASE_CSS = """
:root{
  --font-sans: Pretendard, -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  --font-mono: ui-monospace, "SF Mono", Consolas, monospace;
  --bg:#FAFAFC; --surface:#FFFFFF; --surface-subtle:#F0F4F8;
  --text-strong:#14191E; --text-primary:#252832; --text-secondary:#5F6673; --border:#E6E8EF;
  --warning-accent:#FF5C00; --warning:#9A4A19; --warning-bg:#FFF1E6;
  --radius-card:20px; --radius-button:12px; --radius-tag:999px;
}
/* 글꼴은 .streamlit/config.toml(theme.font, fontFaces)에서 지정한다. 아이콘 글꼴을 덮어쓰지 않도록 여기서 font-family를 전역으로 바꾸지 않는다. */
.lf-hero, .lf-schedule, .lf-content, .lf-flow, .lf-secs, .lf-rec { font-family: var(--font-sans); }
.lf-content pre, .lf-content code { font-family: var(--font-mono); }
[data-testid="stAppViewContainer"]{ background: var(--bg); }
[data-testid="stMainBlockContainer"]{ max-width: 1200px; padding-top: 2rem; }
h1{ font-size:28px !important; line-height:38px !important; letter-spacing:-0.0236em; font-weight:700 !important; color:var(--text-strong); }
h2{ font-size:22px !important; line-height:30px !important; letter-spacing:-0.0194em; font-weight:700 !important; color:var(--text-strong); }
h3{ font-size:18px !important; line-height:26px !important; font-weight:600 !important; color:var(--text-strong); }
[data-testid="stVerticalBlockBorderWrapper"]{ border-radius: var(--radius-card) !important; background: var(--surface); }
.stButton button, .stFormSubmitButton button{ border-radius: var(--radius-button) !important; transition: background-color .2s ease-out, border-color .2s ease-out; }
/* 주요 버튼(primary)도 WONMORE 배너 버튼과 같은 흰색 버튼: 흰 바탕 + 회색 테두리 + 진한 글자, 호버는 보라 테두리 */
button[kind="primary"], button[kind="primaryFormSubmit"]{ background:#FFFFFF !important; border:1px solid var(--border) !important; color:var(--text-strong) !important; }
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover{ border-color:var(--accent-border) !important; }
button[kind="primary"] p, button[kind="primaryFormSubmit"] p{ color:var(--text-strong) !important; font-weight:600; }
[data-testid="stProgress"] > div > div > div > div{ background: var(--grad) !important; }
/* 선택 상태 공통: 메인 배너 그라데이션 배경 + 강조 그라데이션 테두리 */
.lf-grad-sel, button[kind="segmented_controlActive"], button[kind="pillsActive"]{
  background: var(--grad-soft) !important; border:1px solid var(--accent-border) !important; }
button[kind="segmented_controlActive"] p, button[kind="pillsActive"] p{ color:var(--accent-strong) !important; font-weight:600; }
.lf-eyebrow{ font-size:12px; line-height:16px; letter-spacing:.0252em; color:var(--text-secondary); font-weight:600; }
.lf-hero{ padding:32px; border-radius:var(--radius-card); border:1px solid var(--border);
  background: var(--grad-soft); }
.lf-hero p{ color:var(--text-primary); font-size:16px; line-height:26px; margin:8px 0 0; }
/* 홈 배너: 글 + 오른쪽 '교육 자료 추가하기' 버튼 */
.st-key-lf_hero{ padding:32px; border-radius:var(--radius-card); border:1px solid var(--border); gap:24px;
  background: linear-gradient(120deg, rgba(0,102,255,.08), rgba(131,100,255,.10)); flex-wrap:wrap; }
.st-key-lf_hero > div:first-child{ flex:1 1 360px; min-width:0; }
.st-key-lf_hero{ margin-bottom:40px; }  /* 배너와 아래 캠프 일정 사이 간격 */
.lf-hero-text{ font-family:var(--font-sans); }
button[kind="primary"]:disabled, button[kind="primaryFormSubmit"]:disabled{ opacity:.4; cursor:not-allowed; }
/* 배너 문구 3줄 간격을 좁히고, 마지막 줄 아래를 오른쪽 버튼 아래와 맞춘다 (컨테이너는 아래 정렬) */
.lf-hero-text .lf-eyebrow{ margin:0 0 12px; }  /* 아래 정렬이라 이 여백만큼 위로 올라간다 */
.lf-hero-text h1{ margin:2px 0 0 !important; padding:0 !important; }
.lf-hero-text p{ color:var(--text-primary); font-size:16px; line-height:24px; margin:4px 0 0; }
.st-key-open_upload button, .st-key-open_note button{ min-height:44px; padding:0 20px !important; white-space:nowrap;
  background:#FFFFFF !important; border:1px solid var(--border) !important; color:var(--text-strong) !important; }
.st-key-open_upload button:hover, .st-key-open_note button:hover{ border-color:var(--accent-border) !important; }
.st-key-open_upload button p, .st-key-open_note button p{ color:var(--text-strong) !important; font-weight:600; }
/* 메인 배너
   - 넓은 화면(1101px~): 문구는 버튼 때문에 줄바꿈되지 않게 한 줄 유지, 버튼은 오른쪽에 위아래 2개
   - 1100px 이하: 문구가 버튼에 밀려 꺾이기 전에 버튼을 문구 아래로 내리고, 가로 2개로 양 끝까지 꽉 채운다 */
.lf-hero-text h1, .lf-hero-text p{ white-space:nowrap; }
@media (max-width: 1100px){
  .lf-hero-text h1, .lf-hero-text p{ white-space:normal; }
  .st-key-lf_hero{ flex-direction:column !important; align-items:stretch !important; flex-wrap:nowrap !important; gap:20px !important; }
  .st-key-lf_hero > div:first-child{ flex:none !important; }
  /* 버튼 묶음을 감싸는 Streamlit 바깥 상자(220px 고정)도 줄 전체 너비로 */
  .st-key-lf_hero > :has(.st-key-lf_hero_actions), [data-testid="stLayoutWrapper"]:has(> .st-key-lf_hero_actions){
    flex:none !important; width:100% !important; max-width:100% !important; }
  .st-key-lf_hero_actions{ flex-direction:row !important; width:100% !important; max-width:100% !important; gap:8px !important; }
  .st-key-lf_hero_actions > *{ flex:1 1 0 !important; min-width:0 !important; width:auto !important; }
  .st-key-open_upload button, .st-key-open_note button{ width:100% !important; min-width:0; }
}
@media (max-width: 640px){
  .st-key-open_upload button, .st-key-open_note button{ padding:0 10px !important; }
  .st-key-open_upload button p, .st-key-open_note button p{ font-size:14px; white-space:normal !important; line-height:18px; }
}
.lf-tag{ display:inline-block; padding:2px 10px; border-radius:var(--radius-tag); font-size:12px; font-weight:600;
  background:var(--surface-subtle); color:var(--text-primary); }
.lf-tag.warn{ background:var(--warning-bg); color:var(--warning); }

/* 빠르게 둘러보기 흐름 (F13) */
.lf-flow{ list-style:none; padding:0; margin:8px 0 4px; display:flex; flex-wrap:wrap; gap:8px; }
.lf-flow-step{ display:flex; align-items:center; gap:8px; padding:6px 12px 6px 6px; border:1px solid var(--border);
  border-radius:var(--radius-tag); background:var(--surface); font-size:14px; line-height:20px; color:var(--text-primary); max-width:100%; }
.lf-flow-num{ flex:none; width:24px; height:24px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
  background:var(--surface-subtle); color:var(--text-primary); font-weight:700; font-size:12px; }

.lf-secs{ display:flex; flex-direction:column; gap:8px; margin-top:12px; }
.lf-sec{ border:1px solid var(--border); border-radius:var(--radius-button); background:var(--surface); padding:10px 14px; }
.lf-sec summary{ cursor:pointer; font-size:15px; line-height:22px; font-weight:600; color:var(--text-strong); }
.lf-sec[open] summary{ margin-bottom:6px; }
.lf-sec ul{ margin:4px 0 4px 20px; padding:0; font-size:15px; line-height:24px; color:var(--text-primary); }
.lf-muted{ margin:4px 0 0; font-size:12px; line-height:16px; color:var(--text-secondary); }

/* 상단 메뉴(GNB): 화면 맨 위에 붙어 있고, 흰 배경과 아래 선은 화면 가로 끝까지 이어진다 */
[data-testid="stHeader"]{ background:transparent; height:0; }
[data-testid="stMainBlockContainer"]{ padding-top:0 !important; }
/* Streamlit이 메뉴바를 같은 높이의 래퍼로 감싸므로, 고정(sticky)은 래퍼에 건다 */
[data-testid="stLayoutWrapper"]:has(> .st-key-lf_gnb){ position:sticky; top:0; z-index:999; margin-bottom:16px;
  background:var(--surface); box-shadow:0 0 0 100vmax var(--surface); clip-path:inset(0 -100vmax -1px -100vmax); }
[data-testid="stLayoutWrapper"]:has(> .st-key-lf_gnb)::after{ content:""; position:absolute; left:-100vmax; right:-100vmax; bottom:-1px; height:1px; background:var(--border); }
.st-key-lf_gnb{ min-height:64px; flex-wrap:nowrap; }
/* GNB: 로고 영역과 메뉴 영역을 나눈다. 로고는 오른쪽 여백을 두고 고정, 화면이 줄면 메뉴가 그만큼 밀린다(따로 바뀌는 규칙 없음) */
.st-key-lf_logo{ width:auto !important; flex:none !important; margin-right:32px; }
.lf-gnb-end{ display:none; }
.st-key-lf_logo{ position:relative; gap:0 !important; }
.lf-logo{ display:flex; align-items:center; gap:8px; font-size:20px; font-weight:800; letter-spacing:-0.02em; color:var(--text-strong); }
.st-key-gnb_logo{ position:absolute; inset:0; z-index:1; }
.st-key-gnb_logo .stButton, .st-key-gnb_logo button{ width:100%; height:100%; }
.st-key-gnb_logo button{ opacity:0; cursor:pointer; }
.st-key-lf_logo:has(button:focus-visible) .lf-logo{ outline:2px solid var(--accent-border); outline-offset:4px; border-radius:6px; }
/* 메뉴는 항상 한 줄. Streamlit이 메뉴를 한 겹 더 감싸므로 바깥 상자에도 같은 규칙을 준다
   (바깥 상자가 좁게 줄어들면 메뉴가 한 개씩 세로로 쌓였다) */
[data-testid="stLayoutWrapper"]:has(> .st-key-lf_nav){ flex:1 1 auto !important; width:auto !important; }
.st-key-lf_nav{ flex:1 1 auto; flex-wrap:nowrap !important; justify-content:flex-start !important; width:auto !important; }
.st-key-lf_nav > *{ flex:none !important; width:auto !important; }
/* 좁은 화면: 메뉴 버튼 사이 간격과 버튼 양옆 여백을 줄여 한 줄에 더 잘 들어가게 */
@media (max-width: 640px){
  .st-key-lf_nav{ gap:2px !important; }
  .st-key-lf_nav button{ padding:6px 8px !important; }
}
.st-key-lf_nav button{ padding:6px 14px !important; }
.st-key-lf_nav button p{ font-size:15px; font-weight:500; color:var(--text-primary); white-space:nowrap; }
.st-key-lf_nav button:hover p{ color:var(--text-strong); }
/* 현재 메뉴: 포인트 색 대신 굵기 + 살짝 둥근 라이트그레이 배경. 누를 때 Streamlit 기본 파란색도 막는다 */
.st-key-lf_nav button{ border-radius:8px !important; transition:background-color .2s ease-out; }
.st-key-lf_nav button:hover, .st-key-lf_nav button:focus, .st-key-lf_nav button:active,
.st-key-lf_nav button:focus:not(:active){ color:var(--text-strong) !important; background:transparent; border-color:transparent !important; }
.st-key-lf_nav button:hover{ background:var(--surface-subtle) !important; }
.st-key-lf_nav button:hover p, .st-key-lf_nav button:focus p, .st-key-lf_nav button:active p{ color:var(--text-strong) !important; }
.st-key-lf_nav button:focus-visible{ outline:2px solid var(--text-secondary); outline-offset:2px; }
[class*="st-key-gnbon_"] button{ background:var(--surface-subtle) !important; }
[class*="st-key-gnbon_"] button p{ font-weight:700; color:var(--text-strong) !important; }

/* 캠프 일정 */
.st-key-lf_cal{ padding:24px !important; border:1px solid var(--border) !important; border-radius:var(--radius-card) !important; background:var(--surface); }
.st-key-lf_cal [data-testid="stColumn"] [data-testid="stVerticalBlock"]{ gap:6px; }
.lf-month-head{ font-size:18px; font-weight:700; color:var(--text-strong); margin-bottom:2px; }
.lf-month-head span{ font-size:12px; font-weight:400; color:var(--text-secondary); }
.lf-unit{ padding:8px 10px; border-radius:var(--radius-button); background:var(--surface-subtle); font-size:13px; line-height:18px;
  border:2px solid transparent; transition: background-color .2s ease-out, border-color .2s ease-out; }
.lf-unit.sel{ background: var(--grad-soft); border:1px solid var(--accent-border); }
.lf-today{ display:inline-block; margin-left:6px; padding:0 6px; border-radius:var(--radius-tag); background:#6541F2; color:#fff; font-size:12px; line-height:16px; font-weight:600; }  /* [오늘] 태그는 어디서나 보라 단색 */
/* 구간 카드 위에 투명 버튼을 겹쳐서, 카드 전체를 눌러 구간을 고르게 한다 */
[class*="st-key-lfunit_"]{ position:relative; gap:0 !important; }
[class*="st-key-lfpick_"]{ position:absolute; inset:0; z-index:1; }
[class*="st-key-lfpick_"] .stButton, [class*="st-key-lfpick_"] button{ width:100%; height:100%; }
[class*="st-key-lfpick_"] button{ opacity:0; cursor:pointer; }
[class*="st-key-lfunit_"]:hover .lf-unit:not(.sel){ border-color:var(--border); }
[class*="st-key-lfunit_"]:has(button:focus-visible) .lf-unit{ outline:2px solid var(--accent-border); outline-offset:2px; }
.lf-unit-date{ display:block; font-size:12px; color:var(--text-secondary); font-weight:600; }
.lf-unit-tag{ display:block; font-size:12px; color:var(--text-secondary); }
.lf-unit-title{ font-weight:600; color:var(--text-strong); }
.lf-event{ display:inline-block; margin-left:6px; padding:0 8px; border-radius:var(--radius-tag); background:#14191E; color:#fff; font-size:12px; line-height:18px; }
.lf-group{ display:flex; align-items:center; gap:8px; margin:20px 0 8px; font-size:16px; color:var(--text-strong); }
.lf-rec-sec{ margin:12px 0 4px; font-size:14px; font-weight:600; color:var(--text-strong); }
.lf-rec{ padding:8px 12px; border:1px solid var(--border); border-radius:var(--radius-button); margin-bottom:6px; }
.lf-rec-text{ margin-top:4px; font-size:15px; line-height:22px; color:var(--text-primary); white-space:pre-wrap; }

/* 월별 캘린더 */
.lf-cal-title{ text-align:center; font-size:20px; font-weight:700; color:var(--text-strong); }
.lf-cal-title span{ font-size:12px; font-weight:400; color:var(--text-secondary); }
.lf-cal-head{ display:grid; grid-template-columns:repeat(5, 1fr); gap:8px; font-size:12px; color:var(--text-secondary); text-align:left; padding:0 4px; }
.lf-cell{ min-height:76px; padding:6px 8px; border-radius:var(--radius-button); border:1px solid transparent;
  display:flex; flex-direction:column; gap:2px; font-size:12px; line-height:16px; overflow:hidden; }
.lf-cell.empty{ background:transparent; }
.lf-cell.off{ background:transparent; border:1px dashed var(--border); color:var(--text-secondary); }
.lf-cell.in{ background:var(--surface-subtle); }
.lf-cell.unit-sel{ background: var(--grad-soft); border:1px solid var(--accent-border); }
.lf-cell.unit-sel .lf-cell-note{ color:var(--accent-strong); font-weight:600; }
.lf-cell.holiday{ background:repeating-linear-gradient(135deg, var(--surface-subtle) 0 6px, #fff 6px 12px); color:var(--text-secondary); }
.lf-cell.sel{ border-color:var(--accent-strong); box-shadow:inset 0 0 0 1px var(--accent-strong); }
.lf-cell-day{ font-size:14px; font-weight:700; color:var(--text-strong); }
.lf-cell-dn{ font-size:12px; font-weight:600; color:var(--accent-strong); }
.lf-cell-note{ font-size:12px; color:var(--text-primary); display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.lf-cell .lf-event, .lf-cell .lf-today{ margin-left:0; align-self:flex-start; }
[class*="st-key-lfcell_"]{ position:relative; gap:0 !important; }
[class*="st-key-lfday_"]{ position:absolute; inset:0; z-index:1; }
[class*="st-key-lfday_"] .stButton, [class*="st-key-lfday_"] button{ width:100%; height:100%; }
[class*="st-key-lfday_"] button{ opacity:0; cursor:pointer; }
[class*="st-key-lfcell_"]:hover .lf-cell.in{ border-color:var(--accent-border); }
[class*="st-key-lfcell_"]:has(button:focus-visible) .lf-cell{ outline:2px solid var(--accent-border); outline-offset:2px; }
.lf-list-unit{ margin:12px 0 4px; display:flex; flex-wrap:wrap; align-items:center; gap:6px; font-size:14px; color:var(--text-strong); }
.lf-list-unit .lf-unit-date{ display:inline; }
.st-key-lf_daylist button{ justify-content:flex-start; text-align:left; }
.st-key-lf_daylist button p{ text-align:left; }

/* 월별 캘린더: 구간별로 합친 블록 */
.lf-blk{ min-height:84px; padding:8px 10px; border-radius:var(--radius-button); border:1px solid transparent;
  display:flex; flex-direction:column; justify-content:space-between; gap:6px; font-size:12px; line-height:16px; height:100%; }
.lf-blk.empty{ background:transparent; }
.lf-blk.off{ border:1px dashed var(--border); color:var(--text-secondary); }
.lf-blk.holiday{ background:repeating-linear-gradient(135deg, var(--surface-subtle) 0 6px, #fff 6px 12px); color:var(--text-secondary); }
.lf-blk.in{ background:var(--surface-subtle); }
.lf-blk.in.sel{ background: var(--grad-soft); border:1px solid var(--accent-border); }
.lf-blk-days{ display:flex; }
.lf-blk-day{ flex:1; font-size:14px; font-weight:700; color:var(--text-strong); display:flex; align-items:center; gap:4px; }
.lf-blk.off .lf-blk-day, .lf-blk.holiday .lf-blk-day{ color:var(--text-secondary); font-weight:600; }
.lf-blk-body{ display:flex; flex-direction:column; align-items:flex-start; gap:2px; }
.lf-blk-tag{ font-size:12px; color:var(--text-secondary); }
.lf-blk-title{ font-size:13px; font-weight:700; color:var(--text-strong); }
.lf-blk.sel .lf-blk-title{ color:var(--accent-strong); }
.lf-blk .lf-event, .lf-blk .lf-today{ margin-left:0; }
[class*="st-key-lfcell_"]:hover .lf-blk.in:not(.sel){ border-color:var(--accent-border); }
[class*="st-key-lfcell_"]:has(button:focus-visible) .lf-blk{ outline:2px solid var(--accent-border); outline-offset:2px; }

/* 월별 캘린더 반응형: 767px 이하에서는 블록 캘린더 대신 그 달 구간 카드 목록 */
[class*="st-key-lfmunit_"]{ position:relative; gap:0 !important; }
[class*="st-key-lfmpick_"]{ position:absolute; inset:0; z-index:1; }
[class*="st-key-lfmpick_"] .stButton, [class*="st-key-lfmpick_"] button{ width:100%; height:100%; }
[class*="st-key-lfmpick_"] button{ opacity:0; cursor:pointer; }
[class*="st-key-lfmunit_"]:has(button:focus-visible) .lf-unit{ outline:2px solid var(--accent-border); outline-offset:2px; }
.st-key-lf_callist{ display:none !important; }
@media (max-width: 767px){
  .st-key-lf_calgrid{ display:none !important; }
  .st-key-lf_callist{ display:flex !important; gap:6px; }
}

/* 월별 캘린더 ‹ › : 고정 크기 정사각형, 살짝 둥근 모서리 */
.st-key-cal_prev button, .st-key-cal_next button{ width:36px !important; height:36px !important; min-height:36px !important;
  min-width:36px !important; padding:0 !important; border-radius:8px !important; font-size:20px; line-height:1;
  display:inline-flex; align-items:center; justify-content:center; flex:none; }
.st-key-cal_prev button p, .st-key-cal_next button p{ margin:0; font-size:20px; line-height:1; }
.st-key-lf_calnav .lf-cal-title{ white-space:nowrap; }

/* 캠프 일정 제목·보기 전환 버튼 줄: 좌우 여백 10px */
.st-key-lf_schedhead{ padding:0 10px; }

/* 일별 캘린더: ‹ mm.dd › + 그날의 학습 목록 */
.st-key-lf_daily{ padding:24px !important; border:1px solid var(--border) !important; border-radius:var(--radius-card) !important;
  background:var(--surface); gap:12px; }
.lf-day-title{ display:flex; flex-direction:column; align-items:center; font-size:32px; line-height:40px; font-weight:700;
  color:var(--text-strong); letter-spacing:-0.02em; min-width:120px; text-align:center; }
.lf-day-sub{ display:inline-flex; align-items:center; gap:6px; white-space:nowrap;
  font-size:14px; line-height:20px; font-weight:500; color:var(--text-secondary); letter-spacing:0; }
.lf-day-sub .lf-today{ margin-left:0; }
.st-key-day_prev button, .st-key-day_next button{ width:40px !important; height:40px !important; min-height:40px !important;
  min-width:40px !important; padding:0 !important; border-radius:8px !important; flex:none; }
.st-key-day_prev button p, .st-key-day_next button p{ margin:0; font-size:22px; line-height:1; }
.lf-daylist-head{ margin-top:8px; font-size:16px; font-weight:700; color:var(--text-strong); }
.st-key-lf_daily [data-testid="stColumn"] [data-testid="stVerticalBlock"]{ gap:8px; }
.lf-dsec{ display:flex; gap:10px; align-items:flex-start; min-height:88px; padding:12px; border-radius:var(--radius-button);
  background:var(--surface-subtle); border:2px solid transparent; transition: border-color .2s ease-out; }
.lf-dsec.done{ background:var(--accent-soft); }
.lf-dsec-body{ display:flex; flex-direction:column; align-items:flex-start; gap:4px; font-size:14px; line-height:20px; color:var(--text-strong); }
[class*="st-key-lfdsec_"]{ position:relative; gap:0 !important; }
[class*="st-key-lfdopen_"]{ position:absolute; inset:0; z-index:1; }
[class*="st-key-lfdopen_"] .stButton, [class*="st-key-lfdopen_"] button{ width:100%; height:100%; }
[class*="st-key-lfdopen_"] button{ opacity:0; cursor:pointer; }
[class*="st-key-lfdsec_"]:hover .lf-dsec{ border-color:var(--accent-border); }
[class*="st-key-lfdsec_"]:has(button:focus-visible) .lf-dsec{ outline:2px solid var(--accent-border); outline-offset:2px; }

/* 지나간 날: 연한 회색 글자 + 연한 바탕 (사용자 요청으로 보조 정보 취급, 대비 약 2.6:1) */
:root{ --past-text:#767D88; --past-bg:#F8F9FB; }
.lf-blk-day.past{ color:var(--past-text); font-weight:600; }
.lf-blk.past{ background:var(--past-bg); }
.lf-blk.past .lf-blk-title, .lf-blk.past .lf-blk-tag, .lf-blk.past .lf-cell-dn{ color:var(--past-text); }
.lf-unit.past{ background:var(--past-bg); }
.lf-unit.sel.past{ background: var(--grad-soft); border:1px solid var(--accent-border); }  /* 선택된 구간은 지나갔어도 선택 색 유지 */
.lf-unit.past .lf-unit-title, .lf-unit.past .lf-unit-date, .lf-unit.past .lf-unit-tag{ color:var(--past-text); }
[class*="st-key-lfpast_"] button:not([kind="primary"]){ background:var(--past-bg); }
[class*="st-key-lfpast_"] button:not([kind="primary"]) p{ color:var(--past-text); }
/* 지나간 이벤트 태그(입과, 1차 프로젝트 등)는 연한 색, 휴무일 글자는 언제나 지나간 날 색 */
.lf-event.past{ background:#E9ECF1; color:var(--past-text); }
.lf-blk.holiday, .lf-blk.holiday .lf-blk-day, .lf-blk.holiday .lf-blk-title{ color:var(--past-text) !important; }

/* 포인트 색 줄이기: 포인트 색은 주요 버튼·진행률·'오늘'·선택된 하나에만 쓴다.
   마우스 올림·키보드 포커스·D번호·완료 카드는 회색 계열로 (위 규칙들을 덮어쓴다) */
:root{ --border-strong:#C9CED8; --focus:#5F6673; }
[class*="st-key-lfunit_"]:hover .lf-unit:not(.sel), [class*="st-key-lfcell_"]:hover .lf-cell.in,
[class*="st-key-lfcell_"]:hover .lf-blk.in:not(.sel), [class*="st-key-lfdsec_"]:hover .lf-dsec{ border-color:var(--border-strong); }
[class*="st-key-lfunit_"]:has(button:focus-visible) .lf-unit, [class*="st-key-lfmunit_"]:has(button:focus-visible) .lf-unit,
[class*="st-key-lfcell_"]:has(button:focus-visible) .lf-cell, [class*="st-key-lfcell_"]:has(button:focus-visible) .lf-blk,
[class*="st-key-lfdsec_"]:has(button:focus-visible) .lf-dsec, .st-key-lf_logo:has(button:focus-visible) .lf-logo{ outline-color:var(--focus); }
.lf-cell-dn{ color:var(--text-secondary); }
.lf-blk.sel .lf-blk-title{ color:var(--text-strong); }
.lf-dsec.done{ background:var(--surface-subtle); }
.lf-dsec.done .lf-dsec-body b{ color:var(--text-secondary); }
.lf-content a{ color:var(--text-strong); text-decoration:underline; }
/* 구간 안 날짜 목록: 선택한 날은 진한 파란 버튼 대신 회색 바탕 + 진한 테두리 */
.st-key-lf_daylist button[kind="primary"]{ background:var(--surface-subtle) !important; border:1.5px solid var(--text-strong) !important; }
.st-key-lf_daylist button[kind="primary"] p{ color:var(--text-strong) !important; font-weight:700; }

/* 보기 전환 스위치 (월별 캘린더 / 일별 / 전체 일정, 구간 날짜 선택):
   회색 트랙 안에서 선택된 칸만 흰 알약 모양으로 떠 있다. 포인트 색은 쓰지 않는다 */
.st-key-cal_view [role="radiogroup"], [class*="st-key-date_pick_"] [role="radiogroup"]{
  display:inline-flex; flex-wrap:wrap; gap:2px; padding:3px; border-radius:var(--radius-tag); background:#EEF0F3; }
.st-key-cal_view button[role="radio"], [class*="st-key-date_pick_"] button[role="radio"]{
  border:none !important; border-radius:var(--radius-tag) !important; background:transparent !important;
  min-height:32px; padding:4px 16px !important; box-shadow:none; transition:background-color .2s ease-out, box-shadow .2s ease-out; }
.st-key-cal_view button[role="radio"] p, [class*="st-key-date_pick_"] button[role="radio"] p{
  color:var(--text-secondary) !important; font-size:14px; font-weight:500; white-space:nowrap; }
.st-key-cal_view button[role="radio"]:hover p, [class*="st-key-date_pick_"] button[role="radio"]:hover p{ color:var(--text-strong) !important; }
.st-key-cal_view button[aria-checked="true"], [class*="st-key-date_pick_"] button[aria-checked="true"]{
  background:var(--surface) !important; box-shadow:0 1px 3px rgba(20,25,30,.12); }
.st-key-cal_view button[aria-checked="true"] p, [class*="st-key-date_pick_"] button[aria-checked="true"] p{
  color:var(--text-strong) !important; font-weight:600; }
.st-key-cal_view button[role="radio"]:focus-visible, [class*="st-key-date_pick_"] button[role="radio"]:focus-visible{
  outline:2px solid var(--focus); outline-offset:1px; }

/* "수업 열기" 버튼: 흰 바탕 + 회색 테두리 (배너 버튼과 같은 보조 버튼 모양) */
[class*="st-key-panel_open_"] button, [class*="st-key-rec_open_"] button{ background:#FFFFFF !important;
  border:1px solid var(--border) !important; }
[class*="st-key-panel_open_"] button p, [class*="st-key-rec_open_"] button p{ color:var(--text-strong) !important; font-weight:600; }
[class*="st-key-panel_open_"] button:hover, [class*="st-key-rec_open_"] button:hover{ background:var(--surface-subtle) !important; }

/* 오늘로 돌아가기 버튼: ‹ › 옆, 같은 높이의 작은 보조 버튼 */
.st-key-cal_today button, .st-key-day_today button{ height:36px !important; min-height:36px !important; padding:0 12px !important;
  border-radius:8px !important; background:#FFFFFF !important; border:1px solid var(--border) !important; }
.st-key-day_today button{ height:40px !important; min-height:40px !important; }
.st-key-cal_today button p, .st-key-day_today button p{ font-size:13px; font-weight:600; color:var(--text-strong) !important; white-space:nowrap; }
.st-key-cal_today button, .st-key-day_today button{ gap:4px; }
.st-key-cal_today [data-testid="stIconMaterial"], .st-key-day_today [data-testid="stIconMaterial"]{ font-size:16px; color:var(--text-strong); }
.st-key-cal_today button:disabled [data-testid="stIconMaterial"], .st-key-day_today button:disabled [data-testid="stIconMaterial"]{ color:var(--past-text); }
.st-key-cal_today button:disabled p, .st-key-day_today button:disabled p{ color:var(--past-text) !important; }

/* 월별 캘린더: 한 주(한 줄) 안의 블록 높이를 그 줄에서 가장 높은 블록에 맞춘다 */
.st-key-lf_calgrid [data-testid="stHorizontalBlock"]{ align-items:stretch !important; }
.st-key-lf_calgrid [data-testid="stColumn"]{ display:flex; flex-direction:column; }
/* 칸(stColumn)부터 .lf-blk까지 사이의 모든 감싸는 요소가 남은 높이를 채우도록 */
.st-key-lf_calgrid [data-testid="stColumn"] :is(div):has(.lf-blk){ flex:1 1 auto; height:100%; display:flex; flex-direction:column; }
.st-key-lf_calgrid .lf-blk{ flex:1 1 auto; height:auto; }

/* 그 밖의 segmented control(보기 모드, 기록 유형 등): 흰 바탕 + 회색 테두리, 호버하면 보라 테두리 */
button[kind="segmented_control"]{ background:#FFFFFF !important; border:1px solid var(--border) !important; }
button[kind="segmented_control"] p{ color:var(--text-primary); }
button[kind="segmented_control"]:hover{ border-color:var(--accent-border) !important; }
button[kind="segmented_control"]:hover p{ color:var(--accent-strong) !important; }

/* 월별 보기 날짜 버튼: 전체 일정의 날짜 스위치(date_pick_)와 똑같이 보이게 한다.
   회색 트랙 안에 테두리 없는 알약 버튼, 선택한 날만 흰 알약 + 옅은 그림자, 호버는 글자만 진하게 */
/* 간격은 이전 규격 유지: 영역 안쪽 여백 8px, 버튼 사이 8px, 버튼 4px 16px · 높이 36px.
   영역은 가장 긴 줄(3개) 너비에 맞춰 줄어든다 */
.st-key-lf_datebtns{ width:fit-content !important; max-width:100%; gap:8px !important; padding:8px;
  border-radius:12px; background:#EEF0F3; }
/* 줄 나눔은 아래 "선택한 구간" 격자 규칙(3칸, 좁은 화면 2칸)이 맡는다 */
.st-key-lf_datebtns button{ border:none !important; border-radius:var(--radius-tag) !important; background:transparent !important;
  min-height:36px; padding:4px 16px !important; box-shadow:none; transition:background-color .2s ease-out, box-shadow .2s ease-out;
  justify-content:center !important; text-align:center; }  /* 좌우 여백 16px(이전 14px에서 양옆 2px씩 넓힘) */
/* 글자 가운데 정렬: 버튼 안 감싸는 요소들도 가운데로 모은다 */
.st-key-lf_datebtns button > div, .st-key-lf_datebtns button [data-testid="stMarkdownContainer"]{
  display:flex; justify-content:center; width:100%; margin:0 auto; }
.st-key-lf_datebtns button p{ color:var(--text-secondary) !important; font-size:14px; font-weight:500; white-space:nowrap;
  text-align:center; margin:0; }
.st-key-lf_datebtns button:hover p{ color:var(--text-strong) !important; }
.st-key-lf_datebtns button:focus-visible{ outline:2px solid var(--focus); outline-offset:1px; }
[class*="st-key-lfdsel_"] button{ background:var(--surface) !important; box-shadow:0 1px 3px rgba(20,25,30,.12); }
[class*="st-key-lfdsel_"] button p{ color:var(--text-strong) !important; font-weight:600; }
/* 지나간 날짜는 글자만 연한 회색 (호버하면 진한 글자) */
[class*="st-key-lfdpast_"] button:not(:hover) p{ color:var(--past-text) !important; }

/* 월별 보기 "선택한 구간": 오른쪽 정렬 + 날짜 버튼 3칸 격자(모든 칸 = 가장 넓은 버튼 폭) */
.st-key-lf_monthpanel .lf-eyebrow, .st-key-lf_monthpanel .lf-muted{ text-align:right; }
.st-key-lf_monthpanel .lf-list-unit{ justify-content:flex-end; }
[data-testid="stLayoutWrapper"]:has(> .st-key-lf_datebtns){ width:100% !important; align-self:stretch !important; }  /* 바깥 상자도 꽉 채움 */
.st-key-lf_datebtns{ display:grid !important; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:8px; width:100% !important; max-width:100%; margin-left:0; box-sizing:border-box; }  /* 한 줄에 2개, 아래 카드와 같은 너비로 꽉 채움 */
.st-key-lf_datebtns > *{ width:100% !important; min-width:0; }
.st-key-lf_datebtns .stButton, .st-key-lf_datebtns button{ width:100% !important; }
@media (max-width: 767px){ .st-key-lf_datebtns{ grid-template-columns:repeat(3, 1fr); } }  /* 좁은 화면은 캘린더 아래로 내려가 폭이 넓어지므로 3개 */

/* 선택한 구간: 2차 프로젝트 같은 이벤트 태그는 기간(날짜) 왼쪽 */
.lf-unit-when{ display:flex; flex-wrap:wrap; align-items:center; gap:6px; }
.lf-unit-when .lf-event{ margin:0; }
.st-key-lf_monthpanel .lf-unit-when{ justify-content:flex-end; }

/* 일별 보기: [태그] 아래 대주제(h1) */
.lf-daily-unit{ text-align:center; margin-top:8px; }
.lf-daily-unit .lf-list-unit{ margin:0; }
.lf-daily-topic{ margin:6px 0 0 !important; padding:0 !important; text-align:center;
  font-size:28px !important; line-height:38px !important; letter-spacing:-0.0236em; font-weight:700 !important; }

/* 일별 보기: ‹ mm.dd › 를 대주제와 같은 가운데 기준에 두고, [오늘] 버튼은 그 오른쪽 바깥에 */
.st-key-lf_daycore{ position:relative; overflow:visible; }
.st-key-day_today, .st-key-day_today button, .st-key-cal_today, .st-key-cal_today button{ flex:none; white-space:nowrap; }
.st-key-lf_daycore .st-key-day_today{ position:absolute; left:100%; top:50%; transform:translateY(-50%);
  margin-left:12px; width:max-content; }

/* 일별 보기 반응형: 좁아져도 페이지 가로 스크롤이 생기지 않게 */
.st-key-lf_daily{ max-width:100%; min-width:0; overflow-x:clip; }
.st-key-lf_daily *{ min-width:0; }
.lf-daily-topic{ overflow-wrap:anywhere; word-break:keep-all; }
.st-key-lf_daily .lf-list-unit{ flex-wrap:wrap; justify-content:center; }
.lf-dsec-body{ overflow-wrap:anywhere; }
@media (max-width: 640px){
  /* [오늘] 버튼: 좁을 때는 › 바로 옆 같은 줄에. 버튼이 눌려서 글자가 두 줄로 깨지지 않게 줄어들지 않도록 고정 */
  .st-key-lf_daynav, .st-key-lf_daycore{ flex-wrap:nowrap !important; gap:8px !important; }
  .st-key-lf_daycore .st-key-day_today{ position:static; transform:none; margin-left:0; width:max-content; flex:none; }
  .st-key-lf_daycore .st-key-day_today button{ width:max-content !important; white-space:nowrap; padding:0 10px !important; }
  .lf-day-title{ min-width:0; }
  .lf-daily-topic{ font-size:22px !important; line-height:30px !important; }
}

/* 일별 보기 학습 목록 카드: 넓은 화면(1101px~) 3열, 중간(641~1100px) 2열, 좁은 화면(~640px) 1열 */
.st-key-lf_dseclist{ display:grid !important; grid-template-columns:minmax(0, 1fr); gap:8px; }  /* 학습 목록: 한 줄에 하나 */
.st-key-lf_dseclist > *{ min-width:0; width:100% !important; }
/* 여백 줄어드는 시점 통일: 학습 목록이 2열이 되는 1100px에서 일별·월별·전체 일정·배너의 안쪽 여백을 함께 줄인다
   (3열 카드는 1100px 아래에서 한 칸이 300px 안팎으로 좁아져 답답해지므로 이때 2열로 바꾼다) */
/* 화면 양옆 여백(Streamlit 본문 컨테이너)도 직접 정해서 2열이 되는 시점에 함께 줄인다
   (Streamlit 기본값은 자기 기준 시점에 갑자기 바뀌어 어색했다) */
[data-testid="stMainBlockContainer"]{ padding-left:80px !important; padding-right:80px !important; }
@media (max-width: 1100px){
  [data-testid="stMainBlockContainer"]{ padding-left:32px !important; padding-right:32px !important; }
  .st-key-lf_daily, .st-key-lf_cal{ padding:16px !important; }
  .st-key-lf_hero{ padding:24px; }
}
@media (max-width: 640px){
  [data-testid="stMainBlockContainer"]{ padding-left:16px !important; padding-right:16px !important; } }

/* 좁은 화면: 일별(11/5)·월별(11월)·전체 일정(10월~1월) 날짜 제목 크기를 월별 기준(20px)으로 통일 */
@media (max-width: 640px){
  .lf-day-title, .lf-cal-title, .lf-month-head{ font-size:20px !important; line-height:28px !important; }
}

/* 위쪽 애매한 여백 제거: CSS·스크립트만 들어 있는 st.html 칸은 화면에 보이는 내용이 없으므로 자리를 차지하지 않게 */
[data-testid="stElementContainer"]:has(> [data-testid="stHtml"] > script:only-child),
[data-testid="stElementContainer"]:has(> [data-testid="stHtml"] > style:only-child){ display:none !important; }

/* 일별·월별·전체 일정 스위치: 제목 아래 둘째 줄로 내려오면(Streamlit 칸이 세로로 쌓이는 640px 이하) 양옆을 꽉 채운다 */
@media (max-width: 640px){
  .st-key-lf_viewtoggle{ justify-content:stretch !important; width:100% !important; }
  .st-key-lf_viewtoggle > *, .st-key-lf_viewtoggle [data-testid="stButtonGroup"]{ flex:1 1 100% !important; width:100% !important; max-width:100% !important; }
  .st-key-lf_viewtoggle [data-testid="stButtonGroup"] div:has(> button){ display:flex !important; width:100% !important; }
  .st-key-lf_viewtoggle [data-testid="stButtonGroup"] button{ flex:1 1 0 !important; min-width:0; }
}


/* 캘린더 흰 카드(일별·월별·전체 일정): 반투명 흰 바탕 + 블러 */
.st-key-lf_cal, .st-key-lf_daily{ background:rgba(255,255,255,.72) !important;
  -webkit-backdrop-filter:blur(12px); backdrop-filter:blur(12px); }

/* 월별: 선택한 구간 요약을 좁은 화면에서는 ‹ n월 › 아래(캘린더 카드 안)에 보여주고,
   오른쪽 패널의 같은 안내 문구는 숨긴다(날짜 버튼은 그대로) */
.lf-month-unit{ display:none; text-align:center; }
.lf-month-unit .lf-list-unit{ margin:0; }
.lf-month-unit-title{ margin:6px 0 2px; font-size:20px; line-height:28px; font-weight:700; color:var(--text-strong); overflow-wrap:anywhere; }
.lf-month-unit .lf-muted{ margin:0; font-size:14px; line-height:20px; }
@media (max-width: 767px){
  .lf-month-unit{ display:block; }
  .st-key-lf_monthpanel [data-testid="stElementContainer"]:has(.lf-unit-when){ display:none !important; }
}

/* 일별 학습 목록 + 미리보기
   - 넓은 화면 2:1, 1100px 이하 1:1, 640px 이하는 위아래로 쌓이고 목록 카드 대신 숫자 버튼만 */
.lf-dsec{ min-height:0 !important; }
.lf-dsec.sel{ background:var(--grad-soft) !important; border-color:var(--accent-border) !important; }
.st-key-lf_dnums{ display:none !important; }
/* 숨긴 숫자 버튼 줄의 바깥 상자도 숨겨 빈 간격(8px)이 생기지 않게 (좁은 화면에서는 아래에서 다시 보인다) */
[data-testid="stLayoutWrapper"]:has(> .st-key-lf_dnums){ display:none !important; }
.st-key-lf_dpreview{ background:var(--surface-subtle); border-radius:var(--radius-card); padding:16px !important; gap:12px; }
.lf-dprev-title{ margin:4px 0 8px !important; padding:0 !important; font-size:18px !important; line-height:26px !important; overflow-wrap:anywhere; }
.lf-dprev ul{ margin:0 0 8px 18px; padding:0; font-size:14px; line-height:22px; color:var(--text-primary); }
.lf-dprev-text{ margin:0; font-size:14px; line-height:22px; color:var(--text-secondary); overflow-wrap:anywhere; }
@media (max-width: 1100px){
  .st-key-lf_dsplit [data-testid="stColumn"]{ flex:1 1 0% !important; width:auto !important; min-width:0 !important; }
}
@media (max-width: 640px){
  /* 1:1 규칙을 풀고 위아래로 쌓는다 (목록 숫자 → 그 아래 미리보기) */
  .st-key-lf_dsplit [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]){ flex-direction:column !important; }  /* 칸 상자에만 (숫자 버튼 줄 제외) */
  .st-key-lf_dsplit [data-testid="stColumn"]{ flex:1 1 100% !important; width:100% !important; }
  .st-key-lf_dseclist{ display:none !important; }
  .st-key-lf_dnums{ display:flex !important; flex-direction:row !important; flex-wrap:wrap !important; gap:6px !important; }
  [data-testid="stLayoutWrapper"]:has(> .st-key-lf_dnums){ display:flex !important; }
  .st-key-lf_dnums > *{ width:auto !important; flex:none !important; }
  .st-key-lf_dnums button{ width:40px !important; height:40px !important; min-height:40px !important; padding:0 !important;
    border-radius:999px !important; background:#FFFFFF !important; border:1px solid var(--border) !important; }
  [class*="st-key-lfdnumsel_"] button{ background:var(--grad-soft) !important; border-color:var(--accent-border) !important; }
  [class*="st-key-lfdnumsel_"] button p{ color:var(--accent-strong) !important; font-weight:700; }
}

/* 일별: 대주제(h2) 아래 그날 수업 제목 소제목(h3) */
.lf-daily-sub{ margin:4px 0 0 !important; padding:0 !important; text-align:center; font-size:16px !important; line-height:24px !important;
  font-weight:600 !important; color:var(--text-secondary) !important; overflow-wrap:anywhere; }

/* 과제 뽐내기: 정사각형 썸네일 타일 갤러리 (마지막 + 타일 = 새 등록) */
.st-key-lf_showhead{ margin-top:8px; }
.st-key-lf_showgrid{ gap:12px !important; }
[class*="st-key-lfshowtile_"], [class*="st-key-lfshowadd_"]{ position:relative; gap:4px !important; width:112px !important; }
.lf-tile{ width:112px; height:112px; border-radius:12px; overflow:hidden; border:1px solid var(--border); background:var(--surface-subtle);
  display:flex; align-items:center; justify-content:center; }
.lf-tile{ background:#FFFFFF !important; }
.lf-tile-img{ width:100%; height:100%; object-fit:contain; display:block; padding:10px; box-sizing:border-box; }  /* 로고가 잘리지 않게 전체 보이기 */
.lf-tile-logo{ padding:14px; }
.lf-tile-big{ width:100% !important; height:200px !important; }
.lf-tile-ph{ font-size:32px; font-weight:700; color:var(--text-secondary); }
.lf-tile-add{ border:1.5px dashed var(--border); background:var(--surface); }
.lf-tile-add span{ font-size:32px; line-height:1; color:var(--text-secondary); font-weight:300; }
.lf-tile-cap{ width:112px; font-size:13px; line-height:18px; color:var(--text-primary); font-weight:600;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; text-align:center; }
[class*="st-key-lfshowopen_"], [class*="st-key-lfshowaddbtn_"]{ position:absolute; inset:0; z-index:1; }
[class*="st-key-lfshowopen_"] .stButton, [class*="st-key-lfshowopen_"] button,
[class*="st-key-lfshowaddbtn_"] .stButton, [class*="st-key-lfshowaddbtn_"] button{ width:100%; height:100%; }
[class*="st-key-lfshowopen_"] button, [class*="st-key-lfshowaddbtn_"] button{ opacity:0; cursor:pointer; }
[class*="st-key-lfshowtile_"]:hover .lf-tile, [class*="st-key-lfshowadd_"]:hover .lf-tile{ border-color:var(--accent-border); }
[class*="st-key-lfshowtile_"]:has(button:focus-visible) .lf-tile,
[class*="st-key-lfshowadd_"]:has(button:focus-visible) .lf-tile{ outline:2px solid var(--accent-border); outline-offset:2px; }

/* 일별: 오른쪽 미리보기 카드 높이를 왼쪽 학습 목록 높이에 맞춘다 (나란히 놓일 때만) */
@media (min-width: 641px){
  .st-key-lf_dsplit [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]){ align-items:stretch !important; }
  .st-key-lf_dsplit [data-testid="stColumn"]{ display:flex; flex-direction:column; }
  .st-key-lf_dsplit [data-testid="stColumn"] div:has(.st-key-lf_dpreview){ flex:1 1 auto; display:flex; flex-direction:column; }
  .st-key-lf_dpreview{ flex:1 1 auto; }
  .st-key-lf_dpreview [data-testid="stElementContainer"]:has(.lf-dprev){ flex:1 1 auto; }
}

/* 선택한 구간: [태그] 위, 제목 아래로 쌓기 (월별은 오른쪽 정렬, 전체 일정은 왼쪽 정렬) */
.lf-unit-stack{ display:flex; flex-direction:column; align-items:flex-start; gap:4px; margin:6px 0 2px; }
.lf-unit-stack-title{ font-size:18px; line-height:26px; font-weight:700; color:var(--text-strong); overflow-wrap:anywhere; }
.st-key-lf_monthpanel .lf-unit-stack{ align-items:flex-end; text-align:right; }

/* 월별 보기: "선택한 구간" 글자는 숨긴다 */
.st-key-lf_monthpanel .lf-eyebrow{ display:none; }

/* 월별: 1100px 이하에서는 오른쪽 정보 파트를 캘린더 아래로 (캘린더 주 칸에는 걸리지 않게 바깥 칸 상자에만) */
@media (max-width: 1100px){
  .st-key-lf_msplit > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"],
  .st-key-lf_msplit > [data-testid="stHorizontalBlock"]{ flex-direction:column !important; }
  .st-key-lf_msplit > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  .st-key-lf_msplit > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{ width:100% !important; flex:1 1 100% !important; }
}

/* 전체 일정: 넓은 화면은 날짜 토글, 767px 이하는 월별과 같은 날짜 버튼 */
.st-key-lf_allpanel .st-key-lf_datebtns, .st-key-lf_allpanel [data-testid="stLayoutWrapper"]:has(> .st-key-lf_datebtns){ display:none !important; }
@media (max-width: 767px){
  .st-key-lf_allpanel .st-key-lf_alltoggle{ display:none !important; }
  .st-key-lf_allpanel [data-testid="stLayoutWrapper"]:has(> .st-key-lf_datebtns){ display:flex !important; }
  .st-key-lf_allpanel .st-key-lf_datebtns{ display:grid !important; }
}

/* 학습 캘린더 일별: 선택하지 않은 학습 목록은 글자를 연하게 */
.lf-dsec:not(.sel) .lf-dsec-body b{ color:var(--text-secondary); font-weight:500; }

/* 조별 편성 */
.lf-team{ padding:10px 12px; border:1px solid var(--border); border-radius:var(--radius-button); margin-bottom:8px; background:var(--surface); }
.lf-team-name{ font-size:14px; font-weight:700; color:var(--text-strong); margin-bottom:6px; }
.lf-members{ display:flex; flex-wrap:wrap; gap:6px; }
.lf-member{ display:inline-flex; align-items:center; gap:4px; padding:2px 10px; border-radius:var(--radius-tag);
  background:var(--surface-subtle); font-size:13px; line-height:20px; color:var(--text-primary); }
.lf-member.absent{ color:var(--past-text); text-decoration:line-through; }
.lf-absent-tag{ text-decoration:none; display:inline-block; padding:0 6px; border-radius:var(--radius-tag);
  background:var(--warning-bg); color:var(--warning); font-size:12px; font-weight:600; }

/* 학습 기록 탭 */
.lf-rec-day{ margin:16px 0 6px; font-size:14px; color:var(--text-strong); display:flex; align-items:center; gap:6px; flex-wrap:wrap; }

/* 조별 편성: 참석 / 불참 줄 나누기 */
.lf-att-row{ display:flex; align-items:flex-start; gap:8px; margin-top:6px; }
.lf-att-label{ flex:none; min-width:44px; font-size:12px; line-height:24px; font-weight:600; color:var(--text-secondary); }
.lf-att-label.away{ color:var(--warning); }
.lf-member.absent{ background:var(--warning-bg); color:var(--warning); text-decoration:none; }

/* 기록: 구간마다 카드 하나, 그 안에 한 줄씩 */
.lf-recsec-head{ display:flex; align-items:center; justify-content:space-between; gap:8px;
  font-size:14px; font-weight:700; color:var(--text-strong); margin-bottom:2px; }
.lf-recrow{ display:flex; flex-wrap:wrap; align-items:center; gap:6px; font-size:14px; line-height:20px; }
.lf-recrow .lf-muted{ margin:0; font-size:12px; }
.lf-recrow-text{ flex-basis:100%; color:var(--text-primary); white-space:pre-wrap; overflow-wrap:anywhere; }
[class*="st-key-lfrecsec_"], [class*="st-key-lfdaysec_"]{ gap:4px !important; }

/* 수업 화면 "D? 기록": 카드 머리의 구간 이름 버튼 */
[class*="st-key-lfdaysec_"] [class*="st-key-jump_"] button{ padding:0 !important; min-height:0 !important; justify-content:flex-start; }
[class*="st-key-lfdaysec_"] [class*="st-key-jump_"] button p{ font-size:14px; font-weight:700; color:var(--text-strong) !important; text-align:left; }
[class*="st-key-lfdaysec_"] [class*="st-key-jump_"] button:hover p{ color:var(--accent-strong) !important; text-decoration:underline; }

/* 조별 편성: 조원마다 참석/불참 버튼 */
[class*="st-key-lfteam_"]{ gap:6px !important; }
[class*="st-key-lfatt_"]{ gap:8px !important; }
[class*="st-key-lfatt_"] [data-testid="stButtonGroup"] button{ min-height:28px !important; padding:2px 10px !important; }
[class*="st-key-lfatt_"] [data-testid="stButtonGroup"] button p{ font-size:12px !important; }

/* 관리자 모드: 구간별 진행 현황 */
.lf-prow{ display:flex; align-items:center; gap:8px; padding:8px 10px; border:1px solid var(--border);
  border-radius:var(--radius-button); margin-bottom:6px; background:var(--surface); }
.lf-prow.cur{ border-color:var(--accent-border); }
.lf-prow-body{ flex:1; min-width:0; display:flex; flex-direction:column; font-size:13px; line-height:18px; }
.lf-prow-body b{ overflow-wrap:anywhere; color:var(--text-strong); }

/* 수업 화면 오른쪽 위: 다음 구간만 있으면 오른쪽 끝, 이전만 있으면 왼쪽 끝 (둘 다면 양쪽) */
.st-key-lf_secnav{ flex-wrap:nowrap !important; }
.st-key-lf_lessonhead{ gap:10px !important; }

/* 관리자 진행 현황: 줄을 누르면 이동 (투명 버튼 겹치기) */
[class*="st-key-lfprow_"]{ position:relative; gap:0 !important; }
[class*="st-key-lfprowgo_"]{ position:absolute; inset:0; z-index:1; }
.st-key-lf_prowlist{ gap:6px !important; }  /* 진행 현황 카드 사이 6px */
.st-key-lf_prowlist .lf-prow{ margin-bottom:0; }
[class*="st-key-lfprowgo_"] .stButton, [class*="st-key-lfprowgo_"] button{ width:100%; height:100%; }
[class*="st-key-lfprowgo_"] button{ opacity:0; cursor:pointer; }
[class*="st-key-lfprow_"]:hover .lf-prow:not(.cur){ border-color:var(--accent-border); }
[class*="st-key-lfprow_"]:has(button:focus-visible) .lf-prow{ outline:2px solid var(--accent-border); outline-offset:2px; }

/* 체크 단계 탭: 탭 이름이 길어 한 줄로 두고 가로로 넘겨 본다 */
/* 단계 탭: 번호만 원형으로. 선택 = 보라 바탕 흰 글자, 선택 안 됨 = 회색 */
.st-key-lf_steptabs [data-baseweb="tab-list"]{ gap:8px; overflow-x:auto; scrollbar-width:thin; padding:4px 2px; }
.st-key-lf_steptabs [data-baseweb="tab-highlight"], .st-key-lf_steptabs [data-baseweb="tab-border"]{ display:none !important; }
.st-key-lf_steptabs [role="tab"]{ width:34px; height:34px; min-width:34px; padding:0 !important; border-radius:50% !important;
  display:inline-flex; align-items:center; justify-content:center; background:#E6E8EF; flex:none; }
.st-key-lf_steptabs [role="tab"] p{ font-size:14px; font-weight:700; color:var(--text-secondary) !important; margin:0; }
.st-key-lf_steptabs [role="tab"][aria-selected="true"]{ background:#6541F2; }
.st-key-lf_steptabs [role="tab"][aria-selected="true"] p{ color:#FFFFFF !important; }
.st-key-lf_steptabs [role="tab"]:hover:not([aria-selected="true"]){ background:#D9DCE3; }
.st-key-lf_steptabs [role="tab"]:focus-visible{ outline:2px solid var(--accent-border); outline-offset:2px; }
.st-key-lf_steptabs .lf-content ol.steps{ padding-left:0; list-style:none; margin:8px 0 0; }

/* 원본 수업 본문 재구성 */
.lf-content{ color:var(--text-primary); font-size:16px; line-height:26px; overflow-wrap:anywhere; }
.lf-content h3{ margin:24px 0 8px; }
.lf-content p{ margin:0 0 12px; }
.lf-content a{ color:var(--accent-strong); }
.lf-content pre, .lf-content .code{ background:#14191E; color:#F0F4F8; padding:16px; border-radius:var(--radius-button);
  overflow-x:auto; font-size:14px; line-height:22px; white-space:pre; margin:0 0 16px; }
.lf-content .codebar{ display:flex; justify-content:space-between; font-size:12px; color:var(--text-secondary); margin-top:8px; }
.lf-content code{ background:var(--surface-subtle); padding:1px 6px; border-radius:6px; font-size:14px; }
.lf-content pre code{ background:transparent; padding:0; color:inherit; }
.lf-content .tip, .lf-content .hint{ background:var(--accent-soft); border-left:4px solid var(--accent); padding:12px 16px;
  border-radius:var(--radius-button); margin:0 0 16px; }
.lf-content .warn, .lf-content .caution{ background:var(--warning-bg); border-left:4px solid var(--warning-accent); padding:12px 16px; border-radius:var(--radius-button); }
.lf-content .box, .lf-content .panel, .lf-content .card{ background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius-card); padding:16px 20px; margin:0 0 16px; }
.lf-content table{ display:block; max-width:100%; overflow-x:auto; border-collapse:collapse; margin:0 0 16px; font-size:15px; }
.lf-content th, .lf-content td{ border:1px solid var(--border); padding:8px 12px; text-align:left; vertical-align:top; }
.lf-content th{ background:var(--surface-subtle); }
.lf-content img{ max-width:100%; height:auto; }
.lf-content .chk, .lf-content .check{ display:flex; gap:8px; align-items:flex-start; }
@media (prefers-reduced-motion: reduce){ *{ transition:none !important; animation:none !important; } }
"""


def inject(mode: str | None = None) -> None:
    """mode는 호환을 위해 받기만 한다. 강조색은 모드와 상관없이 같다."""
    st.html(f"<style>{BASE_CSS}\n:root{{{ACCENT_VARS}}}</style>")
    st.html("<script>document.documentElement.lang = 'ko';</script>", unsafe_allow_javascript=True)
