# LearnFlow PRD v0.3

- 상위 브랜드: WONMORE
- 서비스: LearnFlow
- 버전: v0.3 (변경 이력은 맨 아래 참고)
- 날짜: 2026-11-05
- 목표: 개인 개발 MVP (원티드 AI Native Camp 교육생 대상)
- 기술 스택: **Python + Streamlit** (로컬 실행)
- 핵심 결정: **원본 HTML 수업 자료를 자동 분석해 구간(section) 단위로 재구성하고, 구간을 하나씩 따라가며 진행 상황과 어려움을 기록한다.**

## 1. 제품 정의
LearnFlow는 매일 제공되는 HTML 수업 자료를 자동 분석해 **구간별로 나눠 보기 좋게 다시 보여주고**, 학습자가 구간을 따라가며 **잘 따라가고 있는지, 어디서 막혔는지** 기록하고 Day별로 다시 확인하는 Streamlit 앱이다.

### 문제 가설
- 수업 자료 하나가 길어서(6~11개 구간, 최대 약 350KB) 지금 어디쯤인지 알기 어렵다.
- 지난 수업 자료를 찾고, 보던 위치로 돌아가기 번거롭다.
- 학습 중 막힌 지점과 해결 방법을 구간과 연결해서 남기기 어렵다.

### MVP 성공 기준
사용자가 Day를 선택하고, 구간 목록으로 이동하며 학습하고, 구간마다 진행 상태와 어려움을 기록하고, 앱을 다시 켰을 때 보던 위치에서 이어볼 수 있다.

## 2. 대상 사용자
- 우선: AI Native Camp 초심자, 학습 내용을 기록하려는 학습자
- 숙련자: 빠르게 훑어보고 필요한 구간만 찾는 학습자
- 학습 모드(초심자/숙련자)를 선택할 수 있고, 모드에 따라 포인트 컬러가 바뀐다 (§9).
- **사용자는 1명(본인)이다.** 로컬에서 혼자 실행하는 것을 전제로 한다.

## 3. 핵심 정책
1. **원본 파일은 수정하지 않는다.** `Data/` 원본 HTML은 읽기 전용으로 두고, 빌드 스크립트가 분석해 만든 결과물만 화면에 쓴다.
2. **보여주는 방식은 바꾸되 내용은 지어내지 않는다.** 구간 나누기, 레이아웃 정리, LearnFlow 디자인 적용은 허용한다. 원본에 없는 설명을 생성하거나 요약하지 않는다.
3. **구간 = 원본의 `<section id>` 단위.** 구간 제목은 원본 `<h2>`를 그대로 쓴다.
4. **기록은 Day와 구간에 연결한다.** 하나의 구간에 여러 기록을 남길 수 있다.
5. **원본 메뉴(`<nav class="toc">`)와 원본 스크립트는 화면에서 쓰지 않는다.** LearnFlow의 구간 목록이 원본 메뉴를 대신한다. (원본 스크립트는 `st.html`에서 실행되지도 않는다.)
6. **개인 데이터는 로컬 JSON 파일 하나(`app/.userdata/learnflow.v1.json`)에만 저장한다.** 계정·기기 간 동기화는 제공하지 않는다. 파일 읽기·쓰기는 `lib/storage.py`에서만 한다.
7. **수업 자료, 분석 결과물, 개인 데이터는 GitHub에 올리지 않는다.** `Data/`, 생성된 수업 JSON, `.userdata/`는 `.gitignore`에 넣는다. 재배포 권한을 확인하기 전에는 Streamlit Community Cloud 등에 배포하지 않고 로컬(`localhost:8501`)에서만 실행한다.
   - 참고: 서버에 배포하면 JSON 파일을 모든 방문자가 공유하게 되므로, 배포하려면 저장 방식부터 다시 설계해야 한다.

## 4. 기능

