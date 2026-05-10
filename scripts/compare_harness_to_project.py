#!/usr/bin/env python3
"""
Compare project state against harness, detect stale references.
Status: stub
"""
import sys
import json
import re
from pathlib import Path

def compare_harness_to_project(project_path: str) -> dict:
    project = Path(project_path)
    findings = []

    # Get current project files
    current_files = set()
    for ext in ["*.tsx", "*.ts", "*.jsx", "*.js", "*.py"]:
        for f in project.glob(f"**/{ext}"):
            if ".next" not in str(f) and "node_modules" not in str(f):
                current_files.add(f.relative_to(project))

    # Get current package scripts
    pkg = project / "package.json"
    current_scripts = set()
    if pkg.exists():
        try:
            import json
            data = json.loads(pkg.read_text())
            current_scripts.update(data.get("scripts", {}).keys())
        except Exception:
            pass

    # Get harness-referenced paths (from commands.md, working-boundaries.md, etc.)
    harness_files = list(project.glob("**/.harness/*.md")) + \
                   list(project.glob("**/CONTEXT-MAP.md")) + \
                   list(project.glob("**/CONTEXT.md"))

    path_pattern = re.compile(r'[`"\']([./a-zA-Z0-9_-]+\.(tsx?|jsx?|py))[`"\']')
    missing_files = []
    new_files = []

    for hf in harness_files:
        try:
            content = hf.read_text()
        except Exception:
            continue
        for match in path_pattern.finditer(content):
            p = match.group(1).lstrip("./")
            if not (project / p).exists():
                missing_files.append({"harness_file": str(hf.relative_to(project)), "missing_path": p})

    # Check for new routes/APIs
    new_routes = []
    for f in project.glob("**/*.tsx"):
        content = f.read_text()
        if any(kw in content for kw in ["Route", "router", "createBrowserRouter"]):
            new_routes.append(str(f.relative_to(project)))

    return {
        "missing_files_in_harness": missing_files,
        "new_routes_detected": new_routes,
        "status": "stale" if missing_files or new_routes else "ok"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: compare_harness_to_project.py /path/to/project")
        sys.exit(1)
    result = compare_harness_to_project(sys.argv[1])
    print(json.dumps(result, indent=2))
