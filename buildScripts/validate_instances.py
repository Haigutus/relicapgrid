"""PROF-driven SHACL validation of all CGMES and NC instance files.

Every Instance/**/*.xml is mapped to its SHACL shape set through the DX-PROF
descriptors of the ENTSO-E application-profiles-library (see prof_map.py):
CGMES files by their md:Model.profile header, NC files by dcterms:conformsTo.

Two validation passes per group, matching the two kinds of shapes:
  * per-dataset — the profile's Simple shapes (cardinality, datatypes,
    in-file valueType) run per instance file via scope=, so the legal
    rdf:about continuation across a model set never counts double;
  * union — Complex / AllProfiles shapes run on the group frame, where
    cross-file references resolve (CGMES per area with boundary context,
    the Jotunheim CGM as a full assembly, NC per area with the area's
    Grid files as context). Context files are loaded but their violations
    are reported only in their own group.

One grouped SARIF per release (single run, one code-scanning category each)
plus full sh:ValidationReports (turtle + RDF/XML) per group in reports/.

Run from the repo root:
    uv run buildScripts/validate_instances.py --apl cgmes-3.0=.apl-main --apl ncp-2.4=.apl-ncp24
"""
import argparse
import json
import logging
import os
import time
from dataclasses import dataclass
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

# Cross-cutting CGMES shapes referenced by no PROF descriptor (APL gap, filed
# as application-profiles-library#130)
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
    union_shapes: list        # Complex/AllProfiles shapes, run on the group frame
    dataset_shapes: dict      # instance_id -> [Simple shapes], run with scope=
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


def is_dataset_shape(path):
    """Simple shapes check per-dataset conformance (cardinality, datatypes)."""
    return "-Con-Simple-" in path.name or path.name == "DatasetMetadata-AP-Con-SHACL.ttl"


def drop_boundary(paths):
    """EquipmentBoundary shapes (bundled into the EQ PROF) constrain Terminal/
    ConnectivityNode to boundary-legal classes — boundary datasets only."""
    return [p for p in paths if "EquipmentBoundary" not in p.name]


def shape_split(files, prof_map, keep_boundary=False):
    """(union_shapes, dataset_shapes, unmapped) for a set of reported files.

    union_shapes = everything (reference checks need the full group frame);
    dataset_shapes = the file's own Simple shapes, re-run per file with scope=
    for the cardinality constraints (see validate_group)."""
    union, dataset, unmapped = set(), {}, {}
    for fi in files:
        shapes, missing = resolve_shapes(fi.profile_uris, prof_map)
        if missing:
            unmapped[fi.path] = missing
            continue
        if not keep_boundary:
            shapes = drop_boundary(shapes)
        dataset[fi.instance_id] = [p for p in shapes if is_dataset_shape(p)]
        union.update(shapes)
    return sorted(union), dataset, unmapped


def build_cgmes_groups(infos, prof_map, apl_dir, rdf_map):
    grid = [fi for fi in infos if fi.kind == "cgmes"]
    boundary = [fi for fi in grid if fi.area in ("boundaryData", "commonData")]
    jotunheim = [fi for fi in grid if fi.area == "Jotunheim"]
    areas = sorted({fi.area for fi in grid} - {"boundaryData", "commonData", "Jotunheim"})

    common = [apl_dir / rel for rel in CGMES_COMMON_SHACL if (apl_dir / rel).exists()]

    def cgmes_group(name, reported, context):
        union, dataset, unmapped = shape_split(reported, prof_map, keep_boundary=(name == "cgmes-boundary"))
        if unmapped:
            raise SystemExit(f"unmapped CGMES Model.profile URIs (APL PROF broken?): {unmapped}")
        return Group(name, reported + context, {fi.path for fi in reported},
                     sorted(set(union) | set(common)), dataset, rdf_map)

    groups = [cgmes_group(f"cgmes-{area}", [fi for fi in grid if fi.area == area], boundary)
              for area in areas]
    groups.append(cgmes_group("cgmes-boundary", boundary, []))

    eq_files = [fi for fi in grid if fi.profile_uris[0].startswith("http://iec.ch/TC57/ns/CIM/CoreEquipment")
                and fi.area != "Jotunheim"]
    groups.append(cgmes_group("cgmes-CGM-Jotunheim", jotunheim, eq_files))
    return groups, []


