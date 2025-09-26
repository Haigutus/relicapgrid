---
title: Implementing SIPS Gate Logic with Cardinality Constraints (Run-back Function on HVDC Link)
---
# Implementing SIPS Gate Logic with Cardinality Constraints (Run-back Function on HVDC Link)

The validation for this use case should be:

1)  Open the CGM model or [IGM Belgovia](https://github.com/entsoe-tso/relicapgrid/tree/main/Instance/Grid/IGM_Belgovia).

2)  Import the list of SIPS from Remedial Action Profile ([Belgovia_RA.xml](https://github.com/entsoe-tso/relicapgrid/blob/main/Instance/NetworkCode/Belgovia/Belgovia_instance/Belgovia_RA.xml))

3)  Check if SIPS was uploaded correctly and the logic is as expected.

4)  Import the Contingency List from Contingency Profile ([Belgovia_CO\_SIPS.xml](https://github.com/entsoe-tso/relicapgrid/blob/main/Instance/NetworkCode/Belgovia/Belgovia_instance/Belgovia_CO_SIPS.xml)).

5)  For Import power flow:

    a.  Check, if power flow on TieLine_GA_BO2 is towards Alfavik substation and is higher than 20 MW. If not increase the generated power on EquivalentInjection Injection_GA_BO2 to +30 MW.

    b.  Run contingency analysis including SIPS activation.

    c.  Check if SIPS was triggered correctly:

> for both contingencies from CO list (loss of line BO-Line_2 and BO-Line_6) the power in TieLine_GA_BO2 was decreased to 10 MW -- power on Injection_GA_BO2 was set to +10MW.

6)  For Export power flow:

    a.  Check, if power flow on TieLine_GA_BO2 is from Alfavik substation and is higher than 20 MW. If not increase the power consumption on EquivalentInjection Injection_GA_BO2 to -30 MW.

    b.  Run contingency analysis including SIPS activation.

    c.  Check if SIPS was triggered correctly:

> for both contingencies from CO list (loss of line BO-Line_2 and BO-Line_6) the power in TieLine_GA_BO2 was decreased to 10 MW -- power on Injection_GA_BO2 was set to -10MW.

To refer to HVDC link.

- EquivalentInjection is currently used.

- It could be explored to represent the full model

The triggering logic is using the contingencies.

- To refer to the Contingencies dataset and add new contingencies if there is something lacking.

Test data was prepared based on Belgovia individual grid model. All required elements are situated in Alfavik substation:

![](images/media/image2.svg)

As HVDC link, interconnection between Belgovia and Galia was used -- TieLine_GA_BO2 with EquivalentInjection Injection_GA_BO2 (mRID: 9dc33660-e284-4c74-bb9a-44604390634e).

Two contingencies on lines:

- BO-Line_2 (ACLineSegment b58bf21a-096a-4dae-9a01-3f03b60c24c7) and

- BO-Line_6 (ACLineSegment ffbabc27-1ccd-4fdc-b037-e341706c8d29)

were used as triggering events.

For that purpose, separate contingency list (Belgovia_CO_SIPS.xml) were prepared with two ordinary contingencies:

- on line BO-Line_2 (CO mRID 83ef276e-86ae-4d95-a877-6eb89d6ffd45);

- on line BO-Line_6 (CO mRID 2084c569-ff2f-4f21-b67e-720384ce23ba).

The SIPS model was prepared in separate file named: [Belgovia_RA_SIPS_UC2_Run-back.xml](https://github.com/entsoe-tso/relicapgrid/blob/main/Instance/NetworkCode/Belgovia/Belgovia_instance/SIPS/SIPS_UC2_Run-back_Belgovia.xml).
