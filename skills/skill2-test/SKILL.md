---
name: skill2-test
description: "用户问 skill 是否有效、是否触发、是否误触发，或要求隔离评测时使用。"
---

# Skill2 Test

目标：证明一个 skill 自己有效，不靠当前会话、全局记忆、邻近 skills 偷帮忙。

## 协议

1. 复制目标 skill 到临时 skill root。
2. 创建临时 home 和最小 agent 配置。
3. 每个 case 用新会话。
4. 检测 activation。
5. 检查输出断言。
6. 输出 JSON 结果。

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
- 只在文本里提到 skill name = low confidence。

## 硬规则

- 不继承 chat history。
- 不加载无关 skills。
- 不读用户 memory，除非 case 显式允许。
- 测试失败不能自动删除 skill。
- `inconclusive` 是有效结果。

## CLI

```bash
skill2 test skills/<name> --agent codex --cases cases/<name>.yaml --isolate
```

读：

- `docs/ISOLATED_TESTING.md`
- `docs/ARCHITECTURE.md`
- `docs/MVP.md`