def build_nc_groups(infos, prof_map, rdf_map):
    nc = [fi for fi in infos if fi.kind == "nc"]
    grid = [fi for fi in infos if fi.kind == "cgmes"]
    groups, skipped = [], []

    def area_name(fi):
        return "Jotunheim-GridSituation" if (fi.area, Path(fi.path).parts[2]) == ("Jotunheim", "GridSituation") else fi.area

    for area in sorted({area_name(fi) for fi in nc}):
        area_files = [fi for fi in nc if area_name(fi) == area]
        union, dataset, unmapped = shape_split(area_files, prof_map)
        skipped += [(path, f"unmapped profile URI: {', '.join(uris)}") for path, uris in unmapped.items()]
        mapped = [fi for fi in area_files if fi.path not in unmapped]
        if not mapped:
            continue
        base_area = area.split("-GridSituation")[0]
        context = [fi for fi in grid if fi.area in (base_area, "boundaryData", "commonData")]
        groups.append(Group(f"nc-{area}", mapped + context, {fi.path for fi in mapped},
                            union, dataset, rdf_map))
    return groups, skipped


CARDINALITY = ("sh:minCount", "sh:maxCount")


def validate_group(frame, group):
    data = frame[frame["INSTANCE_ID"].isin({fi.instance_id for fi in group.files})]

    # reference checks need the group frame; cardinality must not see the
    # rdf:about continuation of other files, so it comes from per-file scope=.
    # Dataset shapes run one shape FILE at a time: several Simple files
    # re-declare the same IdentifiedObject property shapes, and the merged
    # shapes graph double-counts values (triplets cardinality bug, reported).
    union = data.shacl.validate(group.union_shapes, rdf_map=group.rdf_map)
    passes = [union[~union["VIOLATION_TYPE"].isin(CARDINALITY)] if len(union) else union]
    for instance_id, shapes in group.dataset_shapes.items():
        for shape in shapes:
            per_file = data.shacl.validate([shape], rdf_map=group.rdf_map, scope=[instance_id])
            if len(per_file):
                passes.append(per_file[per_file["VIOLATION_TYPE"].isin(CARDINALITY)])
    violations = pandas.concat([v for v in passes if len(v)], ignore_index=True) if any(len(v) for v in passes) \
        else passes[0]
    if violations.empty:
        return violations, violations
    # duplicated statements (rdf:about continuation) yield identical violation
    # rows from the union pass — one finding per fact
    violations = violations.drop_duplicates(subset=["ID", "KEY", "VALUE", "VIOLATION_TYPE", "SOURCE_SHAPE"])

    all_shapes = sorted({str(p) for p in group.union_shapes}
                        | {str(p) for shapes in group.dataset_shapes.values() for p in shapes})
    enriched = violations.shacl.enrich(data=data, shapes=all_shapes, rdf_map=group.rdf_map)
    located = enriched.shacl.locate(sources=[fi.path for fi in group.files])
    located["GROUP"] = group.name

    reported = located[located["SOURCE_URI"].isin(group.report_paths) | located["SOURCE_URI"].isna()].copy()
    # shape-level meta findings (e.g. triplets:invalidSparql) get anchored to
    # the group's first reported file — an in-repo path GitHub can display
    # (rc3's native fallback points at the shapes file, which is not in-repo)
    anchor = sorted(group.report_paths)[0]
    reported.loc[reported["SOURCE_URI"].isna(), "SOURCE_LINE"] = 1
    reported.loc[reported["SOURCE_URI"].isna(), "SOURCE_URI"] = anchor
    return located, reported


def profile_name(uri):
    parts = [s for s in str(uri).split("/") if s]
    return parts[-2] if len(parts) >= 2 else None


def build_schema_index(rdf_map_path):
    """Index the export schema's profile sections by versionIRI and by profile
    name segment (the NC map uses ap-voc.cim4.eu, instance data ap.cim4.eu)."""
    doc = json.loads(Path(rdf_map_path).read_text())
    index = {}
    for keyword, section in doc.items():
        version_iri = section.get("ProfileMetadata", {}).get("versionIRI", "")
        index[version_iri] = keyword
        if profile_name(version_iri):
            index[profile_name(version_iri)] = keyword
    return doc, index


def run_schema_pass(frame, infos, config, release):
    """Schema conformance per instance file: the file's own profile section of
    the export schema, evaluated with scope= (per-dataset semantics). Complements
    the SHACL layers with a shapes-independent check straight from the schema."""
    doc, index = build_schema_index(config["rdf_map"])
    files, frames, skipped = [], [], []
    for fi in [f for f in infos if f.kind == config["kind"]]:
        keyword = next((index.get(uri) or index.get(profile_name(uri)) for uri in fi.profile_uris), None)
        if keyword is None:
            skipped.append((fi.path, f"{release}: no schema section for declared profile"))
            continue
        violations = frame.shacl.validate_schema({keyword: doc[keyword]}, scope=[fi.instance_id])
        if len(violations):
            frames.append(violations)
        files.append(fi)

    if not frames:
        return None, files, skipped
    combined = pandas.concat(frames, ignore_index=True)
    located = combined.shacl.locate(sources=[fi.path for fi in files])
    sarif_path = located.shacl.to_sarif(path=REPORTS / f"schema-{release}.sarif")
    return json.loads(Path(sarif_path).read_text()), files, skipped


