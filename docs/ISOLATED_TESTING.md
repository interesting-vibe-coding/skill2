# Skill 隔离测试

## 问题

Skill 有效，还是当前会话、全局 Skills、用户文件替它完成了任务？

Skill2 在新 Codex 会话中只安装目标 Skill，再分测触发与结果。

## 三层

1. Activation：该触发时读取目标 `SKILL.md`。
2. Non-activation：无关/相邻请求不读取目标 Skill。
3. Outcome：触发后满足确定性断言。

## 隔离契约

每 trial 新建：

```text
tmp/
  codex-home/   # 仅 auth、installation id、目标 Skills
  home/         # 空 HOME
  work/         # 空目录或 fixture 副本
```

Codex 参数：

```text
--ephemeral --ignore-user-config --ignore-rules --json
```

额外边界：

- PATH 去掉 repo venv、`~/.local/bin`、用户工具。
- macOS 用外层 Seatbelt 拒绝真实 HOME 全部读写。
- Codex 以临时 worktree 作为进程 cwd；不是只依赖 `-C`。
- 外层 sandbox 存在时，Codex 使用官方 externally-sandboxed bypass，避免嵌套 Seatbelt 失败。
- 非 macOS/无文件 guard 默认失败；`SKILL2_ALLOW_UNGUARDED=1` 才显式降级。
- Fixture 由父进程复制进临时 worktree。
- 网络未隔离：Codex 需要模型 API；case 不应要求访问私有网络。
- Codex CLI 不暴露完整 system prompt/tool schema 控制；这是干净 workspace，不是 raw-model prompt-clean。

父进程保存 artifact；被测 Codex 不能写真实仓库。

## Case

```yaml
schema_version: "1"
skill: agent-search
agent: codex
defaults:
  repetitions: 3
cases:
  - id: core
    prompt: "调研 agent skill testing prior art。"
    expect_activation: agent-search
    assertions:
      - type: contains
        value: "prior art"

  - id: unrelated
    prompt: "把变量 foo 改名为 bar。"
    expect_not_activation: [agent-search]
```

## 检测

| 信号 | 置信度 |
| --- | --- |
| Harness 显式 activation event | high |
| 精确读取隔离目录中的目标 `SKILL.md` | medium |
| 只在文本提到 Skill 名 | 不计 |

Activation 与 Outcome 独立。只模仿输出、不读取 Skill，不能算 activation pass。

## Artifact

每 trial 保存：

- `manifest.json`：模型、版本、skill hash、sandbox、prompt hash。
- `events.jsonl`：Codex 结构化事件。
- `last-message.txt`、`stderr.log`。
- workspace artifact、文件变化、断言结果。
- `run.json`：checkpoint、complete、stopped_early。

不把 prompt 原文写进 manifest；只写 SHA-256。原始 events 属本地敏感证据，`.skill2/` 默认 gitignore。

## 长跑

```bash
skill2 test skills/foo --cases cases/foo.yaml --trials 3 --baseline \
  --max-failure-rate 0.5 --min-trials-before-stop 5
```

- 每 trial 原子写 `run.json`。
- `--resume <run-dir>` 跳过 pass/baseline。
- fail/runner_error 不算完成；resume 会重跑。
- 达失败率阈值后 `stopped_early=true`、`complete=false`。
- 并行 run id 带随机后缀，避免 artifact 碰撞。

## 已验证缺陷

真实 dogfood 曾发现：

- visualize description 过宽，误触发 prune 请求。
- Outcome 断言过弱，without-skill baseline 也通过。
- 仅改 HOME 不阻止 Codex 读取宿主文件。
- 微秒时间戳不足以保证并行 run id 唯一。

当前实现均有修复与回归证据。