### P0
| ID | 기능 | 완료 기준 |
|---|---|---|
| F01 | Day 목록 | D1~D10, D17 총 11개 Day를 카드로 표시. 카드에 구간 수와 진행률(완료 구간 / 전체 구간) 표시 |
| F02 | HTML 자동 분석 | 빌드 스크립트(`scripts/build_lessons.py`)가 `Data/*.html`을 읽어 Day·제목·구간(id, h2 제목, 블록 목록)을 JSON으로 생성 |
| F03 | 구간 재구성 화면 | 선택한 **구간 하나만** 그린다. 원본 본문을 블록 단위로 나눠 Streamlit 요소와 LearnFlow 스타일로 다시 그림 (§8 매핑표) |
| F04 | 구간 이동 | 사이드바에 현재 Day의 구간 목록(상태 아이콘 + 제목). 현재 구간 강조. 구간 끝에 `← 이전 구간 / 다음 구간 →` 버튼. URL에 `?day=D3&sec=install`이 반영되어 새로고침해도 같은 구간 |
| F05 | 원본 인터랙션 재구현 | 코드 복사(`st.code` 기본 복사 버튼), 단계 체크박스(`st.checkbox`), 직군·OS 전환(`st.segmented_control`)이 동작. 직군·OS 선택값은 저장 |
| F06 | 구간별 진행 표시 | 구간마다 `시작 전 / 진행 중 / 완료` 상태 (전환 규칙은 아래). 사이드바와 Day 카드에 반영 |
| F07 | 따라가기 체크인 | 구간 끝에서 "잘 따라가고 있나요?" 질문에 `잘 따라감 / 조금 헤맴 / 막힘` 중 선택. 헤맴·막힘을 고르면 어려웠던 점 입력칸이 열림. 한 구간에 여러 번 남길 수 있고 **가장 최근 체크인**이 그 구간의 상태로 보인다 |
| F08 | 학습 기록 | 구간에서 `어려움 / 해결 / 발견` 유형으로 기록 작성. 공백만 있는 기록은 저장하지 않고 안내 |
| F09 | Day 기록 패널 | 상세 화면 오른쪽 열에서 그 Day의 체크인과 기록 전체를 구간별로 묶어 보여줌. 삭제는 `st.dialog` 확인 후 해당 기록만 삭제 |
| F10 | 이어보기 | 마지막으로 보던 Day·구간을 기억해 홈에 "이어보기" 버튼 표시(기록이 없으면 숨김). 누르면 해당 구간으로 이동 |
| F11 | 학습 모드 | 초심자(블루) / 숙련자(퍼플) 선택. 선택은 저장되고 포인트 컬러에 반영 |
| F12 | 반응형 | 브라우저 창을 줄여도 잘림·페이지 가로 스크롤 없이 사용 가능 (§9 기준) |

**F06 진행 상태 전환 규칙**
| 상황 | 상태 |
|---|---|
| 한 번도 열지 않음 | 시작 전 ○ |
| 구간을 열었거나 체크박스를 하나라도 체크함 | 진행 중 ◐ |
| 체크인을 `잘 따라감` 또는 `조금 헤맴`으로 제출함 | 완료 ✓ |
| 체크인을 `막힘`으로 제출함 | 진행 중 ◐ 유지 (막힘 표시 함께) |

- 완료된 구간에서 "다시 진행 중으로" 버튼으로 되돌릴 수 있다.
- 체크인의 "어려웠던 점"은 체크인 안에만 저장한다(별도 `어려움` 기록을 자동으로 만들지 않음). 기록 패널에서는 체크인과 기록을 시간순으로 함께 보여준다.

### P1 (시간 여유 시)
- 전체 Day 기록 모아보기 (유형·Day 필터)
- 기록 수정, 기록 검색
- JSON 내보내기/가져오기 (`st.download_button` / `st.file_uploader`, 백업)
- 숙련자 모드에서 구간 전체 펼쳐보기
- 구간 선택 바를 본문 상단에 고정(CSS 주입)

### MVP 제외
- AI 요약·퀴즈 생성 (정책 2)
- 로그인·회원가입, DB, 클라우드 동기화, 여러 사용자
- 공동 기록, 멘토링, 댓글
- 공개 배포 (재배포 권한 확인 전)
- 키보드 ←/→ 구간 이동, 커스텀 애니메이션 (Streamlit 기본 동작으로 대체)

