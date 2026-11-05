# -*- coding: utf-8 -*-
"""작업 일지 훅.

Claude가 Write/Edit 도구로 파일을 저장한 직후(PostToolUse) 실행된다.
.claude/작업일지.txt 에 한 줄씩 덧붙인다.

한 줄 형식:
    2026-11-05 14:32:10 | Edit | src/app.py

어떤 경우에도 작업을 막지 않는다. 실패하면 조용히 종료(exit 0)한다.
"""
import json
import os
import sys
from datetime import datetime


def main():
    # 입력을 바이트로 받아 UTF-8로 직접 해석한다 (Windows 콘솔 인코딩 영향 차단)
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))

    tool = data.get("tool_name", "?")
    file_path = (data.get("tool_input") or {}).get("file_path", "")
    if not file_path:
        return

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()

    # 프로젝트 안의 파일이면 상대 경로로, 밖이면 절대 경로 그대로
    try:
        rel = os.path.relpath(file_path, project_dir)
        shown = file_path if rel.startswith("..") else rel
    except ValueError:  # 드라이브가 다른 경우 (Windows)
        shown = file_path
    shown = shown.replace("\\", "/")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{now} | {tool} | {shown}\n"

    log_path = os.path.join(project_dir, ".claude", "작업일지.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8", newline="\n") as f:
        f.write(line)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # 일지를 못 써도 조용히 넘어간다
    sys.exit(0)
