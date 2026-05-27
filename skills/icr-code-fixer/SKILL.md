---
name: icr-code-fixer
description: "当用户涉及以下任何场景时，应使用此技能: 修复代码; 修复代码中全部问题; 查询代码扫描结果并修复; 查看扫描报告并进行修复; 帮我修复扫描ID的代码问题; 查看并修复代码问题、bug 列表、HIGH 级别问题"
metadata:
  cli_version: "0.2.0"
---

# 代码修复器

## 概述

本技能通过 `aiscan-cli` 命令行工具查询代码扫描结果，针对各语言类型的代码问题进行分析、定位原因并实施正确的修复。修复完成后，会依据典型案例库进行二次Review，确保无遗漏问题；且无论修复成功与失败都务必要把临时文件删除

## CLI 安装检查（每次会话仅需一次）

**在本次会话中第一次执行 CLI 命令之前**，必须先运行版本检查:
```bash
  aiscan-cli version
```   

1. CLI 未安装（command not found）→ 再尝试完整路径 ~/.aiscan-cli/bin/aiscan-cli
version，仍然失败则执行安装:

AISCAN_CLI_VERSION=0.2.0 bash -c "$(curl -fsSL
https://bep-qa.bj.bcebos.com/aiscan-cli/install_aiscan_cli.sh)"

安装完成后使用 ~/.aiscan-cli/bin/aiscan-cli（如果 PATH 未生效，后续命令用完整路径）。

2. 版本低于要求（低于 0.2.0）→ 执行上面的安装命令更新。
3. 版本符合要求 → 记住可用的命令路径，本次会话内不再重复检查


## 循环控制与终止条件

**最大尝试次数限制：**
- 对同一个文件的问题修复，最多尝试 **3 次**
- 如果 3 次后仍未解决，停止修复并输出以下话术：
  > "文件 [文件名] 中的问题经过 3 次尝试仍未修复成功，建议人工介入处理。问题描述：[具体问题]"

**禁止行为：**
- 禁止对同一个文件的同一个问题重复应用相同的修复方案超过 1 次
- 禁止在无变化的情况下重新调用 API 获取扫描报告
- 禁止在修复完成后再次进入定位→修复的循环

**终止信号识别：**
当出现以下情况时，必须立即停止修复并输出当前状态：
1. 连续两次修复后代码没有任何变化
2. 修复后的代码引入了相同类型的新错误
3. 扫描报告中所有问题都已修复（通过文件内容比对确认）

**输出格式要求：**
- 查询失败：输出上述话术，并删除本地的`bug_report.txt`文件
- 修复成功：直接输出修复后的代码，并删除本地的`bug_report.txt`文件
- 达到上限停止：输出上述话术，并附上最后一次修复尝试的代码

## 工作流程

代码修复涉及以下步骤：
### 0. 调试参数检查： 
    - 获取以下环境变量，并确认参数是否正确传入：
    - IDE名称: ${COMATE_IDE_NAME}
    - 插件版本: ${COMATE_PLUGIN_VERSION}
    - 用户名: ${COMATE_USERNAME}
    - 会话ID: ${COMATE_SESSION_ID}
    
### 1. 查询扫描结果：
**场景 A：输入内容包含 jobId**

- 检测用户输入中是否包含 jobId 参数
- 如果存在 jobId，使用  **aiscan-cli scan <job_id> -o bug_report.txt** 获取代码扫描报告并保存到文件
  - 如果查询成功（exit code 0），将查询的扫描结果总结一下以 markdown表格的形式展示出来，只需要展示一共有多少个高危问题，不要展示问题文件列表
  - 如果查询失败，请一定要删除本地的`bug_report.txt`文件。

**场景 B：输入内容不包含 jobId**

- 检测用户输入中不包含 jobId 参数
- 分析用户输入的内容，识别其中存在的代码缺陷和代码规范相关问题
- 如果发现代码缺陷或规范问题，将问题描述、位置信息、严重程度等整理成结构化格式
- 将分析结果写入 `bug_report.txt` 文件，同时结果总结一下以 markdown表格的形式展示出来，只需要展示一共有多少个高危问题，不要展示问题文件列表
- 如果未发现代码问题，输出提示："未检测到代码缺陷或规范问题，暂不进行修复”


