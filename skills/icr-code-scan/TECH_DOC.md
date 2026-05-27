# Code Review Skill — 技术文档

> 本文档描述 `code-review` skill 的执行逻辑、知识体系、审查模式与整体架构。

---

## 零、全局视图

### 0.1 整体架构图

> 严格对应手稿结构：用户 → diff处理 → [基本审查 | 深度审查] → Meta-Review → 输出。
> 知识层置于执行层正上方，整体连接为垂直向下，消除线交叉。

```mermaid
graph TB
    USER(["👤 用户 query 触发 skill\ncode review / CR / 帮我审查代码"])
    USER --> D1

    subgraph DIFF["🔍 diff 处理  主 Agent"]
        direction TB
        D1["① 范围探测\nstaged → unstaged/untracked → 分支差异 → 最近提交\n单次 run_command，记录基准 diff 命令"]
        D2["② 范围过滤\n跳过: lockfile · 构建产物 · 二进制 · 格式噪音\n保留: 鉴权 · 命令执行 · 网络 · 持久化 · 启动入口"]
        D3["③ 风险分级\n统计文件数/行数，检测高风险目录/公共API/异步状态/新协议"]
        D4{"④ 审查模式决策"}
        D1 --> D2 --> D3 --> D4
    end

    subgraph KNOW["📚 知识层  SubAgent 收到 SKILL_DIR 路径后自行按需读取"]
        direction TB
        KN1["agents/  审查指令文件 ×6\ncorrectness · reliability · style · reuse · custom · meta"]
        KN2["references/rules/  各语言缺陷规则\nJs · Go · Java · Python"]
        KN3["output-schema.md  统一 JSON 输出格式\n.comate/custom-rules/  团队自定义规则"]
    end

    KNOW -. "路径传递\n各 SA 自行读取\n仅加载所需规则" .-> SB0
    KNOW -. "路径传递\n各 SA 自行读取\n仅加载所需规则" .-> SS1

    subgraph SA_BASIC["📋 基本审查  常规模式"]
        SB0["综合审查 SubAgent × 1\n依次读取 5 个维度指令，各抽取 2-3 个核心检查点\n执行 git diff → 按语言加载规则 → 输出 findings JSON"]
    end

    subgraph SA_DEEP["⚡ 深度审查  5 个并行 SubAgent"]
        direction LR
        SS1["SA① 正确性\n空值/类型/异常/控制流\n[Critical] → locked=true"]
        SS2["SA② 可靠性\n资源泄漏/并发竞态\n鉴权缺失/越权/N+1"]
        SS3["SA③ 风格\n命名/格式/注释\n仅报规则明确列出的问题"]
        SS4["SA④ 复用\n搜索 utils/helpers/lib\nread_file 确认后才上报"]
        SS5["SA⑤ 自定义\n.comate/custom-rules/\n无有效文件则返回空 []"]
    end

    D4 -- "≤5文件 ≤200行\n未命中高风险" --> SB0
    D4 -- ">5文件 或 >200行\n或命中高风险" --> SS1

    SB0 --> MT0
    SS1 & SS2 & SS3 & SS4 & SS5 --> MT0

    subgraph META["🔎 Meta-Review  质量复核  主 Agent 发起"]
        MT0["Meta-Review SubAgent × 1\n接收所有 findings JSON（≥2 个维度成功才触发）\n逐条质疑真实性 · 等级合理性 · 建议可执行性\nlocked=true → 禁止调整 severity\n输出 actions + missed_findings"]
    end

    MT0 --> OG1

    subgraph OUT["📤 输出 & 用户交互  主 Agent"]
        direction TB
        OG1["结果归并\napply actions → 追加遗漏 → 去重 → P0>P1>P2>P3 排序 → 重编号"]
        OG2["Review 报告 Markdown\nP0🔴 必须阻断  P1🟠 合入前修复  P2🟡 建议修复  P3🔵 可选\n每条限 2 行: 问题描述 + 修复建议  可点击文件路径"]
        OG3["埋点上报  aiscan-cli save-scan  静默执行\n失败则静默跳过，不影响报告与后续交互"]
        OG4["ask_user_question  等待用户决策\n修复全部 / 仅修复 P0P1 / 选择性修复 / 仅记录"]
        OG1 --> OG2 --> OG3 --> OG4
    end

    style KN1 fill:#fce7f3,stroke:#ec4899,color:#831843
    style KN2 fill:#fce7f3,stroke:#ec4899,color:#831843
    style KN3 fill:#fce7f3,stroke:#ec4899,color:#831843
    style SS1 fill:#fce7f3,stroke:#ec4899,color:#9d174d
    style SS2 fill:#fce7f3,stroke:#ec4899,color:#9d174d
    style SS3 fill:#fce7f3,stroke:#ec4899,color:#9d174d
    style SS4 fill:#fce7f3,stroke:#ec4899,color:#9d174d
    style SS5 fill:#fce7f3,stroke:#ec4899,color:#9d174d
    style KNOW fill:#fdf2f8,stroke:#ec4899
    style SA_DEEP fill:#fdf2f8,stroke:#f472b6
```

