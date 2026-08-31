# Mission Flow 发版流程

仓库同时产出 Comate、DUCC 与 Codex 插件。三端共享 skills 和版本号。Comate / DUCC 带 Hook；Codex 当前只打包 skills，不含 Hook。

发版脚本存放在维护者本机的 `scripts/`，该目录被 `.gitignore` 排除，不属于插件仓库内容。执行以下流程前需确认本机已有 `scripts/package-plugin.mjs` 和 `scripts/publish-ducc.mjs`。

## 1. 发版前准备

1. 根据语义化版本更新以下四个文件，版本必须完全一致：
   - `package.json`
   - `plugin.json`
   - `.claude-plugin/plugin.json`
   - `.codex-plugin/plugin.json`
2. 确认仓库已跟踪以下两个常用平台的 Hook 二进制及版本文件：
   - `bin/mission-flow-hook-darwin-arm64`
   - `bin/mission-flow-hook-darwin-arm64.version`
   - `bin/mission-flow-hook-linux-amd64`
   - `bin/mission-flow-hook-linux-amd64.version`
   Comate 与 DUCC 产物都会内置这些文件。Darwin amd64、Linux arm64 等其他平台不进入仓库和安装包，仍由 Hook 启动脚本按需下载。
3. 确认 `~/.comate/skills/.system/icafe/SKILL.md` 存在。该 Skill 只注入 DUCC 产物，不进入源码或 Comate 包。需要使用其他来源时，设置 `MISSION_FLOW_ICAFE_SKILL_DIR`。
4. 执行统一打包。`v2` 分支默认走 Comate `popo` 渠道，`main` 等分支走 `default`。也可显式指定：

```bash
node scripts/package-plugin.mjs              # v2 -> popo，其他分支 -> default
node scripts/package-plugin.mjs --channel popo
node scripts/package-plugin.mjs --channel default
```

产物按端分目录：

| 产物 | 用途 |
| --- | --- |
| `dist/comate/mission-flow-popo.zip` | v2 Comate 插件包，不覆盖线上 v1 的 `mission-flow.zip` |
| `dist/comate/manifest-popo.json` | v2 Comate 分发清单 |
| `dist/comate/mission-flow.zip` | v1 Comate 插件包（`--channel default`） |
| `dist/comate/manifest.json` | v1 Comate 分发清单（`--channel default`） |
| `dist/comate/plugin-distribution-rules.json` | Comate 分发规则，若本机 `dist/` 根目录已有则会移入此目录 |
| `dist/ducc/mission-flow-ducc.zip` | DUCC 本地或离线加载 |
| `dist/ducc/ducc-manifest.json` | DUCC 离线包清单 |
| `dist/ducc/mission-flow-marketplace.tar.gz` | DUCC Marketplace 发布包 |
| `dist/codex/mission-flow-codex/` | Codex 本地 Marketplace 根目录 |
| `dist/codex/mission-flow-codex.tar.gz` | Codex 离线 Marketplace 包 |

打包脚本会校验四个版本号、两个公共内置二进制和 DUCC 的 iCafe Skill 来源，并禁止将 macOS `._*`、`__MACOSX` 及扩展属性写入市场包。Codex 包只含 `.codex-plugin/`、`skills/`、`README.md`，其中 `skills/init` 是内置的初始化 skill，负责生成项目知识文档。

## 2. 发布 Comate

Comate 沿用现有 Stash 静态发布渠道。v1 和 v2 共用同一目录，用不同文件名并存：

```text
https://now.bdstatic.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/
```

v2（popo 渠道，当前 `v2` 分支默认）：

1. 先上传 `dist/comate/mission-flow-popo.zip`。
2. 再上传 `dist/comate/manifest-popo.json`。清单必须最后上传，避免客户端先发现新版本但下载到旧包。
3. 不要覆盖线上的 `mission-flow.zip` 和 `manifest.json`，那是 v1 稳定渠道。
4. 回查线上 popo 清单：