## 5. IA
Streamlit 멀티페이지(`st.navigation`) 2개 화면.
- **홈** (`pages/home.py`): 서비스 소개, 학습 모드 선택, 이어보기 버튼, Day 카드 목록
- **Day 상세** (`pages/day.py`, 노트 페이지를 따로 두지 않음)
  - 사이드바: Day 선택, 구간 목록(상태 아이콘 + 제목), Day 진행률
  - 본문 왼쪽 열: Day 제목 → 구간 제목 → 재구성된 콘텐츠 → 체크인 → 기록 작성 → 이전/다음 버튼
  - 본문 오른쪽 열: 이 Day의 체크인·기록 (구간별 묶음). 좁은 화면에서는 Streamlit이 열을 세로로 쌓아 본문 아래로 내려간다

## 6. 사용자 흐름
**학습 진행**: 홈 → Day 카드 선택(또는 이어보기) → 사이드바에서 구간 선택 → 내용 따라 하기·체크박스 체크 → 구간 끝 체크인 → (막혔다면) 어려운 점 기록 → 다음 구간 버튼

**기록 확인**: Day 상세 → 오른쪽 열에서 구간별 기록 확인 → 기록의 구간 이름을 누르면 해당 구간으로 이동 → 필요하면 삭제 확인 후 삭제

## 7. 데이터 구조
```python
# 빌드 스크립트 생성물: app/data/lessons.generated.json (git 제외)
class Lesson(TypedDict):
    id: str            # 'D1', 'D2', ... 'D17'  ← Day 기준 (§8)
    day: int           # 1, 2, ... 17
    title: str         # 원본 <title>에서 'Dn 워크북 ·' 접두사 제거
    source_file: str   # 'D01_1014.html'
    sections: list[Section]

class Section(TypedDict):
    id: str            # 원본 <section id> 값, 예: 'install'
    title: str         # 원본 <h2> 텍스트
    order: int
    blocks: list[Block]    # 본문을 위에서부터 나눈 블록 (§8 매핑표)
    check_keys: list[str]  # 원본 단계 체크박스 키 목록 (D1은 data-key, 나머지는 data-k)

class Block(TypedDict):
    kind: Literal['html', 'code', 'check', 'callout', 'table', 'jobs', 'os', 'card']
    html: str | None        # kind='html'|'table'|'callout': 정제된 HTML (script·nav·이벤트 속성 제거)
    text: str | None        # kind='code': 코드 원문 / kind='check': 체크 항목 문구
    key: str | None         # kind='check': 체크박스 키
    variants: dict[str, list[Block]] | None  # kind='jobs'|'os': {'dev': [...], 'win': [...]}
    children: list[Block] | None             # kind='card': 묶음 안의 블록
```

### 사용자 데이터 파일: `app/.userdata/learnflow.v1.json`
```python
{
  "version": 1,
  "progress": { lesson_id: { section_id: {
      "status": "todo" | "doing" | "done",
      "checked": [str],          # 체크한 단계 키
      "updated_at": str } } },   # ISO 8601
  "checkins": [ { "id", "lesson_id", "section_id",
                  "level": "good" | "struggling" | "stuck",
                  "note": str | None, "created_at" } ],
  "notes":    [ { "id", "lesson_id", "section_id",
                  "type": "difficulty" | "solution" | "discovery",
                  "content", "created_at" } ],
  "resume":   { "lesson_id", "section_id", "updated_at" } | None,
  "prefs":    { "mode": "beginner" | "advanced",
                "job": "common" | "dev" | "design" | "po" | "mkt",
                "os": "win" | "mac" }
}
```
- 파일이 없으면 기본값으로 만든다. 파일이 깨져 있으면 `learnflow.v1.json.broken-<시각>`으로 옮겨 두고 새로 시작하며 화면에 알린다(조용히 덮어쓰지 않음).
- 쓰기는 임시 파일에 쓴 뒤 교체(`os.replace`)해 중간에 끊겨도 파일이 깨지지 않게 한다.
- 저장 실패 시 `st.error`로 안내하고 성공 토스트를 띄우지 않는다.
- 구조가 바뀌면 `version: 2`로 올리고 이전 데이터를 변환한다.
- 화면 상태(현재 구간 등)는 `st.session_state`와 `st.query_params`에 두고, 남겨야 하는 것만 파일에 쓴다.

