---
name: harness-context-engine
description: 为软件项目生成、评估、同步和优化 AI-Agent Harness 上下文。在创建 AGENTS.md、CONTEXT-MAP.md、.harness 文件，评估现有 harness 质量，根据项目变更同步 harness，创建任务上下文包或审查 harness 差异时使用。
---

# Harness Context Engine

**核心原则：** Harness 上下文必须是可追溯、可验证、可纠正的——不仅仅是完整的。

Harness context is for agent operation, not human documentation. Generate the smallest context-control system that helps an AI coding agent read the right context, respect project boundaries, verify work, and improve after failures.

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
<<<<<<< HEAD
| 生成 harness / 初始化 | **Generate** | references/generate.md, references/project-profile.md, references/grill-before-write.md |
| 检查 harness / 评估 harness | **Evaluate** | references/evaluate.md |
| 重写任务 / 从 issue 创建任务 | **Task Rewrite** | references/task-rewrite.md |
| 同步 harness 与项目 / 从 diff 同步 | **Project-State Sync** | references/project-state-sync.md |
| 发布 harness / 同步 wiki | **Publication Sync** | references/publication-sync.md |
| 创建上下文包 | **Context Pack** | references/context-pack.md |
| 运行报告 / 任务后报告 | **Run Report** | references/run-report.md |
| 优化 harness | **Optimize** | references/optimize.md |
| 审查 harness 差异 | **Diff Review** | references/diff-review.md |
=======
| generate harness / bootstrap | Generate | references/generate.md |
| build project profile / classify project | Project Profile | references/project-profile.md |
| build code graph / generate relationship map / impact map | Code Graph | references/code-graph.md |
| validate code graph / check relationship map | Code Graph Validation | references/code-graph.md, references/evaluate.md |
| check harness / evaluate harness | Evaluate | references/evaluate.md |
| sync harness with project / sync from diff | Project-State Sync | references/project-state-sync.md |
| publish harness / sync wiki | Publication Sync | references/publication-sync.md |
| create context pack | Context Pack | references/context-pack.md |
| run report / after task | Run Report | references/run-report.md |
| optimize harness | Optimize | references/optimize.md |
| review harness diff | Diff Review | references/diff-review.md |
| unclear domain / ADR / boundary claim | Grill Before Write | references/grill-before-write.md |
>>>>>>> 59af4daabd7ba1c24ea573cb92e841fed8b45f4d

---

## 来源与置信度规则（全局底层契约）

每个非显而易见的结论必须包含：

- **source（来源）**: 文件路径、配置、命令输出、git diff 或明确用户上下文
- **confidence（置信度）**: high / medium / low
- **type（类型）**: observed（观察到的）/ inferred（推断的）/ unknown（未知的）

<<<<<<< HEAD
**规则**：
- 不要将推断的结论当作已确认的事实
- 不要在没有来源的情况下生成业务规则、架构决策或命令
- 推断的结论标注：`INFERRED`、`LOW CONFIDENCE`、`NEEDS HUMAN REVIEW`
- 详见：references/source-confidence.md
=======
**Rules**:
- Never present inferred as confirmed fact
- Never generate business rules / architecture decisions / commands without source
- Mark inferred: `INFERRED`, `LOW CONFIDENCE`, `NEEDS HUMAN REVIEW`
- Code Graph edges must follow the same source/confidence/type rule
- See: references/source-confidence.md
>>>>>>> 59af4daabd7ba1c24ea573cb92e841fed8b45f4d

---

## 全局不可协商规则

<<<<<<< HEAD
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
=======
1. Do not invent project facts, commands, paths, business rules, or architecture decisions
2. Every non-obvious claim requires source + confidence + type
3. Generate must produce a Project Profile before writing harness files
4. Create context files lazily; do not create files only for structural completeness
5. Grill before write: unclear business/domain/architecture claims must be verified, questioned, or marked UNKNOWN
6. Keep AGENTS.md and generated context files short and task-useful
7. Prefer scripts for deterministic checks
8. Run Evaluate after Generate or Project-State Sync
9. Publication Sync is blocked if Evaluate has hard failures
10. Code Graph is optional and must be generated only when relationship evidence improves routing, impact analysis, or Context Pack precision

---

## Required Generate Flow

```
Project Scan
  ↓
Optional Code Relationship Scan
  ↓
Project Profile
  ↓
Context Structure Choice
  ↓
Minimal Harness Generation
  ↓
Evaluate
```

