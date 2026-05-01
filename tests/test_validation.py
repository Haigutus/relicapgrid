""" Author: kristjan.vilgo """

print("Loading test script...")
import sys
from pathlib import Path
import pandas
import pytest
from triplets.cgmes_tools import get_dangling_references

# Add buildScripts to path to reuse create_cgm_zip
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT / "buildScripts"))
from create_cgm_zip import discover_tsos, collect_cgm_files

INSTANCE_DIR = REPO_ROOT / "Instance"

@pytest.fixture(scope="module")
def grid_data():
    tsos = discover_tsos(INSTANCE_DIR)
    print(f"Discovered TSOs: {tsos}")
    files, missing = collect_cgm_files(INSTANCE_DIR, tsos, include_ncp=True)
    if missing:
        print(f"Missing files: {missing}")
    xml_files = [str(f) for f, _ in files]
    print(f"Loading {len(xml_files)} files...")
    data = pandas.read_RDF(xml_files)
    print("Data loaded successfully.")
    return data

def test_dangling_references(grid_data):
    print("Checking for dangling references...")



    # Get detailed dangling references
    dangling = get_dangling_references(grid_data, detailed=True)
    
    if not dangling.empty:

        # Filename mapping
        filename_mapping = grid_data[grid_data['KEY'] == 'label'][['INSTANCE_ID', 'VALUE']].rename(columns={'VALUE': 'Filename'})

        dangling = dangling.merge(filename_mapping, left_on='INSTANCE_ID_FROM', right_on='INSTANCE_ID', how='left').drop(columns=['INSTANCE_ID'])

        # Filter out valid missing references or references to profiles not loaded
        to_ignore = [
            'Model.Supersedes',
        ]
        dangling = dangling[~dangling['KEY_FROM'].isin(to_ignore)]

    if not dangling.empty:
        summary = dangling.groupby("Filename")["KEY_FROM"].value_counts().reset_index(name='Count')
        message = f"Found {len(dangling)} dangling references:\n{summary.to_string(index=False)}"
        assert dangling.empty, message

def test_duplicate_ids(grid_data):
    print("Checking for duplicated IDs...")
    ids = grid_data.query("KEY == 'Type'")
    
    # Check for IDs that have more than one distinct type
    # We allow 'Equipment' or 'Dataset' as a generic type if a more specific one exists
    def get_distinct_types(types):
        unique_types = set(types)
        if len(unique_types) > 1:
            for generic in ['Equipment', 'Dataset']:
                if generic in unique_types:
                    unique_types.remove(generic)
        return list(unique_types)

    type_counts = ids.groupby('ID')['VALUE'].apply(get_distinct_types)
    inconsistent_ids = type_counts[type_counts.apply(len) > 1]
    
    if not inconsistent_ids.empty:
        # Prepare a readable summary of inconsistent types
        details = ids[ids.ID.isin(inconsistent_ids.index)].sort_values("ID")
        summary = details.groupby(['ID', 'VALUE']).size().reset_index(name='count')
        assert inconsistent_ids.empty, f"Found {len(inconsistent_ids)} IDs with inconsistent types:\n{summary.to_string(index=False)}"
