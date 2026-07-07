# RA Profile Flag Report

## Flag Paths per Class

| Class | RA Profile | SIS Profile | SSI Profile |
|---|---|---|---|
| `nc:ContingencyWithRemedialAction` | `nc:ContingencyWithRemedialAction.normalEnabled` | `^nc:GenericEnablingSchedule.ContingencyWithRemedialAction / ^nc:EnablingTimePoint.GenericEnablingSchedule / nc:EnablingTimePoint.enabled` | `nc:ContingencyWithRemedialAction.enabled` |
| `nc:GridStateAlterationRemedialAction` | `nc:RemedialAction.normalAvailable` | `^nc:GridStateAlterationSchedule.GridStateAlteration (on child actions) / ^nc:GridStateAlterationTimePoint.GridStateAlterationSchedule / nc:GridStateAlterationTimePoint.enabled` | `nc:GridStateAlteration.enabled` on child `nc:GridStateAlteration` instances |
| `nc:SchemeRemedialAction` | `nc:RemedialAction.normalAvailable` | *unknown / not found* | *unknown / not found* |
| `nc:RedispatchRemedialAction` | `nc:RemedialAction.normalAvailable` | `^nc:PowerBidSchedule.PowerRemedialAction` links exist but `nc:PowerBidSchedule` has **no enabled flag** | *not found* |
| `nc:CountertradeRemedialAction` | `nc:RemedialAction.normalAvailable` | `^nc:PowerBidSchedule.PowerRemedialAction` links exist but `nc:PowerBidSchedule` has **no enabled flag** | *not found* |
| `nc:AvailabilityRemedialAction` | `nc:RemedialAction.normalAvailable` | *not found* | *not found* |

### Key SIS/SSI Discoveries

- **GridStateAlterationRemedialAction**: SIS and SSI flags are not on the RA itself but on its child `nc:GridStateAlteration` instances (e.g. `nc:TopologyAction`, `nc:TapPositionAction`, etc.). The `nc:GridStateAlteration.GridStateAlterationRemedialAction` association identifies which RA owns each child action.
- **RedispatchRemedialAction / CountertradeRemedialAction**: `nc:PowerBidSchedule` links directly to the RA via `nc:PowerBidSchedule.PowerRemedialAction`, but `nc:PowerBidSchedule` carries only commercial data (currency, activationCost, leadTime, direction) — no `enabled` flag. No other SIS/SSI linkage was found.
- **SchemeRemedialAction / AvailabilityRemedialAction**: No SIS schedule entries and no SSI entries were found in any `*_SIS.xml` or `*_SSI.xml` file.
- **SSI files present**: `Espheim_SSI.xml`, `Svedala_SSI.xml` only. No Belgovia SSI file exists.

---

## nc:ContingencyWithRemedialAction

**Total instances: 4**  
RA profile flag: `nc:ContingencyWithRemedialAction.normalEnabled`  
SIS: No `nc:GenericEnablingSchedule` linking to any CWRA instance found in any SIS file.  
SSI: No `nc:ContingencyWithRemedialAction.enabled` found in any SSI file.

| Name / mRID | File | Linked Contingency | Linked RemedialAction | normalEnabled | SIS | SSI |
|---|---|---|---|---|---|---|
| `_87714f02` | `Belgovia_RA.xml` | `_37997e71` | RA18 CountertradeRA `_30f6377d` | *not set* | N/A | N/A |
| `_112c79d2` | `Belgovia_RA.xml` | `_7e31c67d` | TapRA2 GSAltRA `_5e5ff13e` | *not set* | N/A | N/A |
| `_5c7acbe4` | `Belgovia_RA.xml` | `_e9eab3fe` | shunt RA GSAltRA `_7acbe48a` | *not set* | N/A | N/A |
| `_e3512f27` | `Galia_RA.xml` | `_bd7bb012` | RA15 GSAltRA `_f4d57bc2` | *not set* | N/A | N/A |