## 8. 콘텐츠와 Day 기준
- **Day 표기는 D1, D2, D3… 를 기준으로 한다.** 날짜(10/14 등)는 화면에 표시하지 않는다.
- 파일명 → Day 매핑: `D01_1014.html` → `D1`, …, `D17_1105.html` → `D17`. 앞자리 0을 뺀다.
- 보유 자료: D1~D10, D17 (11개). D11~D16은 자료가 없으므로 목록에 표시하지 않는다.

| Day | 제목(원본 기준) | 구간 수 |
|---|---|---|
| D1 | 클로드 업무자동화 워크북 | 11 (정적 7 + 스크립트 생성 4) |
| D2 | HTML이 화면이 되는 원리 + 조별 AI 서비스 리스트 | 6 |
| D3 | Claude Code | 8 |
| D4 | 틀린 걸 찾아 스킬로 가르치기 | 11 |
| D5 | Git으로 같이 일하기 | 9 |
| D6 | 무료 API로 나만의 서비스 만들기 | 6 |
| D7 | 파이썬으로 API 키 지키기 + 하루 3번 오는 서비스 | 6 |
| D8 | 파이썬으로 카카오 지도 + 판다스로 공공데이터 | 6 |
| D9 | 프롬프트 → 생성기 → 30초 릴스 | 11 |
| D10 | 프롬프트 ② 패턴 · 프레임워크 · 고급 기법 | 8 |
| D17 | 서비스 하나 출시하기 — 1/N 정산왕 → 우리 조 캠프 서비스 | 7 |

구간 수는 `<section id>` 개수로 확인한 값이며(2026-11-05), 빌드 스크립트 결과로 확정한다.

### 자동 분석 규칙
- 도구: Python `beautifulsoup4` + `lxml`. 앱 실행 전에 한 번 `python scripts/build_lessons.py`로 JSON을 만든다. 앱은 JSON만 읽는다(`st.cache_data`).
- D2~D17: `<section id="..." class="sec">`를 구간으로, 그 안의 첫 `<h2>`를 구간 제목으로 쓴다.
- **D1**: `class="sec"`가 없고, 구간 4개(`m1`~`m4`)를 원본 스크립트의 `MODULES` 배열이 브라우저에서 만든다. Python으로는 스크립트를 실행할 수 없으므로:
  1. 기본: 브라우저로 원본을 연 뒤 렌더링된 DOM을 `Data/D01_1014.rendered.html`로 저장해 두고(원본은 그대로), 빌드 스크립트는 이 파일이 있으면 이것을 분석한다.
  2. 스냅샷이 없으면 D1은 정적 구간 7개만 만들고 빌드 로그에 경고를 남긴다.
  - (선택) Playwright로 스냅샷 저장을 자동화할 수 있으나 MVP 필수는 아니다.
- 체크박스 키: D1은 `data-key`, D2~D17은 `data-k`를 읽는다. 키는 Day 안에서만 고유하다고 보고 `lesson_id`와 함께 저장한다.
- 원본 구성요소 → 블록 → Streamlit 렌더링 매핑 (출현 빈도 순)

| 원본 class | 용도 | Block kind | Streamlit 렌더링 |
|---|---|---|---|
| `codebar` + `copy`, `prompt pre` | 코드·프롬프트 + 복사 버튼 (약 330개) | `code` | `st.code` (복사 버튼 기본 제공) |
| `chk` / `step` / `steps` / `check` | 단계 체크리스트 (약 235개) | `check` | `st.checkbox` (진행 상태와 연동) |
| `tip` / `hint` | 팁·힌트 | `callout` | 스타일 입힌 `st.html` (초심자: 펼침 / 숙련자: `st.expander`로 접힘 — §13 결정 필요) |
| `tbl` / `tblw` | 표 | `table` | `st.html` + 가로 스크롤 래퍼 |
| `tabs` + `data-job` | 직군별 내용 전환 | `jobs` | `st.segmented_control` (선택값 `prefs.job`에 저장) |
| `os-win` / `os-mac` (D5만) | OS별 안내 | `os` | `st.segmented_control` (선택값 `prefs.os`에 저장) |
| `panel` / `card` / `box` | 묶음 영역 | `card` | `st.container(border=True)` |
| 그 외 | 일반 본문 | `html` | 정제 후 `st.html` |

