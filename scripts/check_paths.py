#!/usr/bin/env python3
"""
Check harness-referenced paths exist in project.
Status: stub
"""
import sys
import json
import re
from pathlib import Path

def check_paths(project_path: str) -> dict:
    project = Path(project_path)
    missing = []
    existing = []

    harness_files = list(project.glob("**/.harness/*.md")) + \
                   list(project.glob("**/AGENTS.md")) + \
                   list(project.glob("**/CONTEXT-MAP.md")) + \
                   list(project.glob("**/CONTEXT.md"))

    path_pattern = re.compile(r'[`"]?([./a-zA-Z0-9_-]+\.(tsx?|jsx?|py|json|ya?ml|toml|md))[`"]?')

    for hf in harness_files:
        try:
            content = hf.read_text()
        except Exception:
            continue

        for match in path_pattern.finditer(content):
            path_str = match.group(1)
            if path_str.startswith('./') or path_str.startswith('/'):
                resolved = project / path_str.lstrip('./')
            elif path_str.startswith('src/') or path_str.startswith('docs/') or path_str.startswith('.'):
                resolved = project / path_str
            else:
                continue

            if not resolved.exists():
                missing.append({"file": str(hf.relative_to(project)), "path": path_str})
            else:
                existing.append({"file": str(hf.relative_to(project)), "path": path_str})

    return {
        "missing_paths": missing,
        "existing_paths": existing[:20],  # cap for readability
        "status": "pass" if not missing else "fail"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: check_paths.py /path/to/project")
        sys.exit(1)
    result = check_paths(sys.argv[1])
    print(json.dumps(result, indent=2))
