#!/usr/bin/env python3
"""
Validate CONTEXT-MAP.md references point to existing files.

If a reference is explicitly marked as MISSING_CONTEXT in the map,
it is allowed to not exist. References that don't exist without
the MISSING_CONTEXT marker are reported as errors.

Outputs unified JSON with missing_references, valid_references,
allowed_missing_contexts.

Usage:
    python scripts/validate_context_map.py /path/to/harness [/path/to/project]
"""
import sys
import json
import re
from pathlib import Path


def extract_file_references(content: str) -> list:
    """Extract file/directory references from markdown content.

    Matches backtick refs, inline paths, and table cells with paths.
    """
    refs = []

    # Backtick code spans: `path` or `file.ext`
    backtick_pattern = re.compile(
        r"`((?:\./)?"
        r"(?:/?(?:src|lib|app|components|pages|docs|\.harness|config|scripts|tests|public)"
        r"[a-zA-Z0-9_/\-.]*"
        r"))`"
    )
    for match in backtick_pattern.finditer(content):
        ref = match.group(1).strip()
        if ref and not ref.startswith("http"):
            refs.append(ref)

    # Table cells that look like paths
    table_pattern = re.compile(
        r"^\s*\|\s*([^|]*?(?:(?:src|lib|app|components|pages|docs|\.harness|config|scripts|tests|public)[/\\][^|]+?))\s*\|",
        re.MULTILINE,
    )
    for match in table_pattern.finditer(content):
        cell = match.group(1).strip()
        if cell and ("/" in cell or cell.startswith(".")):
            refs.append(cell)

    # Inline paths in prose
    path_pattern = re.compile(
        r"(?:^|(?<=\s))"
        r"(\./(?:src|lib|app|components|pages|docs|\.harness|config|scripts|tests|public)"
        r"[a-zA-Z0-9_/\-.]*)",
        re.MULTILINE,
    )
    for match in path_pattern.finditer(content):
        refs.append(match.group(1))

    # Plain table cell paths (unquoted paths in table cells)
    # Matches cells containing paths like .harness/commands.md, src/App.tsx
    cell_path_pattern = re.compile(
        r"\|\s*([a-zA-Z0-9_./\-]+\.(?:tsx?|jsx?|py|json|md|ya?ml|toml|css|scss|html))\s*\|",
    )
    for match in cell_path_pattern.finditer(content):
        refs.append(match.group(1))

    # Plain dot-path references in table cells: ".harness/commands.md"
    dot_path_in_cell = re.compile(
        r"\|\s*([a-zA-Z0-9_./\-]*\.harness/[a-zA-Z0-9_./\-]+)\s*\|",
    )
    for match in dot_path_in_cell.finditer(content):
        refs.append(match.group(1))

    # Also match dot-prefixed paths like .harness/commands.md in plain text
    dot_prefix_pattern = re.compile(
        r"(?:^|(?<=\s|,))(\.harness/[a-zA-Z0-9_./\-]+)(?=\s|,|\\||)",
        re.MULTILINE,
    )
    for match in dot_prefix_pattern.finditer(content):
        refs.append(match.group(1))

    return list(set(refs))


def is_marked_missing_context(ref: str, content: str, ref_pos: int) -> bool:
    """Check if a reference is explicitly marked as MISSING_CONTEXT.

    Looks for MISSING_CONTEXT, MISSING, or allowed_marker near the reference.
    """
    # Check around the reference position
    window_start = max(0, ref_pos - 200)
    window_end = min(len(content), ref_pos + len(ref) + 200)
    window = content[window_start:window_end]

    markers = [
        "MISSING_CONTEXT",
        "MISSING_CONTEXT:",
        "`MISSING_CONTEXT`",
        "MISSING_CONTEXT ->",
        "-> MISSING_CONTEXT",
        "does not exist",
        "not yet created",
        "not yet exists",
        "TODO: create",
    ]
    for marker in markers:
        if marker in window:
            return True

    # Check if the reference is in a row that also has MISSING_CONTEXT
    # Look at the line and surrounding lines
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if ref in line:
            # Check this line and adjacent lines for MISSING_CONTEXT markers
            for j in range(max(0, i - 1), min(len(lines), i + 2)):
                if "MISSING_CONTEXT" in lines[j]:
                    return True
    return False


