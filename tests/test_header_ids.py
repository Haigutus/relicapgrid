"""Every instance file has its own header ID.

The header (md:FullModel or dcat:Dataset) names the dataset. IEC 61970-552 and
the dataset metadata profile require that name to be unique: a tool that keys a
dataset by its header ID merges two files that share one.
"""
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import pandas
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTANCE_DIR = REPO_ROOT / "Instance"

RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
HEADER_TAGS = {
    "{http://iec.ch/TC57/61970-552/ModelDescription/1#}FullModel",
    "{http://iec.ch/TC57/61970-552/DifferenceModel/1#}DifferenceModel",
    "{http://www.w3.org/ns/dcat#}Dataset",
}


def header_id(source):
    """The rdf:about of the file's header element, as a bare ID (no urn:uuid:, #, _); None without one."""
    for _, element in ET.iterparse(source, events=("start",)):
        if element.tag in HEADER_TAGS:
            about = element.get(f"{RDF}about") or element.get(f"{RDF}ID") or ""
            for prefix in ("urn:uuid:", "#", "_"):
                about = about.removeprefix(prefix)
            return about or None
    return None


def shared_header_ids(files):
    """{header ID: [files]} for the IDs more than one file uses."""
    owners = defaultdict(list)
    for file in files:
        identifier = header_id(file)
        if identifier:
            owners[identifier].append(file)
    return {identifier: names for identifier, names in owners.items() if len(names) > 1}


def test_header_ids_are_unique():
    """No two instance files share a header ID."""
    files = sorted(INSTANCE_DIR.rglob("*.xml"))
    shared = shared_header_ids(files)
    if shared:
        table = pandas.DataFrame(
            [(identifier, str(file.relative_to(REPO_ROOT))) for identifier, names in sorted(shared.items())
             for file in names],
            columns=["Header ID", "File"]).to_markdown(index=False)
        pytest.fail(f"**{len(shared)} header IDs are used by more than one file:**\n\n{table}\n\n"
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
    shared = shared_header_ids(sorted(tmp_path.glob("*.xml")))
    assert {identifier: [file.name for file in names] for identifier, names in shared.items()} == {
        "6b3e2c8a-51f0-4c1d-9d2e-7a40c3e1d00b": ["a.xml", "b.xml", "c.xml"]}
