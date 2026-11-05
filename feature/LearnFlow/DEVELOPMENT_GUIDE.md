# LearnFlow 개발 가이드 (PRD v0.4 기준)

## 1. 실행
앱 위치: `feature/LearnFlow/app/` · Python 3.11 이상 · Streamlit **1.66.1 고정**(`requirements.txt`)
```bash
cd feature/LearnFlow/app
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1   /   macOS·Git Bash: source .venv/bin/activate
pip install -r requirements.txt          # 새 패키지는 사용자 허락 후에만 추가 (CLAUDE.md)

python scripts/build_lessons.py          # Data/*.html → data/lessons.generated.json
streamlit run app.py                     # http://localhost:8501
python -m pytest -q                      # 테스트 (53개)
```
- **`lib/` 파일이나 `.streamlit/config.toml`을 고치면 앱을 다시 켠다.** 실행 중인 앱은 처음 읽은 `lib` 모듈을 계속 써서 `module 'lib.schedule' has no attribute ...` 같은 오류가 난다. `app.py`만 고쳤으면 새로고침으로 충분하다.

## 2. 폴더 구조 (실제)
```text
D11-agent/
├── CLAUDE.md                  # 작업 규칙 (꼭 지킬 것 · 실수에서 배운 규칙)
├── .gitignore                 # Data/, lessons.generated.json, .userdata/, .venv/ 제외 (스킬 data/는 예외로 포함)
├── .claude/
│   ├── skills/ship/           # /ship F번호 — 기능 하나 출시 매뉴얼
│   ├── skills/ui-ux-pro-max/  # UI/UX 점검 스킬 (MIT)
│   ├── commands/retro.md      # /retro — 오늘 회고 JSON
│   ├── agents/log-reader.md   # 일지요약직원
│   └── hooks/log_work.py      # 저장할 때마다 .claude/작업일지.txt에 한 줄 (Write/Edit 도구만 기록)
├── Data/                      # 원본 수업 HTML (읽기 전용, git 제외). 업로드는 새 파일만 추가
├── WONMORE/Designsystem.md    # 공통 디자인 시스템
└── feature/LearnFlow/
    ├── PRD.md · DEVELOPMENT_GUIDE.md · colorsystem.md
    └── app/
        ├── app.py             # 단일 진입점: query_params로 화면 선택 + 모든 화면 함수
        ├── .streamlit/config.toml   # 테마(primaryColor #6541F2, Pretendard fontFaces), 업로드 20MB
        ├── assets/wonmore_logo_thumb.png   # 과제 기본 썸네일
        ├── scripts/build_lessons.py        # 원본 분석 → 수업 JSON
        ├── data/lessons.generated.json     # 생성물 (git 제외)
        ├── .userdata/          # 개인 데이터 (git 제외): learnflow.v1.json, backups/, thumbnails/
        ├── lib/                # 계산·저장 로직 (st.* 금지 — theme.py 제외)
        │   ├── storage.py      # 사용자 데이터·썸네일 읽기/쓰기 (이 파일만 .userdata 접근)
        │   ├── progress.py     # 상태 전환·체크인·기록·과제·조 편성·참석/불참·관리자 집계
        │   ├── schedule.py     # 캠프 일정(UNITS)·휴일·Day↔날짜·월 캘린더·조 편성 차수
        │   ├── lessons.py      # 수업 JSON 읽기·미리보기 글자·체크 단계 나누기
        │   ├── upload.py       # 교육 자료 업로드 검사·저장·다시 빌드
        │   └── theme.py        # 디자인 토큰 + 모든 커스텀 CSS (st.html로 주입)
        └── tests/test_core.py  # pytest + AppTest
```

## 3. app.py 화면 지도
| 화면 | 주소 | 주요 함수 |
|---|---|---|
| GNB | 모든 화면 | `gnb(active)` |
| 학습 캘린더 | `/` | `home` → `schedule_section` → `daily_view` / `month_calendar_view` / `all_schedule_view`, `day_panel`, `showcase_section` |
| 교육 모아보기 | `?page=lessons` | `lessons_page`, `day_overview`(빠르게 둘러보기) |
| 수업 화면 | `?day=D17&sec=am` | `day_view` → `progress_overview`, `checkin_form`, `day_notes`, `team_section`, `note_form` |
| 프로젝트 기록 | `?project=D12` | `project_view` |
| 학습 기록 | `?page=records` | `records_page`, `record_row` |
| 관리자 | `?page=admin` | `admin_page`, `team_admin_card`, `team_edit_dialog`, `_absence_editor` |
| 창(dialog) | – | `upload_dialog`, `note_dialog`, `showcase_dialog`, `showcase_detail`, `confirm_delete` |

화면 이동은 `go(day=, sec=, project=, page=)` 하나로 한다. 고른 날짜·달·보기는 `st.session_state`(`sel_date`, `cal_month`, `cal_view`, `dsel_<Day>`).

