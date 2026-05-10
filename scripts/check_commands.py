#!/usr/bin/env python3
"""
Check commands in .harness/commands.md come from real config files.

Extracts commands from Markdown tables (primary) and bash code blocks.
Validates against package.json scripts, Makefile targets, and CI workflow files.

Outputs unified JSON with status, errors, warnings, evidence, unknowns.

Usage:
    python scripts/check_commands.py /path/to/harness /path/to/project
"""
import sys
import json
import re
from pathlib import Path


def get_real_commands(project_path: str) -> dict:
    """Extract commands from package.json, Makefile, and CI workflows.

    Returns: {"commands": {name: command}, "warnings": []}
    """
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
                commands[name] = cmd
                # Also register npm-run-X variants
                commands[f"run {name}"] = cmd
        except (json.JSONDecodeError, Exception) as e:
            warnings.append(f"package.json parse error: {e}")

    # Makefile targets
    makefile = project / "Makefile"
    if makefile.exists():
        try:
            for line in makefile.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = re.match(r"^([a-zA-Z0-9_-]+):", line)
                if m:
                    commands[m.group(1)] = line
        except Exception as e:
            warnings.append(f"Makefile read error: {e}")

    # CI workflow commands (from .github/workflows/*.yml)
    for wf in project.glob(".github/workflows/*.yml"):
        try:
            text = wf.read_text()
            # Extract run: commands from workflow steps
            for match in re.finditer(r"run:\s*(.+)$", text, re.MULTILINE):
                cmd = match.group(1).strip().strip("'\"")
                if cmd:
                    # Create a key from the command
                    key = cmd.split("\n")[0][:60]
                    commands[key] = cmd
        except Exception:
            pass

    return {"commands": commands, "warnings": warnings}


def extract_commands_from_commands_md(content: str) -> dict:
    """Extract commands from .harness/commands.md.

    Returns: {"commands": [{"purpose": str, "command": str, "status": str}],
              "warnings": []}
    """
    extracted = []
    warnings = []

    # 1. Parse Markdown tables (primary source)
    lines = content.splitlines()
    in_table = False
    headers = []
    data_rows = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                headers = cells
                in_table = True
                continue
            # Skip separator rows (|---|)
            if all(re.match(r"^[-:\s]+$", c) for c in cells):
                continue
            data_rows.append(cells)
        else:
            if in_table:
                # Table ended
                if "purpose" in str(headers).lower() or "command" in str(headers).lower():
                    for row in data_rows:
                        record = {}
                        for i, h in enumerate(headers):
                            if i < len(row):
                                record[h.lower()] = row[i]
                        extracted.append(record)
                headers = []
                data_rows = []
                in_table = False

    # Catch table at end of file
    if data_rows:
        if "purpose" in str(headers).lower() or "command" in str(headers).lower():
            for row in data_rows:
                record = {}
                for i, h in enumerate(headers):
                    if i < len(row):
                        record[h.lower()] = row[i]
                extracted.append(record)

    # 2. Also extract from bash code blocks
    commands_from_blocks = []
    code_block_pattern = re.compile(r"```bash\s*\n(.*?)```", re.DOTALL)
    for match in code_block_pattern.finditer(content):
        block = match.group(1)
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line.split("#")[0].strip()
            if line:
                commands_from_blocks.append(line)

    # 3. Generic code blocks (no language)
    generic_block_pattern = re.compile(r"```\s*\n(.*?)```", re.DOTALL)
    for match in generic_block_pattern.finditer(content):
        block = match.group(1)
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            runner_pattern = re.compile(r"^(npm|yarn|pnpm|make|go|python|cargo|node)")
            if runner_pattern.match(line):
                commands_from_blocks.append(line)

    result = {
        "table_commands": extracted,
        "code_block_commands": list(set(commands_from_blocks)),
    }

    if not extracted and not commands_from_blocks:
        warnings.append("No commands found in .harness/commands.md (empty table or no code blocks)")

    return result


