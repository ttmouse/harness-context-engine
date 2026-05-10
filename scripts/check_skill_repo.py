#!/usr/bin/env python3
"""
Self-check script for harness-context-engine skill repository.

Checks:
1. SKILL.md frontmatter is valid YAML
2. SKILL.md is normal multi-line markdown
3. README.md is not compressed text
4. references/*.md have proper title structure
5. scripts/*.py pass py_compile
6. evals/evals.json is formatted JSON
7. fixtures_needed actually exist
8. examples exist
9. Script status labels match actual implementation

Outputs unified JSON with status, errors, warnings, evidence, unknowns.

Usage:
    python scripts/check_skill_repo.py
    python scripts/check_skill_repo.py --verbose
"""
import sys
import json
import re
import importlib.util
import subprocess
from pathlib import Path


def check_skill_repo(verbose: bool = False) -> dict:
    skill_root = Path(__file__).resolve().parent.parent

    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "checks": {},
    }

    # ── Check 1: SKILL.md frontmatter ──
    check_skill_frontmatter(skill_root, result)
    # ── Check 2: SKILL.md markdown ──
    check_skill_markdown(skill_root, result)
    # ── Check 3: README.md ──
    check_readme(skill_root, result)
    # ── Check 4: references/*.md ──
    check_references(skill_root, result)
    # ── Check 5: scripts/*.py compilation ──
    check_scripts_compile(skill_root, result)
    # ── Check 6: evals/evals.json ──
    check_evals_json(skill_root, result)
    # ── Check 7: fixtures ──
    check_fixtures(skill_root, result)
    # ── Check 8: examples ──
    check_examples(skill_root, result)
    # ── Check 9: skill status labels ──
    check_status_labels(skill_root, result)
    # ── Check 10: script file line_count sanity ──
    check_file_line_counts(skill_root, result)

    # Determine overall status
    if result["errors"]:
        result["status"] = "fail"
    elif result["warnings"]:
        result["status"] = "warning"

    result["evidence"].append({
        "source": "check_skill_repo.py",
        "finding": (
            f"Checks: {len(result['errors'])} error(s), "
            f"{len(result['warnings'])} warning(s), "
            f"{len(result['unknowns'])} unknown"
        )
    })

    if verbose:
        for check_name, check_data in result["checks"].items():
            status_icon = "PASS" if check_data.get("status") == "pass" else "FAIL" if check_data.get("status") == "fail" else "WARN"
            print(f"  [{status_icon}] {check_name}")
            if check_data.get("details"):
                for detail in check_data["details"][:5]:
                    print(f"         {detail}")

    return result


def check_skill_frontmatter(skill_root, result):
    """Check SKILL.md has valid YAML frontmatter."""
    check = {"status": "pass", "details": []}
    skill_md = skill_root / "SKILL.md"

    if not skill_md.exists():
        result["errors"].append("SKILL.md not found")
        check["status"] = "fail"
        result["checks"]["skill_frontmatter"] = check
        return

    content = skill_md.read_text()

    # Check frontmatter delimiters
    if not content.startswith("---\n"):
        check["details"].append("Missing opening --- for frontmatter")
        check["status"] = "fail"
    else:
        # Find closing ---
        end_idx = content.find("---\n", 4)
        if end_idx == -1:
            check["details"].append("Missing closing --- for frontmatter")
            check["status"] = "fail"
        else:
            frontmatter = content[4:end_idx]

            # Basic YAML validation: check key: value pairs
            lines = frontmatter.strip().split("\n")
            valid_keys = 0
            for line in lines:
                if ":" in line:
                    valid_keys += 1
                else:
                    check["details"].append(f"Non-YAML line in frontmatter: {line[:50]}")
                    check["status"] = "fail"

            if "name:" not in frontmatter:
                check["details"].append("Missing 'name:' in frontmatter")
                check["status"] = "fail"
            if "description:" not in frontmatter:
                check["details"].append("Missing 'description:' in frontmatter")
                check["status"] = "fail"

            check["details"].append(f"Frontmatter has {valid_keys} key(s)")

    # Also try Python yaml parsing if available
    if check["status"] == "pass":
        try:
            import yaml
            # Only parse the frontmatter, not the whole file
            frontmatter_end = content.find("---\n", 4)
            if frontmatter_end != -1:
                frontmatter_text = content[4:frontmatter_end]
                parsed = yaml.safe_load(frontmatter_text)
                if parsed and isinstance(parsed, dict):
                    check["details"].append(f"yaml.safe_load OK: name={parsed.get('name')}")
                else:
                    check["details"].append("yaml.safe_load returned unexpected result")
            else:
                check["details"].append("Cannot extract frontmatter for yaml parsing")
        except ImportError:
            check["details"].append("PyYAML not available — skipping yaml.safe_load check")
        except Exception as e:
            check["details"].append(f"yaml.safe_load failed: {e}")
            check["status"] = "fail"

    result["checks"]["skill_frontmatter"] = check
    if check["status"] != "pass":
        result["errors" if check["status"] == "fail" else "warnings"].append(
            "SKILL.md frontmatter has issues"
        )


