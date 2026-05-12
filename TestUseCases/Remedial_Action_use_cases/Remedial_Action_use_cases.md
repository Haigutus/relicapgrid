# Remedial Action Use Cases

This file collects modeling use cases for Remedial Actions as illustrated using the synthetic datasets from the ReliCapGrid GitHub repository.

---

## 1. Topology Remedial Action with One Topology Action (No Dependencies)

### Description
This use case describes a basic **Topology Remedial Action** composed of **one single topology action** without any dependencies. The remedial action performs a switch opening operation in a fictitious grid model.

### Context
For illustration purposes, readers can refer to the **EQ and RA synthetic dataset** of the fictitious **TSO Svedala**, available in the **ReliCapGrid GitHub repository**.

### Elements Involved

#### Topology Remedial Action
- **Class:** `GridStateAlterationRemedialAction`
- **mRID:** `6d2c8901-d068-4d22-8ce9-7379644b4f17`
- Represents the container remedial action.

#### Topology Action
- **mRID:** `176d262c-701c-4ced-99b2-a155c136e787`
- Action: Open a switch
- Dataset: Svedala fictitious IGM (EQ profile)

---

### Validation Steps

#### Step 1: Model and Data Import
1. Open the **IGM Svedala**.
2. Import the **Remedial Action Profile** from the Relicap dataset.
3. Verify that the `GridStateAlterationRemedialAction` is loaded correctly.
4. Verify that exactly one topology action is associated with the remedial action.

#### Step 2: Remedial Action Execution
1. Trigger the topology remedial action.
2. Apply the associated topology action.

#### Step 3: Result Verification
1. Check the status of the targeted switch.
2. Verify that:
   - The switch state changes from **closed** to **open**.
   - The network topology reflects the expected change.
3. Confirm that no dependency or precondition was evaluated.

---

### Expected Outcome
- The switch referenced by the topology action is opened.
- The grid topology is updated accordingly.
- The remedial action is executed successfully without dependencies.

---

## 2. Dependent Topology Remedial Actions with Multiple Topology Actions

### Description
This use case describes **Topology Remedial Actions with dependencies**, composed of **multiple Topology Actions**.

### Context
Refer to the **RA and RAS synthetic datasets** of fictitious **TSO Svedala**.

### Scenario
- Two Topology Remedial Actions are defined for **Substation A**.
- Each remedial action includes multiple topology actions on **the same four switches**.
- Each action defines a **different target topology configuration**.
- The two remedial actions cannot be applied simultaneously.

### Dependencies
Two **exclusive dependencies** are defined:

- `598ab84e-a575-40ad-bf66-c1ab41c65093`
- `13c29cc3-3d99-4c5b-abac-085f0d319eab`


### Elements Involved

#### Topology Remedial Actions
- Two `GridStateAlterationRemedialAction` objects are defined.
- Each remedial action groups multiple topology actions affecting Substation A.

### Validation Steps

#### Step 1: Model and Data Import
1. Open the **IGM Svedala**.
2. Import the **Remedial Action profle (RA)** and **RAS profile**.
3. Verify that both topology remedial actions are loaded correctly.
4. Verify that each remedial action contains multiple topology actions.

#### Step 2: Dependency Verification
1. Inspect the dependency definitions between the two remedial actions.
2. Confirm that the dependencies are of **exclusive type**.
3. Verify that each remedial action references the corresponding dependency objects.

#### Step 3: Execution Behavior
1. Trigger the first topology remedial action.
2. Verify that:
   - All associated topology actions are applied.
   - The alternative remedial action is blocked.
3. Trigger the second topology remedial action.
4. Verify that:
   - The first remedial action is blocked.
   - Only the second configuration is applied.

---

### Expected Outcome
- Only one target topology configuration of Substation A can be applied at any time.
- Exclusive dependencies correctly prevent simultaneous activation.
- Grid topology reflects the selected remedial action consistently.

---

## 3. Modification Prior to RAO of a Topology Remedial Action

### Description
This use case illustrates how a TSO modifies (enables/disables) **Topology Actions** before the **RAO process**.

### Context
Refer to the **SIS and SSI synthetic datasets** of fictitious **TSO Espheim**.

### Elements Involved

**Topology Remedial Action**
- mRID: `d856a2a2-3de4-4a7b-aea4-d363c13d9014`

**Topology Action**
- mRID: `4d3757fd-b40a-4d7b-be47-6553935234ff`

### Modification Using SIS
- `GridStateAlterationSchedule` from SIS
  - mRID: `f5205bd4-637a-4eb7-b0d8-e03638bc570b`
- Multiple `GridStateAlterationTimePoint` objects define enable/disable per time point.

