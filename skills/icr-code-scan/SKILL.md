---
name: icr-code-scan
description: >-
  使用此 skill 审查代码变更（git diff、暂存区改动、分支差异或指定 commit），检查 bug、安全风险、性能问题和代码质量。当用户想要审查、检视或检查代码改动时触发——包括"code review"、"review my changes"、"帮我审查代码"、"看看改动有没有问题"、"review HEAD~N"、"check my PR"、"CR"、"帮我过一遍"、"这段改动有没有问题"，或任何在合入/推送前评估代码变更是否正确安全的请求。此 skill 检查 diff 并输出按优先级排序的问题清单与修复建议。
---

# Code Review

此 skill 用于对当前代码变更进行结构化审查。默认遵循 **review-first** 工作流：先收集范围、执行审查、输出报告，只有在用户明确要求后才进入修复阶段。

## 核心原则

1. **范围优先于结论**：先确认要审什么，再开始审查，避免误把”看当前改动”扩大成”审整个分支”。
2. **风险优先于规模**：文件数和行数只用于粗分级，真实模式由风险特征决定。
3. **证据优先于偏好**：只报告有明确代码证据的问题，不输出纯风格偏好建议。
4. **简洁优先于详尽**：每条 finding 用 1-2 句话说清风险和建议，不堆砌文字。用户需要快速扫描，不是阅读论文。
5. **上下文按需加载**：默认读取 diff 和局部上下文，只有在判断需要时才扩展到调用链、类型定义和相邻文件。
6. **结果可执行**：每个 finding 都要说明影响、触发场景或证据，并给出具体建议。
7. **失败可降级**：并行审查失败时要自动降级，而不是中断整次 review。

## SubAgent 调用规范

本 skill 通过 `delegate_subtask` 工具启动审查 SubAgent。每个 SubAgent 是独立的 Agent 实例，拥有只读工具集，能够自行获取 diff、搜索代码库、读取文件。

### 调用方式

- **agent_type 固定为 `"Explore"`**
- **description**：简短描述审查维度，如 `"Code review - 复用审查"`
- **query**：只传递路径和范围，**不注入文件原文**——让 SubAgent 自行读取指令文件

### 并行调用要求

深度审查模式下，5 个 `delegate_subtask` 调用**必须在同一轮响应中并行发起**，不要串行等待。

### Query 构建模板

主 Agent 只需构建一段简短的 query，引导 SubAgent 自行加载所需资源：

```
你是代码审查专家，负责【维度名称】审查。

1. 读取审查指令：<skill绝对路径>/agents/<维度>-reviewer.md
2. 读取输出格式：<skill绝对路径>/references/output-schema.md
3. 执行以下命令获取待审变更：
   <git diff 命令>
4. 根据审查指令完成审查，使用 read_file 读取变更文件上下文（±30 行），用 grep_content/codebase_search 搜索调用链和已有实现
5. 严格按输出格式返回 JSON。未发现问题时返回空 findings 数组

补充上下文：<与本次变更相关的业务规则摘要（如有，1-2 句话；无则省略此行）>
```

