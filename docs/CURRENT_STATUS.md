# 当前状态

> 更新：2026-07-13（Task 5：公开安装面）

## 产品

Skill2 = 六个自包含 Skills（create / test / package / publish / audit / visualize）。用户安装后直接获得 Skills 与 Skill-owned 脚本；不要求全局 `skill2` CLI。

## 公开安装（已文档化）

| 入口 | 命令 / 动作 | 状态 |
| --- | --- | --- |
| Claude Code 主入口 | `/plugin marketplace add MisterBrookT/skill2` + `/plugin install skill2@skill2-marketplace` | README 主路径；manifest `0.1.0` + author/homepage/repository |
| Codex 当前 | `npx skills add MisterBrookT/skill2 -g -a codex -y` | 文档化；**未**宣称 curated `/plugins` 可搜索 |
| 手工 fallback | `git clone … && ~/.skill2/install.sh` | Skills-only；无 `uv tool install` |
| 贡献者 CLI | `uv run skill2 …` | 仅 Development / CI |

`uv`：仅当 Skill 执行确定性脚本时需要。无托管服务、telemetry、PyPI 用户安装前提。

## 已完成（本分支进展）

- Skill runtime bundle：`scripts/run` + `_runtime/` + hash gate（Tasks 1–3）。
- Installer 与 Skill 文档脱离全局 CLI（Task 4）。
- 公开 README / package-publish 规则 / DESIGN 对齐 marketplace-first（Task 5）。

## 未完成 / 外部条件

- Task 6：Claude / npx / install.sh 三条 clean-install smoke 与证据落盘。
- Codex curated marketplace 未提交；上架前 README 保持 `npx skills add`。
- 未做 tag、GitHub Release、PyPI upload、marketplace 远端提交。

## 版本

- 项目与 plugin manifest：`0.1.0`
