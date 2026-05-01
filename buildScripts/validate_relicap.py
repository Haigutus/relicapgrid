""" Author: kristjan.vilgo """
from pathlib import Path
import pandas
from triplets.cgmes_tools import get_dangling_references
import uuid

# ====================== CONFIGURATION ======================
BASE_PATH = Path("../test_data/relicapgrid")
INSTANCE_PATH = BASE_PATH / "Instance"
REPORT_FILENAME = "validation_report.xlsx"
NON_TSO_FOLDERS = {"boundaryData", "commonData", "referenceData", "NetworkCode", "Jotunheim"}
# ===========================================================

tsos = sorted([d.name for d in INSTANCE_PATH.iterdir() if d.is_dir() and d.name not in NON_TSO_FOLDERS])

xml_files = []

# 1. TSO EQ and NetworkCode files
for tso in tsos:
    xml_files.extend((INSTANCE_PATH / tso / "Grid" / "cimxml").glob("*_EQ_*.xml"))
    xml_files.extend((INSTANCE_PATH / tso / "NetworkCode" / "cimxml").glob("*.xml"))

# 2. Jotunheim Grid files (SSH, TP, SV)
xml_files.extend((INSTANCE_PATH / "Jotunheim" / "Grid" / "cimxml").glob("*.xml"))

# 3. Boundary files
xml_files.extend((INSTANCE_PATH / "boundaryData" / "Grid" / "cimxml").glob("*.xml"))

# 4. CommonData files (Grid and NetworkCode)
xml_files.append(INSTANCE_PATH / "commonData" / "Grid" / "cimxml" / "Grid_CommonData_CGM-CD.xml")
xml_files.append(INSTANCE_PATH / "commonData" / "NetworkCode" / "cimxml" / "Org-NineRealms_CD.xml")

# Final list: unique and sorted
xml_files = sorted(list(set(xml_files)))

print(f"Loading RDF from {len(xml_files)} files...")
data = pandas.read_RDF([str(f) for f in xml_files])

# Extract filename mapping
filename_mapping = data[data['KEY'] == 'label'][['INSTANCE_ID', 'VALUE']].rename(columns={'VALUE': 'Filename'})

# Extract profile mapping
profile_mapping = data[data['KEY'] == 'Model.profile'][['INSTANCE_ID', 'VALUE']].rename(columns={'VALUE': 'Profile'})

profile_mapping = data[data['KEY'] == 'conformsTo'][['INSTANCE_ID', 'VALUE']].rename(columns={'VALUE': 'Profile'})

# Start writing report
writer = pandas.ExcelWriter(REPORT_FILENAME)

# Record files used as input
pandas.DataFrame({"Loaded File Path": [str(f) for f in xml_files]}).to_excel(writer, sheet_name="Loaded Files", index=False)

# Check dangling references
print("Checking for dangling references...")
dangling = get_dangling_references(data, detailed=True)

if not dangling.empty:

    # Add file data
    dangling = dangling.merge(filename_mapping, left_on='INSTANCE_ID_FROM', right_on='INSTANCE_ID', how='left').drop(columns=['INSTANCE_ID'])

    # Filter out valid missing references
    dangling = dangling[dangling['KEY_FROM'] != 'Model.Supersedes']

    # Details
    dangling[['ID_FROM', 'KEY_FROM', 'VALUE_FROM', 'Filename']].to_excel(writer, sheet_name="Dangling References - Detailed", index=False)

    # Summary
    dangling.groupby("Filename")["KEY_FROM"].value_counts().reset_index(name='Count').to_excel(writer, sheet_name="Dangling References - Summary", index=False)

    print(f"\nFound {len(dangling)} dangling references. Report saved to {REPORT_FILENAME}")

else:
    print("No dangling references found.")


# Check duplicated ID-s

ids = data.query("KEY == 'Type'")

duplicates = ids[ids.ID.duplicated(keep=False)].sort_values(by="ID")



writer.close()