### Modification Using SSI
- `GridStateAlteration` per Topology Action
- Enables or disables the action without scheduling.


### Modification Using SIS

- **GridStateAlterationSchedule**
  - **mRID:** `f5205bd4-637a-4eb7-b0d8-e03638bc570b`
- The schedule is associated per **Topology Action**.
- It allows defining multiple **GridStateAlterationTimePoint** objects.
- Each time point specifies whether the Topology Action is enabled or disabled at a given time.

---

### Validation Steps

#### Step 1: Model and Data Import
1. Open the **IGM Espheim**.
2. Import the **Remedial Action**.
3. Import the relevant **SIS** profile.

#### Step 2: Modification Verification
1. Verify that the modification objects reference the correct Topology Action.
2. Check that:
   - SIS modifications correctly define enable/disable states per time point.

#### Step 3: Pre‑RAO Consistency Check
1. Verify that the modified availability of the Topology Action is reflected.
2. Confirm that the Topology Action state is correctly considered prior to RAO.

---

### Expected Outcome
- Topology Actions are enabled or disabled as defined in SIS or SSI.
- The Topology Remedial Action reflects the modified availability.
- The RAO process considers only the enabled Topology Actions.

Note:Using SSI the modification can be done by: GridStateAlteration per TopologyAction (4d3757fd-b40a-4d7b-be47-6553935234ff)

---

## 4. Proposing Modifications of a Topology Remedial Action After RAO

### Description
This use case describes how a TSO proposes modifications to a **Topology Remedial Action schedule after RAO**, following a coordination process where an existing schedule is refused and a new schedule is proposed.

### Context
This process is preceded by a coordination phase where the TSO:
- Refuses the existing remedial action schedule, and
- Proposes a new remedial action schedule.

---

### Scenario Description
- A Remedial Action Schedule resulting from RAO is not accepted by a TSO.
- The TSO refuses the complete schedule.
- The TSO proposes a new, complete remedial action schedule.
- The proposal includes new identifiers and updated scheduling information.

---

### Refusal of a Remedial Action Schedule

To refuse a Remedial Action Schedule, the TSO sends a:

#### RemedialActionScheduleResponse
- **mRID:** `96f93b71-420f-456f-932e-9ac3f724b683`
- The refusal applies to the **entire schedule**.
- Refusal is not performed at individual time‑point level.

---

### Proposal of a New Remedial Action Schedule

To propose a new schedule, the TSO sends:

#### RemedialActionScheduleDependency
- **mRID:** `f7231aa5-d497-41f3-a5d5-9d4af74444f0`
- Defines the relationship with the previously refused schedule.
- In this example:
  - No grouping is required.
  - `RemedialActionScheduleDependencyKind` is set to `none`.

#### New RemedialActionSchedule
- **mRID:** `51361821-0a40-4e5a-a49d-29c266ea2ecc`
- Represents the complete counter‑proposal schedule.

---

### Event Schedule Handling
- When making a new proposal, the TSO creates and sends a new **EventSchedule**.
- The EventSchedule associated with the counter‑proposal uses a **new identifier**, distinct from the refused schedule.
- This applies also in the case where the proposal follows a refusal.

---

### Schedule Completeness Requirements
- When creating a new Remedial Action Schedule:
  - The TSO must create the **complete schedule**, including all time points.
  - Partial schedules are not allowed.
- Since the refusal applies to the **entire schedule**, the counter‑proposal must also be complete.
- No rejection or acceptance is applied at individual time‑point level.

---

## Validation Steps

#### Step 1: Refusal of Existing Schedule
1. Open the **IGM Svedala**.
2. Identify the Remedial Action Schedule in the Svedala_RAS_proposal resulting from RAO.
3. Send a `RemedialActionScheduleResponse` refusing the complete schedule.

#### Step 2: Creation of Counter‑Proposal
1. Create a new `RemedialActionSchedule`.
2. Create a `RemedialActionScheduleDependency` referencing the refused schedule.
3. Set `RemedialActionScheduleDependencyKind` to `none`.

#### Step 3: Schedule Completeness Check
1. Create the **full schedule**, including all time points.
2. Verify that:
   - No partial rejection exists.
   - The proposal replaces the refused schedule entirely.

---

### Expected Outcome
- The original remedial action schedule is formally refused.
- A new remedial action schedule is proposed with a new identifier.
- The new proposal fully replaces the refused schedule and follows coordination rules.

---

## 5. Activation After RAO of a Topology Remedial Action

### Description
This use case describes the **activation of a Topology Remedial Action after RAO**, as an output of the RAO process, communicates the activation time of the topology remedial action.

### Context
For illustration purposes, readers can refer to the **RA and RAS synthetic datasets** of the fictitious **TSO Svedala**, and follow the indicated mRIDs below.