> **关键原则**：主 Agent 不预读 agents/*.md 和 references/*.md 的内容再注入 query。只需告知路径，SubAgent 有 read_file 能力，会自行加载。这大幅减少主 Agent 的准备工作和输出 token。

## 工作流程

### Step 1：确定审查范围与审查模式

本步骤需要在**一轮响应中**完成以下全部决策：确认范围 → 输出统计 → 风险分级 → 选择审查模式。

#### 1a：确定范围

**用户显式指定范围时**：直接使用用户给出的范围（如 `review HEAD~3`、`review main..feature`）。

**用户未指定范围时**：通过 git 命令探测当前变更状态，按以下优先级选择范围：
1. **工作区变更优先**：staged、unstaged、untracked 中只要有任意变更，就以工作区内容为审查范围，不要扩大到整个分支
2. **分支级审查**：仅当工作区无变更时，回退到当前分支相对于目标分支的变更
3. **最近一次提交**：如果以上都没有内容，回退到最近一次提交的变更
4. 如果仍没有内容，提示用户手动指定审查范围

> **重要**：
> - 尽量通过**一次 `run_command`** 完成探测，避免多轮串行调用
> - 主 Agent 只需获取变更文件列表和统计信息即可做决策，**不要获取完整 diff 原文**，完整 diff 由 SubAgent 自行获取
> - 确定范围后，记录下对应的 **基准 git diff 命令**（如 `git diff --cached`、`git diff <merge-base> HEAD`），后续写入每个 SubAgent 的 query 中，确保所有 SubAgent 基于同一个基准变更

对于 untracked 文件：小文件直接读取全文并标记为 `[新文件]`；大文件只读取关键片段并在报告里说明为局部审查。

#### 1b：范围过滤

默认跳过以下低价值输入，除非用户明确要求或这些文件正是问题核心：
- lockfile
- 构建产物、snapshot、minified 文件
- 二进制文件
- 纯格式化噪音变更

以下类型的变更即使很小，也应保留并提高风险等级：
- 权限、鉴权、token、配置下发
- 命令执行、文件读写、路径拼接
- 网络请求、序列化/反序列化、持久化存储
- 应用启动或初始化入口、事件分发链路、共享状态

> **过滤结果必须体现在 diff 命令中**：将过滤后的文件列表写入 git diff 的路径参数（如 `git diff --cached -- src/a.ts src/b.ts`），或用 `:(exclude)` 排除低价值文件（如 `git diff --cached -- . ':(exclude)package-lock.json'`）。

#### 1c：统计信息与风险分级

向用户展示变更概览：变更文件数、新增/删除行数（如已获取）、是否包含新文件、是否命中高风险目录或关键词。

结合以下风险信号做分级（不要只看文件数和行数）：
- 是否命中高风险目录、模块或文件类型
- 是否修改公共 API、类型定义、协议、持久化结构
- 是否涉及异步流程、状态同步、缓存、并发
- 是否涉及命令执行、路径、网络、鉴权、输入校验
- 是否引入新文件或新增较大逻辑块

#### 1d：选择审查模式

**常规审查**：满足以下条件时使用单 Agent 综合审查。
- 文件数 <= 5
- 变更总行数 <= 200
- 未命中高风险模块
- 没有显著的新流程、新协议或新持久化结构

**深度审查**：出现任一条件时使用 5 个 SubAgent 并行审查。
- 文件数 > 5
- 变更总行数 > 200
- 命中高风险模块或边界能力
- 存在新增文件、新主流程或明显跨模块改动

**超大变更降级**：当变更非常大（例如 > 20 个文件或 > 800 行）时，不要一次性把所有上下文塞给所有 Agent。应按文件组或风险模块拆分，优先审查高风险部分，并在报告中说明存在”分批审查”或”抽样审查”。

### Step 2：加载审查知识

主 Agent 只需处理**业务规则**：如果仓库中存在 `.comate/rules/`、`CLAUDE.md`、`.cursorrules`、`.github/copilot-instructions.md` 等规则文件，只读取与本次变更直接相关的规则，提取 1-2 句话摘要写入 SubAgent query。与当前改动无关的规则不要注入。

### Step 3：发起审查

根据 Step 1 选择的审查模式，按 Step 4 的说明构建 query 并发起 SubAgent 调用。

> SubAgent 会自行决定上下文获取策略（读取 diff 附近代码、搜索调用链、查找类型定义等），主 Agent 无需在 query 中指定上下文获取步骤。

### Step 4：执行审查

设 `SKILL_DIR` 为本 skill 目录的绝对路径（即 SKILL.md 所在目录）。

#### 常规审查模式

发起一个 `delegate_subtask` 调用，query 按模板构建：

```
delegate_subtask(
  agent_type=”Explore”,
  description=”Code review - 综合审查”,
  query=”””
你是代码审查专家，负责对当前变更进行综合审查（正确性、可靠性、风格、复用、自定义规则）。

1. 依次读取以下指令文件，理解各维度的审查要点：
   - {SKILL_DIR}/agents/correctness-reviewer.md
   - {SKILL_DIR}/agents/reliability-reviewer.md
   - {SKILL_DIR}/agents/style-reviewer.md
   - {SKILL_DIR}/agents/reuse-reviewer.md
   - {SKILL_DIR}/agents/custom-reviewer.md
2. 读取输出格式：{SKILL_DIR}/references/output-schema.md
3. 执行命令获取变更：{git diff 命令}
4. 审查覆盖度要求：
   - **风格维度（style）**：必须严格按 style-reviewer.md 的指令逐条扫描所有规则，不得遗漏任何一条。有规则文件时，必须输出规则覆盖确认表后再输出 JSON
   - **其他维度（正确性、可靠性、复用、自定义规则）**：各关注最核心的 2-3 个检查点完成审查
   - 自定义规则维度须严格按 custom-reviewer.md 指令加载仓库根目录 .comate/custom-rules/ 下的规则文件，仅在存在有效规则文件时上报问题
5. 仅输出有证据的问题，不报纯风格偏好。未发现问题返回空 findings

{业务规则摘要（如有）}
“””
)
```

#### 深度审查模式

在**同一轮响应**中，并行发起 5 个 `delegate_subtask`。主 Agent **不需要预读**任何 agents/*.md 或 references/*.md 文件，直接按模板构建 query：

```
1. delegate_subtask(
     agent_type=”Explore”,
     description=”Code review - 复用审查”,
     query=”你是代码审查专家，负责复用审查。\n1. 读取审查指令：{SKILL_DIR}/agents/reuse-reviewer.md\n2. 读取输出格式：{SKILL_DIR}/references/output-schema.md\n3. 执行：{git diff 命令}\n4. 完成审查并返回 JSON\n{业务规则摘要}”
   )

2. delegate_subtask(
     agent_type=”Explore”,
     description=”Code review - 风格审查”,
     query=”你是代码审查专家，负责风格审查。\n1. 读取审查指令：{SKILL_DIR}/agents/style-reviewer.md\n2. 读取输出格式：{SKILL_DIR}/references/output-schema.md\n3. 执行：{git diff 命令}\n4. 完成审查并返回 JSON\n{业务规则摘要}”
   )

3. delegate_subtask(
     agent_type=”Explore”,
     description=”Code review - 可靠性审查”,
     query=”你是代码审查专家，负责可靠性审查（资源管理、并发安全、接口鉴权）。\n1. 读取审查指令：{SKILL_DIR}/agents/reliability-reviewer.md\n2. 读取输出格式：{SKILL_DIR}/references/output-schema.md\n3. 执行：{git diff 命令}\n4. 完成审查并返回 JSON\n{业务规则摘要}”
   )

4. delegate_subtask(
     agent_type=”Explore”,
     description=”Code review - 正确性审查”,
     query=”你是代码审查专家，负责正确性审查。\n1. 读取审查指令：{SKILL_DIR}/agents/correctness-reviewer.md\n2. 读取输出格式：{SKILL_DIR}/references/output-schema.md\n3. 执行：{git diff 命令}\n4. 完成审查并返回 JSON\n{业务规则摘要}”
   )

5. delegate_subtask(
     agent_type=”Explore”,
     description=”Code review - 自定义规则审查”,
     query=”你是代码审查专家，负责自定义规则审查。\n1. 读取审查指令：{SKILL_DIR}/agents/custom-reviewer.md\n2. 读取输出格式：{SKILL_DIR}/references/output-schema.md\n3. 执行：{git diff 命令}\n4. 按指令加载仓库根目录 .comate/custom-rules/ 下的规则文件，若无有效规则文件则返回空 findings\n5. 完成审查并返回 JSON\n{业务规则摘要}”
   )
```

每个 SubAgent 会自行读取对应的 reviewer 指令和输出格式，自行决定重点关注 diff 的哪些部分。

> 超大变更时，主 Agent 可按文件组拆分给不同 subagent（如只给复用审查传新增文件、只给正确性审查传高风险文件）。

#### 失败回退

- 某个 `delegate_subtask` 失败或超时：继续合并剩余结果，报告中注明”部分维度降级”
- 三个及以上失败：回退为单个综合审查（常规审查模式）
- `delegate_subtask` 工具不可用：主 Agent 直接执行审查，报告中注明”降级为单 Agent 审查”
- 上下文过大：缩小到高风险文件，必要时拆批执行

### Step 5：Meta-Review 与结果归并

当深度审查至少成功返回 2 个维度结果时，发起 Meta-Review：

```
delegate_subtask(
  agent_type=”Explore”,
  description=”Code review - Meta Review”,
  query=”””
你是 Meta-Reviewer，负责审查其他 Agent 的 review 结果质量。

1. 读取审查指令：{SKILL_DIR}/agents/meta-reviewer.md
2. 读取输出格式：{SKILL_DIR}/references/output-schema.md（Meta-Reviewer 输出格式部分）
3. 执行：{git diff 命令}（用于验证 findings 的准确性）
4. 以下是待审的 findings JSON：

{所有 SubAgent 返回的 findings JSON}

按指令完成 Meta-Review，返回 actions 和 missed_findings。
“””
)
```

> 注意：Meta-Review 的 query 中**必须包含已有的 findings 结果（JSON）**，因为 Meta-Reviewer 需要这些内容来判断质量。这是唯一需要在 query 中传递较多内容的 SubAgent 调用。

#### 归并规则

收集所有结果后，执行以下处理：
1. **先应用 Meta-Review actions**，再追加 `missed_findings`
2. **去重**：只有在“同一文件、重叠或相邻代码段、同一类别、同一根因”时才去重，不要机械按行号合并不同问题
3. **合并相近问题**：同一文件的重复模式可合并为一条，但要保留所有关键位置
4. **按严重等级排序**：`P0 > P1 > P2 > P3`
5. **统一重新编号**：输出给用户的最终编号使用连续数字，保留来源维度作为辅助信息

### Step 6：输出 Review 报告

用户需要在 10 秒内抓住关键问题。**简洁是第一优先级。**

#### 报告格式

```markdown
## Code Review 报告

**X 个文件 | +Y/-Z 行 | 深度审查 | 风险：高**

> 降级/分批/局部审查等特殊说明（无则省略）

---

### 🔴 P0 严重 (N)

**1. [file.ts:42](file.ts#L42)** — 一句话描述风险和触发条件
建议：一句话修复方向

### 🟠 P1 高优 (N)

**2. [file.ts:80](file.ts#L80)** — 一句话描述
建议：一句话建议

### 🟡 P2 中等 (N)

### 🔵 P3 低优 (N)

---

**结论**：建议修复 P0/P1 后合入（或：审查通过，可直接合入）
```

#### 输出规则

1. 每条 finding **限 2 行**：问题描述 + 建议，各 1 句话
2. 空级别直接省略，无问题写”审查通过”
3. 使用可点击路径 `[src/file.ts:42](src/file.ts#L42)`
4. 超过 10 条时：展示 P0/P1 全部 + P2/P3 各最多 3 条，末尾注明”另有 N 条，回复「展开」可查看”
5. 来源维度不展示，用户追问时再补充

### Step 7 **HARD-GATE** ：埋点上报与收尾

> **⚠️ 强制要求：埋点上报是必执行步骤，禁止遗漏。** 无论本次审查结果如何（有问题/无问题/降级/分批），都必须执行埋点上报。缺少埋点会导致后续数据链断裂，不得因任何原因跳过此步骤。

> **重要**：此步骤为后台操作，**任何失败（CLI 不存在、安装失败、执行报错）均不影响审查报告的输出和后续用户交互**。埋点失败时静默跳过，不向用户展示错误信息。

执行以下命令上报埋点：

```bash
aiscan-cli save-scan \
  -u <username> \            # ${COMATE_USERNAME}
  -r <repo> \                # 仓库路径，如 baidu/aa/bb
  -t <trace-id>              # ${COMATE_SESSION_ID}
```

在本次会话中第一次执行 CLI 命令之前，直接执行目标命令。若命令执行报错（包括 command not found、CLI 不存在、版本不兼容等任何错误），则执行安装：

```bash
AISCAN_CLI_VERSION=0.2.0 bash -c "$(curl -fsSL https://bep-qa.bj.bcebos.com/aiscan-cli/install_aiscan_cli.sh)"
```

安装完成后使用 `~/.aiscan-cli/bin/aiscan-cli`（如果 PATH 未生效，后续命令均用完整路径）。

- 安装或执行仍报错：**静默跳过，直接进入 Step 8**，不向用户展示任何错误
- 此检查在整个会话中只需执行一次，首次确认可用后后续直接使用已确认的命令路径


### Step 8：用户交互

完成报告后**必须暂停**，使用 `ask_user_question` 工具向用户提供下一步选项，**不要自动执行任何修复或提交操作**。

调用 `ask_user_question` 时，根据实际审查结果动态构建选项：

- 如果存在 P0/P1 问题，提供以下选项：
  1. 修复全部问题
  2. 仅修复 P0/P1
  3. 选择性修复（稍后指定编号）
  4. 仅记录问题，不改代码

- 如果只有 P2/P3 问题，提供以下选项：
  1. 修复全部问题
  2. 选择性修复（稍后指定编号）
  3. 仅记录问题，不改代码

- 如果未发现问题，跳过此步骤，直接告知用户审查通过。

在用户通过 `ask_user_question` 明确选择前：
- 不要自动修改代码
- 不要自动提交代码
- 不要把 review 结论当作已执行修复

用户选择修复后：
- 如果用户选择"选择性修复"，追问具体要修复的 finding 编号
- 优先修复 P0/P1
- 修复后可建议重新运行 review 或最小化验证

## 严重等级定义

| 等级 | 标记 | 含义 | 处理建议 |
|------|------|------|----------|
| `P0` | 🔴 | 明确的严重 bug、安全漏洞、数据损坏或崩溃风险 | 必须阻断合入 |
| `P1` | 🟠 | 高概率逻辑问题、显著性能问题、重要边界错误 | 合入前应修复 |
| `P2` | 🟡 | 中等可维护性或稳定性问题 | 建议本次修复或创建后续任务 |
| `P3` | 🔵 | 低风险改进项 | 可选优化 |

## 资源文件

SubAgent 通过 `SKILL_DIR` 路径自行读取以下文件：

- `agents/reuse-reviewer.md`、`agents/style-reviewer.md`、`agents/reliability-reviewer.md`、`agents/correctness-reviewer.md`：四个维度的审查指令
- `agents/custom-reviewer.md`：自定义规则审查指令
- `agents/meta-reviewer.md`：Meta-Review 指令
- `references/output-schema.md`：SubAgent 输出结构
- `references/custom-rules/`：skill 内置规则模板目录（参考用）
- `.comate/custom-rules/`：团队/项目自定义规则文件目录（仓库根目录，`.md` 格式，无有效文件时 custom-reviewer 自动跳过）

## 备注

- 目标是高价值 finding，不是找出尽可能多的问题
- 报告让用户 10 秒内抓住关键——短句、emoji、可点击路径
- 上下文不足时明确写出”不足以确认”，不强行下结论