> None of the 4 CWRA instances carry `nc:ContingencyWithRemedialAction.normalEnabled`.

---

## nc:GridStateAlterationRemedialAction

**Total instances: 24** — all have `nc:RemedialAction.normalAvailable = true`

SIS and SSI flags are tracked on **child GridStateAlteration instances**, not on the RA element itself.

### SIS — GridStateAlterationSchedule / GridStateAlterationTimePoint

Only 2 of the 24 RA instances have SIS schedule data (via their child actions):

| RA | Region | Child Action mRID | GridStateAlterationSchedule | TimePoint enabled values |
|---|---|---|---|---|
| RA SubstationB_2N `_fa3e3533` | Svedala | `_eb60d1c0` (CL6 to Hallan disc) | `_a951d00f` | **true**, **false** |
| RA22 `_d856a2a2` | Espheim | `_4d3757fd` (RA22 TopologyAction) | `_f5205bd4` | **true**, **false**, **true** |

Child action `_55961174` (CL6 to Jauras C, also owned by RA SubstationB_2N) has **no GridStateAlterationSchedule** in `Svedala_SIS.xml`.  
All other 22 GSAltRA instances: **no SIS entries**.

### SSI — nc:GridStateAlteration.enabled on child actions

Only 2 RA instances have SSI data (via their child actions), found in Espheim_SSI.xml and Svedala_SSI.xml:

| RA | Region | Child Action mRID | Child Action Name | nc:GridStateAlteration.enabled |
|---|---|---|---|---|
| RA22 `_d856a2a2` | Espheim | `_4d3757fd` | RA22 | **true** |
| RA SubstationB_2N `_fa3e3533` | Svedala | `_eb60d1c0` | CL6 to Hallan disc | **false** |
| RA SubstationB_2N `_fa3e3533` | Svedala | `_55961174` | CL6 to Jauras C | **false** |

All other 22 GSAltRA instances: **no SSI entries**.

### Full RA instance list

#### Svedala (12 instances)

| Name | mRID | normalAvailable | SIS (child actions) | SSI (child actions) |
|---|---|---|---|---|
| RA11 | `_b2555ccc` | true | N/A | N/A |
| RA3 | `_5e401955` | true | N/A | N/A |
| CRA1 | `_347f4f7e` | true | N/A | N/A |
| RA SubstationA_quarterbar1B | `_7e422768` | true | N/A | N/A |
| RA17 | `_cfabf356` | true | N/A | N/A |
| RA1 | `_68255abc` | true | N/A | N/A |
| RA12 | `_bf8157d8` | true | N/A | N/A |
| RA5 | `_587cb391` | true | N/A | N/A |
| RA2 | `_d9bd3aaf` | true | N/A | N/A |
| CRA6 | `_b5f07ec3` | true | N/A | N/A |
| RA SubstationB_2N | `_fa3e3533` | true | child `_eb60d1c0`: true/false | child `_eb60d1c0`: **false**, child `_55961174`: **false** |
| Topology RA one Switch | `_6d2c8901` | true | N/A | N/A |

#### Espheim (7 instances)

| Name | mRID | normalAvailable | SIS (child actions) | SSI (child actions) |
|---|---|---|---|---|
| RA16 | `_2e4f4212` | true | N/A | N/A |
| RA22 | `_d856a2a2` | true | child `_4d3757fd`: true/false/true | child `_4d3757fd`: **true** |
| RA21 | `_fb487cc2` | true | N/A | N/A |
| RA1 | `_5898c268` | true | N/A | N/A |
| RA19 | `_c9c76af9` | true | N/A | N/A |
| RA14 | `_c8bf6b19` | true | N/A | N/A |
| RA13 | `_1fd630a9` | true | N/A | N/A |

#### Galia (1 instance)

