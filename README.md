# Larry V2 · A memory-driven desktop companion

English · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Larry remembered an unanswered question about a rubbing from a paper-cut window decoration. Were the bright bands joined or separate? No one had asked her to investigate. At her next review, a newly registered plugin offered a light reader and an audio frequency reader. She chose the light reader. One review later, with both tools still available, she chose to rest.

The experiment began with this fictional memory, translated from Chinese.

> “I just lifted a rubbing from a paper-cut window decoration. I can’t tell by eye whether the bright bands on the paper run together or are separate. I’m curious.”
>
> 刚揭下一张窗花拓片，肉眼分不清纸上的亮带是连成一片还是分开的。我还挺好奇的。

These two decisions were recorded on **4 November 2026** using **`gpt-6.1-sol`**. The experience and sample were fictional. The experimenter installed the plugin, authorized both tools and controlled when the two reviews came due. The model chose what to do at each review. [Archived inputs and decisions](history.json)

## How the life cycle works

The running companion can start a review when it comes due, even during a quiet conversation. Rest ends the current review and leaves the life cycle available for the next one. The runnable example puts two reviews back to back so you can inspect what crosses that boundary.

![The life cycle sits at the center. Memory and previous receipts feed each review. A plugin declares its capabilities, and self-management passes in the authorized catalog. A review can select a tool or rest. The executor writes its result back for the next review.](media/life-cycle.png)

- **The plugin declares what it can do.** Each operation supplies a description, an argument check, an availability check and an execution function. The sample plugin declares both readers once. Adding a reader means declaring it in the plugin and granting access if appropriate. The review loop can present its description without a new routing rule. [Operation contract](action_contract.py#L7) · [Plugin declarations](sample_plugin.py#L41)
- **Self-management builds the menu for this review.** It collects declarations from installed providers and checks grants and current availability. In this example, a prior outcome of `unknown` also blocks the same operation. An authorized audio reader can appear in the menu even when light is what interests Larry. The model judges relevance. [Registry](review.py#L19) · [Eligibility](review.py#L29) · [Catalog and memory snapshot](review.py#L40)
- **The life cycle hands the evidence to the decision-maker.** A review supplies the remembered experience, previous results and effective catalog together. A choice can contain an action or an empty plan. For a selected action the executor rechecks availability, validates the arguments and calls the plugin. It records the operation, status and result in SQLite. The next review reads that receipt alongside the original question. [Decision boundary](review.py#L73) · [Execution](review.py#L55) · [Receipt write](review.py#L84)

The source links point to the runnable example in this repository. The two choices below come from the recorded model run. In the offline example, a preset supplies a choice at the same point in the loop.

## Why the second review ended in rest

![Two historical reviews side by side. Both received the rubbing memory and both tools. The first had no receipt, selected the light reader and obtained three separate bands. The second read that receipt, chose an empty plan and made zero calls.](media/two-reviews.png)

The executor read `0 2 2 0 5 5 0 3 3 0`. Counting positions from one, the three bright bands start at **2, 5 and 8**. The first review’s receipt contains both the ten readings and the three-band result. The same text appears in the second review’s input. That gives us a way to trace the handoff independently of what the model said. [Sample function](sample_plugin.py#L9) · [Returned result](history.json#L35) · [Receipt read in review two](history.json#L62)

| Recorded reason | English translation |
| --- | --- |
| **Review 1 · Read light levels**<br>刚揭下的窗花拓片上，亮带是否连成一片还看不清；读取本地透光样本的亮暗分布，值得用来进一步判断。 | “I still can’t tell whether the bright bands on the rubbing I just lifted run together. Reading the pattern of light and dark in the local sample should help me tell.” |
| **Review 2 · Rest**<br>已有真实读数确认拓片上有3段分离的亮带，当前好奇点已得到解答，无需重复读取；音频样本与当前兴趣无关，先休息。 | “The readings confirm three separate bright bands on the rubbing. That answers my question, so I don’t need another reading. The audio sample is unrelated to what I’m curious about. I’ll rest for now.” |

[First choice and reason](history.json#L24) · [Second choice, reason and empty list of steps](history.json#L65)

## Try the two paths

Python 3.10+ and the standard library are sufficient. Both commands run offline. The example prints Chinese text. The figures and translations above provide an English guide.

| Command | What you can inspect |
| --- | --- |
| `python demo.py history` | Replays the archived model choices and receipts from JSON. This command only reads the record. [Replay entry point](demo.py#L59) |
| `python demo.py offline` | Uses an explicit preset to choose light first and rest after a receipt arrives. It executes the sample function locally, writes the result to an in-memory database and reads it back in the second review. [Preset](demo.py#L17) · [Local entry point](demo.py#L49) |

To see how the handoff behaves with different evidence, change the fourth [sample value](sample_plugin.py#L6) from `0` to `1` in a local copy. The first two bands merge. The offline run will report two bands in both the executor result and the next review’s input. The historical replay will still show the original three.

