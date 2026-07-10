---
name: skill2-publish
description: "用户要公开发布 skill repo、改 OSS README、创建 release，或验证公开安装时使用。"
---

# Skill2 Publish

目标：让陌生用户能发现、理解、安装、验证一个 skill repo。

## 边界

- Package 先生成已验证候选物。
- Publish 写公开界面并执行发布。
- 未通过 `skill2 package-check`，不发布。

## README

顺序：

1. 居中 icon + repo 名。
2. 一句定位；一句具体价值。
3. 语言切换、少量 badges、真实 hero。
4. 单一主安装命令。
5. 4-7 项能力表。
6. 隐私、兼容性、限制。
7. 文档、license。

`README.md` 英文主版；`README.zh.md` 中文版。安装命令一致。只写已交付能力。

## Preflight

- `skill2 lint skills`
- `skill2 package-check . --json`
- 测试、CI、working tree、版本、changelog 全部清楚。
- 列出 artifact、checksum、目标 registry/marketplace、远端动作。
- 全新临时环境安装通过。

## 发布门

tag、push、GitHub Release、PyPI、registry/marketplace 都是远端写操作。

执行前：

1. 输出 dry-run。
2. 获取用户显式确认。
3. 执行一次；失败不伪装成功。
4. 从公开 URL 重新安装。
5. 检查 README、manifest、installer、release 版本一致。

## Skill2 Dogfood

发布 Skill2 时，用本 Skill 检查 Skill2 自己。六个子 Skill 隔离测试、整包路由测试、公开安装测试必须通过。
