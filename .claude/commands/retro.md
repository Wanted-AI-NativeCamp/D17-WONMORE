---
description: 오늘 작업을 정리해 대시보드에 붙여넣을 회고 글을 만듭니다. 나온 결과 전체를 복사해서 붙여넣으세요. 끝에 file을 붙이면 결과 파일도 만들어요.
argument-hint: [직군(선택, 여러 개는 띄어쓰기로): developer=개발자 po=기획자 designer=디자이너 marketer=마케터] [file(선택): 결과를 파일로도 저장] 예: /retro designer po file
allowed-tools: Read, Glob, Grep, Write, Bash(git rev-parse:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*)
---

# /retro — 오늘의 회고 만들기

인자: `$ARGUMENTS`

## 지켜야 할 것 (어기면 안 됨)
- **기본은 파일을 만들거나 고치지 않는다.** 읽기만 한다. (git은 `rev-parse`, `status`, `diff`, `log`만 쓴다) 단, 인자에 `file`이 있을 때만 아래 "2-1. file 인자"대로 결과 파일 **한 개**를 새로 만든다. 그 밖의 파일은 어떤 경우에도 만들거나 바꾸지 않는다.
- **외부 서비스·네트워크를 부르지 않는다.** API 키도 쓰지 않는다.
- **출력은 JSON 한 개뿐이다.** 앞뒤에 설명 문장을 붙이지 않는다. 코드 블록(```json … ```)으로 감싸는 것은 허용한다. 첫 줄은 `{` 또는 ```` ```json ````, 마지막 줄은 `}` 또는 ```` ``` ````여야 한다.
- 경고할 내용은 JSON 밖이 아니라 `warnings` 배열에 넣는다.
- `warnings` 문구는 한국어 쉬운 말로, `어디: 무엇이 문제인지 (어떻게 하면 되는지)` 형식으로 쓴다. 영어 에러 원문이나 코드 용어는 그대로 쓰지 않는다.

## 1. 읽을 것
1. **현재 세션의 대화**: 무엇을 요청했고 AI가 무엇을 내놓았는지의 흐름.
2. **오늘 바뀐 코드**:
   - `git rev-parse --is-inside-work-tree`가 성공하면 `git status --short`와 오늘 날짜 변경분(`git diff HEAD --stat`, 필요하면 `git log --since=midnight --stat`)을 읽는다. 변경이 하나도 없으면 `warnings`에 `"변경 내용: 코드 변경 없음 (문제는 아니에요. 대화 내용만으로 정리했어요. 코드를 고친 뒤 실행하면 더 자세해져요)"`를 넣고 계속한다.
   - git이 아니면 `warnings`에 `"변경 내용: 변경분을 git으로 읽지 못했어요 (이 폴더는 변경 기록(git)이 없어요. 오늘 수정된 파일 목록만 참고했어요. 더 자세한 회고가 필요하면 git이 있는 폴더에서 실행해 주세요)"`를 넣고, 오늘 수정된 파일 목록만 Glob으로 훑어본다. 그래도 중단하지 않는다.
   - 변경이 매우 크면 파일 이름과 통계만 보고 내용은 꼭 필요한 부분만 읽는다. (구독 사용량 절약)
3. 코드 변경이 적거나 없으면 변경 파일보다 "요청한 것 → AI가 내놓은 결과"의 흐름을 중심으로 정리한다.

## 2. 인자 처리 (직군)
- 허용 값: `developer`, `po`, `designer`, `marketer`. 공백으로 여러 개 가능.
- 인자가 없으면 `"role": []`, `extension`은 만들지 않는다(또는 `{}`).
- 허용 값이 아닌 것(예: `chef`)은 `role`에 넣지 않고 `warnings`에 `"직군: 알 수 없는 직군이에요 chef (developer(개발자), po(기획자), designer(디자이너), marketer(마케터) 중에서 골라 다시 실행해 주세요)"`처럼 쓴다. 직군을 추측해서 대신 고르지 않는다.
- 같은 값을 두 번 쓰면 한 번만 넣는다.

