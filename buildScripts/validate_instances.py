"""PROF-driven SHACL validation of all CGMES and NC instance files.

Every Instance/**/*.xml is mapped to its SHACL shape set through the DX-PROF
descriptors of the ENTSO-E application-profiles-library (see prof_map.py):
CGMES files by their md:Model.profile header, NC files by dcterms:conformsTo.

Validation runs in groups so cross-file references resolve instead of raising
false dangling-reference errors: CGMES per area (EQ+SSH+TP+SV with the boundary
files as context), the Jotunheim CGM as a full assembly, and NC files per area
with the area's Grid files as context. Context files are loaded but their
violations are reported only in their own group.

One grouped SARIF per release (single run, one code-scanning category each)
plus full sh:ValidationReports (turtle + RDF/XML) per group in reports/.

Run from the repo root:
    uv run buildScripts/validate_instances.py --apl cgmes-3.0=.apl-main --apl ncp-2.4=.apl-ncp24
"""
import argparse
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

import pandas
import triplets
from triplets.export_schema import schemas

from prof_map import build_prof_map

logging.getLogger("triplets.validation").setLevel(logging.ERROR)

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)  # keep SARIF artifactLocation URIs repo-relative
REPORTS = REPO_ROOT / "reports"
LEVEL_ICONS = {"error": "🔴", "warning": "🟠", "note": "🔵"}

RELEASES = {
    "cgmes-3.0": {"apl": ".apl-main", "kind": "cgmes", "rdf_map": schemas.ENTSOE_CGMES_3_0_0_552_ED1},
    "ncp-2.4": {"apl": ".apl-ncp24", "kind": "nc", "rdf_map": schemas.ENTSOE_NC_2_4_1_552_ED1},
    # "ncp-2.5": add once triplets ships an NC 2.5 export schema (rdf_map)
    # "cgmes-2.4": add once the APL publishes its PROF + SHACL
}

# Cross-cutting CGMES shapes referenced by no PROF descriptor (APL gap).
# IdentifiedObjectCommon is deliberately NOT added: its mRID/name maxCount
# checks assume a single profile dataset and false-fire on the legal
# rdf:about continuation between EQ and SSH/TP/SV in a model-set frame.
CGMES_COMMON_SHACL = [
    "CGMES/SHACL/61970-600-1_AllProfiles-AP-Con-Complex-SHACL.ttl",
]

# Near-duplicates of Instance/Jotunheim/GridSituation/cimxml/ (kept dir wins)
DUPLICATE_GLOB = "Instance/Jotunheim/NetworkCode/*.xml"


@dataclass
class FileInfo:
    path: str                 # repo-relative posix
    instance_id: str
    kind: str                 # "cgmes" | "nc" | "unknown"
    profile_uris: list
    area: str                 # Instance/<area>/...


@dataclass
class Group:
    name: str
    files: list               # FileInfo loaded into the frame (incl. context)
    report_paths: set         # paths whose violations are reported
    shapes: list              # resolved shape Paths
    rdf_map: object


