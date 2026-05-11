# Grill Before Write

When business language, architecture intent, ownership boundary, or risk meaning is unclear, do not write it as fact. Investigate first.

This reference is inspired by the discipline of grilling a plan against existing code, context, and domain language before updating project context.

## When to Use

- During Generate: before writing domain terms, business rules, or architecture claims to harness files
- During Project-State Sync: before inferring business meaning of new code
- During Evaluate: when checking if existing claims have proper basis
- During Context Pack creation: when classifying task type or affected areas
- Whenever a source-code name is the only evidence for a business claim

**Do not use this for obvious observed facts** such as file paths, package scripts, or config values. Those should be cited directly with source + confidence.

**Core principle:** Writing a wrong fact into harness is worse than writing UNKNOWN. Wrong facts mislead every subsequent agent task. UNKNOWN only triggers a human review.

## What Counts as Unclear

A claim is unclear when it relies on meaning rather than direct observation.

| Claim Type | Safe Handling |
|---|---|
| "Reports means revenue reporting" | Inferred from name only; mark LOW CONFIDENCE unless docs/code confirm |
| "This service owns billing" | Confirm from code/docs or mark UNKNOWN |
| "We chose this architecture for scalability" | Requires ADR or explicit source; do not invent |
| "Auth changes are high risk" | Can be a general risk, but cite observed auth files or mark inferred |
| "This route is admin-only" | Verify in route guards, middleware, docs, or tests |

## Investigation Order

When a claim needs verification, follow this order:

### Step 1: Inspect Code

Search the project for evidence. Look at:

- The actual file content, not just the filename
- Package.json, config files, environment variables
- Import/export relationships
- Test files (they often document expected behavior)
- Git history for recent changes
- CI workflow for deployment patterns

If the code provides a clear answer, write with source + confidence.

### Step 2: Inspect Existing Harness / Context

Check if the existing harness, CONTEXT.md, ADR, or domain.md already documents the term or decision. If it does, cite it as source.

If existing context conflicts with code, proceed to Step 5 (Conflict Handling).

### Step 3: Ask One Targeted Question

If code and existing context cannot answer, ask exactly one clarification question. The question must:

- Be specific: not "what does this project do?" but "does the Reports route serve financial reporting or operational monitoring?"
- Reference the specific file, function, or term in question
- Offer the alternative interpretations found
- Explain why code alone cannot resolve it

**Do not ask multiple questions at once.** Resolve one uncertainty before moving to the next.

**Good questions:**
- "Is Reports a financial reporting area, an operational dashboard, or only a placeholder route?"
- "Is this dependency change allowed without approval, or should it remain Requires Approval?"
- "Does this domain term come from product language, customer language, or code-only naming?"

**Bad questions:**
- "Please explain the whole project."
- "What should I write in the context?"
- "Can you confirm everything?"

### Step 4: Mark UNKNOWN

If the user does not answer, or if the answer is still ambiguous:

- Write UNKNOWN for the specific claim
- Add NEEDS HUMAN REVIEW marker
- Document why it could not be resolved
- Do not guess. Do not fill with default values.

### Step 5: Surface Conflicts

If the user's statement, the code, and the existing context disagree, surface the conflict explicitly. Do not pick a side.

## Conflict Output Format

When a conflict is detected, produce a structured conflict report:

```markdown
# Context Conflict

## Conflict
{what is in conflict — one sentence}

## Sources
1. **User statement**: "{exact quote}" (confidence: {high/medium/low})
2. **Code evidence**: {file path + relevant code or structure} (confidence: {high/medium/low}, type: {observed/inferred})
3. **Existing context**: {file path + relevant excerpt} (confidence: {high/medium/low})

## Possible Interpretations
1. {interpretation A}: {explanation}
2. {interpretation B}: {explanation}

## Recommended Clarification Question
{one precise question to resolve the conflict}

## Safe Temporary Handling
{
  What to write in harness until the conflict is resolved.
  Usually UNKNOWN or NEEDS HUMAN REVIEW.
  Never pick a side without strong evidence.
}
```

## Write Rules

When writing after grilling:

