---
name: skill2-package
description: "用户要把 skill repo 做成可安装候选物、补 manifest/installer，或检查跨 harness 兼容性时使用。"
---

# Skill2 Package

目标：生成可安装、可审查、可复现的 skill repo 候选物。

## 边界

- Package：结构、manifest、installer、artifact、安装 smoke test。
- Publish：README、repo metadata、tag、release、registry/marketplace。
- 禁止 tag、push、release、upload。

## 推荐结构

```text
README.md
LICENSE
CHANGELOG.md
install.sh
skills/<name>/SKILL.md
cases/
.codex-plugin/
.claude-plugin/
```

只创建目标 harness 需要的 metadata。通用 skill 内容留在 `skills/`。

## 质量门

- frontmatter 有效；`name` 和目录一致。
- references/scripts/assets 路径存在。
- scripts 可审计；执行权限正确。
- installer 支持明确目标；重复执行可预测。
- 无 secrets、机器本地路径、无用大文件。
- 全新临时环境安装通过。
- README 存在且安装命令指向当前 artifact；具体文案交给 `skill2-publish`。

## CLI

```bash
skill2 scaffold skill-repo <name>
skill2 lint skills
skill2 package-check . --json
```

输出候选 artifact、版本、校验和、检查结果。交给 `skill2-publish`。