def export_release(release, frames):
    combined = pandas.concat([f for f in frames if not f.empty], ignore_index=True) if frames else pandas.DataFrame()
    if combined.empty:
        return None
    meta = combined["VIOLATION_TYPE"].astype(str).str.contains("invalidSparql")
    combined = pandas.concat([combined[~meta],
                              combined[meta].drop_duplicates(subset=["VIOLATION_TYPE", "MESSAGE", "SOURCE_SHAPE"])],
                             ignore_index=True)
    sarif_path = combined.shacl.to_sarif(path=REPORTS / f"shacl-{release}.sarif")
    return json.loads(Path(sarif_path).read_text())


def write_summary(release_sarifs, group_stats, skipped, gaps):
    lines = ["# SHACL validation — PROF-driven full sweep", ""]
    repo, branch = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_REF_NAME")
    if repo and branch:
        alerts = f"https://github.com/{repo}/security/code-scanning?query=is%3Aopen+branch%3A{branch}+tool%3A%22triplets-shacl%22"
        lines += [f"**[Open the code scanning alerts of this branch →]({alerts})**", "",
                  "Full sh:ValidationReports (turtle + RDF/XML) per group are attached as the `shacl-reports` artifact.", ""]

    lines += ["| group | files | errors | warnings | notes | seconds |", "|---|---|---|---|---|---|"]
    for name, file_count, severities, seconds in group_stats:
        lines.append(f"| `{name}` | {file_count} | {severities.get('Violation', 0)} | "
                     f"{severities.get('Warning', 0)} | {severities.get('Info', 0)} | {seconds:.1f} |")

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
    lines += ["", "Notes: Simple shapes run per instance file (scope=) so rdf:about continuation across a "
              "model set is not double-counted; Complex/AllProfiles shapes run on the group frame; "
              "EquipmentBoundary shapes run only on the boundary group; the cross-cutting AllProfiles "
              "shapes are added manually (no PROF references them); variant shape sets "
              "(SolvedMAS/NotSolvedMAS, CrossProfile, InverseAssociation; role/validation) are not run."]
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

    group_stats, release_sarifs, all_gaps = [], {}, []
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
            start = time.monotonic()
            located, reported = validate_group(frame, group)
            seconds = time.monotonic() - start
            severities = reported["SEVERITY"].value_counts().to_dict() if len(reported) else {}
            group_stats.append((group.name, len(group.report_paths), severities, seconds))
            print(f"{group.name}: {len(group.report_paths)} files, {seconds:.1f}s, {severities or 'conforms'}")
            if len(located):  # full unfiltered report incl. context-file findings
                for suffix in ("ttl", "xml"):
                    located.shacl.to_shacl_report(
                        path=REPORTS / f"{group.name}-shacl-report.{suffix}", report_source=group.name,
                        report_references=sorted({p.name for p in group.union_shapes}
                                                 | {p.name for s in group.dataset_shapes.values() for p in s}))
            frames.append(reported)
        release_sarifs[release] = export_release(release, frames)

        start = time.monotonic()
        schema_sarif, schema_files, schema_skipped = run_schema_pass(frame, infos, config, release)
        skipped += schema_skipped
        if schema_sarif:
            release_sarifs[f"schema-{release}"] = schema_sarif
            counts = {}
            for result in schema_sarif["runs"][0]["results"]:
                level = {"error": "Violation", "warning": "Warning", "note": "Info"}[result["level"]]
                counts[level] = counts.get(level, 0) + result.get("occurrenceCount", 1)
            group_stats.append((f"schema-{release}", len(schema_files), counts, time.monotonic() - start))
            print(f"schema-{release}: {len(schema_files)} files, {time.monotonic() - start:.1f}s, {counts}")

    write_summary(release_sarifs, group_stats, skipped, all_gaps)
    for key, sarif in release_sarifs.items():
        if sarif:
            name = key if key.startswith("schema-") else f"shacl-{key}"
            print(f"wrote reports/{name}.sarif: {len(sarif['runs'][0]['results'])} grouped results")
    print(f"wrote {REPORTS / 'summary.md'}")


if __name__ == "__main__":
    main()
