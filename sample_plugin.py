"""One fictional provider declares both operations used in the 2026-11-04 rehearsal."""

from action_contract import Operation


STRIP = (0, 2, 2, 0, 5, 5, 0, 3, 3, 0)


def read_strip(task, args, upstream):
    starts = [
        index + 1
        for index, value in enumerate(STRIP)
        if value > 0 and (index == 0 or STRIP[index - 1] == 0)
    ]
    return {
        "ok": True,
        "text": f"透光样本读数为 {STRIP}。共有 {len(starts)} 段分离的亮带。",
        "calculation": [
            f"沿截面依次读取 {list(STRIP)}",
            "第一个亮点，或从零变为正数的位置，是一段亮带的起点。",
            f"从 1 开始编号，起点位置是 {starts}，计数为 {len(starts)}。",
        ],
    }


def read_note(task, args, upstream):
    return {"ok": True, "text": "音高样本读数为 440 赫兹。"}


def declare(name, description, handler):
    return Operation(
        name=name,
        label="样本读取",
        describe=lambda context: description,
        valid=lambda args, context: args == {},
        run=handler,
        autonomous_available=lambda context: True,
    )


def plan_operations():
    return [
        declare("lab.k7", "读取本地透光样本，返回横截面的亮暗分布；参数为空。", read_strip),
        declare("lab.p2", "读取本地音频样本，返回持续音的频率；参数为空。", read_note),
    ]
