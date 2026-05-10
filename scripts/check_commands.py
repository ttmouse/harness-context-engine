#!/usr/bin/env python3
"""
Check commands in .harness/commands.md come from real config files.
Status: stub
"""
import sys
import json
import re
from pathlib import Path

def get_real_commands(project_path: str) -> set:
    """Extract commands from package.json, Makefile, etc."""
    project = Path(project_path)
    commands = set()

    pkg = project / "package.json"
    if pkg.exists():
        try:
            import json
            data = json.loads(pkg.read_text())
            for name, cmd in data.get("scripts", {}).items():
                commands.add(f"npm run {name}")
                commands.add(f"npm {name}")
                commands.add(cmd.split("&&")[0].strip())
        except Exception:
            pass

    makefile = project / "Makefile"
    if makefile.exists():
        for line in makefile.read_text().splitlines():
            m = re.match(r'^([a-zA-Z0-9_-]+):', line)
            if m:
                commands.add(m.group(1))

    return commands

def check_commands(project_path: str) -> dict:
    project = Path(project_path)
    commands_md = project / ".harness" / "commands.md"

    if not commands_md.exists():
        return {"error": ".harness/commands.md not found", "status": "fail"}

    content = commands_md.read_text()
    real_commands = get_real_commands(project_path)

    # Find command cells in table (after |)
    cmd_pattern = re.compile(r'\|\s*([a-zA-Z0-9_\-]+)\s*\|')
    invented = []

    # Check for placeholder UNKNOWN markers
    for line in content.splitlines():
        if "UNKNOWN" in line or "unknown" in line:
            continue

    return {
        "commands": [],  # stub: needs table parsing
        "invented_commands": invented,
        "status": "pass" if not invented else "fail"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: check_commands.py /path/to/project")
        sys.exit(1)
    result = check_commands(sys.argv[1])
    print(json.dumps(result, indent=2))
