---
title: Modelling Current Flow Conditions Against PATL or TATL
---

# Modelling Current Flow Conditions Against PATL or TATL

The test case should be performed as follows:

1)  Open the CGM model or [IGM Belgovia](https://github.com/entsoe-tso/relicapgrid/tree/main/Instance/Grid/IGM_Belgovia).

2)  Import the list of SIPS from Remedial Action Profile ([Belgovia_RA.xml](https://github.com/entsoe/relicapgrid/blob/cgmes-3.0_ncp-2.4_tc-1.1/Instance/NetworkCode/Belgovia/Belgovia_instance/Belgovia_RA.xml))

3)  Check if SIPS was uploaded correctly and the logic is as expected.

4)  Import the Contingency List from Contingency Profile ([Belgovia_CO_SIPS.xml](https://github.com/entsoe/relicapgrid/blob/cgmes-3.0_ncp-2.4_tc-1.1/Instance/NetworkCode/Belgovia/Belgovia_instance/Belgovia_CO.xml)).

5)  Change the TATL value for line BO-Line_6 in Alfavik substation to 110 -- name: tatl 600 for BO-Line_6 mRID: 524301ff-c48a-836e-f914-ed06ac42e2e1.

6)  Run contingency analysis including SIPS activation.

7)  Check if SIPS was triggered correctly:

- For contingency on line BO-Line_2 the current flow on line BO-Line_6 was higher than 110A and the line was disconnected by opening switches on both ends of the line.

Test data was prepared based on Belgovia individual grid model. The elements connected to the Alfavik substations were used:

- ![](images/media/image2.svg)

- The triggering action is the current flow on line BO-Line_6 exceeding the TATL limit (mRID 524301ff-c48a-836e-f914-ed06ac42e2e1) set in terminal to which the line is connected.

- To force higher flow (exceeding TATL) the line BO-Line_2 is disconnected (included in contingency list).

- The action was modelled by opening the switches on both ends of line BO-Line_6:

<!-- -->

- CIRCB-1230992408 (mRID: 0a84038e-1952-4d9d-9909-3b49c364a1ac)

CIRCB-1230992285 (mRID: ddc148fc-3abd-459d-aec1-396283e0def6)
