## 컬러 사용 전략
전체적으로 화이트 기반의 깔끔한 UI를 유지하면서, 화면마다 다른 포인트 컬러로 개성을 주는 방향
- 메인 홈: 원티드 몽타주 디자인 시스템의 블루, 퍼플 조합
- 초심자 학습: 원티드 몽타주 디자인 시스템의 블루
- 숙련자 학습: 원티드 몽타주 디자인 시스템의 퍼플
- 공동 학습 아카이브: 원티드 몽타주 디자인 시스템의 핑크
- 경고 시멘틱 컬러: 원티드 몽타주 디자인 시스템의 오렌지

## CSS
:root {
  /* Neutral */
  --bg: #FAFAFC;
  --surface: #FFFFFF;
  --surface-subtle: #F6F7FA;
  --text-primary: #252832;
  --text-secondary: #717987;
  --border: #E6E8EF;

  /* Page Accent */
  --home-blue: #4E8BFF;
  --home-purple: #A76AF2;
  --beginner: #4E8BFF;
  --advanced: #A76AF2;
  --archive: #D94DAA;

  /* Semantic */
  --warning: #B85A20;
  --warning-bg: #FFF1E6;

  /* Shape */
  --radius-card: 20px;
  --radius-button: 12px;
  --radius-tag: 999px;

  /* Spacing */
  --space-unit: 8px;
}