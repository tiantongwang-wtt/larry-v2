"""A small extraction of the catalog, immediate execution and receipt handoff."""

from copy import deepcopy

from action_contract import Unavailable


def initialize(db, experiences):
    db.executescript("""
        CREATE TABLE experience (body TEXT NOT NULL);
        CREATE TABLE receipt (
            review INTEGER, step INTEGER, operation TEXT NOT NULL,
            state TEXT NOT NULL, text TEXT NOT NULL, PRIMARY KEY (review, step)
        );
    """)
    db.executemany("INSERT INTO experience VALUES (?)", [(text,) for text in experiences])


def registry(providers):
    operations = {}
    for provider in providers:
        for op in provider.plan_operations():
            if op.name in operations:
                raise ValueError(f"重复的能力名称 {op.name}")
            operations[op.name] = op
    return operations


def permitted(op, context, grants):
    if op.name not in grants or op.autonomous_available is None:
        return False
    if any(r["operation"] == op.name and r["state"] == "unknown" for r in context["prior_receipts"]):
        return False
    try:
        return bool(op.autonomous_available(context))
    except (OSError, Unavailable):
        return False


def snapshot(db, operations, grants):
    memory = [row["body"] for row in db.execute("SELECT body FROM experience ORDER BY rowid")]
    receipts = [dict(row) for row in db.execute("SELECT * FROM receipt ORDER BY review, step")]
    context = {"memory": memory, "prior_receipts": receipts}
    context["catalog"] = {
        name: {
            "说明": op.describe(context),
            "可延后": op.delayed,
            "接受上一步结果": op.accepts_result,
        }
        for name, op in operations.items() if permitted(op, context, grants)
    }
    return context


def execute(op, args, context):
    if not isinstance(args, dict) or not op.valid(args, context):
        return "failed", {"text": "参数未通过声明校验，本次未执行。"}
    try:
        result = op.run(None, args, None)
        if type(result["ok"]) is not bool or not isinstance(result["text"], str):
            raise ValueError("invalid_receipt")
        state = "done" if result["ok"] else "failed"
        if result.get("outcome") == "unknown":
            state = "unknown"
        return state, result
    except Exception as error:
        return "unknown", {"text": f"执行结果未知（{type(error).__name__}）。"}


def review(db, number, providers, grants, choose):
    operations = registry(providers)
    seen = snapshot(db, operations, grants)
    decision = choose(deepcopy(seen))
    steps = []
    for index, choice in enumerate(decision["selected"], 1):
        name = choice["action"]
        current = snapshot(db, operations, grants)
        if name in seen["catalog"] and name in current["catalog"]:
            state, result = execute(operations[name], choice["args"], current)
        else:
            state, result = "failed", {"text": "该能力不在可用目录中，本次未执行。"}
        with db:
            db.execute(
                "INSERT INTO receipt VALUES (?, ?, ?, ?, ?)",
                (number, index, name, state, result["text"]),
            )
        steps.append({"name": name, "state": state, "text": result["text"],
                      "calculation": result.get("calculation", [])})

    return {"number": number, **seen, **decision, "steps": steps}