def scan_instances():
    """Parse every instance file once; classify by header profile declaration."""
    everything = sorted(str(p.relative_to(REPO_ROOT)) for p in REPO_ROOT.glob("Instance/**/*.xml"))
    duplicates = {p for p in everything if Path(p).match(DUPLICATE_GLOB)}
    files = [p for p in everything if p not in duplicates]
    skipped = [(p, "duplicate of GridSituation/cimxml") for p in sorted(duplicates)]

    frame = pandas.read_RDF(files, max_workers=os.cpu_count())

    labels = frame[frame["KEY"] == "label"][["INSTANCE_ID", "VALUE"]]
    path_by_instance = {row.INSTANCE_ID: str(Path(row.VALUE).resolve().relative_to(REPO_ROOT))
                        for row in labels.itertuples()}

    # INSTANCE_ID is arrow-dictionary-typed: groupby would emit every dictionary
    # value (also unmatched ones) regardless of observed=, so group on plain str
    profiles = frame[frame["KEY"] == "Model.profile"].astype({"INSTANCE_ID": str})
    cgmes = profiles.groupby("INSTANCE_ID")["VALUE"].apply(list)
    conforms = frame[(frame["KEY"] == "conformsTo")
                     & frame["VALUE"].str.startswith("https://ap.cim4.eu/")].astype({"INSTANCE_ID": str})
    nc = conforms.groupby("INSTANCE_ID")["VALUE"].apply(lambda v: sorted(set(v)))

    infos = []
    for instance_id, path in sorted(path_by_instance.items(), key=lambda item: item[1]):
        area = Path(path).parts[1]
        if instance_id in cgmes.index:
            infos.append(FileInfo(path, instance_id, "cgmes", cgmes[instance_id], area))
        elif instance_id in nc.index:
            infos.append(FileInfo(path, instance_id, "nc", nc[instance_id], area))
        else:
            skipped.append((path, "no application profile declared"))
    return frame, infos, skipped


def resolve_shapes(profile_uris, prof_map):
    """(shape paths, unmapped uris) for a set of declared profile URIs."""
    shapes, unmapped = set(), []
    for uri in profile_uris:
        profile = prof_map.get(uri)
        if profile is None:
            unmapped.append(uri)
        else:
            shapes.update(profile.shacl_paths)
    return sorted(shapes), unmapped


def build_cgmes_groups(infos, prof_map, apl_dir, rdf_map):
    grid = [fi for fi in infos if fi.kind == "cgmes"]
    boundary = [fi for fi in grid if fi.area in ("boundaryData", "commonData")]
    jotunheim = [fi for fi in grid if fi.area == "Jotunheim"]
    areas = sorted({fi.area for fi in grid} - {"boundaryData", "commonData", "Jotunheim"})

    all_uris = sorted({uri for fi in grid for uri in fi.profile_uris})
    shapes, unmapped = resolve_shapes(all_uris, prof_map)
    if unmapped:
        raise SystemExit(f"unmapped CGMES Model.profile URIs (APL PROF broken?): {unmapped}")
    shapes = sorted(set(shapes) | {apl_dir / rel for rel in CGMES_COMMON_SHACL if (apl_dir / rel).exists()})
    # the EquipmentBoundary shapes (pulled in via the EQ PROF) constrain
    # Terminal/ConnectivityNode to the boundary-legal classes — they only
    # apply to boundary datasets, not to full equipment models
    model_shapes = [p for p in shapes if "EquipmentBoundary" not in p.name]

    groups = []
    for area in areas:
        area_files = [fi for fi in grid if fi.area == area]
        groups.append(Group(f"cgmes-{area}", area_files + boundary,
                            {fi.path for fi in area_files}, model_shapes, rdf_map))
    groups.append(Group("cgmes-boundary", boundary, {fi.path for fi in boundary}, shapes, rdf_map))

    eq_files = [fi for fi in grid if fi.profile_uris[0].startswith("http://iec.ch/TC57/ns/CIM/CoreEquipment")
                and fi.area not in ("Jotunheim",)]
    groups.append(Group("cgmes-CGM-Jotunheim", jotunheim + eq_files + [fi for fi in boundary if fi not in eq_files],
                        {fi.path for fi in jotunheim}, model_shapes, rdf_map))
    return groups, []


def build_nc_groups(infos, prof_map, rdf_map):
    nc = [fi for fi in infos if fi.kind == "nc"]
    grid = [fi for fi in infos if fi.kind == "cgmes"]
    groups, skipped = [], []

    def area_name(fi):
        return "Jotunheim-GridSituation" if (fi.area, Path(fi.path).parts[2]) == ("Jotunheim", "GridSituation") else fi.area

    for area in sorted({area_name(fi) for fi in nc}):
        area_files = [fi for fi in nc if area_name(fi) == area]
        mapped, area_uris = [], set()
        for fi in area_files:
            shapes, unmapped = resolve_shapes(fi.profile_uris, prof_map)
            if unmapped:
                skipped.append((fi.path, f"unmapped profile URI: {', '.join(unmapped)}"))
            else:
                mapped.append(fi)
                area_uris.update(fi.profile_uris)
        if not mapped:
            continue
        shapes, _ = resolve_shapes(sorted(area_uris), prof_map)
        base_area = area.split("-GridSituation")[0]
        context = [fi for fi in grid if fi.area in (base_area, "boundaryData", "commonData")]
        groups.append(Group(f"nc-{area}", mapped + context, {fi.path for fi in mapped}, shapes, rdf_map))
    return groups, skipped


