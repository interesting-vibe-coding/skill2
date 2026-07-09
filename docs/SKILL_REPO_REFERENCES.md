# 热门 skill 仓库结构参考

## 结论

Skill2 应学习三类 repo：

1. **Superpowers 型**：少量强 workflow skills + 多 harness 打包 + 测试。
2. **官方/科学库型**：大量 skills + `references/` / `scripts/` + CI 扫描。
3. **目录/市场型**：索引、贡献规范、质量门、发现入口。

Skill2 不该只做 CLI。最终应是：

```text
skills-first repo + optional CLI + tests + install/package metadata
```

## 参考仓库

| 仓库 | 规模/信号 | 结构特点 | Skill2 学什么 |
| --- | --- | --- | --- |
| [obra/superpowers](https://github.com/obra/superpowers) | 超高星；多 harness | `skills/`、多 plugin manifest、hooks、tests、docs/porting | 正式 `skills/` 分发；多 harness 打包；测试目录分平台 |
| [anthropics/skills](https://github.com/anthropics/skills) | 官方 | `skills/<name>/SKILL.md`，可带 templates、fonts、SDK references | 资源随 skill 打包；重资产也放 skill 内 |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 大型垂直库 | `skills/<name>/references/`、`scripts/`、CI scan、release | 大库要有 scanner、PR scan、安全 scan |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | 超大集合 | `.codex/skills`、`.claude/commands`、plugin manifest、skills index | 大集合需要 index；但容易噪声膨胀 |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | 官方社区集合 | `.github/skills`、agents、workflows、schemas、quality gates | 贡献门、schema、PR 自动检查 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 目录型 | README + CONTRIBUTING | 做发现入口，不做执行层 |
| [Bhanunamikaze/Agentic-SEO-Skill](https://github.com/Bhanunamikaze/Agentic-SEO-Skill) | 单能力深 repo | 顶层 `SKILL.md`、resources、agents、scripts、reports | 单领域深 skill 可配很多 evidence scripts |
| [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace) | marketplace | marketplace manifest | marketplace repo 可很薄，只管索引 |

## 可复制模式

### 1. 正式 `skills/` 目录

不要用 `.agents/skills` 作为分发源。那是安装目标，不是 repo 源码结构。

```text
skills/
  skill2-build/
    SKILL.md
  skill2-test/
    SKILL.md
```

### 2. 多 harness metadata

Superpowers 参考：

```text
.claude-plugin/
.codex-plugin/
.cursor-plugin/
.kimi-plugin/
.opencode/
```

Skill2 先支持：

```text
.codex-plugin/
.claude-plugin/
```

### 3. 测试目录

Superpowers 参考：

```text
tests/claude-code/
tests/codex/
tests/opencode/
tests/explicit-skill-requests/
```

Skill2 应有：

```text
tests/codex/
tests/skill-cases/
```

### 4. 引用和脚本随 skill 走

科学库参考：

```text
skills/<name>/references/*.md
skills/<name>/scripts/*.py
```

规则：正文短，细节进 references，确定性采集进 scripts。

### 5. CI 扫描

科学库和 GitHub awesome-copilot 都有 PR/quality workflows。

Skill2 应提供：

```text
skill2 lint
skill2 test --isolate
skill2 package-check
```

## 反模式

- 顶层 `SKILL.md` + 巨大 `resources/skills/*`，容易绕过标准 discovery。
- 超大 skill 集合无 index，用户无法判断质量。
- 只有目录，没有测试/安装。
- README 承诺多平台，但 repo 没对应 manifest/installer。
- usage analytics 上传云端；Skill2 应 local-first。

## 对 Skill2 的结构建议

```text
README.md
README.zh.md
LICENSE
CHANGELOG.md
install.sh
skills/
  skill2-build/
  skill2-test/
  skill2-package/
  skill2-audit/
  skill2-prune/
cases/
tests/
docs/
.codex-plugin/
.claude-plugin/
src/skill2/
```

## 下一步

1. 实现 `skill2 scaffold skill`。
2. 实现 `skill2 lint` 最小版。
3. 实现 `skill2 test --agent codex --isolate`。
4. 增加 `tests/codex/`。
5. 补 `CHANGELOG.md`。