Never jump directly from project scan to file generation. The Project Profile is the decision layer that prevents template-first harness generation.

Use Code Relationship Scan only when the project structure or task complexity makes relationship evidence useful. Do not generate a graph for tiny projects just because the capability exists.

---

## Lazy Creation Rule

Only create files that have a real job and evidence-backed content.

Do not create:

- formal ADRs without decision evidence
- domain.md without source-backed domain terms
- multi-context structures for simple projects
- local AGENTS.md without real independent subprojects
- known-risks.md without observed or explicitly provided risks
- code graph files for simple projects where a graph would only restate the directory tree
- empty TODO files merely to satisfy structure

Use UNKNOWN / NEEDS HUMAN REVIEW instead of filling blank sections with guesses.
>>>>>>> 59af4daabd7ba1c24ea573cb92e841fed8b45f4d

---

## 工具脚本

运行这些脚本进行确定性检查。见 scripts/ 目录

| 脚本 | 检查内容 |
|---|---|
<<<<<<< HEAD
| scripts/scan_project.py | 项目结构、语言、框架、package 脚本、CI、monorepo 线索 — **已实现** |
| scripts/check_commands.py | 命令来自真实配置文件 — **已实现** |
| scripts/validate_context_map.py | CONTEXT-MAP 引用、MISSING_CONTEXT 检测 — **已实现** |
| scripts/check_paths.py | Harness 引用的路径是否在项目中存在 — **部分实现** |
| scripts/validate_source_confidence.py | 关键结论是否有 source/confidence/type — **部分实现** |
| scripts/compare_harness_to_project.py | 项目变更使 harness 变旧 — **部分实现** |
| scripts/validate_harness_diff.py | Harness 变更不削弱控制 — **部分实现** |
| scripts/run_evals.py | Eval fixture 完整性检查 — **已实现** |
| scripts/check_skill_repo.py | 自检：格式、编译、fixtures — **已实现** |
=======
| scripts/scan_project.py | Project structure, language, framework, package scripts, CI, monorepo clues — **implemented** |
| scripts/generate_code_graph.py | Lightweight relationship evidence graph from observable files, imports, routes, API strings, docs, tests, and configs — **partial** |
| scripts/validate_code_graph.py | Validates code_graph.json schema, node/edge references, evidence, confidence, and optional path existence — **partial** |
| scripts/check_commands.py | Commands come from real config files — **implemented** |
| scripts/validate_context_map.py | CONTEXT-MAP references, MISSING_CONTEXT detection — **implemented** |
| scripts/check_paths.py | Harness-referenced paths exist in project — **partial** |
| scripts/validate_source_confidence.py | Key conclusions have source/confidence/type — **partial** |
| scripts/compare_harness_to_project.py | Project changes make harness stale — **partial** |
| scripts/validate_harness_diff.py | Harness changes do not weaken controls — **partial** |
| scripts/run_evals.py | Eval fixture integrity checks — **implemented** |
| scripts/check_skill_repo.py | Self-check: format, compile, fixtures, and structural issues — **implemented** |
>>>>>>> 59af4daabd7ba1c24ea573cb92e841fed8b45f4d

---

## 上下文层次

```
🔥 热（每次任务）:
  AGENTS.md, CONTEXT-MAP.md

🌡️ 温（按任务类型）:
  .harness/commands.md, .harness/task-workflow.md,
  .harness/working-boundaries.md, .harness/testing-and-verification.md

<<<<<<< HEAD
❄️ 冷（按需）:
=======
冷（on demand）:
  .harness/code-graph/code_graph.json,
  .harness/code-graph/impact_map.md,
  .harness/code-graph/feature_trace.md,
>>>>>>> 59af4daabd7ba1c24ea573cb92e841fed8b45f4d
  .harness/code-review.md, .harness/failure-analysis.md,
  .harness/known-risks.md, docs/adr/, docs/agents/

📋 生成决策（每次生成）:
  references/project-profile.md    # scan→profile→generate 判断
  references/grill-before-write.md  # 业务术语验证
```

Code Graph belongs to cold context. Do not load the full graph for every task. Use it when creating a Context Pack, analyzing impact, planning refactors, or tracing cross-module relationships.

---

## 评估

使用 `skill-quality-evaluation` 运行评估。见 evals/evals.json 和 evals/fixtures/

---

## 示例

每个功能的输入/输出示例。见 examples/
