# AssessedElement Profile Flag Report

**Branch:** cgmes-3.0_ncp-2.4_tc-1.1  
**Date:** 2026-07-07  
**Sources:** `*_AE.xml`, `*_SIS.xml`, `*_SSI.xml` in `Instance/`

## Flags per class type

| Class | AE profile attribute | SIS profile path | SSI profile attribute |
|---|---|---|---|
| `nc:AssessedElement` | `nc:AssessedElement.normalEnabled` | `^nc:AssessedElementSchedule.AssessedElement / ^nc:AssessedElementTimePoint.AssessedElementSchedule / nc:AssessedElementTimePoint.enabled` | `nc:AssessedElement.enabled` |
| `nc:AssessedElementWithRemedialAction` | `nc:AssessedElementWithRemedialAction.normalEnabled` | `^nc:GenericEnablingSchedule.AssessedElementWithRemedialAction / ^nc:EnablingTimePoint.GenericEnablingSchedule / nc:EnablingTimePoint.enabled` | `nc:AssessedElementWithRemedialAction.enabled` |
| `nc:AssessedElementWithContingency` | `nc:AssessedElementWithContingency.normalEnabled` | `^nc:GenericEnablingSchedule.AssessedElementWithContingency / ^nc:EnablingTimePoint.GenericEnablingSchedule / nc:EnablingTimePoint.enabled` | `nc:AssessedElementWithContingency.enabled` |

> **SIS note — AEWRA/AEWCO:** No `nc:GenericEnablingSchedule` or `nc:EnablingTimePoint` instances exist in any `*_SIS.xml` file. All AEWRA/AEWCO SIS values are **N/A**.  
> **SIS note — AE:** Only `Belgovia_SIS.xml` contains an `nc:AssessedElementSchedule`, covering one AE (`_992c2de6`, AE1). `AssessedElementTimePoint.enabled = false`.  
> **SSI note:** No `nc:AssessedElement.enabled`, `nc:AssessedElementWithRemedialAction.enabled`, or `nc:AssessedElementWithContingency.enabled` entries exist in any `*_SSI.xml` file. All SSI values are **N/A**.

---

## 1. nc:AssessedElement (26 instances)

### Belgovia (7)

| AE name | mRID | AE `normalEnabled` | SIS `AETP.enabled` | SSI `AE.enabled` |
|---|---|---|---|---|
| AE1 | `_992c2de6` | ✅ true | ⚠️ **false** | N/A |
| AE2 | `_d463cbba` | ✅ true | N/A | N/A |
| AE3 | `_1eb2eb03` | ✅ true | N/A | N/A |
| AE4 | `_3686af46` | ✅ true | N/A | N/A |
| AE4 *(RA-linked)* | `_13d17257` | ✅ true | N/A | N/A |
| AE5-CO | `_d17943b5` | ✅ true | N/A | N/A |
| AE5-CO3 | `_663c6c3c` | ✅ true | N/A | N/A |

### Espheim (7)

| AE name | mRID | AE `normalEnabled` | SIS `AETP.enabled` | SSI `AE.enabled` |
|---|---|---|---|---|
| AE1 | `_2cc84c47` | ✅ true | N/A | N/A |
| AE2 | `_3a364a5b` | ✅ true | N/A | N/A |
| AE3 | `_989535e7` | ✅ true | N/A | N/A |
| AE4 | `_ea577780` | ✅ true | N/A | N/A |
| AE5 | `_2bd363ca` | ✅ true | N/A | N/A |
| AE6 | `_3bc10ae6` | ✅ true | N/A | N/A |
| AE9 | `_97cb3913` | ✅ true | N/A | N/A |

### Galia (2)

| AE name | mRID | AE `normalEnabled` | SIS `AETP.enabled` | SSI `AE.enabled` |
|---|---|---|---|---|
| AE1 | `_e43a18a9-2` | ✅ true | N/A | N/A |
| AE2 | `_e43a18a9-3` | ✅ true | N/A | N/A |

### Svedala (10)

| AE name | mRID | AE `normalEnabled` | SIS `AETP.enabled` | SSI `AE.enabled` |
|---|---|---|---|---|
| AE1 | `_65174269` | ✅ true | N/A | N/A |
| AE2 | `_662cc3bd` | ✅ true | N/A | N/A |
| AE3 | `_808b9ea1` | ✅ true | N/A | N/A |
| AE4 | `_07c95f06` | ✅ true | N/A | N/A |
| AE5 | `_05675c5e` | ✅ true | N/A | N/A |
| AE6 | `_2cb8db8c` | ✅ true | N/A | N/A |
| AE7 | `_53aec823` | ✅ true | N/A | N/A |
| AE8 | `_614648d2` | ✅ true | N/A | N/A |
| AE10 | `_57246b44` | ✅ true | N/A | N/A |
| AE11_Exclusive_CRA | `_bde1ef4b` | ✅ true | N/A | N/A |

**Section summary:** All 26 AEs have `normalEnabled=true`. Belgovia AE1 is the only AE with a SIS schedule; its `AssessedElementTimePoint.enabled=false` ⚠️.

