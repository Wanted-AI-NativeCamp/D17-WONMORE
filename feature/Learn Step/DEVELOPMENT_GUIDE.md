# LearnFlow 개발 시작 가이드 (PRD v0.2 기준)

## 1. 프로젝트 생성
앱은 `feature/Learn Step/app/`에 만든다. (폴더 이름에 공백이 있으니 경로는 항상 따옴표로 감싼다.)
```bash
cd "feature/Learn Step"
npm create vite@latest app -- --template react
cd app
npm install
npm install -D jsdom
npm run dev
```

## 2. 폴더 구조
```text
D11-agent/                      # 저장소 루트 (origin: Wanted-AI-NativeCamp/D17-WONMORE)
├── .gitignore                  # Data/, 생성된 수업 JSON 제외
├── CLAUDE.md                   # 공통 작업 규칙
├── Data/                       # 원본 수업 HTML (읽기 전용, git 제외)
│   ├── D01_1014.html
│   └── ...
├── WONMORE/
│   └── Designsystem.md         # WONMORE 공통 디자인 시스템 (몽타주 참고)
├── WONMORE_landing.html        # 상위 브랜드 랜딩 (팀 작업 가정)
└── feature/
    └── Learn Step/
        ├── PRD.md              # LearnFlow PRD v0.2
        ├── DEVELOPMENT_GUIDE.md
        ├── colorsystem.md      # LearnFlow 컬러 토큰
        └── app/                # Vite + React 앱
            ├── scripts/
            │   └── build-lessons.mjs     # ../../../Data/*.html 분석 → src/data/lessons.generated.json
            ├── src/
            │   ├── data/
            │   │   └── lessons.generated.json   # 생성물 (git 제외)
            │   ├── components/
            │   │   ├── DayCard.jsx
            │   │   ├── SectionTabs.jsx          # sticky 구간 탭
            │   │   ├── SectionView.jsx          # 재구성된 구간 본문
            │   │   ├── CheckIn.jsx              # 잘 따라가고 있나요?
            │   │   ├── NoteForm.jsx
            │   │   ├── DayNotesPanel.jsx        # 옆 패널 / 드로어 / 하단 시트
            │   │   └── content/                 # 원본 구성요소 대체 컴포넌트
            │   │       ├── CodeBlock.jsx
            │   │       ├── StepChecklist.jsx
            │   │       ├── Callout.jsx
            │   │       ├── Table.jsx
            │   │       ├── SegmentedTabs.jsx
            │   │       └── OsSwitch.jsx
            │   ├── pages/
            │   │   ├── Home.jsx                 # 모드 선택, 이어보기, Day 목록
            │   │   └── DayDetail.jsx
            │   ├── lib/
            │   │   └── storage.js               # learnflow.v1.* 읽기·쓰기 (이 파일만 localStorage 접근)
            │   ├── styles/
            │   │   └── tokens.css               # colorsystem.md 토큰
            │   ├── App.jsx
            │   └── main.jsx
            └── package.json
```

## 3. 구현 순서
1. `.gitignore`에 `Data/`, `**/lessons.generated.json` 등록 후 `git status`로 확인
2. `build-lessons.mjs`: 파일명 → Day(`D01` → `D1`), `<section id>` + `<h2>` 추출, script·nav 제거, 미처리 class 로그
3. D1 처리 (jsdom으로 스크립트 실행 후 DOM 추출, 실패 시 수동 매핑)
4. Day 목록 → 상세 → sticky 탭 → 구간 렌더링
5. 원본 구성요소 컴포넌트 (CodeBlock → StepChecklist → Callout → Table → SegmentedTabs → OsSwitch 순)
6. 진행 표시·이어보기 (`learnflow.v1.progress`, `learnflow.v1.resume`)
7. 체크인·기록·옆 패널 (`learnflow.v1.checkins`, `learnflow.v1.notes`)
8. 학습 모드 컬러 (`learnflow.v1.prefs`), 반응형 점검, PRD §10 인수 기준 점검

## 4. 안전/배포 주의
- `Data/`와 `lessons.generated.json`은 커밋하지 않는다. 재배포 권한을 확인하기 전에는 공개 배포하지 않는다.
- 원본 HTML을 수정하지 않는다. 원본에 없는 내용을 생성하지 않는다.
- localStorage 접근은 `lib/storage.js`에서만, 키는 `learnflow.v1.` 접두사만 쓴다.
- localStorage는 브라우저별 저장이라 기기 간 동기화·백업이 되지 않는다.
- WONMORE 랜딩 페이지는 별도 작업이며 LearnFlow P0보다 우선하지 않는다.
