#!/usr/bin/env python3
"""
Scan project structure: language, framework, package scripts, directory tree.
Status: implemented
"""
import sys
import json
import subprocess
from pathlib import Path

def scan_project(project_path: str) -> dict:
    project = Path(project_path)

    result = {
        "project_path": str(project),
        "language": "unknown",
        "framework": "unknown",
        "package_manager": "unknown",
        "scripts": {},
        "directories": [],
        "config_files": [],
        "status": "ok"
    }

    # package.json
    pkg = project / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            result["scripts"] = data.get("scripts", {})

            if "react" in deps or "react-dom" in deps:
                result["framework"] = "react"
            elif "vue" in deps:
                result["framework"] = "vue"
            elif "@angular/core" in deps:
                result["framework"] = "angular"

            if "typescript" in deps or "typescript" in data.get("devDependencies", {}):
                result["language"] = "typescript"

            if "pnpm" in str(pkg.read_text()):
                result["package_manager"] = "pnpm"
            elif "yarn" in str(pkg.read_text()):
                result["package_manager"] = "yarn"
            else:
                result["package_manager"] = "npm"
        except Exception as e:
            result["error"] = str(e)

    # Source directories
    for d in ["src", "lib", "app", "internal"]:
        if (project / d).is_dir():
            result["directories"].append(d)
            # list subdirs
            try:
                subdirs = [str(p.relative_to(project)) for p in (project / d).iterdir() if p.is_dir() and not p.name.startswith('.')]
                result["directories"].extend(subdirs)
            except Exception:
                pass

    # Config files
    for pattern in ["vite.config.*", "webpack.config.*", "tailwind.config.*",
                    "tsconfig.json", ".eslintrc*", ".prettierrc*", "Makefile"]:
        for f in project.glob(pattern):
            result["config_files"].append(str(f.relative_to(project)))

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scan_project.py /path/to/project")
        sys.exit(1)
    result = scan_project(sys.argv[1])
    print(json.dumps(result, indent=2))
