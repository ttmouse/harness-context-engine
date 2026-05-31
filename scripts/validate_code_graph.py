#!/usr/bin/env python3
import json
import sys
from pathlib import Path

VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_CLAIM_TYPES = {"observed", "inferred", "unknown"}
VALID_NODE_TYPES = {"file", "module", "page", "component", "route", "api", "controller", "service", "function", "class", "model", "table", "field", "config", "test", "doc", "business_feature"}
VALID_EDGE_TYPES = {"imports", "calls", "renders", "routes_to", "handles", "reads", "writes", "updates", "depends_on", "tests", "documents", "implements", "affects", "configures"}


def make_result(status="pass", errors=None, warnings=None, evidence=None, unknowns=None):
    return {"status": status, "errors": errors or [], "warnings": warnings or [], "evidence": evidence or [], "unknowns": unknowns or []}


def read_graph(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("code_graph"), dict):
        return data["code_graph"]
    return data


def validate_code_graph(graph_path, project_path=None):
    graph_file = Path(graph_path)
    if not graph_file.is_file():
        return make_result("fail", errors=[f"code graph file missing: {graph_path}"])
    try:
        graph = read_graph(graph_file)
    except Exception as exc:
        return make_result("fail", errors=[f"cannot read code graph: {exc}"])

    errors = []
    warnings = []
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list):
        errors.append("nodes must be a list")
        nodes = []
    if not isinstance(edges, list):
        errors.append("edges must be a list")
        edges = []

    node_ids = set()
    path_nodes = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"nodes[{index}] must be an object")
            continue
        node_id = node.get("id")
        if not node_id:
            errors.append(f"nodes[{index}] missing id")
        elif node_id in node_ids:
            errors.append(f"duplicate node id: {node_id}")
        else:
            node_ids.add(node_id)
        if not node.get("name"):
            errors.append(f"node {node_id or index} missing name")
        if node.get("type") not in VALID_NODE_TYPES:
            warnings.append(f"node {node_id or index} has unknown type: {node.get('type')}")
        if node.get("confidence") not in VALID_CONFIDENCE:
            errors.append(f"node {node_id or index} has invalid confidence: {node.get('confidence')}")
        if node.get("claim_type") not in VALID_CLAIM_TYPES:
            errors.append(f"node {node_id or index} has invalid claim_type: {node.get('claim_type')}")
        if node.get("path"):
            path_nodes.append(node)

    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object")
            continue
        source = edge.get("source")
        target = edge.get("target")
        if not source or source not in node_ids:
            errors.append(f"edge {index} source is not a known node: {source}")
        if not target or target not in node_ids:
            errors.append(f"edge {index} target is not a known node: {target}")
        if edge.get("type") not in VALID_EDGE_TYPES:
            warnings.append(f"edge {index} has unknown type: {edge.get('type')}")
        if not edge.get("evidence"):
            errors.append(f"edge {index} missing evidence")
        if edge.get("confidence") not in VALID_CONFIDENCE:
            errors.append(f"edge {index} has invalid confidence: {edge.get('confidence')}")
        if edge.get("claim_type") not in VALID_CLAIM_TYPES:
            errors.append(f"edge {index} has invalid claim_type: {edge.get('claim_type')}")

    if project_path:
        project = Path(project_path)
        if project.is_dir():
            missing = [n.get("path") for n in path_nodes if n.get("path") and not (project / n.get("path")).exists()]
            if missing:
                errors.append("path node(s) missing from project: " + ", ".join(sorted(missing)[:20]))
        else:
            warnings.append(f"project path unavailable; path checks skipped: {project_path}")

    inferred = [e for e in edges if isinstance(e, dict) and e.get("claim_type") == "inferred"]
    if edges and len(inferred) / len(edges) > 0.5 and not graph.get("unknowns"):
        warnings.append("More than 50% of edges are inferred but graph.unknowns is empty")
    if nodes and not edges:
        warnings.append("Graph contains nodes but no edges")
    if not nodes:
        errors.append("Graph contains no nodes")

    status = "fail" if errors else "warning" if warnings else "pass"
    evidence = [{"source": str(graph_file), "finding": f"Validated {len(nodes)} nodes and {len(edges)} edges"}]
    return make_result(status, errors, warnings, evidence, [])


def main():
    if len(sys.argv) not in (2, 3):
        print(json.dumps(make_result("fail", errors=["Usage: validate_code_graph.py code_graph.json [project_path]"]), indent=2, ensure_ascii=False))
        return 1
    data = validate_code_graph(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if data["status"] in ("pass", "warning") else 1


if __name__ == "__main__":
    raise SystemExit(main())
