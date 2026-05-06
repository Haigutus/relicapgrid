
## Use Case: Availability Schedule

### Description
This use case describes an **Availability Remedial Action**, which is used to **cancel, shorten, or reschedule an availability schedule**, for example to cancel or reduce an outage.

Availability remedial actions are defined by referencing an **AvailabilitySchedule** and may optionally be used to temporarily modify operational limits.

---

### Context
For illustration purposes, readers can refer to the **Availability Schedule and Remedial Action datasets** of the fictitious **TSO Svedala**, available in the **ReliCapGrid GitHub repository**.

---

### Scenario Description
- An outage or unavailability is planned via an AvailabilitySchedule.
- A change is required to cancel, shorten, or reschedule this availability.
- The change is implemented via an **Availability Remedial Action**.
- Optionally, the same availability schedule may be used to alter operational limits through `AvailabilityExceptionalLimit`.

---

### Elements Involved

#### AvailabilitySchedule
- **File:** `Svedala_AS.xml`
- **rdf:ID:** `_d394295f-9d18-4d9f-9808-bd23282bf60f`
- Defines the original availability or outage schedule.

#### AvailabilityRemedialAction
- **File:** `Svedala_RA.xml`
- **rdf:ID:** `_14b2b671-e92b-40e6-abf8-ad37811b33c7`
- Cancels, shortens, or reschedules the associated AvailabilitySchedule.

---

### Optional: Operational Limit Modification
- Availability Remedial Actions may reference `AvailabilityExceptionalLimit`.
- This can be used, for example, to:
  - Enable or disable a current limit on an `ACLineSegment` terminal.
  - Derate limits due to fault conditions.
- This approach is **not recommended** for defining permanent or replacement limits.
  - For that purpose, the **Steady State Hypothesis profile** should be used instead.

---

### Validation Steps

#### Step 1: Model and Dataset Preparation
1. Open the **IGM Svedala**.
2. Load the **Availability Schedule dataset**:
   - `Svedala_AS.xml`
3. Verify that the AvailabilitySchedule is present.

#### Step 2: Remedial Action Import
1. Load the **Remedial Action dataset**:
   - `Svedala_RA.xml`
2. Verify that the AvailabilityRemedialAction is present.
3. Confirm that the remedial action references the correct AvailabilitySchedule.

#### Step 3: Schedule Effect Verification
1. Check whether the availability is:
   - Cancelled, or
   - Shortened, or
   - Rescheduled.
2. Verify that the resulting availability window matches the remedial action intent.


---

### Expected Outcome
- The original availability schedule is correctly cancelled, shortened, or rescheduled.