---

## 2. nc:AssessedElementWithRemedialAction (2 instances)

| Region | AEWRA mRID | Connected AE | AEWRA `normalEnabled` | SIS `EnablingTP.enabled` | SSI `AEWRA.enabled` |
|---|---|---|---|---|---|
| Belgovia | `_66f786ce` | AE4 RA-linked (`_13d17257`) | ✅ true | N/A | N/A |
| Svedala | `_abb23ba4` | AE11_Exclusive_CRA (`_bde1ef4b`) | ✅ true | N/A | N/A |

**Section summary:** Both AEWRA instances have `normalEnabled=true`. No `nc:GenericEnablingSchedule` or `nc:AssessedElementWithRemedialAction.enabled` entries exist in any file.

---

## 3. nc:AssessedElementWithContingency (15 instances)

### Belgovia (3)

| AEWCO mRID | Connected AE | AEWCO `normalEnabled` | SIS `EnablingTP.enabled` | SSI `AEWCO.enabled` |
|---|---|---|---|---|
| `_1f38d403` | AE1 (`_992c2de6`) | ✅ true | N/A | N/A |
| `_deb4c65f` | AE5-CO3 (`_663c6c3c`) | ✅ true | N/A | N/A |
| `_237de243` | AE3 (`_1eb2eb03`) | ✅ true | N/A | N/A |

### Espheim (6)

| AEWCO mRID | Connected AE | AEWCO `normalEnabled` | SIS `EnablingTP.enabled` | SSI `AEWCO.enabled` |
|---|---|---|---|---|
| `_e8a03f97` | AE1 (`_2cc84c47`) | ✅ true | N/A | N/A |
| `_8f585428` | AE2 (`_3a364a5b`) | ✅ true | N/A | N/A |
| `_9cccd979` | AE3 (`_989535e7`) | ✅ true | N/A | N/A |
| `_e8c39ec9` | AE5 (`_2bd363ca`) | ✅ true | N/A | N/A |
| `_225ca44e` | AE6 (`_3bc10ae6`) | ✅ true | N/A | N/A |
| `_7f3166c3` | AE9 (`_97cb3913`) | ✅ true | N/A | N/A |

### Galia (1)

| AEWCO mRID | Connected AE | AEWCO `normalEnabled` | SIS `EnablingTP.enabled` | SSI `AEWCO.enabled` |
|---|---|---|---|---|
| `_e3165c3a` | AE1 (`_e43a18a9-2`) | ✅ true | N/A | N/A |

### Svedala (5)

| AEWCO mRID | Connected AE | AEWCO `normalEnabled` | SIS `EnablingTP.enabled` | SSI `AEWCO.enabled` |
|---|---|---|---|---|
| `_35e22789` | AE3 (`_808b9ea1`) | ✅ true | N/A | N/A |
| `_ba2c0214` | AE8 (`_614648d2`) | ✅ true | N/A | N/A |
| `_675c5ed8` | AE4 (`_07c95f06`) | ✅ true | N/A | N/A |
| `_256a1257` | AE6 (`_2cb8db8c`) | ✅ true | N/A | N/A |
| `_8eadfd27` | AE5 (`_05675c5e`) | ✅ true | N/A | N/A |

**Section summary:** All 15 AEWCO instances have `normalEnabled=true`. No `nc:GenericEnablingSchedule` or `nc:AssessedElementWithContingency.enabled` entries exist in any file.

---

## Overall summary

| Class | Flag | Instances | Compliant | Issues |
|---|---|---|---|---|
| `nc:AssessedElement` | AE `normalEnabled` | 26 | 26 ✅ | None |
| `nc:AssessedElement` | SIS `AETP.enabled` | 1 has schedule | 0 | Belgovia AE1 → **false** ⚠️ |
| `nc:AssessedElement` | SSI `AE.enabled` | 0 | N/A | Property absent from all SSI files |
| `nc:AssessedElementWithRemedialAction` | AE `normalEnabled` | 2 | 2 ✅ | None |
| `nc:AssessedElementWithRemedialAction` | SIS `EnablingTP.enabled` | 0 | N/A | No `GenericEnablingSchedule` in any SIS file |
| `nc:AssessedElementWithRemedialAction` | SSI `AEWRA.enabled` | 0 | N/A | Property absent from all SSI files |
| `nc:AssessedElementWithContingency` | AE `normalEnabled` | 15 | 15 ✅ | None |
| `nc:AssessedElementWithContingency` | SIS `EnablingTP.enabled` | 0 | N/A | No `GenericEnablingSchedule` in any SIS file |
| `nc:AssessedElementWithContingency` | SSI `AEWCO.enabled` | 0 | N/A | Property absent from all SSI files |

**Only open issue:** Belgovia AE1 (`_992c2de6`) has `AssessedElementTimePoint.enabled=false` in `Belgovia_SIS.xml`. All `normalEnabled` flags across all 43 instances (26 AE + 2 AEWRA + 15 AEWCO) are compliant.
