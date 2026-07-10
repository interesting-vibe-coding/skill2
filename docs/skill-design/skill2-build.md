# `skill2-build`

## 参考

| 来源 | 借鉴原则 | 当前采用 |
| --- | --- | --- |
| Superpowers `writing-skills` | 先判断是否值得做通用 Skill；一次性方案、项目私有约定不应变成通用 Skill | 先判：顶层 Skill / reference / 项目级 / 不做 |
| Superpowers `writing-skills` | `description` 负责触发；不要复述 workflow | description 只写“用户何时需要它” |
| Superpowers `writing-skills` | 平铺 Skill namespace；重内容才拆 supporting files | `skills/<name>/SKILL.md`；需要时才加 `references/`、`scripts/`、`assets/` |
| Superpowers `writing-skills` | Skill 是行为规则；修改应有 case 与 baseline | 新 Skill 要有正例、邻近反例、无关反例、outcome 断言 |
| Agent Skills spec | 目录、frontmatter、相对引用、渐进加载 | 标准 `SKILL.md`；短正文；细节按需加载 |
| Agent Skills `skills-ref` | 格式校验交给参考实现 | `skill2 lint` 调用 `skills-ref`；不自写格式标准 |

## 取舍

| 不采用 | 原因 |
| --- | --- |
| Superpowers 的完整 RED/GREEN/REFACTOR 与多轮 pressure testing | Skill2 当前用 `1 trial + 人工 dogfood`，先保持轻量 |
| 长篇 rationalization / loophole tables | 当前 Skill 保持短；只在真实失败后补规则 |
| 跨多个 harness 的行为矩阵 | 0.1 先验证 Codex |
| 所有流程都建成 Skill | 机械规则交给 validator/script；项目私有规则留项目内 |

## 当前设计

```text
请求
  → 判范围：Skill / reference / project / 不做
  → 写最小 SKILL.md
  → 需要时拆 resources
  → 写 cases
  → lint
```

对应 [skill2-build](../../skills/skill2-build/SKILL.md)。

## 来源链接

- [Superpowers: writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md)
- [Agent Skills specification](https://agentskills.io/specification)
- [skills-ref](https://pypi.org/project/skills-ref/)
