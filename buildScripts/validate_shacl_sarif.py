"""SHACL validation of a ReliCapGrid instance with native SARIF 2.1.0 export.

Uses triplets >= 0.2.0a2, which exports SARIF directly (``.shacl.to_sarif``) —
the previous custom ``shacl_report_to_sarif.py`` converter is no longer needed.

Validates the Svedala EQ instance against the official ENTSO-E CGMES Equipment
SHACL (Simple = cardinality/datatype/valueType, Complex = cross-object sh:sparql).
Three issues are injected deliberately so code scanning shows error-level alerts
with exact source locations. Output: reports/shacl-results.sarif (repo-relative
artifact URIs so GitHub code scanning can map results to the file).

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

# EQ instance, path relative to the repo root (becomes the SARIF artifact URI)
EQ = "Instance/Svedala/Grid/cimxml/20220615T2230Z__Svedala_EQ_1.xml"

UPSTREAM_RAW = "https://raw.githubusercontent.com/entsoe/application-profiles-library/main/CGMES/SHACL"
SHACL_FILES = [
    "61970-600-2_Equipment-AP-Con-Simple-SHACL.ttl",   # cardinality, datatype, valueType
    "61970-301_Equipment-AP-Con-Complex-SHACL.ttl",    # cross-object sh:sparql rules
]


def entsoe_shapes():
    cache = REPO_ROOT / ".shacl_cache"
    cache.mkdir(exist_ok=True)
    for name in SHACL_FILES:
        if not (cache / name).exists():
            print(f"downloading {name}")
            urllib.request.urlretrieve(f"{UPSTREAM_RAW}/{name}", cache / name)
    return [str(cache / name) for name in SHACL_FILES]


print("triplets", triplets.__version__)
shapes = entsoe_shapes()

data = pandas.read_RDF([EQ])
print(f"parsed {len(data):,} triples from {Path(EQ).name}")

# Inject three issues so the report carries error-level results:
line = sorted(data.loc[(data["KEY"] == "Type") & (data["VALUE"] == "ACLineSegment"), "ID"])[0]
winding = sorted(data.loc[(data["KEY"] == "Type") & (data["VALUE"] == "PowerTransformerEnd"), "ID"])[0]
terminal = sorted(data.loc[(data["KEY"] == "Type") & (data["VALUE"] == "Terminal"), "ID"])[0]
substation = sorted(data.loc[(data["KEY"] == "Type") & (data["VALUE"] == "Substation"), "ID"])[0]

broken = data[~((data["ID"] == line) & (data["KEY"] == "IdentifiedObject.name"))].copy()  # 1: missing name
broken.loc[(broken["ID"] == winding) & (broken["KEY"] == "PowerTransformerEnd.ratedU"), "VALUE"] = "-400"  # 2: value range
broken.loc[(broken["ID"] == terminal) & (broken["KEY"] == "Terminal.ConductingEquipment"), "VALUE"] = substation  # 3: value type

violations = broken.shacl.validate(shapes, rdf_map=schemas.ENTSOE_CGMES_3_0_0_552_ED1)
print("severities:", violations["SEVERITY"].value_counts().to_dict())

enriched = violations.shacl.enrich(data=broken, shapes=shapes, rdf_map=schemas.ENTSOE_CGMES_3_0_0_552_ED1)
located = enriched.shacl.locate(sources=[EQ])

reports = REPO_ROOT / "reports"
reports.mkdir(exist_ok=True)
sarif_path = located.shacl.to_sarif(path=reports / "shacl-results.sarif")

# GitHub code scanning requires every result to carry at least one location.
# Some violations (e.g. a missing required property) have no source line — give
# them a file-level fallback location so the SARIF is accepted.
sarif = json.loads(Path(sarif_path).read_text())
run = sarif["runs"][0]
patched = 0
for result in run["results"]:
    if not result.get("locations"):
        result["locations"] = [{"physicalLocation": {
            "artifactLocation": {"uri": EQ}, "region": {"startLine": 1}}}]
        patched += 1
if patched:
    Path(sarif_path).write_text(json.dumps(sarif, indent=2))
    print(f"added file-level fallback location to {patched} result(s)")
print("wrote", sarif_path)
levels = {}
for r in run["results"]:
    levels[r["level"]] = levels.get(r["level"], 0) + 1
print(f"SARIF: {len(run['tool']['driver'].get('rules', []))} rules, "
      f"{len(run['results'])} results, levels={levels}")
