#!/usr/bin/env python3
"""
Validate CONTEXT-MAP.md references point to existing files.
Status: implemented

Outputs JSON with pass/fail/unknown status.
References to missing files are flagged as MISSING_CONTEXT.
"""
import sys
import json
import re
from pathlib import Path

def extract_file_references(content: str) -> list:
    """Extract file/directory references from markdown content.
    
    Matches:
    - Backtick refs: `src/App.tsx`, `.harness/commands.md`
    - Relative paths: ./src, ../docs
    - Inline code: `file.ts`
    - Table cells with paths
    """
    refs = []
    
    # Backtick code spans: `path` or `file.ext`
    backtick_pattern = re.compile(r'`((?:\./)?(?:/?(?:src|lib|app|components|pages|docs|\.harness)[a-zA-Z0-9_/\-.]*))`')
    for match in backtick_pattern.finditer(content):
        ref = match.group(1).strip()
        if ref and not ref.startswith('http'):
            refs.append(ref)
    
    # Table cells that look like paths (start with . or src, lib, etc.)
    # Only match cells that contain path-like content
    table_pattern = re.compile(r'^\s*\|\s*([^|]*?(?:(?:src|lib|app|components|pages|docs|\.harness)[/\\][^|]+?))\s*\|', re.MULTILINE)
    for match in table_pattern.finditer(content):
        cell = match.group(1).strip()
        if cell and ('/' in cell or cell.startswith('.')):
            refs.append(cell)
    
    # Inline paths in prose: src/components, .harness/commands.md
    path_pattern = re.compile(r'(?:^|(?<=\s))(\./(?:src|lib|app|components|pages|docs|\.harness)[a-zA-Z0-9_/\-.]*)', re.MULTILINE)
    for match in path_pattern.finditer(content):
        refs.append(match.group(1))
    
    return list(set(refs))


def resolve_ref(ref: str, harness_root: Path, project_root: Path) -> Path:
    """
    Resolve a reference to an absolute path.
    
    Strategy:
    1. If starts with ./ — relative to project root
    2. If starts with .harness/ — relative to harness root
    3. Otherwise try project root first, then harness root
    """
    # Strip leading/trailing whitespace
    ref = ref.strip()
    
    if ref.startswith('./'):
        return project_root / ref[2:]
    
    if ref.startswith('.harness/'):
        return harness_root / ref
    
    # Try project root
    candidate = project_root / ref
    if candidate.exists():
        return candidate
    
    # Try harness root for .harness/ files
    if harness_root != project_root:
        return harness_root / ref
    
    return candidate


def validate_context_map(harness_path: str, project_path: str) -> dict:
    """
    Validate all file references in CONTEXT-MAP.md exist.
    
    Args:
        harness_path: Path to harness root (contains CONTEXT-MAP.md)
        project_path: Path to project root (contains actual source files)
                     May be same as harness_path for in-repo harnesses.
    
    Returns:
        JSON dict with status, missing_references, valid_references, errors, warnings
    """
    harness = Path(harness_path)
    project = Path(project_path)
    
    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "missing_references": [],
        "valid_references": [],
        "unresolved_references": []
    }

    map_file = harness / "CONTEXT-MAP.md"
    if not map_file.exists():
        result["errors"].append("CONTEXT-MAP.md not found in harness root")
        result["status"] = "fail"
        return result

    content = map_file.read_text()
    refs = extract_file_references(content)
    
    if not refs:
        result["warnings"].append("No file references found in CONTEXT-MAP.md")
        result["status"] = "unknown"
        return result

    for ref in refs:
        resolved = resolve_ref(ref, harness, project)
        
        if not resolved.exists():
            result["missing_references"].append({
                "referenced": ref,
                "attempted_path": str(resolved),
                "status": "MISSING_CONTEXT"
            })
        else:
            result["valid_references"].append({
                "referenced": ref,
                "resolved_path": str(resolved),
                "status": "exists"
            })

    if result["missing_references"]:
        result["status"] = "fail"
    elif not result["valid_references"]:
        result["status"] = "unknown"

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: validate_context_map.py /path/to/harness [/path/to/project]"],
            "missing_references": [],
            "valid_references": []
        }, indent=2))
        sys.exit(1)
    
    # Second arg optional: project root (defaults to harness root)
    project_path = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
    
    result = validate_context_map(sys.argv[1], project_path)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "pass" else 1)
