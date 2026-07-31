# Contingency Profile Flag Report

**Branch:** cgmes-3.0_ncp-2.4_tc-1.1  
**Date:** 2026-07-07  
**Sources:** `*_CO.xml` (10 files), `*_SIS.xml` (3 files), `*_SSI.xml` (2 files) in `Instance/`

## Flags per class type

| Class | CO profile attribute | SIS profile path | SSI profile attribute |
|---|---|---|---|
| `nc:OrdinaryContingency` | `nc:Contingency.normalMustStudy` | `^nc:ContingencySchedule.Contingency / ^nc:ContingencyTimePoint.ContingencySchedule / nc:ContingencyTimePoint.mustStudy` | `cim17:Contingency.mustStudy` |
| `nc:OutOfRangeContingency` | same | same | same |
| `nc:ExceptionalContingency` | same | same | same |

> **SIS note:** No `nc:ContingencySchedule` or `nc:ContingencyTimePoint` instances exist in any `*_SIS.xml` file. All SIS values are **N/A**.  
> **SSI note:** No `cim17:Contingency.mustStudy` (or any `Contingency.mustStudy` variant) exists in any `*_SSI.xml` file. All SSI values are **N/A**.  
> **Versioned Belgovia files note:** `Belgovia_v1`–`v4_CO.xml` are dataset version snapshots in `Dataset_version_dependency/`. They share mRIDs with `Belgovia_CO.xml` (same logical contingencies, progressively more entries per version). All are reported for completeness.

---

## 1. nc:OrdinaryContingency (34 instances)

### Svedala — `Svedala_CO.xml` (7)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_5d587c7e` | ✅ true | N/A | N/A |
| CO2 | `_475ba18f` | ✅ true | N/A | N/A |
| CO4 | `_264e9a19` | ✅ true | N/A | N/A |
| CO5 | `_d9ef0d5e` | ✅ true | N/A | N/A |
| CO1 | `_e05bbe20` | ✅ true | N/A | N/A |
| CO_VComp_1 | `_ab92defa` | ✅ true | N/A | N/A |
| CO_ConformLoad_1 | `_f3a8c241` | ✅ true | N/A | N/A |

### Svedala — `Svedala-Belgovia_CO.xml` (4)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_ee6365ea` | ✅ true | N/A | N/A |
| CO2 | `_5ebda6cf` | ✅ true | N/A | N/A |
| CO1 | `_ef85f6be` | ✅ true | N/A | N/A |
| CO1 | `_547ad193` | ✅ true | N/A | N/A |

### Galia — `Galia_CO.xml` (2)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_bd7bb012` | ✅ true | N/A | N/A |
| CO_HVDC | `_a4f7a22a` | ✅ true | N/A | N/A |

### Espheim — `Espheim_CO.xml` (5)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO6 | `_ce19dd34` | ✅ true | N/A | N/A |
| CO2 | `_b6b780cb` | ✅ true | N/A | N/A |
| CO1 | `_8cdec4c6` | ✅ true | N/A | N/A |
| CO5 | `_96c96ad8` | ✅ true | N/A | N/A |
| CO_VComp_Linear | `_62eac668` | ✅ true | N/A | N/A |

### DC-Espheim-Svedala — `DC-Espheim-Svedala_CO.xml` (2)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO_HVDC1 | `_66627b36` | ✅ true | N/A | N/A |
| CO_HVDC2 | `_504b48fb` | ✅ true | N/A | N/A |

### Belgovia — `Belgovia_CO.xml` (4)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_37997e71` | ✅ true | N/A | N/A |
| CO2 | `_7e31c67d` | ✅ true | N/A | N/A |
| CO1 | `_e9eab3fe` | ✅ true | N/A | N/A |
| CO_NonConformLoad_1 | `_65582e87` | ✅ true | N/A | N/A |

### Belgovia — `Belgovia_v4_CO.xml` (4 — same mRIDs as above)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_37997e71` | ✅ true | N/A | N/A |
| CO2 | `_7e31c67d` | ✅ true | N/A | N/A |
| CO1 | `_e9eab3fe` | ✅ true | N/A | N/A |
| CO_NonConformLoad_1 | `_65582e87` | ✅ true | N/A | N/A |

### Belgovia — `Belgovia_v3_CO.xml` (3)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_37997e71` | ✅ true | N/A | N/A |
| CO2 | `_7e31c67d` | ✅ true | N/A | N/A |
| CO1 | `_e9eab3fe` | ✅ true | N/A | N/A |

### Belgovia — `Belgovia_v2_CO.xml` (2)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_37997e71` | ✅ true | N/A | N/A |
| CO2 | `_7e31c67d` | ✅ true | N/A | N/A |

### Belgovia — `Belgovia_v1_CO.xml` (1)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_37997e71` | ✅ true | N/A | N/A |

**Section summary:** All 34 `nc:OrdinaryContingency` instances have `normalMustStudy=true`.

---

## 2. nc:OutOfRangeContingency (3 instances)

### Svedala — `Svedala_CO.xml` (1)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO1 | `_e8e8300b` | ✅ true | N/A | N/A |

### Espheim — `Espheim_CO.xml` (2)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO3 | `_13334fdf` | ✅ true | N/A | N/A |
| CO4 | `_9d17b84c` | ✅ true | N/A | N/A |

**Section summary:** All 3 `nc:OutOfRangeContingency` instances have `normalMustStudy=true`.

---

## 3. nc:ExceptionalContingency (2 instances)

### Svedala — `Svedala_CO.xml` (2)

| CO name | mRID | CO `normalMustStudy` | SIS `CTP.mustStudy` | SSI `mustStudy` |
|---|---|---|---|---|
| CO1_CL7_and_CT72_T1_LAST | `_92d4f3c9` | ✅ true | N/A | N/A |
| CO3 | `_2c1fe55c` | ✅ true | N/A | N/A |

**Section summary:** All 2 `nc:ExceptionalContingency` instances have `normalMustStudy=true`.

---

## Overall summary

| Class | Flag | Instances | Compliant | Issues |
|---|---|---|---|---|
| `nc:OrdinaryContingency` | CO `normalMustStudy` | 34 | 34 ✅ | None |
| `nc:OrdinaryContingency` | SIS `CTP.mustStudy` | 0 | N/A | No `ContingencySchedule` in any SIS file |
| `nc:OrdinaryContingency` | SSI `mustStudy` | 0 | N/A | Property absent from all SSI files |
| `nc:OutOfRangeContingency` | CO `normalMustStudy` | 3 | 3 ✅ | None |
| `nc:OutOfRangeContingency` | SIS `CTP.mustStudy` | 0 | N/A | No `ContingencySchedule` in any SIS file |
| `nc:OutOfRangeContingency` | SSI `mustStudy` | 0 | N/A | Property absent from all SSI files |
| `nc:ExceptionalContingency` | CO `normalMustStudy` | 2 | 2 ✅ | None |
| `nc:ExceptionalContingency` | SIS `CTP.mustStudy` | 0 | N/A | No `ContingencySchedule` in any SIS file |
| `nc:ExceptionalContingency` | SSI `mustStudy` | 0 | N/A | Property absent from all SSI files |

**All 39 contingency instances across all 10 CO files have `normalMustStudy=true`. No open issues.**