---

### 0.2 整体流程图

> 从触发到用户交互的完整端到端执行流，涵盖所有分支与降级路径。

```mermaid
flowchart TD
    START([触发 code-review skill]) --> PROBE

    PROBE["探测工作区  单次 run_command"]
    PROBE --> CHK_WS{工作区有变更?}

    CHK_WS -- "有 staged/unstaged" --> RNG_WS["git diff / git diff --cached\n使用过滤后的文件列表"]
    CHK_WS -- "有 untracked 文件" --> RNG_UT["read_file 读取\n小文件全读 · 大文件读关键片段"]
    CHK_WS -- 无变更 --> CHK_BR{分支有差异?}

    CHK_BR -- 是 --> RNG_BR["git diff merge-base HEAD\n当前分支 vs 目标分支"]
    CHK_BR -- 否 --> RNG_CM["git diff HEAD~1 HEAD\n最近一次提交"]
    RNG_CM -- 仍无内容 --> STOP_ASK([提示用户手动指定范围])

    RNG_WS --> FILTER
    RNG_UT --> FILTER
    RNG_BR --> FILTER
    RNG_CM --> FILTER

    FILTER["范围过滤\n跳过: lockfile · 构建产物 · 二进制 · 格式噪音\n保留: 鉴权 · 命令执行 · 网络 · 持久化"]
    FILTER --> STAT

    STAT["统计变更概览\n文件数 · +/- 行数 · 是否有新文件 · 高风险目录"]
    STAT --> RULES

    RULES["加载业务规则\n读取 .comate/rules · CLAUDE.md 等\n提取与本次变更相关的 1-2 句摘要"]
    RULES --> MODE{审查模式判断}

    MODE -- "文件≤5 且 行≤200\n且 未命中高风险" --> NML_SA["发起综合审查 SA\n5维度各 2-3 个核心检查点"]
    MODE -- "文件>5 或 行>200\n或 命中高风险" --> DPL["同一轮响应\n并行发起 5 个 delegate_subtask"]
    MODE -- "文件>20 或 行>800\n超大变更" --> SPLIT["拆批 / 抽样审查\n优先高风险部分，报告注明分批情况"]
    SPLIT --> DPL

    NML_SA --> NML_OUT["返回 findings JSON"]

    subgraph DEEP_BOX["深度审查  5 个并行 SubAgent"]
        DPL --> DEP1["SA: 正确性\ncorrectness-reviewer.md"]
        DPL --> DEP2["SA: 可靠性\nreliability-reviewer.md"]
        DPL --> DEP3["SA: 风格\nstyle-reviewer.md"]
        DPL --> DEP4["SA: 复用\nreuse-reviewer.md"]
        DPL --> DEP5["SA: 自定义\ncustom-reviewer.md"]
        DEP1 & DEP2 & DEP3 & DEP4 & DEP5 --> DPL_OUT["收集各维度 findings JSON"]
    end

    DPL_OUT --> CHK_META{成功维度 ≥ 2?}
    CHK_META -- 是 --> META_SA["发起 Meta-Review SA\nmeta-reviewer.md\n传入已有 findings JSON"]
    CHK_META -- "否  全部失败" --> FALLBACK["降级为常规审查\n报告注明「部分维度降级」"]
    FALLBACK --> NML_OUT

    META_SA --> META_OUT["返回 actions\n+ missed_findings"]

    NML_OUT --> MERGE
    META_OUT --> MERGE

    MERGE["结果归并\n① 应用 Meta actions\n② 追加 missed_findings\n③ 去重 · 合并相近\n④ P0>P1>P2>P3 排序 · 重编号"]
    MERGE --> REPORT

    REPORT["输出 Review 报告  Markdown\nP0🔴 · P1🟠 · P2🟡 · P3🔵\n超 10 条时 P2/P3 各最多展示 3 条"]
    REPORT --> TRACK

    TRACK["埋点上报  aiscan-cli save-scan  静默\n失败则静默跳过"]
    TRACK --> INTERACT

    INTERACT["ask_user_question\n根据问题严重度动态构建选项"]
    INTERACT --> CHK_CHOICE{用户选择}

    CHK_CHOICE -- "修复全部 / 仅修复 P0P1 / 选择性修复" --> FIX["执行代码修复\n优先 P0/P1\n修复后建议重新 review"]
    CHK_CHOICE -- "仅记录 不改代码" --> END_R([记录问题  结束])
    FIX --> END_F([修复完成])
```

