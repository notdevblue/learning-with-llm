# learning

직접 공부할 때 에이전트를 선생님으로 두는 스킬이다. 설명, 마일스톤, 읽을 곳, 중간 질문을 준다. 코드와 결과물은 사용자가 만든다.

본문은 [`skills/learning/SKILL.md`](skills/learning/SKILL.md) 하나다. `.grok/skills/learning`, `.claude/skills/learning`, `.agents/skills/learning`은 그 폴더를 가리키는 링크다.

## 설치

이 저장소를 에이전트에게 주고 스킬을 넣으라고 한다.

```text
https://github.com/notdevblue/learning-with-llm 이 스킬 넣어줘
```

에이전트는 아래만 따른다.

1. `skills/learning/`을 가져온다. `SKILL.md`는 그 폴더 바로 안에 있다. 저장소 전체를 스킬 폴더에 넣지 않는다. `.grok`, `.claude`, `.agents` 아래의 `learning`은 링크이므로 복사 원본으로 쓰지 않는다.
2. 사용자가 도구를 지정하지 않으면, 지금 응답 중인 도구의 개인 경로에만 넣는다. 이 프로젝트에만 넣으라고 하면 개인 경로 대신 프로젝트 경로를 쓴다.
3. 대상에 이미 `learning`이 있으면 덮어쓰지 말고 사용자에게 묻는다.
4. 폴더를 그대로 복사해서 `SKILL.md`가 대상의 `learning/` 바로 아래에 있게 한다. 링크는 풀어서 실제 파일로 둔다.
5. 복사한 경로를 알려 준다. 그다음 세션에서 읽힌다.

| 도구 | 개인 경로. 모든 프로젝트 | 프로젝트 경로 |
| --- | --- | --- |
| Grok | `~/.grok/skills/learning` | `<프로젝트>/.grok/skills/learning` |
| Claude Code | `~/.claude/skills/learning` | `<프로젝트>/.claude/skills/learning` |
| Codex | `~/.agents/skills/learning` | `<프로젝트>/.agents/skills/learning` |

## 호출

Grok과 Claude Code에서는 `/learning`이다. Codex에서는 `$learning`이다. 공부, 이어서, 이해했는지처럼 스킬 설명에 있는 말로 시작해도 된다.

진행 기록은 공부하는 프로젝트의 `study/<slug>/progress.md`에 생긴다. 스킬을 복사할 때 같이 넣지 않는다.
