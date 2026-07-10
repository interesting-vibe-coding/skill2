---
name: skill2-test
description: "用户问 skill 是否有效、是否触发、是否误触发，或要求隔离评测时使用。"
---

# Skill2 Test

目标：证明一个 skill 自己有效，不靠当前会话、全局记忆、邻近 skills 偷帮忙。

## 协议

1. 复制目标 skill 到临时 `CODEX_HOME/skills`。
2. 临时 home 只复制 Codex auth/installation id；不复制 config、hooks、rules、memory、sessions。
3. 每个 case 用新会话。
4. `codex exec` 使用 `--ephemeral --ignore-user-config --ignore-rules --json`。
5. 子进程 cwd 指向临时 worktree；PATH 去掉用户/repo 工具。
6. macOS Seatbelt 拒绝真实 HOME 读写；无 guard 默认失败。
7. 检测 activation；检查输出断言。
8. 与 without-skill baseline 对比。
9. 每 trial checkpoint；保存 JSONL、输出、workspace artifact、模型/版本/skill hash。

## Case 分层

- 核心正例：应该触发。
- 邻近正例：应该触发。
- 反例：不该触发。
- 压力场景：容易误触发/漏触发。
- 输出断言：触发后结果要对。

## Codex 优先

默认检测：

- 读到隔离路径 `skills/<name>/SKILL.md` = medium confidence activation。
- 显式 activation event = high confidence。
- 只在文本里提到 skill name = 不计 activation。

## 硬规则

- 不继承 chat history。
- 不加载无关 skills。
- 不读用户 memory，除非 case 显式允许。
- 测试失败不能自动删除 skill。
- `inconclusive` 是有效结果。
- baseline 也通过时，不能宣称 skill 有确定性增益；加强断言或增加 rubric。
- Codex system prompt/tool schema 仍由 harness 管理；不是 raw-model prompt-clean。
- 网络未隔离；case 不访问私有网络。
- fail/runner_error 不算完成；`--resume` 只跳过 pass/baseline。

## CLI

```bash
skill2 test skills/<name> --agent codex --cases cases/<name>.yaml \
  --trials 3 --baseline --max-failure-rate 0.5
```
