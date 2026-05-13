# DLR_UC1: Dynamic Line Rating for BO-Line_2

## Description
This use case demonstrates **Dynamic Line Rating (DLR)** by creating time-varying
PATL values for the Belgovia-Galia cross-border tie line BO-Line_2.

DLR provides additional transfer capacity by calculating real-time thermal limits
based on weather conditions (wind speed, ambient temperature). The dynamic rating
is always at or above the static PATL baseline, unlocking capacity that would
otherwise be unavailable under conservative static assumptions.

## Data chain

```
ACLineSegment: BO-Line_2 (b58bf21a-096a-4dae-9a01-3f03b60c24c7) — EQ
  └─ Terminal
       └─ OperationalLimitSet (9f6e19b4-4360-a6b0-2b73-35ed991e48a7) — EQ
            └─ CurrentLimit PATL: 1574 A (b59a4b04-016f-ec37-917a-3297a36f61f8) — EQ
                 └─ CurrentLimitSchedule: DLR values — SHS (this file)
                      └─ CurrentLimitTimePoint (96 x 15-min intervals)

AssessedElement: AE2 (d463cbba-c89c-4199-bbb9-1a33d90cae2c) — AE
  └─ .OperationalLimit → CurrentLimit PATL (1574 A)
  └─ .ConductingEquipment → BO-Line_2
```

## DLR Schedule

- **96 time points** (24h x 15-min intervals)
- **Date**: 2023-07-22
- **Rating range**: 1687–1854 A (always >= baseline PATL of 1574 A)
- **Uplift range**: +7% to +18% above static PATL
- **Interpolation**: linear

### DLR pattern
- **Night** (00:00–06:00): Cool ambient provides ~7–10% uplift despite low wind
- **Morning** (06:00–12:00): Wind picks up, uplift rises to ~15–18%
- **Afternoon** (12:00–15:00): Peak wind cooling, maximum uplift ~17–18%
- **Evening** (18:00–24:00): Wind drops, uplift decreases to ~7–8%

## Profiles involved

| Profile | Role | File |
|---|---|---|
| **EQ** | ACLineSegment, Terminal, OperationalLimitSet, CurrentLimit definition | `Belgovia_EQ_1.xml` |
| **ER** | OperationalLimitType (PATL/TATL duration definitions) | `Belgovia_ER.xml` |
| **SHS** | CurrentLimitSchedule with DLR time points | `Belgovia_SHS_DLR.xml` |
| **AE** | AssessedElement referencing the CurrentLimit for capacity calculation | `Belgovia_AE.xml` |

## Test flow

### Step 1: Model and Dataset Preparation
1. Open the **IGM Belgovia**
2. Load the **Equipment dataset** (`Belgovia_EQ_1.xml`)
3. Verify that **BO-Line_2** (`b58bf21a`) exists with an OperationalLimitSet

### Step 2: Load Static Limits
1. Verify the **CurrentLimit PATL** on BO-Line_2 Terminal:
   - normalValue: **1574 A**
   - OperationalLimitType: PATL (isInfiniteDuration=true)

### Step 3: Import DLR Schedule
1. Load the **SHS DLR dataset** (`Belgovia_SHS_DLR.xml`)
2. Verify that the **CurrentLimitSchedule** references the PATL CurrentLimit
3. Verify that **96 CurrentLimitTimePoints** are loaded (15-min intervals)
4. Confirm all DLR values are >= the static PATL of 1574 A

### Step 4: Capacity Calculation with DLR
1. Load the **Assessed Element dataset** (`Belgovia_AE.xml`)
2. Verify that **AE2** references the same CurrentLimit
3. For each 15-min interval, the PATL should be overridden by the DLR value
4. Run N-1 security analysis with dynamic ratings

### Step 5: Result Verification
1. Verify that flow margins increase compared to static PATL
2. The additional transfer capacity from DLR should be 7–18% depending on the time of day

### Step 6: Export
1. Export the updated SHS with DLR values
2. Verify the exported data is valid against SHACL constraints

## Expected Outcome
- DLR values override the static PATL for each time interval
- Capacity calculation uses the higher dynamic ratings
- Additional cross-border transfer capacity is unlocked
- Exported SHS dataset is SHACL-compliant

## Sample DLR values

| Time | Rating (A) | vs Baseline |
|---|---|---|
| 2023-07-22T00:00:00Z | 1708 | +8.5% |
| 2023-07-22T03:00:00Z | 1766 | +12.2% |
| 2023-07-22T06:00:00Z | 1826 | +16.0% |
| 2023-07-22T09:00:00Z | 1854 | +17.8% |
| 2023-07-22T12:00:00Z | 1833 | +16.5% |
| 2023-07-22T15:00:00Z | 1776 | +12.8% |
| 2023-07-22T18:00:00Z | 1715 | +9.0% |
| 2023-07-22T21:00:00Z | 1687 | +7.2% |