def validate_group(frame, group, compiled_cache):
    key = tuple(str(p) for p in group.shapes)
    if key not in compiled_cache:
        compiled_cache[key] = triplets.validation.compile([str(p) for p in group.shapes])
    compiled = compiled_cache[key]

    ids = {fi.instance_id for fi in group.files}
    data = frame[frame["INSTANCE_ID"].isin(ids)]
    violations = data.shacl.validate(compiled, rdf_map=group.rdf_map)
    if violations.empty:
        return violations, violations
    enriched = violations.shacl.enrich(data=data, shapes=compiled, rdf_map=group.rdf_map)
    located = enriched.shacl.locate(sources=[fi.path for fi in group.files])
    located["GROUP"] = group.name

    reported = located[located["SOURCE_URI"].isin(group.report_paths) | located["SOURCE_URI"].isna()].copy()
    # shape-level meta findings (e.g. triplets:invalidSparql) have no instance
    # line — anchor them to the group's first reported file so GitHub accepts them
    anchor = sorted(group.report_paths)[0]
    reported.loc[reported["SOURCE_URI"].isna(), "SOURCE_LINE"] = 1
    reported.loc[reported["SOURCE_URI"].isna(), "SOURCE_URI"] = anchor
    return located, reported


def export_release(release, frames):
    combined = pandas.concat([f for f in frames if not f.empty], ignore_index=True) if frames else pandas.DataFrame()
    if combined.empty:
        return None
    meta = combined["VIOLATION_TYPE"].astype(str).str.contains("invalidSparql")
    combined = pandas.concat([combined[~meta],
                              combined[meta].drop_duplicates(subset=["VIOLATION_TYPE", "MESSAGE", "SOURCE_SHAPE"])],
                             ignore_index=True)
    sarif_path = combined.shacl.to_sarif(path=REPORTS / f"shacl-{release}.sarif")

    # shape-level meta findings are exported without locations; GitHub needs
    # one per result — anchor them to the file recorded on the frame row
    anchors = combined.dropna(subset=["SOURCE_URI"]).drop_duplicates("SOURCE_SHAPE").set_index("SOURCE_SHAPE")["SOURCE_URI"]
    sarif = json.loads(Path(sarif_path).read_text())
    for result in sarif["runs"][0]["results"]:
        if not result.get("locations"):
            uri = anchors.get(str((result.get("properties") or {}).get("sourceShape")), anchors.iloc[0])
            result["locations"] = [{"physicalLocation": {
                "artifactLocation": {"uri": uri}, "region": {"startLine": 1, "endLine": 1}}}]
    Path(sarif_path).write_text(json.dumps(sarif, indent=2))
    return sarif


