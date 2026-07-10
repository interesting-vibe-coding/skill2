---
name: skill2-visualize
description: "用户明确要为 skill library 生成或更新本地 HTML 报告、Dashboard、图表时使用。"
---

# Skill2 Visualize

目标：用本地单文件 HTML 查看 skill library 证据；不把日志证据伪装成完整历史。

## 输入

- 库存：`skill2 scan skills --json`
- usage：`skill2 usage --codex ~/.codex --skills skills --json`
- 测试：已有 `skill2 test` JSON 输出；没有则标记缺失。

usage 来自 agent session log adapter：读取命令中出现的 skill 路径，带 confidence/category。

不要声称 APFS、FSEvents、文件 atime 可统计历史读取或调用。

## 产物

```bash
skill2 visualize --skills skills --codex ~/.codex --out report.html
```

`report.html` 必须本地、自包含、只读。展示：库存、频率、最近调用、零调用、usage 分类/置信度、测试状态。

## 解释

- 零调用：仅当前 adapter 未见事件；不是未使用证明。
- 最近调用：最近已解析日志事件时间；缺失时间不猜。
- broad scan、worker read、unknown：低置信度；不等同直接 activation。
- 低频不等于删除；转给 `skill2-prune` 做决策。
