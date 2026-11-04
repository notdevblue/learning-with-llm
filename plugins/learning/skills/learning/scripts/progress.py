#!/usr/bin/env python3
"""Study progress for the learning skill. The record stores no answers."""

import argparse
import io
import json
import re
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def study_dir(root):
    return root / "study"


def record_path(root, slug):
    return study_dir(root) / slug / "progress.json"


def die(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def topics(root):
    base = study_dir(root)
    if not base.is_dir():
        return []
    found = []
    for path in sorted(base.glob("*/progress.json")):
        found.append((path.parent.name, load(path)))
    return found


def milestone(data, name):
    for item in data["milestones"]:
        if item["name"] == name:
            return item
    return None


def active(data):
    return [item for item in data["milestones"] if item["status"] in ("진행 중", "확인 대기")]


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def blank(topic, goal):
    return {
        "topic": topic,
        "goal": goal,
        "current": "",
        "milestones": [],
        "pending": None,
        "checks": [],
        "next": "",
    }


def render(slug, data):
    current = milestone(data, data.get("current"))
    lines = [
        f"slug: {slug}",
        f"topic: {data['topic']}",
        f"goal: {data['goal']}",
    ]
    if current:
        lines.extend(
            [
                f"current: {current['name']}",
                f"status: {current['status']}",
                f"artifact: {current['artifact']}",
                f"criterion: {current['criterion']}",
                f"shown: {current['understanding']['shown']}",
                f"gap: {current['understanding']['gap']}",
            ]
        )
    else:
        lines.append("current: 없음")
    pending = data.get("pending")
    if pending:
        lines.append(f"pending: {pending['kind']}")
        lines.append("question: |")
        for line in pending["question"].splitlines() or [""]:
            lines.append(f"  {line}")
    else:
        lines.append("pending: 없음")
    lines.append(f"next: {data.get('next', '')}")
    lines.append("milestones:")
    for item in data["milestones"]:
        lines.append(f"- [{item['status']}] {item['name']}")
    return "\n".join(lines)


def open_record(root, slug):
    if not slug or not SLUG.fullmatch(slug):
        die("slug는 영문 소문자, 숫자, 하이픈만 쓴다.")
    path = record_path(root, slug)
    if not path.is_file():
        die(f"기록이 없다: {slug}")
    return path, load(path)


def resolve_slug(root, slug):
    if slug:
        return slug
    found = topics(root)
    if not found:
        die("기록이 없다.")
    open_items = []
    for name, data in found:
        current = milestone(data, data.get("current"))
        if data.get("pending") or (current and current["status"] != "통과"):
            open_items.append(name)
    if len(open_items) == 1:
        return open_items[0]
    if len(found) == 1:
        return found[0][0]
    print("주제가 여러 개다. slug를 고른다.", file=sys.stderr)
    for name, data in found:
        current = milestone(data, data.get("current"))
        status = current["status"] if current else "없음"
        label = current["name"] if current else "없음"
        print(f"{name}\t{status}\t{label}", file=sys.stderr)
    raise SystemExit(2)


def show(slug, data):
    print(render(slug, data))


def cmd_list(root):
    found = topics(root)
    if not found:
        print("기록 없음")
        return
    for slug, data in found:
        current = milestone(data, data.get("current"))
        status = current["status"] if current else "없음"
        label = current["name"] if current else "없음"
        print(f"{slug}\t{status}\t{label}\t{data['topic']}")


def cmd_status(root, slug):
    slug = resolve_slug(root, slug)
    _, data = open_record(root, slug)
    show(slug, data)


def cmd_start(root, topic, goal, slug):
    slug = slug or slugify(topic)
    if not slug or not SLUG.fullmatch(slug):
        die("영문 slug가 필요하다. --slug 로 준다.")
    path = record_path(root, slug)
    if path.exists():
        die(f"이미 있다: {slug}")
    data = blank(topic.strip(), goal.strip())
    if not data["topic"] or not data["goal"]:
        die("주제와 목표 결과물이 필요하다.")
    save(path, data)
    show(slug, data)


def cmd_milestone(root, slug, name, artifact, criterion):
    slug = resolve_slug(root, slug)
    path, data = open_record(root, slug)
    if data.get("pending"):
        die("답이 없는 질문이 있다.")
    name, artifact, criterion = name.strip(), artifact.strip(), criterion.strip()
    if not name or not artifact or not criterion:
        die("이름, 결과물, 기준이 필요하다.")
    if milestone(data, name):
        die(f"같은 이름의 마일스톤이 있다: {name}")
    if active(data):
        die("진행 중인 마일스톤이 있다.")
    data["milestones"].append(
        {
            "name": name,
            "artifact": artifact,
            "criterion": criterion,
            "status": "진행 중",
            "understanding": {"shown": "", "gap": ""},
        }
    )
    data["current"] = name
    save(path, data)
    show(slug, data)


def current_of(data):
    item = milestone(data, data.get("current"))
    if not item:
        die("현재 마일스톤이 없다.")
    return item


def cmd_ask(root, slug, kind, question):
    slug = resolve_slug(root, slug)
    path, data = open_record(root, slug)
    if data.get("pending"):
        die("이미 답이 없는 질문이 있다.")
    if kind not in ("mid", "milestone"):
        die("kind는 mid 또는 milestone 이다.")
    item = current_of(data)
    if item["status"] != "진행 중":
        die("질문은 진행 중인 마일스톤에만 낸다.")
    question = question.strip()
    if not question:
        die("질문이 비어 있다.")
    data["pending"] = {"kind": kind, "question": question, "milestone": item["name"]}
    if kind == "milestone":
        item["status"] = "확인 대기"
    data["next"] = ""
    save(path, data)
    show(slug, data)


def cmd_grade(root, slug, shown, gap):
    slug = resolve_slug(root, slug)
    path, data = open_record(root, slug)
    pending = data.get("pending")
    if not pending:
        die("채점할 질문이 없다.")
    item = milestone(data, pending["milestone"])
    if not item:
        die("질문의 마일스톤이 없다.")
    shown, gap = shown.strip(), gap.strip()
    if not shown and not gap:
        die("사용자가 보인 것 또는 빈틈을 적는다. 답은 적지 않는다.")
    item["understanding"] = {"shown": shown, "gap": gap}
    data["checks"].append(
        {
            "date": date.today().isoformat(),
            "kind": pending["kind"],
            "question": pending["question"],
            "shown": shown,
            "gap": gap,
            "change": "",
        }
    )
    data["pending"] = None
    save(path, data)
    show(slug, data)


def cmd_pass(root, slug):
    slug = resolve_slug(root, slug)
    path, data = open_record(root, slug)
    if data.get("pending"):
        die("답이 없는 질문이 있다.")
    item = current_of(data)
    if item["status"] != "확인 대기":
        die("통과는 확인 대기인 마일스톤만 한다.")
    if item["understanding"]["gap"]:
        die("빈틈이 남아 있다.")
    item["status"] = "통과"
    if data["checks"]:
        data["checks"][-1]["change"] = f"통과: {item['name']}"
    data["current"] = ""
    data["next"] = ""
    save(path, data)
    show(slug, data)


def cmd_revise(root, slug, name, artifact, criterion, reason):
    slug = resolve_slug(root, slug)
    path, data = open_record(root, slug)
    if data.get("pending"):
        die("답이 없는 질문이 있다.")
    item = current_of(data)
    if item["status"] == "통과":
        die("통과한 마일스톤은 다시 두지 않는다.")
    name, artifact, criterion, reason = (
        name.strip(),
        artifact.strip(),
        criterion.strip(),
        reason.strip(),
    )
    if not name or not artifact or not criterion or not reason:
        die("이름, 결과물, 기준, 이유가 필요하다.")
    if milestone(data, name):
        die(f"같은 이름의 마일스톤이 있다: {name}")
    old = item["name"]
    item["status"] = "다시"
    data["milestones"].append(
        {
            "name": name,
            "artifact": artifact,
            "criterion": criterion,
            "status": "진행 중",
            "understanding": {"shown": "", "gap": ""},
        }
    )
    data["current"] = name
    change = f"다시: {old} -> {name}. {reason}"
    if data["checks"]:
        data["checks"][-1]["change"] = change
    else:
        data["checks"].append(
            {
                "date": date.today().isoformat(),
                "kind": "revise",
                "question": "",
                "shown": "",
                "gap": "",
                "change": change,
            }
        )
    save(path, data)
    show(slug, data)


def cmd_next(root, slug, text):
    slug = resolve_slug(root, slug)
    path, data = open_record(root, slug)
    if data.get("pending"):
        die("답이 없는 질문이 있다. 다음 행동을 넘기지 않는다.")
    text = text.strip()
    if not text:
        die("다음 행동이 비어 있다.")
    data["next"] = text
    save(path, data)
    show(slug, data)


def build_parser():
    parser = argparse.ArgumentParser(description="학습 진행과 확인 기록을 다룬다. 답은 저장하지 않는다.")
    parser.add_argument("--root", default=".", help="study/ 를 만들 작업 디렉터리")
    sub = parser.add_subparsers(dest="cmd", required=True)

    start = sub.add_parser("start", help="주제를 만든다")
    start.add_argument("--topic", required=True)
    start.add_argument("--goal", required=True)
    start.add_argument("--slug")

    mile = sub.add_parser("milestone", help="마일스톤을 추가하고 현재로 둔다")
    mile.add_argument("--slug")
    mile.add_argument("--name", required=True)
    mile.add_argument("--artifact", required=True)
    mile.add_argument("--criterion", required=True)

    ask = sub.add_parser("ask", help="질문을 남긴다")
    ask.add_argument("--slug")
    ask.add_argument("--kind", required=True, choices=("mid", "milestone"))
    ask.add_argument("--question", required=True)

    grade = sub.add_parser("grade", help="보인 이해와 빈틈을 남긴다")
    grade.add_argument("--slug")
    grade.add_argument("--shown", default="")
    grade.add_argument("--gap", default="")

    passed = sub.add_parser("pass", help="확인 대기 마일스톤을 통과시킨다")
    passed.add_argument("--slug")

    revise = sub.add_parser("revise", help="현재 마일스톤을 다시로 두고 새 마일스톤을 연다")
    revise.add_argument("--slug")
    revise.add_argument("--name", required=True)
    revise.add_argument("--artifact", required=True)
    revise.add_argument("--criterion", required=True)
    revise.add_argument("--reason", required=True)

    nxt = sub.add_parser("next", help="다음에 할 일을 적는다")
    nxt.add_argument("--slug")
    nxt.add_argument("--text", required=True)

    status = sub.add_parser("status", help="현재 기록을 보여 준다")
    status.add_argument("--slug")

    sub.add_parser("list", help="주제 목록")
    return parser


def dispatch(args):
    root = Path(args.root)
    if args.cmd == "list":
        cmd_list(root)
    elif args.cmd == "status":
        cmd_status(root, args.slug)
    elif args.cmd == "start":
        cmd_start(root, args.topic, args.goal, args.slug)
    elif args.cmd == "milestone":
        cmd_milestone(root, args.slug, args.name, args.artifact, args.criterion)
    elif args.cmd == "ask":
        cmd_ask(root, args.slug, args.kind, args.question)
    elif args.cmd == "grade":
        cmd_grade(root, args.slug, args.shown, args.gap)
    elif args.cmd == "pass":
        cmd_pass(root, args.slug)
    elif args.cmd == "revise":
        cmd_revise(root, args.slug, args.name, args.artifact, args.criterion, args.reason)
    elif args.cmd == "next":
        cmd_next(root, args.slug, args.text)


def keys_of(value):
    found = set()
    if isinstance(value, dict):
        found.update(value)
        for item in value.values():
            found.update(keys_of(item))
    elif isinstance(value, list):
        for item in value:
            found.update(keys_of(item))
    return found


def self_test():
    sink = io.StringIO()
    with redirect_stdout(sink), redirect_stderr(sink), tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        script = Path(__file__).resolve()
        cmd_start(root, "스케줄러", "작은 스케줄러", "scheduler")
        try:
            cmd_start(root, "스케줄러", "작은 스케줄러", "scheduler")
        except SystemExit as err:
            assert err.code == 1
        else:
            raise AssertionError("duplicate start")
        cmd_milestone(root, "scheduler", "전환", "전환 추적", "왜 전환하는지 말한다")
        try:
            cmd_milestone(root, "scheduler", "다른 것", "결과", "기준")
        except SystemExit:
            pass
        else:
            raise AssertionError("second active milestone")
        cmd_ask(root, "scheduler", "mid", "준비 상태가 아니면 어떻게 되나?")
        try:
            cmd_next(root, "scheduler", "다음")
        except SystemExit:
            pass
        else:
            raise AssertionError("next during pending")
        cmd_grade(root, "scheduler", "순서는 말했다", "조건을 빠뜨렸다")
        data = load(record_path(root, "scheduler"))
        assert data["pending"] is None
        assert "answer" not in keys_of(data)
        cmd_revise(root, "scheduler", "조건", "조건 표", "한 조건이 빠지면 말한다", "조건을 빠뜨림")
        cmd_ask(root, "scheduler", "milestone", "조건이 하나 빠지면 선택은 어떻게 바뀌나?")
        data = load(record_path(root, "scheduler"))
        assert data["pending"]["kind"] == "milestone"
        assert milestone(data, "조건")["status"] == "확인 대기"
        cmd_grade(root, "scheduler", "빠지면 그 후보는 빠진다", "")
        cmd_pass(root, "scheduler")
        data = load(record_path(root, "scheduler"))
        assert milestone(data, "조건")["status"] == "통과"
        assert data["current"] == ""
        cmd_start(root, "다른 주제", "다른 결과", "other")
        try:
            cmd_status(root, None)
        except SystemExit as err:
            assert err.code == 2
        else:
            raise AssertionError("ambiguous status")
        import subprocess

        done = subprocess.run(
            [sys.executable, str(script), "--root", tmp, "list"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert "scheduler" in done.stdout
        assert "other" in done.stdout
    print("ok")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["--self-test"]:
        self_test()
        return
    dispatch(build_parser().parse_args(argv))


if __name__ == "__main__":
    main()
