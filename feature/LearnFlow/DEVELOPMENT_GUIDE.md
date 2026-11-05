# LearnFlow 개발 시작 가이드 (PRD v0.3 기준)

## 1. 프로젝트 생성
앱은 `feature/LearnFlow/app/`에 만든다. Python 3.11 이상.
```bash
cd feature/LearnFlow
mkdir app && cd app
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# macOS / Git Bash:     source .venv/bin/activate
pip install streamlit beautifulsoup4 lxml pytest
pip freeze > requirements.txt

python scripts/build_lessons.py   # Data/*.html → data/lessons.generated.json
streamlit run app.py              # http://localhost:8501
```

## 2. 폴더 구조
```text
D11-agent/                      # 저장소 루트 (origin: Wanted-AI-NativeCamp/D17-WONMORE)
├── .gitignore                  # Data/, 생성된 수업 JSON, .userdata/, .venv/ 제외
├── Data/                       # 원본 수업 HTML (읽기 전용, git 제외)
│   ├── D01_1014.html
│   ├── D01_1014.rendered.html  # D1 렌더링 스냅샷 (직접 저장, §4)
│   └── ...
├── WONMORE/
│   └── Designsystem.md         # WONMORE 공통 디자인 시스템 (몽타주 참고)
├── WONMORE_landing.html        # 상위 브랜드 랜딩 (LearnFlow 버튼 → localhost:8501)
└── feature/
    └── LearnFlow/
        ├── PRD.md              # LearnFlow PRD v0.3
        ├── DEVELOPMENT_GUIDE.md
        ├── colorsystem.md      # LearnFlow 컬러 토큰
        └── app/                # Streamlit 앱
            ├── .streamlit/
            │   └── config.toml           # 기본 테마 (light, primaryColor, 배경)
            ├── .userdata/                # 개인 학습 데이터 (git 제외)
            │   └── learnflow.v1.json
            ├── scripts/
            │   └── build_lessons.py      # ../../../Data/*.html 분석 → data/lessons.generated.json
            ├── data/
            │   └── lessons.generated.json   # 생성물 (git 제외)
            ├── lib/
            │   ├── lessons.py            # 수업 JSON 읽기 (st.cache_data)
            │   ├── storage.py            # 사용자 데이터 읽기·쓰기 (이 파일만 .userdata 접근)
            │   ├── progress.py           # 진행 상태 전환 규칙 (PRD §4 F06)
            │   └── theme.py              # 토큰·모드별 CSS 주입 (커스텀 CSS는 여기만)
            ├── components/
            │   ├── day_card.py
            │   ├── section_nav.py        # 사이드바 구간 목록 + 이전/다음 버튼
            │   ├── blocks.py             # Block kind → Streamlit 렌더러 (code, check, callout, table, jobs, os, card, html)
            │   ├── checkin.py            # 잘 따라가고 있나요?
            │   ├── note_form.py
            │   └── day_notes.py          # 오른쪽 열 기록 목록 + 삭제 dialog
            ├── pages/
            │   ├── home.py               # 모드 선택, 이어보기, Day 카드
            │   └── day.py                # Day 상세 (?day=D3&sec=install)
            ├── tests/
            │   ├── test_build_lessons.py
            │   ├── test_storage.py
            │   ├── test_progress.py
            │   └── test_app.py           # streamlit.testing.v1.AppTest
            ├── app.py                    # st.navigation 진입점
            └── requirements.txt
```

## 3. 구현 순서
1. `.gitignore` 확인 후 `git status`로 `Data/`, `.userdata/`, `lessons.generated.json`이 안 나오는지 확인
2. `build_lessons.py`
   - 파일명 → Day (`D01_1014.html` → `D1`), `<title>`에서 `Dn 워크북 ·` 접두사 제거
   - `<section id>` + 첫 `<h2>` 추출, `<script>`·`nav.toc`·`on*` 속성 제거
   - 최상위 자식 단위로 블록 분리 (PRD §8 매핑표), 카드 안 위젯은 `children`으로 재귀
   - 체크박스 키: D1 `data-key`, 나머지 `data-k`
   - 미처리 class 목록과 Day별 구간 수를 로그로 출력
3. D1 처리: `Data/D01_1014.rendered.html`이 있으면 그것을 분석, 없으면 정적 7구간 + 경고 (§4)
4. `test_build_lessons.py`: 구간 수가 PRD §8 표와 같은지, 정제가 됐는지
5. `app.py` + 홈(Day 카드) → 상세(사이드바 구간 목록) → `blocks.py` 렌더러 (code → html → table → callout → check → card → jobs → os 순)
6. `storage.py` (원자적 쓰기, 깨진 파일 백업) + `progress.py` + 이어보기
7. 체크인·기록·오른쪽 열 기록 목록·삭제 dialog
8. 학습 모드 컬러(`theme.py`), 반응형 점검(1280 / 1024 / 768 / 375px), PRD §10 인수 기준 점검

## 4. D1 렌더링 스냅샷 만들기
D1은 구간 4개(`m1`~`m4`)를 원본 스크립트가 브라우저에서 만들기 때문에 Python으로는 읽을 수 없다. 한 번만 직접 저장한다.
1. 브라우저로 `Data/D01_1014.html`을 연다.
2. 개발자 도구(F12) → Console에서 `copy(document.documentElement.outerHTML)` 실행
3. 새 파일 `Data/D01_1014.rendered.html`에 붙여넣고 저장 (원본 파일은 건드리지 않는다)
4. `python scripts/build_lessons.py` 로그에서 D1 구간 수가 11인지 확인

## 5. Streamlit 구현 주의
- 위젯을 누를 때마다 스크립트 전체가 다시 실행된다. 수업 JSON은 `st.cache_data`로 한 번만 읽고, 사용자 데이터는 저장할 때만 파일에 쓴다.
- 현재 Day·구간은 `st.query_params`(`day`, `sec`)와 `st.session_state`에 둔다. 구간이 바뀌면 `resume`을 저장한다.
- 위젯 `key`는 `f"{lesson_id}:{section_id}:{check_key}"`처럼 Day·구간을 넣어 겹치지 않게 한다.
- 화면에는 선택한 구간 하나만 그린다 (D4는 원본이 약 350KB).
- `st.html`은 스크립트를 실행하지 않는다. 원본 인터랙션은 모두 Streamlit 위젯으로 다시 만든다.
- CSS는 `theme.py`에서만 주입하고, `st-emotion-cache-*` 같은 내부 class 대신 `data-testid`와 `st-key-*` class를 기준으로 쓴다.
- 기본 포커스 링을 CSS로 지우지 않는다.

## 6. 안전/배포 주의
- `Data/`, `lessons.generated.json`, `.userdata/`는 커밋하지 않는다. 재배포 권한을 확인하기 전에는 Streamlit Community Cloud 등에 배포하지 않는다.
- 배포하면 `.userdata/` 파일을 모든 방문자가 공유하게 되므로, 배포 전에 저장 방식을 다시 설계해야 한다.
- 원본 HTML을 수정하지 않는다. 원본에 없는 내용을 생성하지 않는다.
- 사용자 데이터 파일 접근은 `lib/storage.py`에서만 한다.
- WONMORE 랜딩 페이지는 별도 작업이며 LearnFlow P0보다 우선하지 않는다.