- Observed facts may be written as confirmed (with source + confidence)
- Inferred meaning must be marked INFERRED or LOW CONFIDENCE
- Unsupported claims must remain UNKNOWN
- Disputed claims must be listed as conflicts (do not pick a side)
- Formal ADRs require real decision evidence; do not invent
- domain.md requires source-backed domain terms; skip if none exist

## Examples

### Example 1: Filing ambiguous purpose

Code has `src/pages/Reports.tsx`. No README. No existing context.

**Step 1 — Inspect code:** Reports.tsx imports chart components and data tables. Routes to `/reports`. No API calls visible. Component name only.

**Step 2 — Inspect context:** No existing harness or context.

**Step 3 — Ask one question:** "I see src/pages/Reports.tsx renders charts and data tables at the /reports route. The code doesn't reveal whether this is for financial reporting, operational analytics, or something else. Can you clarify the business purpose of /reports?"

**Step 4 — If no answer:**
```markdown
- /reports route purpose: UNKNOWN
  Source: src/pages/Reports.tsx (naming + chart imports only)
  Confidence: low, type: inferred
  Needs human review
```

### Example 2: Auth mechanism

User says "we use JWT auth". Code has `src/auth/login.ts` with session cookie handling, no JWT library.

**Step 1 — Inspect code:** login.ts sets cookies, checks `req.session`. No `jsonwebtoken` in dependencies. No token expiry logic.

**Step 2 — Inspect context:** No existing harness.

**Step 3 — Conflict detected.**

```markdown
# Context Conflict

## Conflict
User states JWT auth, but code shows session-cookie auth.

## Sources
1. User statement: "we use JWT auth"
2. Code evidence: src/auth/login.ts uses session cookies, no JWT library in dependencies
3. Existing context: none

## Possible Interpretations
1. The project uses session cookies, not JWT; user may be describing a planned migration
2. JWT is used at a different layer (API gateway) not visible in this repo

## Recommended Clarification Question
src/auth/login.ts manages login via session cookies, and I don't see a JWT library in package.json.
Is auth session-cookie based at the application layer, with JWT possibly at the infrastructure/gateway level?

## Safe Temporary Handling
Write auth mechanism as UNKNOWN until confirmed.
```

### Example 3: Business rule from directory name

Directory `src/services/` contains `apiClient.ts` and `legacyApi.ts`.

**Incorrect:** "Services layer provides API abstraction — INFERRED from src/services/ naming."

**Correct:** "src/services/ contains apiClient.ts and legacyApi.ts — OBSERVED. Whether this constitutes an abstraction layer over business logic vs simple HTTP client: UNKNOWN."

## Rules

1. Do not infer business rules from source-code naming alone
2. Do not infer architecture intent from directory structure alone
3. Do not choose sides in conflicts — surface them
4. One question per uncertainty
5. UNKNOWN is safe; guessed fact is dangerous
6. Source-code names are evidence of naming convention, not of business meaning
7. If code, context, and user all agree, write with high confidence
8. The evidence table in Project Profile must reflect the resolution status of each uncertainty

## Stop Conditions

Stop and escalate to human if:

- A requested harness update would encode a business rule with no source
- A requested ADR has no real decision evidence
- A risk boundary is being weakened without explicit approval
- Code and docs contradict each other on a safety-critical area
- The agent cannot identify whether a claim is observed or inferred

## Related References

| Reference | Role |
|---|---|
| `references/project-profile.md` | Captures unknowns and human review needs |
| `references/source-confidence.md` | Source/confidence marking rules |
| `references/generate.md` | Lazy creation rules — don't create files for unknown claims |
| `references/evaluate.md` | Hard Fail: invented content without source |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Writing inferred as fact | Treating naming as business definition | Mark INFERRED until confirmed |
| Asking too many questions | Trying to resolve everything at once | One question at a time, highest uncertainty first |
| Picking a side in conflict | Preferring user statement or code assumption | Surface conflict, let human decide |
| Skipping Step 1 (code inspect) | Assuming user knows best | Always check code first — code is the source of truth |
| Filling UNKNOWN with default | Guessing to avoid UNKNOWN markers | UNKNOWN is correct; guessed fact is harmful |