---

## 一、目录结构

```
code-review/
├── SKILL.md                    # 主控指令（主 Agent 执行）
├── agents/
│   ├── correctness-reviewer.md # 正确性审查 SubAgent
│   ├── reliability-reviewer.md # 可靠性审查 SubAgent
│   ├── style-reviewer.md       # 风格审查 SubAgent
│   ├── reuse-reviewer.md       # 复用审查 SubAgent
│   ├── custom-reviewer.md      # 自定义规则审查 SubAgent
│   └── meta-reviewer.md        # Meta-Review SubAgent（质量复核）
└── references/
    ├── output-schema.md        # 统一 JSON 输出格式规范
    └── rules/
        ├── Js/                 # JS/TS 规则文件
        │   ├── JS_CORRECTNESS_RULES.md
        │   ├── JS_RESOURCE_CONCURRENCY_RULES.md
        │   ├── JS_AUTH_RULES.md
        │   └── JS_STYLE_RULES.md
        ├── Go/                 # Go 规则文件
        ├── Java/               # Java 规则文件
        └── Python/             # Python 规则文件
```

---

## 二、知识体系

### 2.1 知识类型

| 类型 | 内容 | 位置 |
|------|------|------|
| **审查指令** | 各维度的检测方法、排除条件、分级标准 | `agents/*.md` |
| **语言规则** | 按语言分类的具体缺陷模式，含 `[Critical]`/`[high]`/`[middle]`/`[low]` 标记 | `references/rules/<Lang>/` |
| **输出规范** | SubAgent 统一 JSON Schema、Category 分类表、合并规则 | `references/output-schema.md` |
| **业务规则** | 团队/项目自定义规则（仓库根目录） | `.comate/custom-rules/*.md` |
| **项目规范** | 仓库级 AI 指令文件 | `.comate/rules/`、`CLAUDE.md`、`.cursorrules` 等 |

### 2.2 知识加载方式

**核心原则**：主 Agent 不预读、不注入知识内容，只传递路径。SubAgent 有完整工具集，自行按需加载，大幅节省主 Agent token。

