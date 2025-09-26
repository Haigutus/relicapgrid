# ReliCapGrid Test Model Release 1.0.0

ICTC approved on 11 September 2025

## Introduction
This repository contains a synthetic grid model (fake, with no reference to real IGM/CGM elements)​ to which instances of the CIM-extension called "Network Code Profiles" developed at ENTSO-E refer to.

The aim is demonstrating ​practical TSO and RCC data exchange use cases for the purposes of the Regional Coordination Processes, namely the Coordinatied Security Analysis (CSA), Coordinated Capacity Calculation (CCC), Outage Planning Coordination (OPC) and the Short-Term Adequacy (STA).

More concretely, the grid model (both synthetic IGMs and CGM) is available under [Instance/Grid](https://github.com/entsoe-tso/relicapgrid/tree/main/Instance/Grid) folder. Similarly, the test Network Code Profiles instanced datasets can be found under [Instance/NetworkCode](https://github.com/entsoe-tso/relicapgrid/tree/main/Instance/NetworkCode). Additionally, ENTSO-E provides examples of the use of boundary configurations but they are not linked any of the previously mentioned test datasets under [Instance/BoundaryConfigurationExamples](https://github.com/entsoe-tso/relicapgrid/tree/main/Instance/BoundaryConfigurationExamples).

The Regional Coordination Processes Data Exchange Specification (RCP DES) complements the test model as this is the document describing use cases and general guidance on the use Network Code Profiles. Find this data exchange specification and more on the [ENTSO-E's CGMES Library](https://www.entsoe.eu/data/cim/cim-for-grid-models-exchange).

ENTSO-E continously collaborates with an ecosystem of TSOs, RCCs, regional projects and relevant industry software vendors. One of the outputs of this collaboration is the ReliCapGrid test model. Readers can consult the Accreditations section down below to see the list of people and organisations collaborating under the [CC-BY-SA-4.0 open-source License](https://github.com/entsoe-tso/relicapgrid/blob/main/LICENSE.md).

The following chapters describe the model content and it will continously improved in subsequent releases.

### How to provide feedback
When importing any data contained in the repository, you might find some bugs or issues to report. Please, open a GitHub issue and include your export log when applicable.

Do not forget to read [CONTRIBUTING](https://github.com/entsoe-tso/relicapgrid/blob/main/.github/CONTRIBUTING.adoc) file.

### License
Please, refer to the [LICENSE](https://github.com/entsoe-tso/relicapgrid/blob/main/LICENSE.md) for more information on the open-source license collaboration framework of the repository.

### Accreditations
List of the people and organisations contributing to this repository.

- [@tviegut](https://github.com/viegut) - AspenTech
- [@fmalicevicdigsilent](https://github.com/fmalicevicdigsilent) - DIgSILENT
- [@LarsTruelsenEnerginet](https://github.com/LarsTruelsenEnerginet) and (https://github.com/Holdersen)[@Holdersen] - Energinet
- [@griddigit-ci](https://github.com/griddigit-ci), [@Decodre](https://github.com/Decodre) and [@benceszirbik](https://github.com/benceszirbik) - gridDigIt
- [@jakubscg](https://github.com/jakubscg) - PSE
- [@pweaver-rte](https://github.com/pweaver-rte) - RTE
- [@sindrevh](https://github.com/sindrevh) - Siemens A.G.
- [@Sveino](https://github.com/Sveino) - Statnett
- [@emhg23](https://github.com/emhg23) - Svenska kraftnät
- [@dariaT-swissgrid](https://github.com/dariaT-swissgrid) - Swissgrid
- [@PavelKocica](https://github.com/PavelKocica) - Unicorn
- [@makkes](https://github.com/makkes) - Valimate

It must be mentioned that the synthetic grid model *Svedala* is based on [Svenska Kraftnät's](https://www.svk.se/) test model of the same name, which is licensed under [CC BY-SA 4-0 open-source license](https://creativecommons.org/licenses/by-sa/4.0/).

### The Grid Test Model
ReliCapGrid organisations are fake TSOs as it can be visualised in Figure 1 below:
- Espheim - developed based on legacy SmallGrid Test Configuration
- Svedala - developed based on Svenska Kraftnät's Svedala Test Configuration
- Belgovia - developed based on legacy MicroGrid Test Configuration
- Galia - developed based on legacy MicroGrid Test Configuration
- Nordheim - only one node
- Britheim - includes HVDC internal interconnection VSC and also some small grid 1-2 nodes
- Portheim
- HVDC Espheim-Svedala - an HVDC IGM LCC
- HVDC Nordheim-Galia - an HVDC IGM VSC Bipole

All of them are in a geographical region called *Nine Realms*. This information and more--like the voltage level of the transmission network--is available in the synthetic *Common Data* dataset that has been created for ReliCapGrid. As readers might guess, this intends to replicate the real (public), more extensive ENTSO-E Common Data dataset available on the [CGMES Library](https://www.entsoe.eu/data/cim/cim-for-grid-models-exchange/).

![Figure 1: Visualisation of ReliCapGrid's synthetic grid model](https://github.com/entsoe-tso/relicapgrid/blob/main/.github/Media/Readme_TheGridModel_1.PNG)

### The Network Code Instances
The *Nine Realms* region that ReliCapGrid represents also happens to be a capacity calculation region called *CCR-NineRealms* that has only one synchronous area *SyncArea-NineRealms*. 

The *SecurityCoordinator* and *CoordinatedCapacityCalculator* roles are represented by *Jotunheim* which in the real world, it could be assimilated to a Regional Coordinator Centre (RCC).

This information and more (e.g., BiddingZoneBorder) is again represented in the *Common Data* dataset that the Network Code Profiles instances use. A [synthetic common data dataset for the Network Code Profiles](https://github.com/entsoe-tso/relicapgrid/blob/main/Instance/NetworkCode/CommonData/NineRealms_CGM-CD.xml) has been created and it follows the roles defined in the PowerSystemOrganizationRole diagram of the EquipmentReliability profile (refer to Figure 2).

![Figure 2: roles defined in the PowerSystemOrganizationRole diagram of the EquipmentReliability profile](https://github.com/entsoe-tso/relicapgrid/blob/main/.github/Media/PowerSystemOrganizationRole.png)


### Currently demonstrated Network Code Profiles instances
Currently, four of the TSOs in NineRealms (Belgovia, Galia, Svedala and Espheim) have sent their [Network Code Profile instances](https://github.com/entsoe-tso/relicapgrid/tree/main/Instance/NetworkCode) that Jotunheim will use for coordination.

Namely, the AssessedElement (AE), Contingency (CO), EquipmentReliability (ER), RemedialAction (RA), RemedialActionSchedule (RAS), StateInstructionSchedule (SIS), SteadyStateInstruction (SSI) and ImpactAssessmentMatric (IAM) are demonstrated in the ReliCapGrid repository.

As already mentioned, ENTSO-E explains the use of the Network Code Profiles in the Regional Coordination Processes Data Exchange Specification.

The content of ReliCapGrid Network Code Profiles datasets' instances will be further developed and demonstrated in subsequent releases.

