#!/usr/bin/env python3
"""
Check commands in .harness/commands.md come from real config files.
Status: implemented

Outputs JSON with pass/fail/unknown status.
Commands not found in package.json or Makefile are flagged as invented.
"""
import sys
import json
import re
from pathlib import Path

def get_real_commands(project_path: str) -> dict:
    """Extract commands from package.json and Makefile. Returns dict: canonical_name -> command."""
    project = Path(project_path)
    commands = {}
    warnings = []

    # package.json scripts
    pkg = project / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            scripts = data.get("scripts", {})
            for name, cmd in scripts.items():
                # Normalize: "npm run dev", "npm dev", and raw "vite" all map to same script
                commands[name] = cmd
                # Also register npm-run-X variants
                commands[f"run {name}"] = cmd
        except json.JSONDecodeError as e:
            warnings.append(f"package.json parse error: {e}")

    # Makefile targets
    makefile = project / "Makefile"
    if makefile.exists():
        try:
            for line in makefile.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                m = re.match(r'^([a-zA-Z0-9_-]+):', line)
                if m:
                    target = m.group(1)
                    commands[target] = line
        except Exception as e:
            warnings.append(f"Makefile read error: {e}")

    return {"commands": commands, "warnings": warnings}


def extract_commands_from_markdown(content: str) -> list:
    """Extract command names/strings from markdown code blocks and tables."""
    commands = []

    # 1. Extract from ```bash ... ``` code blocks (most reliable)
    code_block_pattern = re.compile(r'```bash\s*\n(.*?)```', re.DOTALL)
    for match in code_block_pattern.finditer(content):
        block = match.group(1)
        for line in block.splitlines():
            line = line.strip()
            # Skip empty lines and comment-only lines
            if not line or line.startswith('#'):
                continue
            # Remove inline comments
            if '#' in line:
                line = line.split('#')[0].strip()
            if line:
                commands.append(line)

    # 2. Also check for inline ``` ``` blocks (no language spec)
    generic_block_pattern = re.compile(r'```\s*\n(.*?)```', re.DOTALL)
    for match in generic_block_pattern.finditer(content):
        block = match.group(1)
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Only include if it looks like a command (starts with known runners)
            runner_pattern = re.compile(r'^(npm|yarn|pnpm|make|go|python|cargo|node)')
            if runner_pattern.match(line):
                commands.append(line)

    return list(set(commands))


def check_commands(harness_path: str, project_path: str) -> dict:
    """
    Check if commands in .harness/commands.md exist in project's real configs.
    
    Args:
        harness_path: Path to harness root (contains .harness/ dir)
        project_path: Path to project root
    
    Returns:
        JSON dict with status, invented_commands, valid_commands, warnings, errors
    """
    harness = Path(harness_path)
    project = Path(project_path)
    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "invented_commands": [],
        "unattributed_commands": [],
        "valid_commands": []
    }

    commands_md = harness / ".harness" / "commands.md"
    if not commands_md.exists():
        result["errors"].append(".harness/commands.md not found")
        result["status"] = "fail"
        return result

    content = commands_md.read_text()
    
    # Get real project commands
    real = get_real_commands(project_path)
    result["warnings"].extend(real.get("warnings", []))
    real_commands = real.get("commands", {})

    # Extract commands from harness
    harness_commands = extract_commands_from_markdown(content)

    if not harness_commands:
        result["warnings"].append("No commands found in .harness/commands.md — could not parse table")
        result["status"] = "unknown"
        return result

    # Check each harness command against real commands
    for cmd in harness_commands:
        # Normalize for comparison
        normalized = re.sub(r'^npm\s+run\s+', '', cmd)
        normalized = re.sub(r'^npm\s+', '', normalized)
        
        found = False
        for real_name, real_cmd in real_commands.items():
            if normalized == real_name or normalized in real_cmd:
                found = True
                result["valid_commands"].append({"command": cmd, "source": real_name})
                break
        
        if not found:
            # Check if it's marked as UNKNOWN or needs human review
            if "UNKNOWN" in cmd.upper() or "needs human review" in cmd.lower():
                result["unattributed_commands"].append({"command": cmd, "reason": "marked as unknown"})
            else:
                result["invented_commands"].append({"command": cmd, "reason": "not found in package.json or Makefile"})

    if result["invented_commands"]:
        result["status"] = "fail"
    elif result["unattributed_commands"] and not result["valid_commands"]:
        result["status"] = "unknown"

    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: check_commands.py /path/to/harness /path/to/project"],
            "invented_commands": [],
            "valid_commands": []
        }, indent=2))
        sys.exit(1)
    
    result = check_commands(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "pass" else 1)
