<p align="center">
  <img src="docs/readme-icon-v2.svg" width="88" alt="Skill2 图标">
</p>

<h1 align="center">Skill2</h1>

<p align="center"><strong>给 Skills 的 Skills。</strong></p>

<p align="center">
  一个可安装的 Skill Library，教 Agent 创建、测试、打包、发布、审计、可视化其他 Skill Library。
</p>

<p align="center"><a href="README.md">English</a></p>

<p align="center">
  <img alt="GitHub stars" src="https://img.shields.io/github/stars/MisterBrookT/skill2?style=flat-square">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-111111?style=flat-square">
  <img alt="本地数据" src="https://img.shields.io/badge/data-local--only-111111?style=flat-square">
  <img alt="MIT license" src="https://img.shields.io/github/license/MisterBrookT/skill2?style=flat-square&color=111111">
</p>

<p align="center">
  <img src="docs/readme-hero.svg" alt="Skill2 终端工作流">
</p>

## 安装

### Claude Code（主入口）

```text
/plugin marketplace add MisterBrookT/skill2
/plugin install skill2@skill2-marketplace
```

安装六个自包含 Skills。不安装全局 Skill2 CLI。

### Codex（当前）

```bash
npx skills add MisterBrookT/skill2 -g -a codex -y
```

为 Codex 复制六个自包含 Skills。当前不宣称 Skill2 已进入 curated Codex `/plugins` 列表。

### 手工 fallback

```bash
git clone https://github.com/MisterBrookT/skill2.git ~/.skill2 && ~/.skill2/install.sh
```

只复制 Skills（从 checkout 运行时 `install.sh` 支持 `--dry-run` 与冲突门控的 `--force`）。需要 Git。[uv](https://docs.astral.sh/uv/) 仅在 Skill 执行其确定性脚本时需要。数据只留本地；无托管服务、无 telemetry、用户无需 PyPI 安装。

## Skill Library

| Skill | Agent 何时使用 |
| --- | --- |
| `skill2-create` | 创建、更新或重构 Skill。 |
| `skill2-test` | 隔离测试触发和结果。 |
| `skill2-package` | 生成可安装候选物；不写远端。 |
| `skill2-publish` | 准备 README、Release、公开安装检查。 |
| `skill2-audit` | 查找契约、安全、行为缺口。 |
| `skill2-visualize` | 查看库存、直接调用、零调用候选、测试状态，以及保守的生命周期复审候选项。 |

直接告诉 Agent：

```text
给这个工作流创建一个项目级 Skill。
审计这个 Skill Library，只给有证据的问题。
可视化哪些 Skills 被直接调用，哪些没有直接调用。
```

## 本地证据

Skill2 从本地 Agent session 日志识别精确 `SKILL.md` 读取，区分直接调用、批量扫描、维护、Worker 读取。APFS 不保存历史文件打开次数，因此 Skill2 不声称掌握完整使用历史。

确定性库存与使用视图通过已安装 Skill 自带脚本运行：

```bash
uv run --script <skill-dir>/scripts/run -- visualize --skills ~/workspace/my-skill-library/skills --codex ~/.codex
```

需要结构化输入时使用 `--json`。低频是证据，不是删除结论。输出不包含 prompt 或 transcript。

## 设计

Skill2 采用 Superpowers 型结构：Skills 是产品，顶层 CLI 是贡献者脚手架。仓库必须符合自己教的规则。Package 不发布。Publish 在 tag、push、Release、upload 前必须 dry-run 并获得明确确认。Visualize 不自动删除、移动或合并。

详见[设计](docs/DESIGN.md)与[先例调研](docs/PRIOR_ART.md)。

## 开发

贡献者与 CI 使用 checkout 内 CLI。这不是用户安装步骤：

```bash
uv sync
PYTHONPATH=src uv run python -m unittest discover -s tests
uv run ruff check .
uv run skill2 lint skills
uv run skill2 package-check .
```

MIT
