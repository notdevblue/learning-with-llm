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

## 사용

새 세션에서 주제로 시작한다. Codex는 `$learning`으로 연다.

```text
/learning 프로세스 스케줄러를 이해하고 싶다. 아주 작은 스케줄러를 내가 짜는 게 목표다.
```

에이전트는 먼저 이미 설명하거나 할 수 있는 것이 어디까지인지, 어디서 멈추는지를 묻는다. 그다음 첫 마일스톤과 읽을 곳을 정한다. 원리를 설명한 뒤 질문을 하나 던지고, 답을 받기 전에는 다음으로 넘어가지 않는다.

```text
준비 상태가 아닌 작업이 있으면 스케줄러는 어떻게 고르나?
```

사용자는 그 답을 자기 말로 하고, 스케줄러 코드도 직접 쓴다. 막히면 힌트를 받고, 빈틈이 있으면 그 지점에 남는다.

다음 세션에서는 기록을 이어서 연다.

```text
/learning 이어서
```

답이 없는 질문이 있으면 그 질문을 다시 보여주고 기다린다. 아니면 현재 마일스톤과 다음에 할 일을 알려 준다.

결과물을 만든 뒤 확인을 요청한다.

```text
스케줄러 확인 부탁해
```

확인 문제를 풀면, 기준에 못 미칠 때는 마일스톤을 더 작게 나누거나 각도를 바꿔 다시 연다. 기준을 넘으면 통과시키고 다음 마일스톤을 연다.
