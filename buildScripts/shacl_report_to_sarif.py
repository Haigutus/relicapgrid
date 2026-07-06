"""Convert a SHACL ValidationReport (RDF/XML) to SARIF for GitHub code scanning."""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

SH = "http://www.w3.org/ns/shacl#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DCTERMS = "http://purl.org/dc/terms/"
PROV = "http://www.w3.org/ns/prov#"

SEVERITY_TO_LEVEL = {
    f"{SH}Violation": "error",
    f"{SH}Warning": "warning",
    f"{SH}Info": "note",
}

RULE_DESCRIPTIONS = {
    "sh:MinCountConstraintComponent": {
        "name": "Minimum cardinality violation",
        "shortDescription": "A required property has fewer values than the minimum specified by the shape.",
        "fullDescription": "SHACL sh:MinCountConstraintComponent violation.",
        "helpUri": "https://www.w3.org/TR/shacl/#MinCountConstraintComponent",
        "defaultLevel": "error",
    },
    "sh:MaxCountConstraintComponent": {
        "name": "Maximum cardinality violation",
        "shortDescription": "A property has more values than the maximum specified by the shape.",
        "fullDescription": "SHACL sh:MaxCountConstraintComponent violation.",
        "helpUri": "https://www.w3.org/TR/shacl/#MaxCountConstraintComponent",
        "defaultLevel": "error",
    },
    "sh:PatternConstraintComponent": {
        "name": "Pattern mismatch",
        "shortDescription": "Value does not match the required regular expression pattern.",
        "fullDescription": "SHACL sh:PatternConstraintComponent violation.",
        "helpUri": "https://www.w3.org/TR/shacl/#PatternConstraintComponent",
        "defaultLevel": "warning",
    },
}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _text_values(element: ET.Element, local: str) -> list[str]:
    tag = f"{{{SH}}}{local}"
    return [child.text.strip() for child in element.findall(tag) if child.text]


def _resource_value(element: ET.Element, local: str) -> str | None:
    tag = f"{{{SH}}}{local}"
    child = element.find(tag)
    if child is None:
        return None
    return child.get(f"{{{RDF}}}resource") or (child.text.strip() if child.text else None)


def _infer_rule_id(result: ET.Element) -> str:
    component = _resource_value(result, "sourceConstraintComponent")
    if component:
        return component.rsplit("#", 1)[-1] if "#" in component else component.rsplit("/", 1)[-1]

    shape = _resource_value(result, "sourceShape")
    if shape:
        return shape.rsplit("#", 1)[-1] if "#" in shape else shape.rsplit("/", 1)[-1]

    return "sh:ValidationResult"


def _rule_description(rule_id: str) -> dict:
    if rule_id in RULE_DESCRIPTIONS:
        meta = RULE_DESCRIPTIONS[rule_id]
        return {
            "id": rule_id,
            "name": meta["name"],
            "shortDescription": {"text": meta["shortDescription"]},
            "fullDescription": {"text": meta["fullDescription"]},
            "helpUri": meta["helpUri"],
            "defaultConfiguration": {"level": meta["defaultLevel"]},
        }

    return {
        "id": rule_id,
        "name": rule_id,
        "shortDescription": {"text": f"SHACL constraint violation ({rule_id})."},
        "fullDescription": {"text": f"SHACL validation failed for rule {rule_id}."},
        "helpUri": "https://www.w3.org/TR/shacl/",
        "defaultConfiguration": {"level": "error"},
    }


def _resolve_source_uri(source_name: str, repo_root: Path) -> str:
    if "/" in source_name or "\\" in source_name:
        return source_name.replace("\\", "/")

    matches = list(repo_root.rglob(source_name))
    if len(matches) == 1:
        return str(matches[0].relative_to(repo_root)).replace("\\", "/")
    return source_name


def _fingerprint(rule_id: str, focus_node: str | None, result_path: str | None, source_uri: str) -> str:
    payload = f"{rule_id}|{focus_node or ''}|{result_path or ''}|{source_uri}"
    digest = hashlib.sha256(payload.encode()).hexdigest()[:12]
    return f"{digest}:1"


def _element_types(element: ET.Element) -> list[str]:
    return [
        child.get(f"{{{RDF}}}resource", "")
        for child in element
        if _local_name(child.tag) == "type"
    ]


