---
name: skill2-audit
description: "用户要审计 skill library 的结构、安全、断链、体积或触发冲突时使用。"
---

# Skill2 Audit

目标：找出 skill library 里会影响安装、触发、维护的问题。

## 扫描项

- 缺 `SKILL.md`
- frontmatter 缺 `name` / `description`
- `name` 和目录不一致
- description 太长或像工作流摘要
- 引用文件不存在
- scripts 缺执行权限或有高风险命令
- skill 过大，应该拆 references
- 触发词重叠，容易误触发
- repo-local skill 混进全局分发包

## 输出

按严重级别：

- P0：安装/运行会坏
- P1：会误触发/漏触发
- P2：维护风险
- P3：风格/清理

## CLI

```bash
skill2 scan ./skills --json
skill2 lint ./skills
```

不要直接改。先给问题清单和建议 patch。