```mermaid
flowchart LR
    A["主 Agent\n(SKILL.md)"]
    B["SubAgent\n(Explore)"]

    A -- "① 传递 SKILL_DIR 路径\n+ git diff 命令\n+ 业务规则摘要(1-2句)" --> B

    B --> C["读取 agents/&lt;role&gt;-reviewer.md"]
    B --> D["读取 references/output-schema.md"]
    B --> E["读取 rules/&lt;Lang&gt;/*.md\n(按文件扩展名按需)"]
    B --> F["读取 .comate/custom-rules/*.md\n(custom-reviewer 专用)"]
```

---

## 三、整体架构

```mermaid
flowchart TD
    S([触发 code-review skill])

    S --> S1["Step 1\n确定审查范围\n探测 staged / unstaged / branch"]
    S1 --> S2["Step 2\n加载业务规则\n读取 .comate/rules 等项目规范摘要"]
    S2 --> S3["Step 3\n选择审查模式"]

    S3 --> M1["常规审查\n文件≤5 且 行≤200 且 低风险"]
    S3 --> M2["深度审查\n文件>5 或 行>200 或 高风险"]

    M1 --> S4A["Step 4A\n单 SubAgent 综合审查"]
    M2 --> S4B["Step 4B\n5个 SubAgent 并行审查"]
    S4B --> S5["Step 5\nMeta-Review 复核 + 补漏"]

    S4A --> S6["Step 6\n结果归并 + 输出报告"]
    S5  --> S6

    S6 --> S7["Step 7\n埋点上报 aiscan-cli（静默）"]
    S7 --> S8["Step 8\n用户交互 ask_user_question"]
```

---

## 四、执行流程

### 4.1 主流程图

```mermaid
flowchart TD
    A([开始]) --> B["探测工作区变更\n单次 run_command"]

    B --> C{有 staged/unstaged\n/untracked?}

    C -- 是 --> D["以工作区内容\n为审查范围"]
    C -- 否 --> E{分支有差异?}
    E -- 是 --> F["当前分支 vs 目标分支"]
    E -- 否 --> G["最近一次提交\nHEAD~1"]
    E -- 都没有 --> H([提示用户手动指定])

    D --> I["范围过滤\n跳过: lockfile / 构建产物 / 二进制\n保留: 鉴权 / 命令执行 / 网络 / 持久化"]
    F --> I
    G --> I

    I --> J["风险分级\n统计文件数 / 行数\n检测高风险模块 / 新流程 / 新协议"]

    J --> K{审查模式判断}

    K -- "文件≤5 且 行≤200\n且 低风险" --> L["常规审查\n单 SubAgent 综合审查\n5维度各 2-3 个检查点"]
    K -- "文件>5 或 行>200\n或 高风险" --> M["深度审查\n5个 SubAgent 并行"]

    M --> N["Meta-Review 复核\n至少 2 个维度成功时触发"]

    L --> O["结果归并"]
    N --> O

    O --> P["输出 Markdown 报告\nP0→P1→P2→P3 排序"]
    P --> Q["埋点上报（静默）"]
    Q --> R["ask_user_question\n等待用户决策"]
    R --> Z([结束])
```

### 4.2 Git Diff 获取逻辑

```mermaid
flowchart TD
    A["探测工作区状态\n单次 run_command"] --> B{工作区有变更?}

    B -- 有 staged --> C["git diff --cached\n-- 过滤后的文件列表"]
    B -- 有 unstaged --> D["git diff\n-- 过滤后的文件列表"]
    B -- 有 untracked --> E{文件大小?}
    E -- 小文件 --> F["read_file 全文\n标记 [新文件]"]
    E -- 大文件 --> G["read_file 关键片段\n报告说明局部审查"]

    B -- 无变更 --> H["git diff merge-base HEAD\n当前分支 vs 目标分支"]
    H -- 无内容 --> I["git diff HEAD~1 HEAD\n最近一次提交"]

    C --> Z["记录基准 diff 命令\n写入所有 SubAgent query\n保证基于同一基准"]
    D --> Z
    F --> Z
    G --> Z
    H --> Z
    I --> Z
```