def resolve_ref(ref: str, harness_root: Path, project_root: Path) -> Path:
    """Resolve a reference to an absolute path."""
    ref = ref.strip()

    if ref.startswith("./"):
        return project_root / ref[2:]

    if ref.startswith(".harness/"):
        return harness_root / ref

    # Try project root
    candidate = project_root / ref
    if candidate.exists():
        return candidate

    # Try harness root if different
    if harness_root != project_root:
        candidate2 = harness_root / ref
        if candidate2.exists():
            return candidate2
        return candidate2

    return candidate


def validate_context_map(harness_path: str, project_path: str) -> dict:
    """Validate all file references in CONTEXT-MAP.md exist.

    References explicitly marked as MISSING_CONTEXT are allowed.
    """
    harness = Path(harness_path)
    project = Path(project_path)

    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "missing_references": [],
        "valid_references": [],
        "allowed_missing_contexts": [],
    }

    map_file = harness / "CONTEXT-MAP.md"
    if not map_file.exists():
        result["errors"].append("CONTEXT-MAP.md not found in harness root")
        result["status"] = "fail"
        return result

    content = map_file.read_text()
    result["evidence"].append({
        "source": "CONTEXT-MAP.md",
        "finding": f"Read CONTEXT-MAP.md ({len(content)} chars)"
    })

    refs = extract_file_references(content)

    if not refs:
        result["warnings"].append("No file references found in CONTEXT-MAP.md")
        result["status"] = "warning"
        return result

    result["evidence"].append({
        "source": "CONTEXT-MAP.md",
        "finding": f"Found {len(refs)} unique file references"
    })

    for ref in refs:
        resolved = resolve_ref(ref, harness, project)

        if resolved.exists():
            result["valid_references"].append({
                "referenced": ref,
                "resolved_path": str(resolved),
                "status": "exists",
            })
        else:
            # Check if this is an explicitly allowed MISSING_CONTEXT
            try:
                ref_pos = content.index(ref)
                if is_marked_missing_context(ref, content, ref_pos):
                    result["allowed_missing_contexts"].append({
                        "referenced": ref,
                        "attempted_path": str(resolved),
                        "status": "allowed_missing_context",
                    })
                else:
                    result["missing_references"].append({
                        "referenced": ref,
                        "attempted_path": str(resolved),
                        "status": "missing",
                        "reason": "Reference not found and not marked as MISSING_CONTEXT",
                    })
            except ValueError:
                result["missing_references"].append({
                    "referenced": ref,
                    "attempted_path": str(resolved),
                    "status": "missing",
                    "reason": "Reference not found (could not check context)",
                })

    # Determine overall status
    if result["missing_references"]:
        result["errors"].append(
            f"Found {len(result['missing_references'])} unmarked missing reference(s)"
        )
        result["status"] = "fail"
    elif result["warnings"]:
        result["status"] = "warning"
    else:
        result["status"] = "pass"

    result["evidence"].append({
        "source": "validate_context_map.py",
        "finding": (
            f"valid={len(result['valid_references'])}, "
            f"missing={len(result['missing_references'])}, "
            f"allowed_missing={len(result['allowed_missing_contexts'])}"
        )
    })

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: validate_context_map.py /path/to/harness [/path/to/project]"],
            "warnings": [],
            "evidence": [],
            "unknowns": [],
            "missing_references": [],
            "valid_references": [],
            "allowed_missing_contexts": [],
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    project_path = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]

    result = validate_context_map(sys.argv[1], project_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