---

### Scenario Description
- The RAO process determines whether and when a topology remedial action shall be activated.
- The RCC communicates the activation decision to TSOs.
- Activation information is exchanged using scheduling objects in the **RAS dataset**.

---

### Elements Involved

#### Topology Remedial Actions (RA profile)
Two topology remedial actions are defined, each containing multiple `GridStateAlteration` objects:

- **mRID:** `7e422768-207d-455f-976e-0b1cb2338509`
- **mRID:** `fa3e3533-345a-4ef1-a46d-3ab6d251924a`

#### Remedial Action Group and Dependencies
- The two remedial actions are grouped.
- They have **exclusive dependencies**, meaning only one can be activated.
- **Group mRID:** `6a9b5221-bb3f-421b-89c1-886b100aa68a`

---

### Communication of Activation (RAS Dataset)

For each remedial action, the RCC exports the following objects:

#### EventSchedule
- **mRID:** `1c1e39cf-15a1-4874-9739-d9e6dc90ee11`
- **mRID:** `023512a8-150d-4300-8159-807275eafd48`

The `EventSchedule` carries the activation information of the remedial action.


#### RemedialActionSchedule
- **mRID:** `279bfb00-1b2a-4592-af3a-dba9403d1abd`
- **mRID:** `87e90c47-43d8-4e5c-b2ad-5c67d3a74842`

#### EventTimePoint
- Defined for each relevant timestamp.
- Indicates whether the remedial action is activated or not at that time.

---

### Validation Steps

#### Step 1: Model and Dataset Preparation
1. Open the **IGM Svedala**.
2. Load the **RA dataset** containing the topology remedial actions.
3. Load the **RAS dataset**.

#### Step 2: Group and Dependency Verification
1. Verify that the two topology remedial actions belong to the same remedial action group.
2. Confirm that exclusive dependencies are defined between them.
3. Ensure that only one remedial action is eligible for activation at a given time.

#### Step 3: Activation Verification
1. Inspect the `EventSchedule` objects associated with each remedial action.
2. Verify that:
   - Activation timestamps are defined via `EventTimePoint` objects.
   - Activation status is clearly communicated (activated / not activated).
3. Cross‑check that the corresponding `RemedialActionSchedule` is consistent with the activation decision.

---

### Recommendation
It is recommended to use the **EventSchedule** class as the primary carrier of information related to the activation of topology remedial actions after RAO.

---

### Expected Outcome
- Activation decisions from RAO are clearly communicated .
- Only one remedial action within the exclusive group is activated.
- The activation state and timing are unambiguously represented in the RAS dataset.

---

## 6. Countertrade Remedial Action

### Description
This use case illustrates **two ways** to define a Countertrade Remedial Action.

### Variant 1: PowerSchedule

**PowerSchedule**
- File: `Belgovia_PS.xml`
- rdf:ID: `_27940387-6935-47b6-ab25-8742bac2a266`

**CountertradeRemedialAction**
- File: `Belgovia_RA.xml`
- rdf:ID: `_30f6377d-5e35-4dd0-a53d-c1992043855e`

**GeneratingUnit**
- File: `Belgovia_EQ_1.xml`
- rdf:ID: `_413bbc8a-683c-7e07-4fb9-aa6ec83278e0`


### Validation Steps

#### Step 1: Model and Dataset Preparation
1. Open the **IGM Belgovia**.
2. Load the **Equipment dataset**:
   - File: `Belgovia_EQ_1.xml`
3. Verify that the **GeneratingUnit** is available:
   - rdf:ID: `_413bbc8a-683c-7e07-4fb9-aa6ec83278e0`

#### Step 2: Remedial Action Import
1. Load the **Remedial Action dataset**:
   - File: `Belgovia_RA.xml`
2. Verify that the **CountertradeRemedialAction** is present:
   - rdf:ID: `_30f6377d-5e35-4dd0-a53d-c1992043855e`
3. Check that the remedial action references the appropriate generating unit.

#### Step 3: Schedule Import and Linking
1. Load the **PowerSchedule dataset**:
   - File: `Belgovia_PS.xml`
2. Verify that the **PowerSchedule** is present:
   - rdf:ID: `_27940387-6935-47b6-ab25-8742bac2a266`
3. Confirm that the Countertrade Remedial Action is linked to the PowerSchedule.

#### Step 4: Consistency Check
1. Verify that the scheduled power values are consistent.
2. Confirm that the PowerSchedule correctly represents the countertrade instruction.

---


### Variant 2: PowerBidSchedule (SIS)

**PowerBidSchedule**
- File: `Belgovia_SIS.xml`
- rdf:ID: `_ae6a5ddd-fe7e-40b2-bcb6-cbd2882434e7`