---

## 五、审查模式

### 5.1 常规审查（单 Agent）

**触发条件**：文件数 ≤ 5 且 行数 ≤ 200 且 未命中高风险模块

```mermaid
flowchart TD
    A["单个 Explore SubAgent"] --> B["读取 5 个维度\nagents/*.md"]
    B --> C["读取输出规范\nreferences/output-schema.md"]
    C --> D["执行 git diff 获取变更"]
    D --> E["按语言加载对应规则文件"]
    E --> F["各维度各抽取 2-3 个核心检查点"]
    F --> G["输出统一 JSON findings"]
```

### 5.2 深度审查（5 并行 SubAgent）

**触发条件**：文件数 > 5 或 行数 > 200 或 命中高风险模块

```mermaid
flowchart TD
    A["主 Agent\n同一轮响应中并行发起"]

    A --> B1["SubAgent 1\ncorrectness-reviewer\n检测: 空值 / 类型 / 异常 / 控制流"]
    A --> B2["SubAgent 2\nreliability-reviewer\n检测: 资源泄漏 / 并发竞态 / 鉴权缺失"]
    A --> B3["SubAgent 3\nstyle-reviewer\n检测: 格式 / 命名 / 注释规范"]
    A --> B4["SubAgent 4\nreuse-reviewer\n检测: 重复函数 / 可复用内联逻辑"]
    A --> B5["SubAgent 5\ncustom-reviewer\n检测: .comate/custom-rules 自定义规则"]

    B1 --> C["各自输出 JSON findings\n{ reviewer, summary, findings[] }"]
    B2 --> C
    B3 --> C
    B4 --> C
    B5 --> C
```

---

## 六、SubAgent 知识加载流程

```mermaid
flowchart TD
    A["收到 query\nSKILL_DIR 路径 + git diff 命令"] --> B["读取 agents/role-reviewer.md\n获取本维度审查指令"]
    B --> C["读取 references/output-schema.md\n获取 JSON 输出格式"]
    C --> D["执行 git diff 命令\n获取变更内容"]
    D --> E["识别文件扩展名\n判断语言类型"]

    E --> F{匹配到支持语言?}

    F -- 是 --> G["读取对应规则文件\nreferences/rules/Lang/*.md\n(只读检测到的语言)"]
    F -- 否 --> H["基于通用编程知识审查\n不设 locked 字段"]

    G --> I["读取源文件上下文\n变更行 ±30 行"]
    H --> I

    I --> J["按需搜索调用链 / 类型定义\ngrep / glob (仅在判断需要时)"]
    J --> K["输出 JSON findings\n证据不足则留空 []"]
```

---

## 七、Meta-Review 复核流程

```mermaid
flowchart TD
    A["收到所有 SubAgent 的 findings JSON\n（至少 2 个维度成功）"] --> B["逐条质疑每个 finding"]

    B --> C{问题真实存在?}
    C -- 否 --> D["action: remove\n移除误报"]
    C -- 是 --> E{严重等级合理?}

    E -- 偏高/偏低 --> F{finding 有 locked=true?}
    F -- 是 --> G["禁止调整 severity\n可执行 refine / supplement"]
    F -- 否 --> H["action: adjust_severity\n重新定级"]

    E -- 合理 --> I{建议是否可执行?}
    I -- 不够具体 --> J["action: refine_suggestion\n补充修复建议"]
    I -- 可以 --> K["保留原 finding"]

    D --> L["交叉维度检查\n识别跨维度遗漏"]
    G --> L
    H --> L
    J --> L
    K --> L

    L --> M{发现遗漏?}
    M -- 是 --> N["missed_findings\n补充遗漏问题"]
    M -- 否 --> O["输出 Meta-Review JSON\nactions + missed_findings"]
    N --> O
```

