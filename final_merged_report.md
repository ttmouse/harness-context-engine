# Harness Context Engine — 合并最终报告

合并日期: 2026-05-11
基线: `origin/main` (dbe439c)
合并来源: `origin/fix/project-profile-grill-before-write` (OpenAI) + 本地工作区改动

---

## 一、从 OpenAI 版本合并的内容

### `references/project-profile.md`

| 合并项 | 来源 | 位置 |
|---|---|---|
| `data/script project` 类型 | OpenAI | Project Type 列表 |
| "Every structural claim must cite a path" 规则 | OpenAI | Structure 节后 |
| Stop Conditions（5 条） | OpenAI | Related Scripts 前 |

### `references/grill-before-write.md`

| 合并项 | 来源 | 位置 |
|---|---|---|
| 命名来源解释（"inspired by grilling a plan..."） | OpenAI | 开头段落后 |
| "Do not use for obvious observed facts" 边界 | OpenAI | When to Use 末 |
| "What Counts as Unclear" 表格（5 类 claim + safe handling） | OpenAI | When to Use / Core Principle 之间 |
| Clarification Question 好/坏示例（Good × 3, Bad × 3） | OpenAI | Step 3 末 |
| Write Rules（6 条：observed/inferred/unsupported/disputed/ADR/domain） | OpenAI | Conflict Output Format 后 |
| Stop Conditions（5 条） | OpenAI | Rules 后 |

---

## 二、保留的本地内容（OpenAI 未涉及）

| 文件 | 说明 | 改动量 |
|---|---|---|
| `references/generate.md` | 5 步工作流 + Lazy Creation 决策表（15 种文件） | 152→184 行 |
| `SKILL.md` | Capability Router 更新 + 4 条 Non-negotiables + Context Layers 上层 | 97→105 行 |
| `README.md` | Core Loop 图 + Key Concepts × 3 + 2 个 eval 条目 | 179→242 行 |
| `evals/evals.json` | 新增 `generate_then_context_pack` + `sync_then_task` | 5→7 evals |

---

## 三、文件清单

### 新增

| 文件 | 大小 | 内容 |
|---|---|---|
| `references/project-profile.md` | 239 行 | Project Profile 判断产物：10 个 section + Stop Conditions |
| `references/grill-before-write.md` | 225 行 | Grill Before Write：5 步流程 + Conflict 格式 + 3 例子 + Write/Stop 规则 |

### 修改

| 文件 | 基线 | 当前 | diff |
|---|---|---|---|
| `references/generate.md` | 152 行 | 184 行 | +32 行：工作流重写、Lazy Creation 表、Forbidden 扩展 |
| `SKILL.md` | 97 行 | 106 行 | +9 行：Capability Router 引用 + 4 条 Non-negotiables + Context Layers |
| `README.md` | 179 行 | 242 行 | +63 行：Core Loop、Key Concepts、evals 更新、文件树更新 |
| `evals/evals.json` | 5 evals | 7 evals | +2 eval：generate_then_context_pack, sync_then_task |

### 删除（对比临时文件清理）

| 文件 | 操作 |
|---|---|
| `references/comparison-project-profile.md` | 删除 |
| `references/comparison-grill-before-write.md` | 删除 |
| `references/comparison-remaining-files.md` | 删除 |

---

## 四、验证结果

```
check_skill_repo.py: PASS
  - Frontmatter: OK (name=harness-context-engine)
  - SKILL.md: 106 lines, 8 headers
  - README: 242 lines, 5/5 required sections
  - References: 14 files, 0 issues
  - Scripts: 9 compiled, 0 failures
  - Evals: 7 definitions, 4/4 fixtures present
  - Examples: 5 files
  - Total: 0 errors, 0 warnings

run_evals.py: PASS
  - 7 eval definitions loaded
  - 4 fixture directories exist
  - 0 missing fixtures
```

---

## 五、剩余工作

| 事项 | 重要性 | 说明 |
|---|---|---|
| Commit + Push | P0 | 当前改动全在工作区 |
| 远程旧 branch 清理 | P1 | `fix/project-profile-grill-before-write` 和 `fix/project-profile-harness-rules` 可删除 |
| Behavioral eval 手动验证 | P1 | 新增的 2 个 eval 需要人工跑一次确认 agent 实际行为是否匹配预期 |
| evals/README.md | P2 | 当前引用了但文件不存在 |