def check_skill_markdown(skill_root, result):
    """Check SKILL.md is normal multi-line markdown (not compressed)."""
    check = {"status": "pass", "details": []}
    skill_md = skill_root / "SKILL.md"

    if not skill_md.exists():
        check["status"] = "fail"
        result["checks"]["skill_markdown"] = check
        return

    content = skill_md.read_text()
    lines = content.splitlines()

    if len(lines) < 20:
        check["details"].append(f"Only {len(lines)} lines — may be compressed")
        check["status"] = "warning"

    # Check for table content
    if "|" not in content:
        check["details"].append("No markdown tables found (capability router missing?)")
        check["status"] = "warning"

    # Check for headers
    headers = [l for l in lines if l.strip().startswith("#")]
    if len(headers) < 5:
        check["details"].append(f"Only {len(headers)} headers — may be too thin")
        check["status"] = "warning"

    check["details"].append(f"{len(lines)} lines, {len(headers)} headers")

    result["checks"]["skill_markdown"] = check


def check_readme(skill_root, result):
    """Check README.md is not compressed and has required sections."""
    check = {"status": "pass", "details": []}
    readme = skill_root / "README.md"

    if not readme.exists():
        result["errors"].append("README.md not found")
        check["status"] = "fail"
        result["checks"]["readme"] = check
        return

    content = readme.read_text()
    lines = content.splitlines()

    if len(lines) < 30:
        check["details"].append(f"Only {len(lines)} lines — may be compressed")
        check["status"] = "warning"

    # Check for required sections
    required = ["What Problem", "What This Is Not", "Capability Status", "Scripts Status", "Evals Status"]
    found = [s for s in required if s.lower() in content.lower()]

    if len(found) < len(required):
        missing = set(required) - set(found)
        check["details"].append(f"Missing sections: {', '.join(missing)}")
        check["status"] = "warning"

    # Check for table content (status tables)
    table_rows = [l for l in lines if l.strip().startswith("|")]
    if not table_rows:
        check["details"].append("No status tables found")
        check["status"] = "warning"

    check["details"].append(f"{len(lines)} lines, {len(found)}/{len(required)} required sections present")

    result["checks"]["readme"] = check