- 매핑에 없는 구성요소는 `html` 블록으로 기본 스타일로 보여주고 깨지지 않게 한다. 빌드 로그에 미처리 class 목록을 출력한다.
- 정제: `<script>`, `<nav class="toc">`, `on*` 이벤트 속성, 외부 스크립트(cdn.jsdelivr.net 등)를 제거한다. 원본 `<style>`은 쓰지 않고 LearnFlow CSS를 적용한다.
- 외부 링크(github.com, nodejs.org 등)는 `target="_blank" rel="noopener"`로 새 탭에서 연다.
- 주의: 블록이 위젯(체크박스·코드)을 경계로 나뉘므로 HTML 태그가 블록 사이에 걸치지 않게 **최상위 자식 단위로** 자른다. 카드 안에 위젯이 있으면 `card` 블록의 `children`으로 재귀 처리한다.

## 9. 디자인
- **공통 디자인 시스템**: WONMORE 공통 디자인 시스템(`WONMORE/Designsystem.md`)을 따른다. WONMORE 공통 디자인 시스템은 **원티드 몽타주(Montage) 디자인 시스템을 참고**해 만든 것으로 가정한다.
- **컬러 토큰**: `feature/LearnFlow/colorsystem.md` 값을 쓴다. 원티드 브랜드 컬러 기준이다.
  - **초심자 모드 = 원티드 Blue** (`--beginner: #0066FF`, 흰 배경 4.8:1). 연한 선택 배경 위 글자는 `--beginner-strong: #0057D9`
  - **숙련자 모드 = 원티드 Violet** (`--advanced: #8364FF`, 4.0:1이라 아이콘·테두리·큰 글씨만). 글자·CTA 배경은 `--advanced-strong: #6541F2`(5.9:1)
  - 홈 = Blue + Violet 조합, 경고 = 원티드 Orange `#FF5C00`(아이콘·테두리) + 글자 `--warning: #B85A20`
  - 포인트 컬러는 주요 행동(CTA), 선택된 구간, 진행 표시에만 쓴다.
- **글꼴**: Pretendard (CDN CSS를 `lib/theme.py`에서 불러옴, `config.toml`의 `font`는 `sans-serif`). 크기 단계는 `WONMORE/Designsystem.md` §2 표를 따른다. 원본 수업 본문은 Body 1 Reading(16/26px).
- **Streamlit 적용 방식**
  - 기본 테마는 `.streamlit/config.toml`(`base="light"`, `primaryColor`, `backgroundColor="#FAFAFC"`, `font`)로 정한다.
  - `config.toml`의 `primaryColor`는 실행 중에 바뀌지 않으므로, 학습 모드별 포인트 컬러는 `lib/theme.py`가 페이지마다 CSS 변수를 `st.html('<style>…</style>')`로 주입해 바꾼다.
  - 커스텀 CSS는 `lib/theme.py` 한 곳에서만 관리한다. Streamlit 내부 class 이름(`st-emotion-cache-*`)에 의존하지 않고 `data-testid`와 `st.container(key=...)`가 만드는 `st-key-*` class를 기준으로 쓴다.
- **진행 상태 표시**: 색만으로 구분하지 않는다. `시작 전 ○ / 진행 중 ◐ / 완료 ✓`처럼 아이콘과 텍스트를 같이 쓴다.
- **체크인 상태**: 잘 따라감 / 조금 헤맴 / 막힘도 아이콘과 텍스트를 같이 쓴다. 막힘에는 경고색(오렌지)을 쓴다.
- **카드·간격·모서리**: 흰 카드, 얇은 테두리, 카드 20px / 버튼 12px / 태그 999px 모서리, 8px 간격 단위.
- **애니메이션**: 커스텀 애니메이션은 MVP에서 만들지 않는다(Streamlit 기본 전환 사용). 추가한다면 150~300ms ease-out, `prefers-reduced-motion` 존중.
- **반응형**: 창을 줄여서 보는 경우를 기본으로 고려한다. `st.set_page_config(layout="wide")`.