## 2-1. file 인자 (결과를 파일로도 저장)
터미널에서 결과를 복사하면 줄바꿈이 끼어들어 글이 깨질 수 있어서, 원하면 결과를 파일로도 받을 수 있게 한다.
- 인자에 `file`이 있으면(대소문자 무시) 출력할 JSON과 **똑같은 내용**을 `retro-out/retro-YYYY-MM-DD.json`에 저장한다. (Write 도구, 들여쓰기 2칸, 코드 블록 표시 없이 JSON만)
- 같은 이름의 파일이 이미 있으면 **덮어쓰지 않는다.** `retro-out/retro-YYYY-MM-DD-2.json`, `-3`… 처럼 없는 첫 이름을 쓴다. (Glob으로 먼저 확인한다)
- 파일은 이 한 개만 만든다. 파일을 저장한 뒤에 JSON을 출력한다.
- `file`은 직군이 아니다. `role`에 넣지 않고 "알 수 없는 직군" 경고도 만들지 않는다.
- 저장에 실패하면 중단하지 않고 JSON은 그대로 출력하며, `warnings`에 `"파일: 결과 파일을 저장하지 못했어요 (retro-out 폴더에 쓸 수 있는지 확인해 주세요. 위 결과를 복사해 붙여넣어도 돼요)"`를 넣는다.
- `file`이 없으면 이 장은 건너뛴다. 파일을 만들지 않는다.

## 3. 출력 형식
```json
{
  "date": "YYYY-MM-DD",
  "project": "폴더 이름 등 (모르면 생략)",
  "role": [],
  "common": {
    "learned": [],
    "stuck": [{ "topic": "", "solution": "", "minutes": 0, "tags": [] }],
    "ai_usage": { "delegated": [], "tools": [], "edit_level": "" },
    "reflection": "",
    "tomorrow": []
  },
  "extension": {},
  "warnings": []
}
```
- `date`는 오늘 날짜(실제 존재하는 날짜).
- `stuck`: `topic`, `solution`은 문자열(필수). `minutes`는 0 이상 정수이며, 모르면 생략한다(지어내지 않는다). `tags`는 문자열 배열.
- **`ai_usage`는 항상 3개 항목(`delegated`, `tools`, `edit_level`)을 모두 채운다.**
  - `delegated`: AI에게 맡긴 일.
  - `tools`: **이 세션 대화에 실제로 나온** 도구·에이전트 이름만. 나오지 않은 이름은 절대 쓰지 않는다.
  - `edit_level`: AI 결과를 사용자가 얼마나·어떻게 고쳤는지 한 줄. (그대로 썼으면 그렇게, 여러 번 고쳤으면 그렇게)
- 직군을 하나 고르면 `extension` 키는 **직군당 2개 이하**:

| 직군 | extension 키 | 항목 구조 |
|---|---|---|
| developer | `error_patterns` (이것만) | `{ "error": "", "cause": "" }` |
| po | `decisions`, `scope_changes` | `{ "what": "", "why": "" }`, `{ "change": "", "reason": "" }` |
| designer | `ui_decisions`, `design_vs_result` | `{ "what": "", "why": "" }`, 문자열 |
| marketer | `copy_changes`, `hypotheses` | `{ "before": "", "after": "" }`, `{ "hypothesis": "", "metric": "" }` |

- 여러 직군을 골랐으면 고른 직군의 키만 합쳐서 넣는다. 고르지 않은 직군의 키는 넣지 않는다.
- 위 표에 없는 필드는 만들지 않는다.

## 4. 사람마다 다르게 쓰기
- `learned`와 `reflection`은 **고른 직군의 관점**으로 쓴다. (developer: 에러와 해결 / po: 결정과 범위 / designer: UI 판단과 시안 차이 / marketer: 문구와 가설) 직군이 없으면 공통 관점으로 쓴다.
- 또 **그날 AI를 어떻게 썼는지**(맡긴 일, 쓴 도구, 고친 정도)에 맞춰 쓴다. AI 결과를 그대로 썼는지, 여러 번 고쳤는지에 따라 `reflection` 문장이 달라져야 한다.
- 다른 사람에게도 그대로 붙여 쓸 수 있는 일반적인 문장은 쓰지 않는다. 오늘 세션에서 실제로 있었던 일만 근거로 쓴다.
- 대화에 근거가 없는 항목은 지어내지 말고 빈 배열이나 생략으로 둔다.

## 5. 마지막 확인 (출력 전에 속으로)
- JSON 문법이 맞는가? 설명 문장이 JSON 밖에 없는가?
- `role` 값이 허용 목록 안에 있는가? `extension` 키가 고른 직군 것뿐인가?
- `ai_usage` 3개 항목이 다 있고 `tools`에 대화에 없는 이름이 없는가?
- 파일을 만들거나 바꾸지 않았는가? (`file`이 없으면 아무 파일도 안 만들었는가, 있으면 `retro-out/`에 새 파일 하나만 만들었는가, 기존 파일을 덮어쓰지 않았는가)