def write_summary(release_sarifs, group_stats, skipped, gaps):
    lines = ["# SHACL validation — PROF-driven full sweep", ""]
    repo, branch = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_REF_NAME")
    if repo and branch:
        alerts = f"https://github.com/{repo}/security/code-scanning?query=is%3Aopen+branch%3A{branch}+tool%3A%22triplets-shacl%22"
        lines += [f"**[Open the code scanning alerts of this branch →]({alerts})**", "",
                  "Full sh:ValidationReports (turtle + RDF/XML) per group are attached as the `shacl-reports` artifact.", ""]

    lines += ["| group | files | errors | warnings | notes |", "|---|---|---|---|---|"]
    for name, file_count, severities in group_stats:
        lines.append(f"| `{name}` | {file_count} | {severities.get('Violation', 0)} | "
                     f"{severities.get('Warning', 0)} | {severities.get('Info', 0)} |")

    for release, sarif in release_sarifs.items():
        if sarif is None:
            continue
        lines += ["", f"## {release} rules (grouped)", "", "| rule | level | occurrences |", "|---|---|---|"]
        for result in sarif["runs"][0]["results"]:
            icon = LEVEL_ICONS.get(result["level"], "")
            count = result.get("occurrenceCount", len(result.get("locations", [])))
            lines.append(f"| `{result['ruleId']}` | {icon} {result['level']} | {count} |")

    if skipped:
        lines += ["", "## Skipped files", "", "| file | reason |", "|---|---|"]
        lines += [f"| `{path}` | {reason} |" for path, reason in skipped]
    if gaps:
        lines += ["", "## Profile library gaps", ""]
        lines += [f"- {gap}" for gap in sorted(set(gaps))]
    lines += ["", "Notes: the cross-cutting AllProfiles shapes are added manually (no PROF references them); "
              "IdentifiedObjectCommon is excluded (its per-dataset cardinality checks false-fire on rdf:about "
              "continuation in model-set frames); EquipmentBoundary shapes run only on the boundary group; "
              "variant shape sets (SolvedMAS/NotSolvedMAS, CrossProfile, InverseAssociation; role/validation) are not run."]
    (REPORTS / "summary.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apl", action="append", default=[], metavar="RELEASE=PATH",
                        help="APL checkout per release, e.g. cgmes-3.0=.apl-main (repeatable)")
    parser.add_argument("--only", choices=sorted(RELEASES), help="run a single release")
    args = parser.parse_args()
    for override in args.apl:
        release, _, path = override.partition("=")
        RELEASES[release]["apl"] = path

    print("triplets", triplets.__version__)
    REPORTS.mkdir(exist_ok=True)
    frame, infos, skipped = scan_instances()
    print(f"parsed {len(frame):,} triples from {len(infos)} mapped files ({len(skipped)} skipped)")

    compiled_cache, group_stats, release_sarifs, all_gaps = {}, [], {}, []
    for release, config in RELEASES.items():
        if args.only and release != args.only:
            continue
        apl_dir = Path(config["apl"]).resolve()
        prof_map, gaps = build_prof_map(apl_dir)
        all_gaps += [f"{release}: {g}" for g in gaps]
        if not prof_map:
            raise SystemExit(f"{release}: empty PROF map at {apl_dir}")

        if config["kind"] == "cgmes":
            groups, more_skipped = build_cgmes_groups(infos, prof_map, apl_dir, config["rdf_map"])
        else:
            groups, more_skipped = build_nc_groups(infos, prof_map, config["rdf_map"])
        skipped += more_skipped

        frames = []
        for group in groups:
            located, reported = validate_group(frame, group, compiled_cache)
            severities = reported["SEVERITY"].value_counts().to_dict() if len(reported) else {}
            group_stats.append((group.name, len(group.report_paths), severities))
            print(f"{group.name}: {len(group.report_paths)} files, {severities or 'conforms'}")
            if len(located):  # full unfiltered report incl. context-file findings
                for suffix in ("ttl", "xml"):
                    located.shacl.to_shacl_report(
                        path=REPORTS / f"{group.name}-shacl-report.{suffix}", report_source=group.name,
                        report_references=[p.name for p in group.shapes])
            frames.append(reported)
        release_sarifs[release] = export_release(release, frames)

    write_summary(release_sarifs, group_stats, skipped, all_gaps)
    for release, sarif in release_sarifs.items():
        if sarif:
            results = sarif["runs"][0]["results"]
            print(f"wrote reports/shacl-{release}.sarif: {len(results)} grouped results")
    print(f"wrote {REPORTS / 'summary.md'}")


if __name__ == "__main__":
    main()
