# Skill2 产品定位

## 一句话

Skill2 是 **skills for your skills**：一个可安装的 Skill Library，帮助 Agent 管理其他 Skill Library。

形态参考 Superpowers：

```text
用户安装 Skill2 Skills
→ Agent 学会构建、测试、打包、发布、审计、精简、可视化 Skills
→ 需要可重复结果时，Skills 调用辅助 CLI
```

Skills 是产品。CLI 是脚手架。

## 七个 Skills

| Skill | 职责 | 不做 |
| --- | --- | --- |
| `skill2-build` | 设计、编写、重构 Skill | 不负责发布 |
| `skill2-test` | 隔离测试触发与结果 | 不修改生产 Skill |
| `skill2-package` | 生成可安装候选物 | 不 tag、push、upload |
| `skill2-publish` | README、版本、Release、公开安装 | 未确认不写远端 |
| `skill2-audit` | 扫描质量、安全、行为缺口 | 不自动修复 |
| `skill2-prune` | keep/merge/downgrade/projectize/delete candidate | 不自动删除 |
| `skill2-visualize` | 把库存、usage、测试、建议做成本地报告 | 不采集、不上传 |

`skill2-visualize` 独立，因为“看清 Library”是独立用户意图。它只消费证据，不拥有采集逻辑。

## Dogfood

Skill2 必须符合自己教的规则：

```text
build      → 七个 Skill 符合 authoring 规范
test       → 七个 Skill 各有隔离 case；整包有 routing case
package    → Skill2 可预测、原子、可追溯安装
publish    → README、版本、manifest、Release 一致
audit      → 自扫无阻塞问题
prune      → 自己可生成保守维护建议
visualize  → 自己生成真实本地报告
```

## Usage 方案

### 0.1 主方案：Agent 日志适配器

读取本地 Agent session 日志，识别精确 `SKILL.md` 读取。分类：

- `activation`：单个/少量 Skill 的精确读取；中等置信度调用信号。
- `broad_scan`：同一 session 批量读取多个 Skills。
- `maintenance`：编辑、复制、移动 Skill。
- `worker_read`：Worker/Subagent 读取。
- `unknown`：证据不足。

默认只统计 `activation` 作为直接调用频率。其他分类保留，避免伪精确。

输出只含 Skill 名、时间、session 标识、分类、置信度、来源类型。不保留 prompt、transcript、绝对路径。不上传。

### 为什么不直接读磁盘历史

- APFS 不保存“文件被打开次数”。
- FSEvents 记录目录变更，不提供可靠读取事件。
- macOS Endpoint Security/OpenBSM/`fs_usage` 只能监听启动后的读取；需额外权限，噪声高，跨平台差。

结论：不能回溯磁盘读取次数。0.1 不做常驻监视器。

### 后续可选：`skill2 usage watch`

实验能力。仅记录启动后的 Skill 文件读取：

- opt-in；默认关闭。
- 本地聚合；不记录文件内容。
- 明示平台、权限、漏报范围。
- 与 Agent 日志事件去重。

只有能稳定区分 Agent 读取、编辑器预览、索引器扫描后才进入稳定接口。

## Visualization

本地单文件 HTML。首版显示：

- Skill 库存、体积、最近修改。
- 直接调用次数、最近调用时间、零调用候选。
- broad scan / maintenance / worker read 噪声分布。
- activation gap、false positive、测试通过率。
- keep/merge/downgrade/projectize/delete candidate 建议及证据。

低频不是删除结论。建议必须结合 owner、测试、项目边界、最近使用。

## 安装与发布

README 只有一个主安装命令：

```bash
git clone https://github.com/MisterBrookT/skill2.git ~/.skill2 && ~/.skill2/install.sh
```

安装器必须支持：

- `--dry-run`
- 冲突预览
- staging + 原子替换
- 重复执行结果稳定
- source/ref/tree SHA 记录
- Codex/Claude 目标选择

远端发布必须：dry-run → 用户确认 → tag/push/release/upload → 公开重装。

## 0.1 边界

- Codex-first 行为测试。
- Agent Skills 兼容目录。
- Python 3.11+ 辅助 CLI。
- 本地 HTML；无 telemetry SaaS。
- 不做 registry、marketplace、自动删除。
- `watch` 仅研究项，不阻塞 0.1。