| 너비 | 레이아웃 |
|---|---|
| 1200px 이상 | 사이드바(구간 목록) + 본문 열(최대 760px) + 기록 열 (`st.columns([7, 3])`) |
| 768~1199px | 사이드바 접힘 가능, 본문 + 기록 열 유지 |
| 767px 이하 | 사이드바는 햄버거로 열기, 기록 열은 본문 아래로 쌓임 (Streamlit 기본 동작) |

- 최소 지원 너비 375px. 어떤 너비에서도 페이지 가로 스크롤 없음 (코드 블록·표 내부 스크롤만 허용).
- 모든 버튼에 보이는 포커스 표시(Streamlit 기본 포커스 링을 CSS로 지우지 않는다).

## 10. 테스트 / 인수 기준
**자동 테스트** (`pytest`, UI는 `streamlit.testing.v1.AppTest`)
- [ ] 빌드 스크립트가 11개 파일을 모두 분석하고, 구간 수가 §8 표와 일치한다 (D1은 스냅샷이 있을 때 11)
- [ ] 생성 JSON에 `<script>`, `on*` 속성, `nav.toc`가 남아 있지 않다
- [ ] 공백만 있는 기록은 저장되지 않는다
- [ ] 깨진 사용자 데이터 파일이 백업되고 앱이 기본값으로 시작한다
- [ ] 저장 → 재시작 → 진행 상태·기록·모드·이어보기가 그대로다

**수동 확인**
- [ ] 11개 Day가 D1~D10, D17 순서로 표시된다
- [ ] 원본 메뉴가 보이지 않고, 사이드바 구간 목록에서 현재 구간이 강조된다
- [ ] 구간을 누르거나 이전/다음 버튼을 누르면 해당 구간으로 이동하고 URL이 바뀐다
- [ ] 코드 복사, 단계 체크박스, 직군·OS 전환이 동작한다
- [ ] 진행 상태가 §4 전환 규칙대로 사이드바와 Day 카드에 반영된다
- [ ] 체크인에서 헤맴·막힘을 고르면 입력칸이 열리고 저장된다
- [ ] 기록 열에 그 Day의 기록이 구간별로 모여 보이고, 다른 Day 기록과 섞이지 않는다
- [ ] 삭제 확인 후 해당 기록만 삭제된다
- [ ] 1280 / 1024 / 768 / 375px에서 잘림과 페이지 가로 스크롤이 없다
- [ ] `git status`에 `Data/`, `lessons.generated.json`, `.userdata/`가 나오지 않는다

## 11. 일정 (약 4시간)
| 시간 | 작업 |
|---|---|
| 0~20분 | 가상환경·`requirements.txt`(streamlit, beautifulsoup4, lxml, pytest), `.gitignore`, `config.toml`, `lib/theme.py` 토큰 |
| 20~90분 | `build_lessons.py`: 구간 분석·정제·블록 분리·JSON 생성, D1 스냅샷 처리, 테스트 |
| 90~140분 | 홈(Day 카드) + 상세(사이드바 구간 목록, 블록 렌더러: code·html·table·callout 우선) |
| 140~170분 | `lib/storage.py` + 진행 상태 + 체크박스 + 이어보기 |
| 170~205분 | 체크인 + 기록 작성 + 기록 열 (조회·삭제 dialog) |
| 205~240분 | 학습 모드 컬러, 반응형 점검, AppTest·수동 QA |

- 가장 큰 위험은 **블록 분리**(원본 구성요소 매핑과 위젯 경계 자르기)다. 90분 시점에 끝나지 않으면 체크박스·코드만 위젯으로 빼고 나머지는 구간 통째로 `html` 블록으로 둔 채 다음 단계로 넘어간다.
- 직군·OS 전환이 시간 안에 안 되면 모든 내용을 펼쳐서 보여주고 P1로 미룬다.
- Streamlit은 위젯을 누를 때마다 스크립트 전체가 다시 실행되므로, 수업 JSON 읽기는 `st.cache_data`, 사용자 데이터 파일은 저장할 때만 쓴다.

