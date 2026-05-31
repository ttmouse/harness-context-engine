#!/usr/bin/env python3
"""Generate a lightweight relationship evidence graph for a project.

Usage:
  python scripts/generate_code_graph.py /path/to/project
  python scripts/generate_code_graph.py /path/to/project --output /path/to/code_graph.json
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SOURCE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".go", ".rs", ".java", ".php", ".rb"}
DOC_EXTS = {".md", ".mdx", ".rst", ".txt"}
CONFIG_NAMES = {"package.json", "tsconfig.json", "vite.config.ts", "vite.config.js", "webpack.config.js", "pyproject.toml", "Cargo.toml", "go.mod", "Makefile"}
EXCLUDE_DIRS = {".git", "node_modules", "dist", "build", ".next", "coverage", "__pycache__", "venv", ".venv"}
JS_IMPORT_RE = re.compile(r"(?:import\s+(?:[^'\"]+\s+from\s+)?|export\s+[^'\"]+\s+from\s+|require\(|import\()['\"]([^'\"]+)['\"]")
PY_IMPORT_RE = re.compile(r"^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))", re.MULTILINE)
API_RE = re.compile(r"['\"](/api/[a-zA-Z0-9_\-./:{}]+)['\"]")
ROUTE_RE = re.compile(r"\bpath\s*[:=]\s*['\"]([/#a-zA-Z0-9_\-./:{}]*)['\"]")


def result(status="pass", errors=None, warnings=None, evidence=None, unknowns=None, **extra):
    data = {"status": status, "errors": errors or [], "warnings": warnings or [], "evidence": evidence or [], "unknowns": unknowns or []}
    data.update(extra)
    return data


def skip(rel):
    return any(part in EXCLUDE_DIRS for part in rel.parts)


def text(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def node_type(rel):
    parts = [p.lower() for p in rel.parts]
    name = rel.name
    suffix = rel.suffix.lower()
    if suffix in DOC_EXTS:
        return "doc"
    if name in CONFIG_NAMES:
        return "config"
    if "test" in name.lower() or "spec" in name.lower() or "tests" in parts or "__tests__" in parts:
        return "test"
    if any(p in {"pages", "routes", "views", "screens", "app"} for p in parts):
        return "page"
    if any(p in {"components", "component"} for p in parts):
        return "component"
    if any(p in {"controllers", "controller"} for p in parts):
        return "controller"
    if any(p in {"services", "service"} for p in parts):
        return "service"
    if any(p in {"models", "model", "entities", "schema", "schemas"} for p in parts):
        return "model"
    return "file"


def file_id(rel):
    return "file:" + rel.as_posix()


def add_node(nodes, node_id, kind, name, path="", description="", source="", confidence="high", claim_type="observed"):
    if node_id not in nodes:
        nodes[node_id] = {"id": node_id, "type": kind, "name": name, "path": path, "description": description, "source": source or path, "confidence": confidence, "claim_type": claim_type}


def add_edge(edges, seen, source, target, kind, description, evidence, confidence="high", claim_type="observed"):
    key = (source, target, kind, evidence)
    if key not in seen:
        seen.add(key)
        edges.append({"source": source, "target": target, "type": kind, "description": description, "evidence": evidence, "confidence": confidence, "claim_type": claim_type})


def resolve_relative(project, current_rel, target):
    if not target.startswith("."):
        return None
    base = (project / current_rel).parent
    root = project.resolve()
    start = (base / target).resolve()
    try:
        start.relative_to(root)
    except ValueError:
        return None
    candidates = [start]
    for ext in SOURCE_EXTS:
        candidates.append(start.with_suffix(ext))
        candidates.append(start / ("index" + ext))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.relative_to(root)
    return None


def collect(project):
    files = []
    for p in project.rglob("*"):
        rel = p.relative_to(project)
        if skip(rel) or not p.is_file():
            continue
        if p.name in CONFIG_NAMES or p.suffix.lower() in SOURCE_EXTS | DOC_EXTS:
            files.append(rel)
    return sorted(files, key=lambda x: x.as_posix())


def detect(project):
    langs, frameworks = set(), set()
    if (project / "package.json").exists():
        langs.add("typescript" if (project / "tsconfig.json").exists() else "javascript")
        try:
            pkg = json.loads((project / "package.json").read_text(encoding="utf-8"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "typescript" in deps:
                langs.add("typescript")
            for fw, keys in {"react": ["react", "react-dom"], "vue": ["vue"], "nextjs": ["next"], "vite": ["vite"]}.items():
                if any(k in deps for k in keys):
                    frameworks.add(fw)
        except Exception:
            pass
    if list(project.glob("**/*.py")):
        langs.add("python")
    if (project / "go.mod").exists():
        langs.add("go")
    if (project / "Cargo.toml").exists():
        langs.add("rust")
    return sorted(langs), sorted(frameworks)


def generate_code_graph(project_path):
    project = Path(project_path).resolve()
    if not project.is_dir():
        return result("fail", errors=[f"Project path does not exist: {project_path}"])

    nodes, edges, seen = {}, [], set()
    warnings, unknowns, evidence = [], [], []
    files = collect(project)
    languages, frameworks = detect(project)

    for rel in files:
        kind = node_type(rel)
        add_node(nodes, file_id(rel), kind, rel.name, rel.as_posix(), f"Observed {kind} file", rel.as_posix())

    pkg = project / "package.json"
    if pkg.exists():
        try:
            scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
            for name, command in scripts.items():
                sid = f"config:package.json:scripts:{name}"
                add_node(nodes, sid, "config", f"script:{name}", "package.json", f"Package script command: {command}", "package.json")
                add_edge(edges, seen, "file:package.json", sid, "configures", f"package.json defines {name}", f"package.json scripts.{name}")
            evidence.append({"source": "package.json", "finding": f"Found {len(scripts)} scripts"})
        except Exception as exc:
            warnings.append(f"Could not parse package.json: {exc}")

    for rel in files:
        if rel.suffix.lower() not in SOURCE_EXTS:
            continue
        body = text(project / rel)
        source = file_id(rel)
        if rel.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".vue"}:
            for match in JS_IMPORT_RE.finditer(body):
                raw = match.group(1)
                resolved = resolve_relative(project, rel, raw)
                if resolved:
                    add_edge(edges, seen, source, file_id(resolved), "imports", f"{rel.as_posix()} imports {resolved.as_posix()}", f"{rel.as_posix()}: import '{raw}'")
                else:
                    node_id = "external:" + raw
                    add_node(nodes, node_id, "module", raw, "", "External or unresolved import", rel.as_posix(), "medium" if not raw.startswith(".") else "low", "observed" if not raw.startswith(".") else "unknown")
                    add_edge(edges, seen, source, node_id, "depends_on", f"{rel.as_posix()} depends on {raw}", f"{rel.as_posix()}: import/require '{raw}'", "medium" if not raw.startswith(".") else "low", "observed" if not raw.startswith(".") else "unknown")
        if rel.suffix.lower() == ".py":
            for match in PY_IMPORT_RE.finditer(body):
                raw = match.group(1) or match.group(2)
                if raw:
                    node_id = "external:" + raw
                    add_node(nodes, node_id, "module", raw, "", "Python import target", rel.as_posix(), "low", "inferred")
                    add_edge(edges, seen, source, node_id, "depends_on", f"{rel.as_posix()} imports {raw}", f"{rel.as_posix()}: import {raw}", "low", "inferred")
        for match in API_RE.finditer(body):
            api = match.group(1)
            api_id = "api:" + api
            add_node(nodes, api_id, "api", api, "", "Observed API path string", rel.as_posix(), "medium", "observed")
            add_edge(edges, seen, source, api_id, "calls", f"{rel.as_posix()} references API {api}", f"{rel.as_posix()}: string literal '{api}'", "medium", "observed")
        if "route" in rel.as_posix().lower() or "router" in body or "Route" in body:
            for match in ROUTE_RE.finditer(body):
                route = match.group(1) or "/"
                route_id = "route:" + route
                add_node(nodes, route_id, "route", route, "", "Observed route path string", rel.as_posix(), "medium", "observed")
                add_edge(edges, seen, source, route_id, "routes_to", f"{rel.as_posix()} references route {route}", f"{rel.as_posix()}: route path '{route}'", "medium", "observed")

    source_by_stem = {p.stem.lower(): p for p in files if node_type(p) != "test" and p.suffix.lower() in SOURCE_EXTS}
    for rel in files:
        if node_type(rel) == "test":
            stem = rel.stem.lower().replace(".test", "").replace(".spec", "").replace("_test", "")
            target = source_by_stem.get(stem)
            if target:
                add_edge(edges, seen, file_id(rel), file_id(target), "tests", f"{rel.as_posix()} appears to test {target.as_posix()}", f"{rel.as_posix()} filename matches {target.as_posix()}", "low", "inferred")

    if not edges:
        unknowns.append("No relationships detected; project may be small or need deeper language-specific analysis")
    graph = {
        "project": {"name": project.name, "type": "unknown", "root": str(project), "generated_at": datetime.now(timezone.utc).isoformat(), "confidence": "medium" if files else "low", "main_languages": languages, "frameworks": frameworks},
        "nodes": list(nodes.values()),
        "edges": edges,
        "features": [],
        "risk_edges": [],
        "unknowns": unknowns,
    }
    evidence.append({"source": "generate_code_graph.py", "finding": f"Generated {len(nodes)} nodes and {len(edges)} edges from {len(files)} scanned files"})
    return result("warning" if warnings or unknowns else "pass", warnings=warnings, evidence=evidence, unknowns=unknowns, code_graph=graph)


def main():
    parser = argparse.ArgumentParser(description="Generate lightweight code graph JSON")
    parser.add_argument("project_path")
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    data = generate_code_graph(args.project_path)
    if args.output and "code_graph" in data:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data["code_graph"], indent=2, ensure_ascii=False), encoding="utf-8")
        data["evidence"].append({"source": str(out), "finding": "Wrote raw code_graph.json"})
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if data["status"] in ("pass", "warning") else 1


if __name__ == "__main__":
    raise SystemExit(main())
