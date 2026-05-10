#!/usr/bin/env python3
"""
Compare project state against harness, detect stale references.

Scans current project files and compares against harness-referenced paths.
Detects missing files, new routes/APIs, and command changes.

Outputs unified JSON with status, errors, warnings, evidence, unknowns.

Usage:
    python scripts/compare_harness_to_project.py /path/to/project
"""
import sys
import json
import re
from pathlib import Path


def compare_harness_to_project(project_path: str) -> dict:
    project = Path(project_path)

    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "missing_files_in_harness": [],
        "new_routes_detected": [],
        "new_scripts_detected": [],
        "stale_commands": [],
    }

    if not project.is_dir():
        result["errors"].append(f"Project path does not exist: {project_path}")
        result["status"] = "fail"
        return result

    # Get current project source files
    current_files = set()
    for ext in ["*.tsx", "*.ts", "*.jsx", "*.js", "*.py", "*.css", "*.scss"]:
        for f in project.glob(f"**/{ext}"):
            rel = f.relative_to(project)
            if not any(
                part.startswith(".") or part == "node_modules" or part == ".next"
                for part in rel.parts
            ):
                current_files.add(rel)

    # Get current package scripts
    pkg = project / "package.json"
    current_scripts = {}
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            current_scripts = data.get("scripts", {})
        except Exception:
            pass

    # Get harness-referenced paths
    harness_files = (
        list(project.glob(".harness/*.md"))
        + list(project.glob("CONTEXT-MAP.md"))
        + list(project.glob("CONTEXT.md"))
    )

    path_pattern = re.compile(
        r'[`"\']((?:src|lib|app|docs|\.harness)/[a-zA-Z0-9_/\-.]*\.(?:tsx?|jsx?|py))[`"\']'
    )

    missing_count = 0
    for hf in harness_files:
        try:
            content = hf.read_text()
        except Exception:
            continue
        for match in path_pattern.finditer(content):
            p = match.group(1).lstrip("./")
            if not (project / p).exists():
                result["missing_files_in_harness"].append({
                    "harness_file": str(hf.relative_to(project)),
                    "missing_path": p,
                })
                missing_count += 1

    # Check for new routes (files containing Route/router)
    route_files_found = []
    for f in project.glob("**/*.{tsx,jsx}"):
        try:
            content = f.read_text()
            if any(kw in content for kw in ["Route", "router", "createBrowserRouter"]):
                rel = f.relative_to(project)
                route_files_found.append(str(rel))
        except Exception:
            pass

    # Check for new package scripts not in harness
    for hf in project.glob(".harness/commands.md"):
        try:
            content = hf.read_text()
            for name in current_scripts:
                if name not in content:
                    result["new_scripts_detected"].append(name)
        except Exception:
            pass

    result["evidence"].append({
        "source": "compare_harness_to_project.py",
        "finding": (
            f"Scanned {len(current_files)} source files, "
            f"{len(harness_files)} harness files"
        )
    })

    if route_files_found:
        result["new_routes_detected"] = route_files_found[:20]
        result["evidence"].append({
            "source": "compare_harness_to_project.py",
            "finding": f"Found {len(route_files_found)} files with route/router references"
        })

    if result["missing_files_in_harness"]:
        result["warnings"].append(
            f"{missing_count} harness-referenced file(s) no longer exist in project"
        )
        result["status"] = "warning"

    if result["new_scripts_detected"]:
        result["warnings"].append(
            f"{len(result['new_scripts_detected'])} new script(s) not in .harness/commands.md"
        )
        result["status"] = "warning"

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: compare_harness_to_project.py /path/to/project"],
            "warnings": [],
            "evidence": [],
            "unknowns": [],
            "missing_files_in_harness": [],
            "new_routes_detected": [],
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = compare_harness_to_project(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
