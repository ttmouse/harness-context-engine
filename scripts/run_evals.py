#!/usr/bin/env python3
"""
Eval runner for harness-context-engine.

Performs static integrity checks on evals configuration:
- Reads evals/evals.json
- Checks that specified fixtures exist
- Validates fixture structure
- Reports missing fixtures and structural issues

Does NOT call LLM models. For behavioral testing, use skill-quality-evaluation.

Usage:
    python scripts/run_evals.py
    python scripts/run_evals.py --verbose
"""
import sys
import json
from pathlib import Path


def run_evals(verbose: bool = False) -> dict:
    skill_root = Path(__file__).resolve().parent.parent
    evals_file = skill_root / "evals" / "evals.json"

    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "evals": [],
        "fixtures": {},
    }

    if not evals_file.exists():
        result["errors"].append("evals/evals.json not found")
        result["status"] = "fail"
        return result

    # Read evals.json
    try:
        evals_data = json.loads(evals_file.read_text())
    except json.JSONDecodeError as e:
        result["errors"].append(f"evals.json parse error: {e}")
        result["status"] = "fail"
        return result

    result["evidence"].append({
        "source": "evals.json",
        "finding": f"Loaded {len(evals_data)} eval definitions"
    })

    if not isinstance(evals_data, list):
        result["errors"].append("evals.json: expected top-level array")
        result["status"] = "fail"
        return result

    # Check each eval
    fixture_paths = set()

    for i, entry in enumerate(evals_data):
        name = entry.get("name", f"eval-{i}")
        fixture_path = entry.get("fixture_path", "")
        status = entry.get("status", "unknown")

        eval_info = {
            "name": name,
            "index": i,
            "has_name": bool(name),
            "has_description": bool(entry.get("description", "")),
            "has_query": bool(entry.get("query", "")),
            "fixture_path": fixture_path,
            "fixture_exists": False,
            "has_expected_behavior": bool(entry.get("expected_behavior", [])),
            "issues": [],
        }

        # Check required fields
        required_fields = ["name", "description", "query", "expected_behavior"]
        for field in required_fields:
            if not entry.get(field):
                eval_info["issues"].append(f"Missing required field: {field}")

        # Check fixture
        if fixture_path:
            abs_fixture = skill_root / "evals" / fixture_path
            eval_info["fixture_exists"] = abs_fixture.is_dir()
            if not abs_fixture.is_dir():
                result["warnings"].append(
                    f"Eval '{name}': fixture path '{fixture_path}' does not exist"
                )
            fixture_paths.add(fixture_path)

        result["evals"].append(eval_info)

    # Check all fixtures_needed actually exist
    fixtures_root = skill_root / "evals" / "fixtures"
    if fixtures_root.is_dir():
        existing_fixtures = [d.name for d in fixtures_root.iterdir() if d.is_dir()]
        result["fixtures"]["existing"] = existing_fixtures
        result["fixtures"]["count"] = len(existing_fixtures)

        # Check if all declared fixtures exist
        declared = set()
        for eval_info in result["evals"]:
            fp = eval_info.get("fixture_path", "")
            if fp:
                declared.add(fp.replace("fixtures/", ""))

        missing_fixtures = declared - set(existing_fixtures)
        if missing_fixtures:
            result["warnings"].append(
                f"Declared fixture(s) not found: {', '.join(sorted(missing_fixtures))}"
            )

        result["evidence"].append({
            "source": "evals/fixtures/",
            "finding": f"Found {len(existing_fixtures)} fixture directories: {', '.join(sorted(existing_fixtures))}"
        })
    else:
        result["warnings"].append("evals/fixtures/ directory does not exist")

    # Summarize
    total = len(result["evals"])
    passed = sum(1 for e in result["evals"] if not e["issues"] and e["fixture_exists"])
    failed = sum(1 for e in result["evals"] if e["issues"])
    no_fixture = sum(1 for e in result["evals"] if not e["fixture_exists"])

    result["evidence"].append({
        "source": "run_evals.py",
        "finding": (
            f"Eval summary: {total} total, {passed} ok, "
            f"{failed} with issues, {no_fixture} missing fixtures"
        )
    })

    if failed > 0:
        result["warnings"].append(f"{failed} eval(s) have missing required fields")
        result["status"] = "warning"

    if no_fixture > 0:
        result["warnings"].append(f"{no_fixture} eval(s) have missing fixtures")

    if verbose:
        for eval_info in result["evals"]:
            if eval_info["issues"]:
                for issue in eval_info["issues"]:
                    print(f"  [{eval_info['name']}] {issue}")

    return result


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = run_evals(verbose)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