def parse_shacl_report(report_path: Path, repo_root: Path) -> tuple[str, list[dict], list[str]]:
    root = ET.parse(report_path).getroot()
    descriptions = root.findall(f"{{{RDF}}}Description")

    source_uri = "unknown"
    shape_uris: list[str] = []
    for element in descriptions:
        if f"{SH}ValidationReport" not in _element_types(element):
            continue
        source = element.find(f"{{{DCTERMS}}}source")
        if source is not None and source.text:
            source_uri = _resolve_source_uri(source.text.strip(), repo_root)
        shape_uris = [
            child.text.strip()
            for child in element.findall(f"{{{DCTERMS}}}conformsTo")
            if child.text
        ]
        break

    results: list[dict] = []
    for element in descriptions:
        if f"{SH}ValidationResult" not in _element_types(element):
            continue

        focus_node = _text_values(element, "focusNode")
        focus_node_text = focus_node[0] if focus_node else None
        result_path = _text_values(element, "resultPath")
        result_path_text = result_path[0] if result_path else None
        messages = _text_values(element, "resultMessage")
        severity = _resource_value(element, "resultSeverity") or f"{SH}Violation"
        level = SEVERITY_TO_LEVEL.get(severity, "error")
        rule_id = _infer_rule_id(element)
        source_shape = _resource_value(element, "sourceShape")
        source_component = _resource_value(element, "sourceConstraintComponent")
        result_value = _text_values(element, "resultValue")
        result_value_text = result_value[0] if result_value else None

        primary_message = messages[0] if messages else "SHACL validation violation"
        message_text = primary_message
        if focus_node_text or result_path_text:
            message_text = (
                f"{primary_message}. "
                f"Focus node: {focus_node_text or 'n/a'}, "
                f"Path: {result_path_text or 'n/a'}"
            )
            if result_value_text:
                message_text += f", Value: {result_value_text}"

        results.append(
            {
                "ruleId": rule_id,
                "level": level,
                "message": {"text": message_text},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": source_uri,
                                "uriBaseId": "%SRCROOT%",
                            },
                            "region": {"startLine": 1, "startColumn": 1},
                        }
                    }
                ],
                "partialFingerprints": {
                    "primaryLocationLineHash": _fingerprint(
                        rule_id, focus_node_text, result_path_text, source_uri
                    )
                },
                "properties": {
                    "focusNode": focus_node_text,
                    "resultPath": result_path_text,
                    "resultValue": result_value_text,
                    "sourceShape": source_shape,
                    "sourceConstraintComponent": source_component,
                    "resultSeverity": severity.rsplit("#", 1)[-1],
                    "resultMessages": messages,
                },
            }
        )

    return source_uri, results, shape_uris


def build_sarif(
    results: list[dict],
    *,
    tool_version: str = "1.0.0",
    generated_by: str | None = None,
) -> dict:
    rule_ids = list(dict.fromkeys(result["ruleId"] for result in results))
    rules = [_rule_description(rule_id) for rule_id in rule_ids]
    rule_index = {rule["id"]: index for index, rule in enumerate(rules)}

    sarif_results = []
    for result in results:
        entry = dict(result)
        entry["ruleIndex"] = rule_index[entry["ruleId"]]
        sarif_results.append(entry)

    driver = {
        "name": "shacl-validator",
        "semanticVersion": tool_version,
        "informationUri": "https://github.com/Haigutus/relicapgrid",
        "rules": rules,
    }
    if generated_by:
        driver["fullName"] = generated_by

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{"tool": {"driver": driver}, "results": sarif_results}],
    }


def convert(report_path: Path, output_path: Path, repo_root: Path) -> dict:
    source_uri, results, _ = parse_shacl_report(report_path, repo_root)
    sarif = build_sarif(results)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sarif, indent=2), encoding="utf-8")
    print(f"Converted {len(results)} SHACL results from {report_path.name}")
    print(f"Source artifact: {source_uri}")
    print(f"Wrote SARIF to {output_path}")
    return sarif


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report",
        nargs="?",
        default="reports/sample_shacl_report.rdf",
        help="Path to SHACL ValidationReport (RDF/XML)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="reports/shacl-results.sarif",
        help="Output SARIF file path",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root used to resolve dcterms:source filenames",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root or Path(__file__).resolve().parent.parent)
    convert(Path(args.report), Path(args.output), repo_root)


if __name__ == "__main__":
    main()