def check_commands(harness_path: str, project_path: str) -> dict:
    """Check if commands in .harness/commands.md exist in project's real configs."""
    harness = Path(harness_path)
    project = Path(project_path)

    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "source_backed": [],
        "unverified": [],
        "unknown": [],
        "invented": [],
    }

    commands_md = harness / ".harness" / "commands.md"
    if not commands_md.exists():
        result["errors"].append(".harness/commands.md not found")
        result["status"] = "fail"
        return result

    content = commands_md.read_text()
    result["evidence"].append({
        "source": ".harness/commands.md",
        "finding": f"Read commands.md ({len(content)} chars)"
    })

    # Extract commands from harness
    extracted = extract_commands_from_commands_md(content)

    if not extracted["table_commands"] and not extracted["code_block_commands"]:
        result["errors"].append("No commands found in .harness/commands.md")
        result["status"] = "fail"
        return result

    result["evidence"].append({
        "source": ".harness/commands.md",
        "finding": f"Found {len(extracted['table_commands'])} table entries, {len(extracted['code_block_commands'])} code block commands"
    })

    # Get real project commands
    real = get_real_commands(project_path)
    result["warnings"].extend(real.get("warnings", []))
    real_commands = real.get("commands", {})

    if not real_commands:
        result["warnings"].append(
            "No real commands found in package.json, Makefile, or CI workflows"
        )
        result["status"] = "warning"

    # --- Check table commands ---
    for entry in extracted["table_commands"]:
        cmd = entry.get("command", "").strip()
        purpose = entry.get("purpose", "").strip()
        status = entry.get("status", "").strip().lower()

        if not cmd:
            continue

        # Normalize: remove npm run prefix for matching
        normalized = re.sub(r"^npm\s+run\s+", "", cmd)
        normalized = re.sub(r"^npm\s+", "", normalized)

        # Check if marked as UNKNOWN anywhere
        is_marked_unknown = (
            "unknown" in status or
            "unverified" in status or
            cmd.upper().startswith("UNKNOWN") or
            cmd.upper() == "TODO"
        )

        found = False
        matched_source = None
        for real_name, real_cmd in real_commands.items():
            if normalized == real_name or normalized in real_cmd:
                found = True
                matched_source = real_name
                break

        if found:
            result["source_backed"].append({
                "command": cmd,
                "purpose": purpose,
                "source": matched_source,
                "status": status or "verified"
            })
        elif is_marked_unknown:
            result["unknown"].append({
                "command": cmd,
                "purpose": purpose,
                "reason": "command is marked unverified/unknown in harness"
            })
        else:
            result["invented"].append({
                "command": cmd,
                "purpose": purpose,
                "reason": "not found in package.json, Makefile, or CI workflows"
            })

    # --- Check code block commands ---
    for cmd in extracted["code_block_commands"]:
        # Skip if already found in table
        already_tracked = any(
            e.get("command", "").strip() == cmd for e in result["source_backed"]
        ) or any(
            e.get("command", "").strip() == cmd for e in result["invented"]
        ) or any(
            e.get("command", "").strip() == cmd for e in result["unknown"]
        )
        if already_tracked:
            continue

        normalized = re.sub(r"^npm\s+run\s+", "", cmd)
        normalized = re.sub(r"^npm\s+", "", normalized)

        found = False
        matched_source = None
        for real_name, real_cmd in real_commands.items():
            if normalized == real_name or normalized in real_cmd:
                found = True
                matched_source = real_name
                break

        if found:
            result["source_backed"].append({
                "command": cmd,
                "purpose": "from code block",
                "source": matched_source,
                "status": "unverified"
            })
        elif "UNKNOWN" in cmd.upper() or "TODO" in cmd:
            result["unknown"].append({
                "command": cmd,
                "purpose": "from code block",
                "reason": "marked as UNKNOWN/TODO"
            })
        else:
            result["invented"].append({
                "command": cmd,
                "purpose": "from code block",
                "reason": "not found in package.json, Makefile, or CI workflows"
            })

    # Determine overall status
    if result["invented"]:
        result["status"] = "fail"
        result["errors"].append(
            f"Found {len(result['invented'])} invented command(s) not backed by project config"
        )
    elif result["unknown"] and not result["source_backed"]:
        result["status"] = "unknown"
    elif result["warnings"]:
        result["status"] = "warning"
    else:
        result["status"] = "pass"

    result["evidence"].append({
        "source": "check_commands.py",
        "finding": (
            f"source_backed={len(result['source_backed'])}, "
            f"invented={len(result['invented'])}, "
            f"unknown={len(result['unknown'])}, "
            f"unverified=from unexecuted code blocks"
        )
    })

    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: check_commands.py /path/to/harness /path/to/project"],
            "warnings": [],
            "evidence": [],
            "unknowns": [],
            "source_backed": [],
            "unverified": [],
            "unknown": [],
            "invented": [],
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = check_commands(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