---

## 八、结果归并规则

```mermaid
flowchart TD
    A["收集所有 SubAgent findings\n+ Meta-Review 结果"] --> B["应用 Meta actions\n顺序: remove → adjust_severity\n→ refine_suggestion → supplement"]
    B --> C["追加 missed_findings"]
    C --> D["去重\n同文件 + 行号±5 + 同 category = 重复\n保留 description 最详细的"]
    D --> E["合并相近\n同文件同类型多处 → 合为一条\n保留所有关键位置"]
    E --> F["按严重等级排序\nP0 > P1 > P2 > P3"]
    F --> G["连续重新编号\n1, 2, 3 …"]
    G --> H["输出最终 findings 列表"]
```

---

## 九、失败降级策略

```mermaid
flowchart TD
    A["深度审查中 SubAgent 执行"] --> B{失败数量?}

    B -- "1-2 个失败" --> C["继续合并剩余结果\n报告注明「部分维度降级」"]
    B -- "3+ 个失败" --> D["降级为常规审查\n单 Agent 综合审查"]

    A2["其他异常情况"] --> E{异常类型?}
    E -- "delegate_subtask 不可用" --> F["主 Agent 直接审查\n注明「降级为单 Agent」"]
    E -- "变更超大 >20文件 >800行" --> G["拆批 / 抽样审查\n优先高风险部分\n报告说明分批情况"]
    E -- "SubAgent 超时" --> C

    C --> Z["正常输出报告"]
    D --> Z
    F --> Z
    G --> Z
```

---

## 十、严重等级定义

| 等级 | 标记 | 含义 | 规则标记来源 | 处理建议 |
|------|------|------|------------|----------|
| P0 | 🔴 | 严重 bug、安全漏洞、数据损坏、崩溃风险 | `[Critical]` / `[high]` | 必须阻断合入 |
| P1 | 🟠 | 高概率逻辑问题、显著性能问题、重要边界错误 | `[high]` / `[Critical]` | 合入前应修复 |
| P2 | 🟡 | 中等可维护性或稳定性问题 | `[middle]` | 建议本次修复或创建后续任务 |
| P3 | 🔵 | 低风险改进项 | `[low]` | 可选优化 |

**locked 字段**：来自 `[Critical]` 标记规则的 finding 携带 `locked: true`，Meta-Review 禁止对其执行 `adjust_severity`，只允许 `remove`（确认误报）、`refine_suggestion`、`supplement`。

---

## 十一、输出报告格式

```markdown
## Code Review 报告

**X 个文件 | +Y/-Z 行 | 深度审查 | 风险：高**

---

### 🔴 P0 严重 (N)

**1. [file.ts:42](file.ts#L42)** — 一句话描述风险和触发条件
建议：一句话修复方向

### 🟠 P1 高优 (N)
### 🟡 P2 中等 (N)
### 🔵 P3 低优 (N)

---

**结论**：建议修复 P0/P1 后合入
```

**输出规则**：
- 每条 finding 限 2 行（描述 + 建议）
- 空级别省略；无问题写"审查通过"
- 超过 10 条时展示 P0/P1 全部 + P2/P3 各最多 3 条，末尾注明"另有 N 条，回复「展开」可查看"

---

## 十二、核心设计原则

| 原则 | 说明 |
|------|------|
| **范围优先于结论** | 先确认审查范围，避免误扩大到整个分支 |
| **风险优先于规模** | 文件数/行数只是参考，高风险小改动也走深度审查 |
| **证据优先于偏好** | 只报有代码证据的问题，不输出纯风格偏好 |
| **简洁优先于详尽** | 10秒内抓住关键，每条 finding 限 2 行 |
| **上下文按需加载** | SubAgent 自行决定读取哪些上下文，主 Agent 不预加载 |
| **失败可降级** | 任何环节失败均自动降级而非中断审查 |
