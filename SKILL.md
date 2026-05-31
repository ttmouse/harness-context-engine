---
name: harness-context-engine
description: 为软件项目生成、评估、同步和优化 AI-Agent Harness 上下文。在创建 AGENTS.md、CONTEXT-MAP.md、.harness 文件，评估现有 harness 质量，根据项目变更同步 harness，创建任务上下文包或审查 harness 差异时使用。
---

# Harness Context Engine

**核心原则：** Harness 上下文必须是可追溯、可验证、可纠正的——不仅仅是完整的。

---

## 启动行为（自动诊断）

当用户调用技能但请求为空或不明确时，**自动执行诊断流程**：

1. 运行 `scripts/scan_project.py` 扫描项目结构
2. 检查现有 harness 文件是否存在、过时
3. 识别关键发现（缺失文件、过时内容、架构变更）
4. 输出项目状态摘要 + 推荐操作

**输出格式（3 行以内）：**
```
🎯 项目：[项目名]（[框架] + [语言]）
⚠️  发现：[关键发现1]，[关键发现2]
💡 建议：[推荐操作1] 或 [推荐操作2]
```

**示例：**
```
🎯 项目：dashboard-framework（React + TypeScript）
⚠️  发现：AGENTS.md 存在（3个月未更新），缺少 .harness/working-boundaries.md
💡 建议：运行「sync」同步项目最新结构，或「evaluate」检查现有 harness 质量
```

---

## 功能路由表

| 用户说 | 功能 | 读取文档 |
|---|---|---|
| 生成 harness / 初始化 | **Generate** | references/generate.md, references/project-profile.md, references/grill-before-write.md |
| 检查 harness / 评估 harness | **Evaluate** | references/evaluate.md |
| 重写任务 / 从 issue 创建任务 | **Task Rewrite** | references/task-rewrite.md |
| 同步 harness 与项目 / 从 diff 同步 | **Project-State Sync** | references/project-state-sync.md |
| 发布 harness / 同步 wiki | **Publication Sync** | references/publication-sync.md |
| 创建上下文包 | **Context Pack** | references/context-pack.md |
| 运行报告 / 任务后报告 | **Run Report** | references/run-report.md |
| 优化 harness | **Optimize** | references/optimize.md |
| 审查 harness 差异 | **Diff Review** | references/diff-review.md |

---

## 来源与置信度规则（全局底层契约）

每个非显而易见的结论必须包含：

- **source（来源）**: 文件路径、配置、命令输出、git diff 或明确用户上下文
- **confidence（置信度）**: high / medium / low
- **type（类型）**: observed（观察到的）/ inferred（推断的）/ unknown（未知的）

**规则**：
- 不要将推断的结论当作已确认的事实
- 不要在没有来源的情况下生成业务规则、架构决策或命令
- 推断的结论标注：`INFERRED`、`LOW CONFIDENCE`、`NEEDS HUMAN REVIEW`
- 详见：references/source-confidence.md

---

## 全局不可协商规则

1. 不得编造项目事实、命令、路径、业务规则或架构决策
2. 每个非显而易见的结论都需要来源 + 置信度 + 类型
3. 保持 AGENTS.md 和生成的上下文文件简短且对任务有用
4. 优先使用脚本进行确定性检查
5. Generate 或 Project-State Sync 后必须运行 Evaluate
6. 如果 Evaluate 有硬失败，Publication Sync 被阻止
7. **Generate 必须在写入 harness 文件之前生成项目画像（Project Profile）。** 见 `references/project-profile.md`
8. **惰性创建上下文文件。** 不要为了结构完整而创建文件。见 `references/generate.md` 惰性创建规则
9. **写之前先质疑。** 不清晰的业务、领域或架构声明必须被验证、质疑或标记为 UNKNOWN。见 `references/grill-before-write.md`
10. **Harness 上下文是为 agent 操作准备的，不是人类文档。** 保持文件专注于 agent 安全准确工作所需的内容

---

## 工具脚本

运行这些脚本进行确定性检查。见 scripts/ 目录

| 脚本 | 检查内容 |
|---|---|
| scripts/scan_project.py | 项目结构、语言、框架、package 脚本、CI、monorepo 线索 — **已实现** |
| scripts/check_commands.py | 命令来自真实配置文件 — **已实现** |
| scripts/validate_context_map.py | CONTEXT-MAP 引用、MISSING_CONTEXT 检测 — **已实现** |
| scripts/check_paths.py | Harness 引用的路径是否在项目中存在 — **部分实现** |
| scripts/validate_source_confidence.py | 关键结论是否有 source/confidence/type — **部分实现** |
| scripts/compare_harness_to_project.py | 项目变更使 harness 变旧 — **部分实现** |
| scripts/validate_harness_diff.py | Harness 变更不削弱控制 — **部分实现** |
| scripts/run_evals.py | Eval fixture 完整性检查 — **已实现** |
| scripts/check_skill_repo.py | 自检：格式、编译、fixtures — **已实现** |

---

## 上下文层次

```
🔥 热（每次任务）:
  AGENTS.md, CONTEXT-MAP.md

🌡️ 温（按任务类型）:
  .harness/commands.md, .harness/task-workflow.md,
  .harness/working-boundaries.md, .harness/testing-and-verification.md

❄️ 冷（按需）:
  .harness/code-review.md, .harness/failure-analysis.md,
  .harness/known-risks.md, docs/adr/, docs/agents/

📋 生成决策（每次生成）:
  references/project-profile.md    # scan→profile→generate 判断
  references/grill-before-write.md  # 业务术语验证
```

---

## 评估

使用 `skill-quality-evaluation` 运行评估。见 evals/evals.json 和 evals/fixtures/

---

## 示例

每个功能的输入/输出示例。见 examples/
