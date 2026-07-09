---
name: skill2-package
description: "把 skill repo 做成别人好安装的开源包：结构、README、install、manifest、质量门。"
---

# Skill2 Package

目标：让 skill repo 可安装、可审查、可发布。

## 推荐结构

```text
README.md
LICENSE
CHANGELOG.md
install.sh
skills/
  skill-name/
    SKILL.md
    references/
    scripts/
    assets/
cases/
examples/
.claude-plugin/
.codex-plugin/
```

## 必查

- `SKILL.md` frontmatter 有效。
- `description` 短，像触发器。
- `references/` 全部存在。
- scripts 可执行、可审计。
- `install.sh` 支持 dry-run 或明确目标。
- README 写清安装、使用、兼容性、隐私。
- 无 secrets、无机器本地绝对路径、无无用大文件。

## 安装入口

优先支持：

```bash
npx skill2 init
```

并保留手动安装：

```bash
cp -R skills/skill2-* .agents/skills/
```

## CLI

```bash
skill2 scaffold skill-repo
skill2 lint --package
```
