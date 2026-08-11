"""SHACL validation of ReliCapGrid instances with native SARIF 2.1.0 export.

Uses triplets >= 0.2.0rc1: ``.shacl.to_sarif()`` emits grouped results (one per
violated rule with occurrenceCount, per-occurrence file:line regions) with
line-only, fully bounded regions — the 0.2.0a2-era post-processing (column
stripping, fallback locations) is no longer needed.

Two validations, merged into one SARIF log with repo-relative artifact URIs:
  * Svedala EQ against the official CGMES Equipment SHACL, with three issues
    injected deliberately so code scanning always shows error-level alerts;
  * Svedala-Espheim RA (NCP RemedialAction) as-is — the real state of the data.

Each validation also exports the full sh:ValidationReport (turtle + RDF/XML)
into reports/, and reports/summary.md links the run to the code scanning UI.

Run from the repo root:  uv run buildScripts/validate_shacl_sarif.py
"""
import json
import logging
import os
import urllib.request
from pathlib import Path

import pandas
import triplets
from triplets.export_schema import schemas

logging.getLogger("triplets.validation").setLevel(logging.ERROR)

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)  # keep SARIF artifactLocation URIs repo-relative

APL_RAW = "https://raw.githubusercontent.com/entsoe/application-profiles-library/main"

EQ = "Instance/Svedala/Grid/cimxml/20220615T2230Z__Svedala_EQ_1.xml"
EQ_SHACL = ["CGMES/SHACL/61970-600-2_Equipment-AP-Con-Simple-SHACL.ttl",
            "CGMES/SHACL/61970-301_Equipment-AP-Con-Complex-SHACL.ttl"]

RA = "Instance/DC-Espheim-Svedala/NetworkCode/Svedala-Espheim_RA.xml"
RA_SHACL = ["NCP/SHACL/RemedialAction-AP-Con-Simple-SHACL.ttl",
            "NCP/SHACL/RemedialAction-AP-Con-Complex-SHACL.ttl"]

LEVEL_ICONS = {"error": "🔴", "warning": "🟠", "note": "🔵"}
REPORTS = REPO_ROOT / "reports"


def entsoe_shapes(paths):
    cache = REPO_ROOT / ".shacl_cache"
    cache.mkdir(exist_ok=True)
    local = []
    for path in paths:
        name = Path(path).name
        if not (cache / name).exists():
            print(f"downloading {name}")
            urllib.request.urlretrieve(f"{APL_RAW}/{path}", cache / name)
        local.append(str(cache / name))
    return local


def export_reports(located, instance, shape_files):
    stem = Path(instance).stem
    sarif_path = located.shacl.to_sarif(path=REPORTS / f"{stem}.sarif")
    for suffix in ("ttl", "xml"):
        report = located.shacl.to_shacl_report(
            path=REPORTS / f"{stem}-shacl-report.{suffix}",
            report_source=instance, report_references=[Path(s).name for s in shape_files])
        print("wrote", report)

    # GitHub code scanning needs a location on every result. Shape-level
    # meta-findings (triplets:invalidSparql — the sh:sparql constraint itself
    # is broken) have no instance line, so anchor them to the validated file.
    sarif = json.loads(Path(sarif_path).read_text())
    for result in sarif["runs"][0]["results"]:
        if not result.get("locations"):
            result["locations"] = [{"physicalLocation": {
                "artifactLocation": {"uri": instance}, "region": {"startLine": 1, "endLine": 1}}}]
    Path(sarif_path).write_text(json.dumps(sarif, indent=2))
    return sarif


def validate_eq_with_injected_issues():
    shapes = entsoe_shapes(EQ_SHACL)
    data = pandas.read_RDF([EQ])
    print(f"parsed {len(data):,} triples from {Path(EQ).name}")

    line = sorted(data.loc[(data["KEY"] == "Type") & (data["VALUE"] == "ACLineSegment"), "ID"])[0]
    winding = sorted(data.loc[(data["KEY"] == "Type") & (data["VALUE"] == "PowerTransformerEnd"), "ID"])[0]
    terminal = sorted(data.loc[(data["KEY"] == "Type") & (data["VALUE"] == "Terminal"), "ID"])[0]
    substation = sorted(data.loc[(data["KEY"] == "Type") & (data["VALUE"] == "Substation"), "ID"])[0]

    broken = data[~((data["ID"] == line) & (data["KEY"] == "IdentifiedObject.name"))].copy()  # 1: missing name
    broken.loc[(broken["ID"] == winding) & (broken["KEY"] == "PowerTransformerEnd.ratedU"), "VALUE"] = "-400"  # 2: value range
    broken.loc[(broken["ID"] == terminal) & (broken["KEY"] == "Terminal.ConductingEquipment"), "VALUE"] = substation  # 3: value type

    violations = broken.shacl.validate(shapes, rdf_map=schemas.ENTSOE_CGMES_3_0_0_552_ED1)
    print("EQ (3 injected issues):", violations["SEVERITY"].value_counts().to_dict())
    enriched = violations.shacl.enrich(data=broken, shapes=shapes, rdf_map=schemas.ENTSOE_CGMES_3_0_0_552_ED1)
    return export_reports(enriched.shacl.locate(sources=[EQ]), EQ, shapes)


def validate_ra():
    shapes = entsoe_shapes(RA_SHACL)
    data = pandas.read_RDF([RA])
    print(f"parsed {len(data):,} triples from {Path(RA).name}")

    violations = data.shacl.validate(shapes, rdf_map=schemas.ENTSOE_NC_2_4_1_552_ED1)
    print("RA (as-is):", violations["SEVERITY"].value_counts().to_dict() if len(violations) else "conforms")
    enriched = violations.shacl.enrich(data=data, shapes=shapes, rdf_map=schemas.ENTSOE_NC_2_4_1_552_ED1)
    return export_reports(enriched.shacl.locate(sources=[RA]), RA, shapes)


def write_summary(sarif):
    lines = ["# SHACL validation", ""]
    repo, branch = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_REF_NAME")
    if repo and branch:
        alerts = (f"https://github.com/{repo}/security/code-scanning"
                  f"?query=is%3Aopen+branch%3A{branch}+tool%3A%22triplets-shacl%22")
        lines += [f"**[Open the code scanning alerts of this branch →]({alerts})**", "",
                  "Full sh:ValidationReport (turtle + RDF/XML) per instance is attached "
                  "to this run as the `shacl-reports` artifact.", ""]
    lines += ["| rule | level | occurrences |", "|---|---|---|"]
    for run in sarif["runs"]:
        for result in run["results"]:
            icon = LEVEL_ICONS.get(result["level"], "")
            count = result.get("occurrenceCount", len(result.get("locations", [])))
            lines.append(f"| `{result['ruleId']}` | {icon} {result['level']} | {count} |")
    (REPORTS / "summary.md").write_text("\n".join(lines) + "\n")
    print("wrote", REPORTS / "summary.md")


print("triplets", triplets.__version__)
REPORTS.mkdir(exist_ok=True)

logs = [validate_eq_with_injected_issues(), validate_ra()]

merged = logs[0]
for log in logs[1:]:
    merged["runs"].extend(log["runs"])
(REPORTS / "shacl-results.sarif").write_text(json.dumps(merged, indent=2))

results = [r for run in merged["runs"] for r in run["results"]]
levels = {}
for result in results:
    levels[result["level"]] = levels.get(result["level"], 0) + 1
print(f"wrote {REPORTS / 'shacl-results.sarif'}: {len(merged['runs'])} runs, "
      f"{len(results)} grouped results, levels={levels}")
write_summary(merged)