### Validation Steps

#### Step 1: Model and Dataset Preparation
1. Open the **IGM Belgovia**.
2. Load the **Remedial Action dataset**:
   - File: `Belgovia_RA.xml`
3. Verify the presence of the **CountertradeRemedialAction**:
   - rdf:ID: `_30f6377d-5e35-4dd0-a53d-c1992043855e`

#### Step 2: SIS Dataset Import
1. Load the **State Instruction Schedule (SIS) dataset**:
   - File: `Belgovia_SIS.xml`
2. Verify the presence of the **PowerBidSchedule**:
   - rdf:ID: `_ae6a5ddd-fe7e-40b2-bcb6-cbd2882434e7`

#### Step 3: Linking and Validation
1. Verify that the PowerBidSchedule is associated with the Countertrade Remedial Action.
2. Check that bid values and time information are consistent.
3. Confirm that the bid schedule correctly represents the countertrade instruction.

---

### Expected Outcome
- The Countertrade Remedial Action is correctly defined.
- Scheduling information is provided either via **PowerSchedule** or **PowerBidSchedule**.
- Both variants represent valid and interchangeable modeling approaches.


---

## 7. Redispatch Remedial Action


### Description
This use case illustrates **two alternative ways** to define a **Redispatch Remedial Action**, both targeting the same equipment and representing valid modeling approaches.

---

### Common Equipment

- **File:** `Belgovia_EQ_1.xml`
- **SynchronousMachine rdf:ID:** `_3a3b27be-b18b-4385-b557-6735d733baf0`

---

## Variant 1: Redispatch Using Bid Schedules 

### Validation Steps

#### Step 1: Model and Equipment Preparation
1. Open the **IGM Belgovia**.
2. Load the **Equipment dataset**:
   - File: `Belgovia_EQ_1.xml`
3. Verify that the **SynchronousMachine** is available:
   - rdf:ID: `_3a3b27be-b18b-4385-b557-6735d733baf0`

#### Step 2: Remedial Action Import
1. Load the **Remedial Action dataset**:
   - File: `Belgovia_RA.xml`
2. Verify that the **RedispatchRemedialAction** is present:
   - rdf:ID: `_fa73cfee-ff54-43cd-816b-51394cd76f0f`
3. Check that the remedial action is linked to the target SynchronousMachine.

#### Step 3: SIS Dataset Import
1. Load the **State Instruction Schedule (SIS) dataset**:
   - File: `Belgovia_SIS.xml`
2. Verify the presence of the following objects:
   - `PowerBidSchedule` rdf:ID `_6c0ba4c5-5ac0-43f8-87d9-ec2fb41a3dec`
   - `PowerBidScheduleTimePoint` rdf:ID `_250e37a5-50e0-44b7-9bd7-7284c04116db`
   - `PowerShiftKeySchedule` rdf:ID `_3b5748de-39f2-45d7-9a66-65819c667e91`

#### Step 4: Consistency Check
1. Verify that the bid schedules reference the Redispatch Remedial Action.
2. Check that bid values and time points are defined consistently.
3. Confirm that the schedules correctly represent redispatch instructions.

---

## Variant 2: Redispatch Using Power Shift Key Strategy 

### Validation Steps

#### Step 1: Model and Equipment Preparation
1. Open the **IGM Belgovia**.
2. Load the **Equipment dataset**:
   - File: `Belgovia_EQ_1.xml`
3. Verify that the **SynchronousMachine** is available.

#### Step 2: Remedial Action Import
1. Load the **Remedial Action dataset**:
   - File: `Belgovia_RA.xml`
2. Verify the presence of the **RedispatchRemedialAction**:
   - rdf:ID: `_9d72d12a-f135-437a-83fa-ef3e5b23f41f`

#### Step 3: SIS and ER Dataset Import
1. Load the **SIS dataset**:
   - File: `Belgovia_SIS.xml`
2. Load the **Equipment Reliability dataset**:
   - File: `Belgovia_ER.xml`
3. Verify the presence of:
   - `PowerShiftKeyDistribution` rdf:ID `_7ab20445-576c-4162-aad5-d097d894a8e0`
   - `PowerShiftKeySchedule` rdf:ID `_3b5748de-39f2-45d7-9a66-65819c667e91`

#### Step 4: Consistency Check
1. Verify that the Power Shift Key objects are associated with the Redispatch Remedial Action.
2. Confirm that the distribution and schedule are consistent.
3. Check that the redispatch effect is correctly represented via power shift keys.

---

### Expected Outcome
- A Redispatch Remedial Action is correctly defined.
- Redispatch instructions are expressed either via **bid schedules** or **power shift key strategy**.
- Both variants represent valid and consistent modeling approaches.

---
