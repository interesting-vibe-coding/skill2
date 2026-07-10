---
name: skill2-prune
description: "用户要清理 skill library，判断保留、合并、降级、项目化或删除时使用。"
---

# Skill2 Prune

目标：让 skill library 变小、触发更准、维护更轻。

## 输入

- `skill2 scan`
- `skill2 usage`
- `skill2 test`
- 用户项目边界

## 动作

- 保留：高频、边界清楚。
- 合并：高共现、触发重叠。
- 降级：只是父 skill 的组件，移到 `references/`。
- 项目化：只服务单项目，移到该 repo。
- 删除：长期未用、无 owner、无独立价值。

## 硬规则

- 不自动删除。
- 不把低频等同无用；先看是否高价值低频。
- 不动用户未授权文件。
- 给证据：调用次数、最近使用、引用关系、测试结果。

## CLI

```bash
skill2 usage --codex ~/.codex --json
skill2 report --out report.html
skill2 suggest --repo .
```