## 12. 후속 서비스 연동 방향
- WONMORE 아래 LearnFlow(학습 탐색)·PeerLoop(동료 학습)·GrowthLog(성장 기록)·AI Tutor(복습)를 별도 서비스로 소개한다. 이번 MVP에서는 다른 서비스와의 API 연동이나 데이터 공유를 구현하지 않는다. 체크인의 `stuck` 기록은 나중에 PeerLoop·AI Tutor로 넘길 후보 데이터다.
- **WONMORE 랜딩 연결**: `WONMORE_landing.html`의 LearnFlow 버튼은 로컬 실행 주소(`http://localhost:8501`)로 연결한다. 공개 배포 전까지 랜딩에서 "로컬 실행 전용"임을 표시한다.

## 13. 남은 확인 사항
- 원본 수업 자료의 재배포 허용 여부 (허용 전까지 공개 배포 금지)
- 몽타주 의미 토큰·모서리·그림자 실제 값 (공개 문서에 없음, Figma 키트 확인 필요 — `WONMORE/Designsystem.md` §8)
- 학습 모드에 따라 컬러 외에 무엇을 다르게 할지 (제안: 초심자는 팁·힌트 펼침, 숙련자는 접힘)

---
## 변경 이력

### v0.2 → v0.3
| 항목 | v0.2 | v0.3 |
|---|---|---|
| 기술 스택 | Vite + React (언급만) | Python + Streamlit (명시) |
| 빌드 스크립트 | Node + jsdom | Python + BeautifulSoup |
| D1 처리 | jsdom으로 스크립트 실행 | 브라우저 렌더링 스냅샷 파일 분석, 없으면 정적 7구간 |
| D1 구간 수 | 7 + 스크립트 생성 | 11 (정적 7 + `m1`~`m4`) |
| 체크박스 키 | `data-k` | D1 `data-key`, 나머지 `data-k` |
| 구간 데이터 | `html` 문자열 하나 | `blocks` 목록 (위젯 렌더링용) |
| 구간 이동 | sticky 가로 탭 | 사이드바 구간 목록 + 이전/다음 버튼 + URL 반영 |
| 저장소 | localStorage `learnflow.v1.*` 5개 키 | 로컬 JSON 파일 1개, 원자적 쓰기, 깨짐 복구 |
| 진행 상태 | 상태만 정의 | 전환 규칙 명시, 체크인 여러 번 → 최근 값 기준 |
| 기록 패널 | 옆 패널 / 드로어 / 하단 시트 | `st.columns` 오른쪽 열 (좁으면 아래로 쌓임) |
| 삭제 확인 | 방식 미정 | `st.dialog` |
| 직군·OS 선택 | 저장 여부 OS만 | `prefs.job`, `prefs.os` 저장 |
| 컬러 | `#4E8BFF` / `#A76AF2` | 원티드 공식 Blue `#0066FF` / Violet `#8364FF` + 대비 보정 토큰, CSS 주입 방식 명시 |
| 글꼴·화면 기준 | 없음 / 1280px | Pretendard, 몽타주 기준 1200px |
| 키보드 ←/→, 애니메이션 | P0 | MVP 제외 (Streamlit 기본 동작) |
| 테스트 | 수동 체크리스트 | pytest + AppTest 자동 테스트 추가 |
| 경로 | `feature/Learn Step/` | `feature/LearnFlow/` |

### v0.1 → v0.2
| 항목 | v0.1 | v0.2 |
|---|---|---|
| 콘텐츠 | 원본 링크만 제공, 재구성 금지 | 자동 분석 후 구간별로 재구성해 보여줌 (내용 생성은 금지) |
| 탐색 | 수업 목록 → 원본 열기 | sticky 구간 탭 |
| 기록 단위 | 수업 | Day + 구간, 체크인 추가 |
| 진행 | 없음 | 구간별 진행 표시, 이어보기 |
| 노트 화면 | 별도 페이지 | 상세 화면 옆 패널 (Day별 기록) |
| Day 표기 | D01 + 날짜 | D1, D2… (날짜 미표시) |
| 학습 모드 | 없음 | 초심자(블루) / 숙련자(퍼플) |
| 저장 키 | `learnflow.notes.v1` | `learnflow.v1.*` 5개 |
| GitHub | 언급 없음 | `Data/`·생성 JSON 업로드 금지 |
