# Skill2 0.1

## 目标

别人执行一个安装命令；Agent 获得七个 Skill；能管理自己的 Skill Library。

## 已实现

| 面 | 能力 |
| --- | --- |
| Build | scaffold、scan、lint、JSON、SARIF |
| Test | Codex 隔离、activation/outcome、baseline、JUnit、checkpoint/resume/early-stop |
| Package | skill-repo scaffold、package-check、plugin metadata 检查 |
| Publish | README/install/version/release preflight；远端确认门 |
| Audit | 结构、安全、断链、路径、secret、脚本检查 |
| Prune | keep/merge/downgrade/projectize/delete candidate；只读 |
| Visualize | 库存、直接调用、最近调用、零调用、测试、建议；本地 HTML |

## 主要命令

```bash
skill2 scaffold skill <name>
skill2 scan skills --json
skill2 lint skills --format sarif
skill2 test skills/<name> --cases cases/<name>.yaml --baseline --trials 3
skill2 package-check .
skill2 publish-check .
skill2 usage --codex ~/.codex --skills skills --json
skill2 suggest --codex ~/.codex --skills skills --json
skill2 visualize --codex ~/.codex --skills skills --out report.html
```

## 完成门

- 七个 Skills lint clean。
- 七个隔离 suites + 整包 routing 通过。
- 40+ 确定性 tests、Ruff、installer smoke 通过。
- README 英中一致；一个主安装命令；真实报告截图。
- 安装支持 dry-run、冲突拒绝、force、staging、provenance。
- Skill2 自己通过 package/publish preflight。
- 0.1 artifacts 在 clean checkout 可安装。

## 未完成

- 全 suites × 3 trials。
- clean worktree publish preflight。
- `0.1.0` wheel/sdist、checksums。
- GitHub tag/Release、PyPI；需用户确认。
- 公开 URL 重装。

## 非目标

- SaaS、托管 telemetry。
- Skill registry/marketplace。
- 完整多 harness live eval。
- 自动删除。
- APFS 历史读取统计。
