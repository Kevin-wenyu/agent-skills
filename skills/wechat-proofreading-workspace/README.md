# wechat-proofreading Eval 记录

2026-08-19，用 skill-creator 的 Eval 模式对 `wechat-proofreading` 跑的一轮验证，记录在这里方便以后复用/复跑，不用每次现造测试文本。

## 测试设置

`iteration-1/` 下两组测试，每组分别跑"有skill"（读`skills/wechat-proofreading/SKILL.md`）和"没有skill"（Claude凭自己判断，不给任何skill）两个版本，4个独立子agent并行跑：

- `eval-0-broad-coverage`：故意写的压力测试文本（`skills/wechat-proofreading/evals/files/`），塞了多种AI味问题，测覆盖面。
- `eval-1-precision-check`：故意写干净的文本，测精度——会不会为了"找出问题"而误伤本来就对的写法。

断言定义在 `skills/wechat-proofreading/evals/evals.json`。

## 关键发现

1. **精度差异是最重要的结果**：eval-1里，没有skill的baseline把"我又手动修回去——这种细节上的可靠性，还没到完全放手的程度"判成"AI收尾腔"要求改写；但这句话正是write-article"结尾给判断不给总结"的正确写法，是误伤。有skill的版本正确识别为不需要改。
2. **grep计数纪律的差异**：eval-0原文"不是"出现4次（已用`grep -o 不是 | wc -l`独立核实），有skill版本报的是4次，没有skill的baseline报"重复三次"，漏了藏在"而不是"人放权""里的一次。跟SKILL.md自己写的"肉眼数漏了近一半"是同一个失效模式。
3. 覆盖面上两个版本差别不大——AI味本身现在是个被广泛记录的现象（Wikipedia的Signs of AI Writing指南、通用AI高频词清单），通用Claude不靠这个skill也能查出大部分类别，skill真正的增量价值集中在"查得准不准、对不对着Kevin自己的声音标准查"，不是"能不能查出来"。
4. 第10类（书面词汇/AI高频词）、第11类（态度中立）当时还是空定义占位，这次压力测试撞出的例子已经回填进SKILL.md，标注了provenance（来自这次的压力测试文本，不是常规审校撞见的真实文章）。

## 怎么复跑

```bash
# 主流程（有/无skill对比）：起4个Task子agent，参考今天用过的prompt结构，
# with-skill版本让agent先读SKILL.md再审校，baseline版本完全不提skill

# 描述触发优化（可选，独立于上面）：
cd ~/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator
python3 -m scripts.run_loop \
  --eval-set <repo>/skills/wechat-proofreading-workspace/description-opt/trigger-eval.json \
  --skill-path <repo>/skills/wechat-proofreading \
  --model claude-sonnet-5 \
  --max-iterations 3 --verbose
```

## 还没做的

- **是否安装到`.claude/skills/`或`~/.claude/skills/`让它能被真实触发——Kevin 2026-08-20明确决定暂不装**，理由是还不确定实际效果，等在真实文章上跑过验证再说（目前只有本文档里记录的压力测试文本，没有真实文章的对比数据）。装的话是改全局个人目录，不是纯repo内的事，别自作主张装上。
- 没有跑过真实的公众号文章草稿（只有压力测试文本），下次正式审校一篇真文章时，最好也顺手记录一份对比——这也是解除上面"暂不装"决定的前提条件。
- 没有跑skill-creator的Benchmark模式（专门测触发精度的统计验证）。
- `description-opt/`跑的是触发准确率优化，用的是我自己设计的20条测试query，没有走skill-creator标准流程里"给用户在浏览器里过一遍再定稿"这一步（当时在自主执行模式下跳过了这步人工审核）。
