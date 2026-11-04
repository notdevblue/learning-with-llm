# learning

직접 공부할 때 에이전트를 선생님으로 두는 플러그인이다. 설명, 마일스톤, 읽을 곳, 중간 질문을 준다. 코드와 결과물은 사용자가 만든다.

스킬 본문은 [`plugins/learning/skills/learning/SKILL.md`](plugins/learning/skills/learning/SKILL.md) 하나다. 플러그인 정보는 [`plugins/learning/plugin.json`](plugins/learning/plugin.json)에 있고, 목록은 [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) 하나다. 다른 경로에 있는 같은 이름 파일은 이 둘을 가리키는 링크다.

## 설치

이 저장소를 에이전트에게 주고 플러그인을 넣으라고 한다.

```text
https://github.com/notdevblue/learning-with-llm 이 플러그인 넣어줘
```

에이전트는 지금 응답 중인 도구에만 설치한다. 사용자가 도구를 지정하면 그 도구에만 한다.

Grok:

```bash
grok plugin marketplace add notdevblue/learning-with-llm
grok plugin install learning --trust
```

Claude Code:

```bash
claude plugin marketplace add notdevblue/learning-with-llm
claude plugin install learning@learning-with-llm
```

Codex:

```bash
codex plugin marketplace add notdevblue/learning-with-llm
```

마켓플레이스를 추가한 뒤 플러그인 목록에서 `learning`을 설치한다.

이미 설치되어 있으면 덮어쓰거나 지우지 말고 사용자에게 묻는다. 설치한 경로를 알려 주고, 그다음 세션에서 쓰라고 한다.

## 플러그인 설치가 안 될 때

`plugins/learning/skills/learning/` 폴더를 복사한다. `SKILL.md`는 그 폴더 바로 안에 있다. 저장소 전체를 넣지 않는다. 링크는 원본으로 쓰지 말고, 실제 파일이 되게 복사한다. 대상에 이미 `learning`이 있으면 덮어쓰지 말고 묻는다.

| 도구 | 개인 경로. 모든 프로젝트 | 프로젝트 경로 |
| --- | --- | --- |
| Grok | `~/.grok/skills/learning` | `<프로젝트>/.grok/skills/learning` |
| Claude Code | `~/.claude/skills/learning` | `<프로젝트>/.claude/skills/learning` |
| Codex | `~/.agents/skills/learning` | `<프로젝트>/.agents/skills/learning` |

## 호출

스킬 이름은 `learning`이다. Grok에서는 `/learning`, Claude Code에서는 `/learning:learning`, Codex에서는 `$learning`이다. 공부, 이어서, 이해했는지처럼 스킬 설명에 있는 말로 시작해도 된다.

진행과 확인은 스킬 폴더의 `scripts/progress.py`가 공부하는 프로젝트의 `study/<slug>/progress.json`에 남긴다. 답은 저장하지 않는다. 이 기록은 플러그인이나 스킬을 복사할 때 같이 넣지 않는다.