def check_references(skill_root, result):
    """Check references/*.md have proper structure."""
    check = {"status": "pass", "details": []}
    ref_dir = skill_root / "references"

    if not ref_dir.is_dir():
        result["errors"].append("references/ directory not found")
        check["status"] = "fail"
        result["checks"]["references"] = check
        return

    ref_files = sorted(ref_dir.glob("*.md"))
    issues = 0
    for rf in ref_files:
        content = rf.read_text()
        lines = content.splitlines()

        # Must have at least 20 lines (not compressed)
        if len(lines) < 15:
            check["details"].append(f"{rf.name}: only {len(lines)} lines — may be compressed")
            issues += 1

        # Must have a title
        if not lines or not lines[0].strip().startswith("# "):
            check["details"].append(f"{rf.name}: missing main title (h1)")
            issues += 1

        # Should have multiple sections
        header_count = sum(1 for l in lines if l.strip().startswith("## "))
        if header_count < 3:
            check["details"].append(f"{rf.name}: only {header_count} sections")
            issues += 1

    check["details"].append(f"Checked {len(ref_files)} references, {issues} issue(s)")

    if issues > 0:
        check["status"] = "warning"

    result["checks"]["references"] = check
    if issues > 0:
        result["warnings"].append(f"{issues} reference file(s) have structural issues")


def check_scripts_compile(skill_root, result):
    """Check all scripts/*.py pass py_compile."""
    check = {"status": "pass", "details": []}
    scripts_dir = skill_root / "scripts"

    if not scripts_dir.is_dir():
        result["errors"].append("scripts/ directory not found")
        check["status"] = "fail"
        result["checks"]["scripts_compile"] = check
        return

    py_files = sorted(scripts_dir.glob("*.py"))
    failures = 0

    for pyf in py_files:
        try:
            result2 = subprocess.run(
                [sys.executable, "-m", "py_compile", str(pyf)],
                capture_output=True, text=True, timeout=30
            )
            if result2.returncode != 0:
                check["details"].append(f"{pyf.name}: FAILED — {result2.stderr.strip()[:100]}")
                failures += 1
            else:
                if len(py_files) < 10:  # Only list in verbose mode
                    pass
        except subprocess.TimeoutExpired:
            check["details"].append(f"{pyf.name}: TIMEOUT")
            failures += 1
        except Exception as e:
            check["details"].append(f"{pyf.name}: ERROR — {e}")
            failures += 1

    check["details"].append(f"Compiled {len(py_files)} scripts, {failures} failure(s)")

    if failures > 0:
        check["status"] = "fail"

    result["checks"]["scripts_compile"] = check
    if failures > 0:
        result["errors"].append(f"{failures} script(s) failed compilation")


def check_evals_json(skill_root, result):
    """Check evals/evals.json is valid JSON."""
    check = {"status": "pass", "details": []}
    evals_file = skill_root / "evals" / "evals.json"

    if not evals_file.exists():
        result["errors"].append("evals/evals.json not found")
        check["status"] = "fail"
        result["checks"]["evals_json"] = check
        return

    content = evals_file.read_text()

    # Check if it's a single long line (compressed)
    if "\n" not in content.strip():
        check["details"].append("JSON is single line — not pretty-printed")
        check["status"] = "warning"

    try:
        data = json.loads(content)
        check["details"].append(f"Parsed OK: {len(data)} eval definitions")
    except json.JSONDecodeError as e:
        check["details"].append(f"Parse failed: {e}")
        check["status"] = "fail"

    result["checks"]["evals_json"] = check
    if check["status"] == "fail":
        result["errors"].append("evals/evals.json is not valid JSON")


def check_fixtures(skill_root, result):
    """Check fixture directories exist."""
    check = {"status": "pass", "details": []}
    fixtures_dir = skill_root / "evals" / "fixtures"

    if not fixtures_dir.is_dir():
        check["details"].append("evals/fixtures/ not found")
        check["status"] = "fail"
        result["checks"]["fixtures"] = check
        return

    # Read fixtures needed from evals.json
    evals_file = skill_root / "evals" / "evals.json"
    needed_fixtures = set()
    if evals_file.exists():
        try:
            evals_data = json.loads(evals_file.read_text())
            for entry in evals_data:
                fp = entry.get("fixture_path", "")
                if fp:
                    name = fp.replace("fixtures/", "")
                    needed_fixtures.add(name)
        except Exception:
            pass

    existing = sorted([d.name for d in fixtures_dir.iterdir() if d.is_dir()])
    missing = needed_fixtures - set(existing)

    check["details"].append(f"Fixtures: {len(existing)} existing, {len(missing)} missing")

    if missing:
        check["details"].append(f"Missing fixtures: {', '.join(sorted(missing))}")
        check["status"] = "warning"

    # Check each fixture has content
    empty_fixtures = []
    for d in existing:
        fixture_content = list((fixtures_dir / d).rglob("*"))
        if not fixture_content:
            empty_fixtures.append(d)

    if empty_fixtures:
        check["details"].append(f"Empty fixture dirs: {', '.join(empty_fixtures)}")
        check["status"] = "warning"

    result["checks"]["fixtures"] = check


