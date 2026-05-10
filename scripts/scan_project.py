#!/usr/bin/env python3
"""
Scan project structure: language, framework, package scripts, directory tree, CI, monorepo clues.

Outputs unified JSON with status, errors, warnings, evidence, unknowns.

Usage:
    python scripts/scan_project.py /path/to/project
"""
import sys
import json
import re
from pathlib import Path


def scan_project(project_path: str) -> dict:
    project = Path(project_path)

    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "project_path": str(project.resolve()),
    }

    if not project.is_dir():
        result["errors"].append(f"Project path does not exist: {project_path}")
        result["status"] = "fail"
        return result

    # --- Package Manager & Scripts ---
    package_manager = "unknown"
    scripts = {}
    dependencies = {}
    dev_dependencies = {}

    pkg = project / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            scripts = data.get("scripts", {})
            dependencies = data.get("dependencies", {})
            dev_dependencies = data.get("devDependencies", {})

            result["evidence"].append({
                "source": "package.json",
                "finding": f"Found {len(scripts)} scripts, {len(dependencies)} deps, {len(dev_dependencies)} devDeps"
            })

            pkg_text = pkg.read_text()
            if "pnpm" in pkg_text or (project / "pnpm-lock.yaml").exists():
                package_manager = "pnpm"
            elif "yarn" in pkg_text or (project / "yarn.lock").exists():
                package_manager = "yarn"
            elif (project / "package-lock.json").exists():
                package_manager = "npm"
            else:
                result["warnings"].append(
                    "package.json exists but no lockfile found (package-lock.json, yarn.lock, pnpm-lock.yaml)"
                )
                package_manager = "npm"
        except (json.JSONDecodeError, Exception) as e:
            result["errors"].append(f"Failed to parse package.json: {e}")
            result["status"] = "fail"
    else:
        result["unknowns"].append("No package.json found")

    # --- Other package managers ---
    if (project / "Cargo.toml").exists():
        package_manager = "cargo"
        result["evidence"].append({"source": "Cargo.toml", "finding": "Rust project"})
    elif (project / "go.mod").exists():
        package_manager = "go"
        result["evidence"].append({"source": "go.mod", "finding": "Go project"})
    elif (project / "Podfile").exists():
        package_manager = "cocoapods"
        result["evidence"].append({"source": "Podfile", "finding": "iOS project"})

    # --- Language & Framework ---
    language = "unknown"
    framework = "unknown"

    all_deps = {**dependencies, **dev_dependencies}

    if dependencies or (project / "Cargo.toml").exists():
        if "typescript" in all_deps or "typescript" in dev_dependencies:
            language = "typescript"
        elif "react" in all_deps or "react-dom" in all_deps:
            language = "javascript"  # Could be JS or TS without explicit dep
        elif list(project.glob("*.py")) or list(project.glob("**/*.py")):
            language = "python"
        elif (project / "go.mod").exists():
            language = "go"
        elif (project / "Cargo.toml").exists():
            language = "rust"
        elif (project / "Gemfile").exists():
            language = "ruby"
        elif (project / "pom.xml").exists() or (project / "build.gradle").exists():
            language = "java"

    # Language hints from config files
    if language == "unknown":
        if list(project.glob("tsconfig.json")):
            language = "typescript"
        elif list(project.glob("**/*.ts")):
            language = "typescript"
        elif list(project.glob("**/*.py")):
            language = "python"
        elif list(project.glob("**/*.go")):
            language = "go"

    # Framework detection
    if "react" in all_deps or "react-dom" in all_deps:
        framework = "react"
    elif "vue" in all_deps or "vue-router" in all_deps:
        framework = "vue"
    elif "@angular/core" in all_deps:
        framework = "angular"
    elif "next" in all_deps:
        framework = "nextjs"
    elif "svelte" in all_deps or "sveltekit" in all_deps:
        framework = "svelte"
    elif "flask" in all_deps or "django" in all_deps:
        framework = "python"
    elif (project / "Gemfile").exists():
        if "rails" in (project / "Gemfile").read_text():
            framework = "rails"

    # Check for vite / webpack / other bundlers
    if list(project.glob("vite.config.*")):
        result["evidence"].append({"source": "vite.config.*", "finding": "Vite bundler"})
    if list(project.glob("webpack.config.*")):
        result["evidence"].append({"source": "webpack.config.*", "finding": "Webpack bundler"})

    # --- README ---
    readme = None
    for f in ["README.md", "README.txt", "README"]:
        if (project / f).exists():
            readme = f
            break

    if readme:
        readme_size = len((project / readme).read_text())
        result["evidence"].append({
            "source": readme,
            "finding": f"README exists ({readme_size} chars)"
        })
    else:
        result["warnings"].append("No README.md found")

    # --- Source Directories ---
    source_dirs = []
    for d in ["src", "lib", "app", "internal", "packages"]:
        if (project / d).is_dir():
            source_dirs.append(d)

    if not source_dirs:
        result["warnings"].append("No standard source directories found (src/, lib/, app/, internal/, packages/)")

    # --- Pages/Routes ---
    pages_dirs = []
    routes_patterns = ["pages", "routes", "views", "screens"]
    for d in routes_patterns:
        for root_dir in (source_dirs or ["."]):
            candidate = project / root_dir / d
            if candidate.is_dir():
                pages_dirs.append(str(candidate.relative_to(project)))

    route_files = []
    route_extensions = ["*.tsx", "*.jsx", "*.ts", "*.js"]
    for ext in route_extensions:
        for f in project.glob(f"**/{ext}"):
            try:
                content = f.read_text()
                if "Route" in content or "router" in content or "createBrowserRouter" in content:
                    route_files.append(str(f.relative_to(project)))
            except Exception:
                pass

    if route_files:
        result["evidence"].append({
            "source": ", ".join(route_files[:5]),
            "finding": f"Found {len(route_files)} files with route/router references"
        })

    # --- Test Configuration ---
    test_configs = []
    for pattern in ["**/jest.config.*", "**/vitest.config.*", "**/.jest*", "**/karma.conf.*",
                    "**/cypress.json", "**/cypress.config.*", "**/playwright.config.*",
                    "**/pytest.ini", "**/setup.py", "**/tox.ini", "**/go.test*"]:
        for f in project.glob(pattern):
            test_configs.append(str(f.relative_to(project)))

    test_commands = [name for name in scripts if "test" in name.lower()]
    test_framework = "unknown"
    if "jest" in all_deps or "jest" in dev_dependencies:
        test_framework = "jest"
    elif "vitest" in all_deps or "vitest" in dev_dependencies:
        test_framework = "vitest"
    elif "mocha" in all_deps or "mocha" in dev_dependencies:
        test_framework = "mocha"
    elif "cypress" in all_deps or "cypress" in dev_dependencies:
        test_framework = "cypress"
    elif "playwright" in all_deps or "playwright" in dev_dependencies:
        test_framework = "playwright"
    elif "pytest" in str(test_configs) or list(project.glob("**/test_*.py")):
        test_framework = "pytest"
    elif list(project.glob("**/*test*")):
        test_framework = "unknown (test files exist)"

    # --- CI Workflow ---
    ci_files = []
    for pattern in [
        ".github/workflows/*.yml", ".github/workflows/*.yaml",
        ".gitlab-ci.yml", ".circleci/config.yml",
        "Jenkinsfile", ".drone.yml", "azure-pipelines.yml"
    ]:
        for f in project.glob(pattern):
            ci_files.append(str(f.relative_to(project)))

    if ci_files:
        result["evidence"].append({
            "source": ", ".join(ci_files),
            "finding": f"Found {len(ci_files)} CI workflow files"
        })
    else:
        result["unknowns"].append("No CI workflow files found (.github/, .gitlab-ci.yml, etc.)")

    # --- Monorepo clues ---
    monorepo_clues = []
    if (project / "lerna.json").exists():
        monorepo_clues.append("lerna.json")
    if "workspaces" in scripts or "workspaces" in str(pkg.read_text() if pkg.exists() else ""):
        monorepo_clues.append("npm/yarn workspaces")
    if (project / "pnpm-workspace.yaml").exists():
        monorepo_clues.append("pnpm-workspace.yaml")
    if (project / "packages").is_dir() and list((project / "packages").iterdir()):
        monorepo_clues.append("packages/ directory")
    if (project / "turbo.json").exists():
        monorepo_clues.append("turbo.json")
    if (project / "nx.json").exists():
        monorepo_clues.append("nx.json")

    # --- Build result ---
    result["evidence"].append({
        "source": "scan_project.py",
        "finding": f"Language={language}, Framework={framework}, PackageManager={package_manager}"
    })

    if language == "unknown":
        result["unknowns"].append("Could not determine language")

    result["project"] = {
        "language": language,
        "framework": framework,
        "package_manager": package_manager,
        "scripts": scripts,
        "source_directories": source_dirs,
        "pages_directories": pages_dirs,
        "route_files": route_files[:20],
        "readme": readme,
        "test_configs": test_configs,
        "test_framework": test_framework,
        "test_commands": test_commands,
        "ci_files": ci_files,
        "monorepo_clues": monorepo_clues,
        "config_files": sorted([
            str(f.relative_to(project))
            for pattern in ["vite.config.*", "webpack.config.*", "tailwind.config.*",
                            "tsconfig.json", ".eslintrc*", ".prettierrc*", "Makefile"]
            for f in project.glob(pattern)
        ])
    }

    if result["warnings"] and result["status"] == "pass":
        result["status"] = "warning"

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: scan_project.py /path/to/project"],
            "warnings": [],
            "evidence": [],
            "unknowns": []
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = scan_project(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] in ("pass", "warning") else 1)
