# Skill2 架构

## 边界

```text
skills/        产品：教 Agent 判断和工作流
src/skill2/    脚手架：确定性扫描、测试、统计、报告
cases/         行为契约
.skill2/       本地证据；不提交
```

七个 Skills：build、test、package、publish、audit、prune、visualize。

## 数据流

```text
scan ───────────────┐
usage adapter ──────┼→ suggest → visualize.html
isolated test runs ─┘
```

- `scan`：库存、description、body tokens、resources、hash。
- `lint`：消费 scan；输出 ERROR/WARN/ADVICE。
- `test`：临时 HOME/CODEX_HOME；activation/outcome/baseline 分离。
- `usage`：读取 Agent session 日志；分类并去重。
- `suggest`：只读维护建议。
- `visualize`：自包含本地 HTML。

## Usage 事件

```json
{
  "timestamp": "2026-07-09T21:00:00Z",
  "harness": "codex",
  "session": "rollout-id",
  "skill": "agent-search",
  "source": "command",
  "confidence": "medium",
  "category": "activation"
}
```

分类：

| category | 含义 |
| --- | --- |
| `activation` | 精确读取少量 `SKILL.md`；直接调用代理 |
| `broad_scan` | 同 session 批量读取多个 Skills |
| `maintenance` | 编辑、复制、移动 |
| `worker_read` | Worker/Subagent 读取 |
| `unknown` | 证据不足 |

APFS 无历史读取计数。FSEvents 无可靠 read event。未来 `usage watch` 只可监听启动后的读取；默认关闭。

## 测试隔离

```text
tmp/
  codex-home/     # 仅 auth、installation id、目标 Skills
  home/           # 空用户 HOME
  work/           # 空目录或 fixture
```

Codex 参数：`--ephemeral --ignore-user-config --ignore-rules --json`。macOS 外层 Seatbelt 拒绝真实 HOME 读写；PATH 去掉用户/repo 工具；非受保护环境默认失败。

每 trial 保存：manifest、JSONL、stderr、last message、workspace artifact、断言、skill hash。

长跑：每 trial 原子 checkpoint；`--resume` 跳过已完成键；可按失败率 early-stop。

## 建议安全门

- merge 只用直接 activation 共现；broad scan 不算。
- projectize 只认 `metadata.skill2.scope: project`；不从 `/workspace` 路径猜。
- 低频不自动删除。
- 所有建议带 evidence。

## 发布安全门

- Package 不产生远端副作用。
- Publish check 只读。
- installer 默认拒绝不同内容；`--force` 才替换。
- tag、push、Release、upload 必须 dry-run 后再次确认。