| Name | mRID | normalAvailable | SIS | SSI |
|---|---|---|---|---|
| RA15 | `_f4d57bc2` | true | N/A | N/A |

#### Belgovia (4 instances)

| Name | mRID | normalAvailable | SIS | SSI |
|---|---|---|---|---|
| shunt RA | `_7acbe48a` | true | N/A | N/A (no Belgovia SSI) |
| Redispatch | `_d874f8e3` | true | N/A | N/A (no Belgovia SSI) |
| TapRA2 | `_5e5ff13e` | true | N/A | N/A (no Belgovia SSI) |
| TapRA2 | `_70b696ac` | true | N/A | N/A (no Belgovia SSI) |

---

## nc:SchemeRemedialAction

**Total instances: 1**

| Name | mRID | File | normalAvailable | SIS | SSI |
|---|---|---|---|---|---|
| CRA | `_31d41e36` | `Svedala_RA.xml` | true | N/A | N/A |

No `nc:GridStateAlterationSchedule` or other schedule entries linking to the SchemeRemedialAction's child actions were found in `Svedala_SIS.xml`. No SSI entries for its child actions were found in `Svedala_SSI.xml`.

---

## nc:RedispatchRemedialAction

**Total instances: 2** (both in `Belgovia_RA.xml`)

SIS note: `nc:PowerBidSchedule` in `Belgovia_SIS.xml` links to `_fa73cfee` via `nc:PowerBidSchedule.PowerRemedialAction`, but `nc:PowerBidSchedule` carries only commercial data — no `enabled` flag exists on `PowerBidSchedule` or `PowerBidScheduleTimePoint`.  
No Belgovia SSI file exists.

| Name | mRID | normalAvailable | SIS PowerBidSchedule link | SIS enabled flag | SSI |
|---|---|---|---|---|---|
| RD RA1 | `_fa73cfee` | true | yes (`PBS` in `Belgovia_SIS.xml`) | **no enabled flag** | N/A |
| RD RA1 | `_9d72d12a` | true | no | **no enabled flag** | N/A |

---

## nc:CountertradeRemedialAction

**Total instances: 1** (in `Belgovia_RA.xml`)

SIS note: `nc:PowerBidSchedule` in `Belgovia_SIS.xml` links to RA18 via `nc:PowerBidSchedule.PowerRemedialAction` (3 PowerBidSchedule instances), but `nc:PowerBidSchedule` has no `enabled` flag.  
No Belgovia SSI file exists.

| Name | mRID | normalAvailable | SIS PowerBidSchedule link | SIS enabled flag | SSI |
|---|---|---|---|---|---|
| RA18 | `_30f6377d` | true | yes (3 PBS in `Belgovia_SIS.xml`) | **no enabled flag** | N/A |

---

## nc:AvailabilityRemedialAction

**Total instances: 1** (in `Svedala_RA.xml`)

No SIS schedule entries and no SSI entries found linking to this RA.

| Name | mRID | normalAvailable | SIS | SSI |
|---|---|---|---|---|
| ARA1 | `_14b2b671` | true | N/A | N/A |

---

## Summary

| Class | Total instances | normalAvailable / normalEnabled values | SIS entries | SSI entries |
|---|---|---|---|---|
| `nc:ContingencyWithRemedialAction` | 4 | *not set* on any instance | None | None |
| `nc:GridStateAlterationRemedialAction` | 24 | all `true` | 2 RAs have SIS data via child actions | 2 RAs have SSI data via child actions |
| `nc:SchemeRemedialAction` | 1 | `true` | None | None |
| `nc:RedispatchRemedialAction` | 2 | all `true` | PowerBidSchedule link exists but no enabled flag | None (no Belgovia SSI) |
| `nc:CountertradeRemedialAction` | 1 | `true` | PowerBidSchedule link exists but no enabled flag | None (no Belgovia SSI) |
| `nc:AvailabilityRemedialAction` | 1 | `true` | None | None |