def check_examples(skill_root, result):
    """Check examples exist."""
    check = {"status": "pass", "details": []}
    examples_dir = skill_root / "examples"

    if not examples_dir.is_dir():
        check["details"].append("examples/ not found")
        check["status"] = "warning"
        result["checks"]["examples"] = check
        return

    example_files = sorted(examples_dir.glob("*.md"))
    check["details"].append(f"Found {len(example_files)} example files: {', '.join(f.name for f in example_files)}")

    if not example_files:
        check["status"] = "warning"

    result["checks"]["examples"] = check


def check_status_labels(skill_root, result):
    """Check SKILL.md script status labels match actual implementation."""
    check = {"status": "pass", "details": []}
    skill_md = skill_root / "SKILL.md"
    scripts_dir = skill_root / "scripts"

    if not skill_md.exists():
        check["status"] = "fail"
        result["checks"]["status_labels"] = check
        return

    content = skill_md.read_text()

    # Parse script status lines from SKILL.md
    script_statuses = {}
    for line in content.splitlines():
        m = re.search(r"scripts/([a-zA-Z0-9_./-]+\.py).*?\*\*(implemented|stub|partial|early prototype)\*\*", line, re.IGNORECASE)
        if m:
            script_statuses[m.group(1)] = m.group(2).lower()

    check["details"].append(f"Found {len(script_statuses)} script status entries in SKILL.md")

    # Check if stub scripts have actual implementations
    for script_name, status in sorted(script_statuses.items()):
        script_path = scripts_dir / script_name
        if not script_path.exists():
            check["details"].append(f"scripts/{script_name} referenced but not found")
            continue

        code = script_path.read_text()

        # If marked as stub but has significant logic, flag
        if status == "stub" and len(code) > 500:
            check["details"].append(f"scripts/{script_name}: marked as '{status}' but has {len(code)} chars — may be under-reported")

        # If status has "implemented" but is actually thin
        if status == "implemented" and len(code) < 200:
            check["details"].append(f"scripts/{script_name}: marked as '{status}' but only {len(code)} chars — may be over-reported")

    result["checks"]["status_labels"] = check


def check_file_line_counts(skill_root, result):
    """Check all key files have reasonable line counts (not compressed)."""
    check = {"status": "pass", "details": []}
    issues = 0

    files_to_check = {
        "SKILL.md": skill_root / "SKILL.md",
        "README.md": skill_root / "README.md",
    }

    # Add references
    for rf in sorted((skill_root / "references").glob("*.md")):
        files_to_check[f"references/{rf.name}"] = rf

    # Add scripts
    for pf in sorted((skill_root / "scripts").glob("*.py")):
        files_to_check[f"scripts/{pf.name}"] = pf

    # Add evals
    files_to_check["evals/evals.json"] = skill_root / "evals" / "evals.json"

    for name, path in sorted(files_to_check.items()):
        if not path.exists():
            continue
        try:
            line_count = len(path.read_text().splitlines())
            if line_count < 10:
                check["details"].append(f"{name}: only {line_count} lines — compressed?")
                issues += 1
        except Exception:
            pass

    check["details"].append(f"Checked {len(files_to_check)} files, {issues} compressed file(s)")

    result["checks"]["file_line_counts"] = check


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = check_skill_repo(verbose)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