### 2. 识别代码类型

从 `bug_report.txt` 中读取扫描报告内容，根据以下规则识别代码语言：

**支持的语言类型：**
如果是以下语言类型，则在实施修复的时候，可以再参考下references文件中各语言类型的修复示例
- **JavaScript/TypeScript**：文件扩展名 `.js`, `.jsx`, `.ts`, `.tsx`, `.vue`, `.css`
- **Java**：文件扩展名 `.java`
- **Python**：文件扩展名 `.py`
- **Go**：文件扩展名 `.go`

**语言类型判断逻辑：**
- 优先从扫描报告中提取文件扩展名进行判断
- 如果报告包含多个文件，分别为每个文件识别语言类型并按语言分组处理


### 3. 定位问题

根据语言类型，在扫描报告中定位到相关的错误代码段及其上下文：
- 提取文件路径、行号、错误类型、错误描述
- 获取错误代码段的上下文（前后若干行）
- 标记需要修复的具体位置

### 4. 实施修复（按语言类型）

#### JavaScript/TypeScript 类型修复
- 基于提供的 JS 代码扫描结果与异常代码块进行分析
- **必须遵循 ESLint 规则**进行代码修正，包括但不限于：
  - 变量声明与作用域规则（no-undef, no-redeclare, no-shadow）
  - 代码风格规则（semi, quotes, comma-dangle, indent）
  - 最佳实践规则（no-var, prefer-const, eqeqeq, no-unused-vars）
  - ES6+ 语法规范（arrow-body-style, no-duplicate-imports）
- 修复时参考 ESLint 官方推荐的修复方案
- 禁止修改代码缩进（除非修复 ESLint indent 规则问题）
- 禁止修改代码闭合结构
- 禁止添加无关注释与思考过程
- 直接输出代码结果

#### Java 类型修复
- 基于提供的 Java 代码扫描结果与完整代码中异常部分的闭合上下文进行分析
- **必须遵循 Java Code Style 与 Google Java Style** 进行代码修正，包括但不限于：
  - 命名规范（类名 UpperCamelCase，方法/变量 lowerCamelCase，常量 CONSTANT_CASE）
  - 代码结构（缩进 2 或 4 空格，大括号使用 K&R 风格）
  - 语句规范（每行一条语句，switch 语句包含 default）
  - 注释规范（类注释、方法注释使用 Javadoc）
  - 导入语句规范（不使用通配符导入，按静态导入→第三方导入→项目导入分组）
- 修复时参考 Google Java Style Guide 规范
- 禁止修改代码缩进
- 禁止修改代码闭合结构
- 禁止添加无关注释与思考过程
- 直接输出代码结果

