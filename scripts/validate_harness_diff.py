#!/usr/bin/env python3
"""
Validate harness diff does not weaken control systems.
Status: stub
"""
import sys
import json
import re
from pathlib import Path

WEKENING_PATTERNS = [
    (re.compile(r'Requires Approval.*?Allowed'), "Requires Approval moved to Allowed"),
    (re.compile(r'verification.*?removed', re.IGNORECASE), "verification requirement removed"),
    (re.compile(r'Hard Fail.*?removed', re.IGNORECASE), "Hard Fail removed"),
    (re.compile(r'Source.*?Confidence.*?removed', re.IGNORECASE), "Source/Confidence removed"),
    (re.compile(r'UNKNOWN.*?replaced', re.IGNORECASE), "UNKNOWN marker replaced with fake data"),
    (re.compile(r'approval.*?not.*?required', re.IGNORECASE), "approval requirement removed"),
]

def validate_harness_diff(project_path: str, diff_text: str = None) -> dict:
    if diff_text is None:
        # Read from stdin or git diff
        import subprocess
        try:
            result = subprocess.run(["git", "diff", "--no-color"],
                                    cwd=project_path, capture_output=True, text=True, timeout=10)
            diff_text = result.stdout
        except Exception as e:
            return {"error": f"Could not get git diff: {e}", "status": "unknown"}

    violations = []
    for pattern, description in WEKENING_PATTERNS:
        if pattern.search(diff_text):
            violations.append(description)

    return {
        "violations": violations,
        "status": "pass" if not violations else "fail"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_harness_diff.py /path/to/project")
        sys.exit(1)
    result = validate_harness_diff(sys.argv[1])
    print(json.dumps(result, indent=2))
