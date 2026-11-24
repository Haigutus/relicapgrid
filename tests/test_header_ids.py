"""Every instance file has its own header ID.

The header (md:FullModel, md:DifferenceModel or dcat:Dataset) names the dataset.
IEC 61970-552 and the dataset metadata profile require that name to be unique: a
tool that keys a dataset by its header ID merges two files that share one.
"""
from pathlib import Path

import pandas
import pytest
import triplets  # noqa: F401  (registers pandas.read_RDF)

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTANCE_DIR = REPO_ROOT / "Instance"

HEADER_TYPES = ["FullModel", "DifferenceModel", "Dataset"]


def shared_header_ids(data):
    """Header ID, file for each header ID that more than one file uses."""
    headers = data[(data["KEY"] == "Type") & data["VALUE"].isin(HEADER_TYPES)][["ID", "INSTANCE_ID"]]
    files = data[data["KEY"] == "label"][["INSTANCE_ID", "VALUE"]].rename(columns={"VALUE": "File"})
    headers = headers.merge(files, on="INSTANCE_ID")
    shared = headers[headers["ID"].duplicated(keep=False)]
    return shared.rename(columns={"ID": "Header ID"})[["Header ID", "File"]].sort_values(["Header ID", "File"])


def test_header_ids_are_unique():
    """No two instance files share a header ID."""
    data = pandas.read_RDF([str(path) for path in sorted(INSTANCE_DIR.rglob("*.xml"))])
    shared = shared_header_ids(data)
    if not shared.empty:
        shared["File"] = shared["File"].map(lambda path: str(Path(path).relative_to(REPO_ROOT)))
        pytest.fail(f"**{shared['Header ID'].nunique()} header IDs are used by more than one file:**\n\n"
                    f"{shared.to_markdown(index=False)}\n\n"
                    "Give each file its own header ID (a new UUID).")


HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:md="http://iec.ch/TC57/61970-552/ModelDescription/1#"
         xmlns:dcat="http://www.w3.org/ns/dcat#">
  {header}
</rdf:RDF>
"""


def test_shared_header_id_detection(tmp_path):
    """Negative test: the same ID in two files is found, whatever its form and header class."""
    files = {
        "a.xml": '<md:FullModel rdf:about="urn:uuid:6b3e2c8a-51f0-4c1d-9d2e-7a40c3e1d00b"/>',
        "b.xml": '<dcat:Dataset rdf:about="urn:uuid:6b3e2c8a-51f0-4c1d-9d2e-7a40c3e1d00b"/>',
        "c.xml": '<md:FullModel rdf:about="#_6b3e2c8a-51f0-4c1d-9d2e-7a40c3e1d00b"/>',
        "d.xml": '<md:FullModel rdf:about="urn:uuid:0d4f7a52-93b1-4e2c-8a6f-5c1e2b3d4f60"/>',
        "e.xml": "",
    }
    for name, header in files.items():
        (tmp_path / name).write_text(HEADER.format(header=header))
    data = pandas.read_RDF([str(path) for path in sorted(tmp_path.glob("*.xml"))])
    shared = shared_header_ids(data)
    assert list(shared["Header ID"]) == ["6b3e2c8a-51f0-4c1d-9d2e-7a40c3e1d00b"] * 3
    assert [Path(path).name for path in shared["File"]] == ["a.xml", "b.xml", "c.xml"]
