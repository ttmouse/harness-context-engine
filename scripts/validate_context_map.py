#!/usr/bin/env python3
"""
Validate CONTEXT-MAP.md references point to existing files.
Status: stub
"""
import sys
import json
import re
from pathlib import Path

def validate_context_map(project_path: str) -> dict:
    project = Path(project_path)
    map_file = project / "CONTEXT-MAP.md"

    if not map_file.exists():
        return {"error": "CONTEXT-MAP.md not found", "status": "fail"}

    content = map_file.read_text()
    missing = []
    found = []

    # Extract file references from CONTEXT-MAP.md
    ref_pattern = re.compile(r'`([^`]+\.md)`|`([^`]+)`')
    for match in ref_pattern.finditer(content):
        ref = match.group(1) or match.group(2)
        ref = ref.strip()

        # Resolve relative to project root
        if ref.startswith("./"):
            resolved = project / ref[2:]
        elif ref.startswith("."):
            resolved = project / ref[1:]
        else:
            resolved = project / ref

        if not resolved.exists():
            missing.append({"referenced": ref, "status": "MISSING_CONTEXT"})
        else:
            found.append({"referenced": ref, "status": "exists"})

    return {
        "missing_references": missing,
        "valid_references": found,
        "status": "pass" if not missing else "fail"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_context_map.py /path/to/project")
        sys.exit(1)
    result = validate_context_map(sys.argv[1])
    print(json.dumps(result, indent=2))