## 4. 기능 추가 순서 (`/ship F번호`)
1. PRD §4에서 기능과 완료 기준 확인 → 2. 계산·저장은 `lib/`에 순수 함수로(시간·경로는 인자로) → 3. 화면은 `app.py` → 4. CSS는 `theme.py` → 5. `tests/test_core.py`에 테스트 → 6. `pytest` → 7. 앱 재시작 후 **브라우저로 확인**(§6) → 8. PRD 상태 갱신 → 9. 커밋은 허락받고.

## 5. 디자인·CSS 규칙
- 커스텀 CSS는 **`lib/theme.py`의 `BASE_CSS` 한 곳**. 새 규칙은 `/* 원본 수업 본문 재구성 */` 표시 앞에 덧붙인다.
- 선택자 기준: `st.container(key="lf_xxx")`가 만드는 `.st-key-lf_xxx`, `data-testid`. `st-emotion-cache-*` 금지.
- Streamlit은 요소를 한 겹 더 감싼다(`stLayoutWrapper`, `stElementContainer`). 폭·간격이 안 먹으면 바깥 상자에도 규칙을 준다: `[data-testid="stLayoutWrapper"]:has(> .st-key-lf_xxx){...}`.
- **카드 전체를 누르는 패턴:** 카드 HTML + 같은 컨테이너 안 `st.button` → 버튼을 `position:absolute; inset:0; opacity:0`로 겹친다. 버튼 이름은 화면 읽기용으로 의미 있게(예: "3. 함께 학습 페이지로"), `:has(button:focus-visible)`로 포커스 테두리.
- **반응형은 CSS로:** 서버는 화면 너비를 모른다. 두 모양을 모두 그리고 미디어 쿼리로 하나만 보인다(예: 월별 `lf_calgrid`/`lf_callist`, 전체 일정 `lf_alltoggle`/`lf_datebtns`). 기준은 **1100 / 767 / 640px**만 쓴다.
- 칸 비율을 CSS로 바꿀 때는 그 칸 상자에만: `:has(> [data-testid="stColumn"])` 또는 `.st-key-x > [data-testid="stHorizontalBlock"]`. 안쪽 가로 상자까지 바뀌는 사고가 있었다.
- 글꼴은 `config.toml`로만. 색은 `colorsystem.md` 토큰(`--accent-strong`, `--accent-border`, `--grad-soft`, `--past-text` …).
- **CSS를 문자열로 자르거나 지울 때 `{}` 짝을 확인한다.** 짝 없는 `}` 하나로 뒤 규칙이 통째로 무시돼 흰 카드가 사라진 적이 있다(테스트 `test_theme_css_braces_balanced`).
- 스타일·스크립트만 든 `st.html` 칸은 자리를 차지하지 않게 숨겨 둔 규칙이 있다(위쪽 빈 여백 방지).

## 6. 확인 방법
- **자동:** `python -m pytest -q`. 화면 테스트는 `AppTest`로, 저장 위치는 `monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_path/...)`로 바꿔 진짜 기록을 건드리지 않는다.
  - AppTest 한계: 창(dialog) 안에서 값을 바꾸면 창이 닫혀 저장까지는 못 따라간다 → 저장 로직은 `lib` 함수 테스트로 확인.
  - HTML 안 글자를 셀 때는 CSS 글자와 섞이지 않게 `class="..."`까지 넣어 센다.
- **브라우저(Claude in Chrome):** 추측으로 고치지 말고 실제 계산된 스타일을 본다(`getComputedStyle`, `getBoundingClientRect`).
  - 창 크기 조절이 안 먹을 때는 같은 페이지를 `iframe`(너비 420/900/1300px)으로 띄워 미디어 쿼리를 확인한다.
  - 진짜 기록 파일에 쓰는 동작(등록·저장·모드 전환)은 브라우저에서 누르지 않는다. 열고 닫기·잘못된 입력 거부까지만.

## 7. 안전·배포
- `Data/`, `lessons.generated.json`, `.userdata/`는 커밋하지 않는다. 커밋 전 `git diff --cached --name-only`로 확인.
- 원본 HTML은 수정하지 않는다(업로드는 새 파일만, 이미 있으면 거절). 원본에 없는 내용을 만들지 않는다.
- 사용자 데이터 접근은 `lib/storage.py`만. Claude는 `.userdata/`를 직접 지우거나 고치지 않는다.
- 공개 배포·여러 수강생 사용은 저장 방식(공유 저장소·수강생 구분·관리자 접근 제한)을 다시 설계한 뒤에(PRD §13).

## 8. D1 렌더링 스냅샷
D1 구간 4개(`m1`~`m4`)는 원본 스크립트가 브라우저에서 만든다. 브라우저로 `Data/D01_1014.html`을 열고 콘솔에서 `copy(document.documentElement.outerHTML)` → `Data/D01_1014.rendered.html`로 저장 → `python scripts/build_lessons.py` 로그에서 D1 구간 11개 확인.
