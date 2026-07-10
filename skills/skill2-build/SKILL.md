---
name: skill2-build
description: "用户要新建、改写、拆分或整理 agent skill 时使用。"
---

# Skill2 Build

目标：帮用户在当前 repo 写出可维护、可测试、可分发的 skill。

## 流程

1. 明确工作流：用户要让 agent 学会什么。
2. 判定范围：顶层 skill、reference、项目级 skill、还是不该做 skill。
3. 写 `SKILL.md`：短 description，正文只放核心规则。
4. 拆资源：重细节进 `references/`，确定性执行进 `scripts/`。
5. 写测试场景：正例、邻近正例、反例、输出断言。
6. 跑检查：`skill2 lint`，能测则跑 `skill2 test`。

## 结构

```text
skills/<skill-name>/
  SKILL.md
  references/
  scripts/
  assets/
```

只建需要的目录。不要空目录。

## 质量门

- `name` 和目录一致。
- `description` 是触发条件，不是长摘要。
- 正文 caveman：短、硬、可执行。
- 不写机器本地绝对路径，除非这是用户私有 repo。
- 不放 secrets。
- 引用文件必须存在。

## CLI

```bash
skill2 scaffold skill <name>
skill2 lint skills/<name>
skill2 test skills/<name> --agent codex --cases cases/<name>.yaml --isolate
```
