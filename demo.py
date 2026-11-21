"""Run the offline example or display the archived model decisions."""

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3

import sample_plugin
from review import initialize, review


MEMORY = "刚揭下一张窗花拓片，肉眼分不清纸上的亮带是连成一片还是分开的。我还挺好奇的。"
GRANTS = frozenset({"lab.k7", "lab.p2"})


def preset(context):
    """The historical offline double selects a known action, then rests after a receipt."""
    if context["prior_receipts"]:
        return {"selected": [], "reason": "已收到上一轮回执，按离线预设休息。"}
    return {"selected": [{"action": "lab.k7", "args": {}}], "reason": "辨认拓片上的光带"}


def display(turn, choice_label):
    print(f"\n第 {turn['number']} 轮")
    for text in turn["memory"]:
        print(f"  读到的记忆　{text}")
    print("  可选能力")
    for name, declaration in turn["catalog"].items():
        print(f"    {name}　{declaration['说明']}")
    print("    休息（空计划）")
    if turn["prior_receipts"]:
        for item in turn["prior_receipts"]:
            print(f"  读到的回执　第 {item['review']} 轮第 {item['step']} 步"
                  f" · {item['operation']} [{item['state']}]　{item['text']}")
    else:
        print("  读到的回执　无")
    selection = "、".join(s["action"] for s in turn["selected"]) or "休息"
    print(f"  {choice_label}　{selection}\n  给出的理由　{turn['reason']}")
    for index, step in enumerate(turn["steps"], 1):
        for line in step.get("calculation", []):
            print(f"    {line}")
        print(f"  本轮回执　第 {turn['number']} 轮第 {index} 步"
              f" · {step['name']} [{step['state']}]　{step['text']}")
    if not turn["steps"]:
        print("  本轮执行　0 步")


def offline():
    print("离线预设回答 · 本机运行样本执行器\n虚构经历，无主人来信。两轮连续运行。")
    with closing(sqlite3.connect(":memory:")) as db:
        db.row_factory = sqlite3.Row
        initialize(db, [MEMORY])
        for number in (1, 2):
            turn = review(db, number, [sample_plugin], GRANTS, preset)
            display(turn, "离线预设选择")


def history():
    path = Path(__file__).with_name("history.json")
    record = json.loads(path.read_text(encoding="utf-8"))
    print(f"历史回放 · {record['date']} · {record['model']}\n{record['conditions']}")
    for turn in record["rounds"]:
        display(turn, "历史模型选择")


if __name__ == "__main__":
    import sys

    # Keep the original quotations intact in redirected output on any Windows code page.
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="拉里的窗花拓片案例（完全离线）")
    parser.add_argument("mode", choices=("offline", "history"), nargs="?", default="offline",
                        help="offline 运行预设与样本执行器，history 回放真实模型旧记录")
    args = parser.parse_args()
    if args.mode == "history":
        history()
    else:
        offline()
