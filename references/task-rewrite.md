# Task Rewrite

## When to Use

- Gitea Issue 进来，需要判断是否能做、如何做
- 生成 tasks.md 之前
- Poller 发现新 issue，需要决定是否 dispatch

## Inputs

- Issue: title, body, number
- Project: harness 上下文（AGENTS.md, CONTEXT-MAP.md, .harness/）
- Project: 实际代码（关键模块）

## Core Principle

**Task Rewrite = Issue + Harness → Code 交叉验证 → 决策**

关键步骤：不能只读 harness，必须验证代码。

## Workflow

```
Issue 进来
    ↓
Step 1: 读取 Harness 上下文
    ├── AGENTS.md（项目概述）
    ├── CONTEXT-MAP.md（文件映射）
    └── .harness/*.md（规则和工作流）
    ↓
Step 2: 从 Issue 提取功能关键词
    └── 找到 harness 中相关模块的描述
    ↓
Step 3: Code 交叉验证（关键！）
    ├── 功能在代码里吗？→ 读关键源文件
    └── 功能在 harness 里吗？
    ↓
Step 4: 决策矩阵
    ├── 代码有 + Harness 有 → duplicate（功能已实现）
    ├── 代码有 + Harness 没有 → needs-info（需同步 harness）
    ├── 代码没有 + Harness 有 → BUG!（harness 过期）
    └── 代码没有 + Harness 没有 → dispatch（需实现）
    ↓
Step 5: 生成 tasks.md（如果 dispatch）
```

## Decision Matrix

| Code | Harness | Decision | Action |
|------|---------|----------|--------|
| 有 | 有 | `close` | 功能已实现，标记 duplicate |
| 有 | 没有 | `needs-info` | 代码已有但 harness 未记录，需同步 |
| 没有 | 有 | `needs-harness-sync` | Harness 说有但代码没有，harness 过时 |
| 没有 | 没有 | `dispatch` | 功能缺失，需要实现 |

## 验证代码的方法

不要全量扫描。用关键词定位：

```bash
# 搜索关键词
grep -rn "alias\|custom.*name\|rename" src/
# 或读关键接口
cat src/components/HTMLPreviewManager.tsx | grep "interface\|type"
```

## Output Format

```markdown
# Task Rewrite: {repo} #{issue_number}

## Issue Summary
{title} - {body}

## Harness Verification
- AGENTS.md: {有无相关描述}
- .harness/commands.md: {有无相关描述}

## Code Verification
- {file}: {验证结果}

## Decision
- Action: {dispatch / close / needs-info}
- Reason: {简短说明}

## Tasks (if dispatch)
1. {task 1}
2. {task 2}

## Allowed Files
- {file list}

## Forbidden Scope
- {forbidden items}

## Verification Command
```bash
{npm run build}
```
```

## 关键教训

### WEB-share #1 实测

**Issue**: 希望增加别名功能

**Code 验证**:
```typescript
interface HtmlFile {
  name: string      // 无 alias 字段
  ctime: string
}
```

**结论**: 代码没有 alias 功能 → dispatch

### 之前的问题

Poller 直接 dispatch OpenCode，不经过 Task Rewrite → OpenCode 读代码发现功能缺失 → 不知道怎么做 → 卡住问人

### Task Rewrite 的价值

在 dispatch 之前先验证：
- 功能真的缺失吗？
- Harness 有相关约束吗？
- 最小改动范围是什么？

## Stop Conditions

- Issue 标题/正文为空 → `close` (invalid)
- Issue 重复 → `close` (duplicate)
- 功能已在代码中 → `close` (already implemented)

## Related

- Evaluate: 评估 harness 质量
- Task Rewrite 验证的是"Issue 能不能做"，Evaluate 验证的是"harness 对不对"
