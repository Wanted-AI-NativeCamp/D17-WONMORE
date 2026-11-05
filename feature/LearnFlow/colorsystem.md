## 컬러 사용 전략
전체적으로 화이트 기반의 깔끔한 UI를 유지하면서, 화면마다 다른 포인트 컬러로 개성을 주는 방향.
값은 `WONMORE/Designsystem.md` §1(원티드 브랜드 컬러 + 접근성 보정)을 따른다.
- 메인 홈: Blue + Violet 조합 (Sky Blue는 장식 보조)
- 초심자 학습: Blue
- 숙련자 학습: Violet (글자·CTA는 `--advanced-strong`)
- 공동 학습 아카이브: Pink (장식만)
- 경고 시멘틱 컬러: Orange (아이콘·테두리) + `--warning` (글자)

## CSS
```css
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css");

:root {
  /* Font */
  --font-sans: Pretendard, -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  --font-mono: ui-monospace, "SF Mono", Consolas, monospace;

  /* Neutral */
  --bg: #FAFAFC;
  --surface: #FFFFFF;
  --surface-subtle: #F0F4F8;     /* 원티드 Grey */
  --text-strong: #14191E;        /* 원티드 Black, 제목 */
  --text-primary: #252832;       /* 본문 */
  --text-secondary: #5F6673;     /* 보조정보 (흰 배경 4.5:1 이상) */
  --border: #E6E8EF;

  /* Page Accent — 원티드 브랜드 컬러 */
  --home-blue: #0066FF;
  --home-violet: #8364FF;
  --home-sky: #00ADFF;           /* 장식 전용 */
  --beginner: #0066FF;           /* CTA 배경·흰 배경 위 글자 (4.8:1) */
  --beginner-strong: #0057D9;    /* 연한 선택 배경 위 글자 (5.4:1), WONMORE 보정값 */
  --beginner-soft: #E5F0FF;      /* 선택 배경 */
  --advanced: #8364FF;           /* 아이콘·테두리·큰 글씨 (4.0:1) */
  --advanced-strong: #6541F2;    /* 글자·CTA 배경 (5.9:1), WONMORE 보정값 */
  --advanced-soft: #F0ECFF;      /* 선택 배경 */
  --archive: #FF8EFF;            /* 장식 전용 (2.0:1) */

  /* Semantic */
  --warning-accent: #FF5C00;     /* 원티드 Orange, 아이콘·테두리 */
  --warning: #B85A20;            /* 경고 글자 (4.6:1), WONMORE 보정값 */
  --warning-bg: #FFF1E6;

  /* Shape */
  --radius-card: 20px;
  --radius-button: 12px;
  --radius-tag: 999px;

  /* Shadow (몽타주 단계 이름) */
  --shadow-xsmall: 0 1px 2px rgba(20, 25, 30, 0.06);
  --shadow-medium: 0 4px 16px rgba(20, 25, 30, 0.10);

  /* Spacing */
  --space-unit: 8px;
  --gutter: 20px;
}
```