#### Python 类型修复
- 基于提供的 Python 代码扫描结果与异常代码块进行分析
- **必须遵循 PEP 8 与 PEP 257 规范** 进行代码修正，包括但不限于：
  - 命名规范（类名 UpperCamelCase，函数/变量 lower_case_with_underscores，常量 UPPER_CASE）
  - 代码格式（4 空格缩进，每行不超过 79 字符，二元运算符前后空格）
  - 导入语句规范（每个导入独占一行，分组：标准库 → 第三方库 → 本地模块，禁止通配符导入）
  - 变量声明规范（使用 is 比较 None/布尔值，避免 from module import *）
  - 异常处理规范（捕获具体异常，except: 禁止裸使用，finally 清理资源）
  - 函数规范（类型注解推荐，可变参数使用 *args/**kwargs，避免可变默认参数）
  - 注释规范（docstring 使用 """triple quotes"""，行注释与代码同级）
  - 异步规范（async/await 正确使用，避免 asyncio.run() 重复调用）
- 修复时参考 Ruff/Pylint/Flake8 推荐修复方案
- 禁止修改代码缩进
- 禁止修改代码闭合结构
- 禁止添加无关注释与思考过程
- 直接输出代码结果

#### 其他语言 类型修复
- 基于提供的代码扫描结果与异常代码块进行分析，并根据对应语言的主流规则进行修复

### 5. Review 修复结果（关键步骤）

修复完成后，务必对照对应语言的典型案例与常见遗漏清单，逐项检查是否存在遗漏未修复的问题：

- **JS/TS 类型**：参阅 `references/javaScript_fix_module.md`
- **Java 类型**：参阅 `references/java_fix_module.md`
- **Python 类型**：参阅 `references/python_fix_module.md`

**Review 检查项：**
- 是否所有报告中的问题都已修复
- 是否有遗漏的格式问题
- 是否引入了新的错误
- 修复后的代码是否符合对应语言的最佳实践

若发现遗漏，补充修复。

### 6. 验证

- 代码扫描报告中可能含有多个文件，要保证所有文件中的问题均被修复
- 不要多次遍历同一个文件
- 不需要重新运行 API 调用获取代码扫描报告，只需检查文件是否确实已修改
- 确认修复不会破坏现有功能

### 7. 收尾
- 修复成功和修复失败都需要删除临时生成的 `bug_report.txt` 文件
- 使用 CLI 上报埋点数据：
    ```bash
    aiscan-cli save-repair \
      -u <username> \      # ${COMATE_USERNAME}
      -r <repo> \          # 仓库路径，如 baidu/aa/bb
      -j <job-id> \        # 扫描任务 ID
      -t <trace-id> \      # ${COMATE_SESSION_ID}
      --bug-num <bug-num> \      # 扫描报告中的 ERROR 类型的 bug 总数
      --repair-num <repair-num> \   # 实际修复的 bug 总个数
      --source icode
    ```   
- 展示文案：是否重新扫描文件发现更多问题

## 输入参数说明

本技能支持两种输入方式：

### 方式一：提供 jobId
- 用户输入应包含 jobId 参数
- 例如："帮我修复 jobId 为 xxx 的代码扫描结果"
- 技能将使用 jobId 调用 API 获取扫描报告

### 方式二：提供代码内容
- 用户直接输入代码片段或问题描述
- 技能将分析输入内容，识别其中的代码缺陷和规范问题
- 例如："帮我修复这段代码：[代码内容]"、"根据代码扫描结果，帮我修复问题”


## 查询扫描结果说明
如果存在jobId参数，则使用 **aiscan-cli** 命令行工具查询扫描报告：
### 基本用法：查询并保存到文件
  aiscan-cli scan <job_id> -o bug_report.txt

### 基本用法：上传修复埋点信息
  aiscan-cli save-repair -u zhangsan -r baidu/aa/bb -j 123456 -t f39d1c8a-455d-4c2f-b2432-a9d691c464be --bug-num 5 --repair-num 3 --source icode

### 带调试信息
  aiscan-cli scan <job_id> -o bug_report.txt -v

### 自定义超时（网络较慢时）
  aiscan-cli scan <job_id> -o bug_report.txt --timeout 60s

#### 错误处理
  | 场景 | 现象 | 处理方式 |
  |------|------|---------|
  | 接口不可达 | stderr 输出网络错误，exit code 1 | 告知用户当前不在内网或接口服务异常 |
  | job_id 不存在 | CLI 返回失败 | 告知用户 ID 不存在或尚未生成扫描结果 |
  | 无任何问题 | 输出问题列表后无内容 | 告知用户该扫描任务没有发现问题 |
  | 超时 | stderr 输出超时错误 | 用 `--timeout 60s` 重试 |

## 典型案例与常见遗漏清单

这些文档记录了以往修复过程中容易遗漏的问题案例，**在 Review 阶段必须逐条对照检查**：

JS类型：请参阅 [references/javaScript_fix_module.md](references/javaScript_fix_module.md)。
JAVA类型：请参阅 [references/java_fix_module.md](references/java_fix_module.md)。
## 验证规则

始终通过以下方式验证修复：
1. 运行代码以确认错误已解决（如环境允许）
2. 检查没有引入新错误
3. 确保修复不会破坏现有功能
4. 禁止添加额外 `}`
5. 禁止添加无关注释与思考过程
6. 直接输出代码结果
7. 禁止修改代码缩进
8. 禁止修改代码闭合结构

## 资源

### references/
- `javaScript_fix_module.md` - JS/TS 类型典型案例与常见遗漏清单（Review 阶段使用）
- `java_fix_module.md` - Java 类型典型案例与常见遗漏清单（Review 阶段使用）