```bash
curl -fsSL \
  'https://now.bdstatic.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/manifest-popo.json' \
  | jq '{pluginKey, version, packageUrl, sha256}'
```

`pluginKey` 仍是 `mission-flow`，由 `plugin-distribution-rules.json` 把指定用户指到 `manifest-popo.json`。包内目录也仍是 `mission-flow/`，安装路径不变。

v1（default 渠道）：

1. 先上传 `dist/comate/mission-flow.zip`。
2. 再上传 `dist/comate/manifest.json`。
3. 回查线上清单：

```bash
curl -fsSL \
  'https://now.bdstatic.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/manifest.json' \
  | jq '{pluginKey, version, packageUrl, sha256}'
```

上传完成后，在 Comate IDE 的插件市场更新 `mission-flow`，新建会话验证 Skill 加载与 SessionStart Hook。

## 3. 发布 DUCC

DUCC 更新接口需要 B 端平台 Token。个人持有的有效 B 端 Token 可以使用；Comate 登录凭据、模型 Token 和普通 API Key 均不能替代。不要把 Token 写入插件仓库、`~/.baidu-cc/user.json`、命令参数或聊天消息。

推荐先将 Token 存入 macOS Keychain：

```zsh
read -s "ducc_market_token?DUCC B 端 Token: "
security add-generic-password -U \
  -a "$USER" \
  -s mission-flow-ducc-market-token \
  -w "$ducc_market_token"
unset ducc_market_token
```

本机脚本可以保存机器本地默认 Token，也可以用环境变量临时覆盖。执行发布：

```zsh
node scripts/package-plugin.mjs

DUCC_MARKETPLACE_TOKEN="$(security find-generic-password \
  -a "$USER" \
  -s mission-flow-ducc-market-token \
  -w)" node scripts/publish-ducc.mjs
```

`publish-ducc.mjs` 会依次执行：

1. 使用 UUID `7bde39bb-88cf-4c3c-a946-13304553b39b` 上传 DUCC Marketplace 包。
2. 调用 Marketplace 查询接口回查市场版本和插件版本。
3. 默认拒绝覆盖已经在线的相同版本。只有明确需要替换同版本产物时才设置 `DUCC_ALLOW_REPUBLISH=1`。

发布完成后执行官方安装验证：

```bash
ducc marketplace install mission-flow
```

检查安装版本与关键文件：

```bash
jq -r '.metadata.version' \
  ~/.claude/plugins/marketplaces/mission-flow/.claude-plugin/marketplace.json

jq -r '.version' \
  ~/.claude/plugins/marketplaces/mission-flow/mission-flow/.claude-plugin/plugin.json

test -x ~/.claude/plugins/marketplaces/mission-flow/mission-flow/bin/mission-flow-hook-darwin-arm64
test -x ~/.claude/plugins/marketplaces/mission-flow/mission-flow/bin/mission-flow-hook-linux-amd64
```

最后启动一个无状态会话，确认插件与 SessionStart Hook 能正常工作：

```bash
ducc --no-session-persistence -p '只回复 MARKETPLACE_READY'
```

发版失败时不要盲目重复 PUT。先查询线上版本；如果市场版本和插件版本都已经更新，则直接进入安装验证。任何已正式发布的内容变更原则上都应提升补丁版本，而不是覆盖同版本。

## 4. 安装 Codex

Codex 当前只分发 skills，不含 Hook。不要把当前仓库根登记成 Marketplace，否则会加载 DUCC 的 `hooks/hooks.json`。IDE 扩展不支持插件，使用 Codex CLI 或 ChatGPT 桌面端。

```bash
node scripts/package-plugin.mjs
codex plugin marketplace add "$(pwd)/dist/codex/mission-flow-codex"
codex plugin add mission-flow@mission-flow-codex
```

也可以在 Codex 里打开 `/plugins` 安装。装完后必须新开一个会话。可用 `$think`、`$impl`、`$worktree`、`$write`、`$handoff`、`$init` 验证 skill 是否出现。
