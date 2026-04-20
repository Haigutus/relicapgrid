# CIMXML to Trig Conversion and Fixes

These tools fix up CIMXML files so they can be loaded to a semantic database

See `../Instances/Makefile` for how to use them together.

The "end-user" command is:
```
cd Instance
make zip
```
This makes `relicapgrid-CGM-trig.zip` (4.1Mb at 20 Apr 2026) that can be loaded directly to GraphDB

## Tools
The tools were developed by Vladimir Alexiev (Graphwise) for ENTSO-E
and copied from https://github.com/Sveino/Inst4CIM-KG/tree/develop/rdf-improved :

- `fix-namespaces.pl`: Convert old `cim:` and `eu:` namespaces to the newest namespaces
  - Also fix the `dcterms:` namespace
  - Also remove the leadings space from " http://belgovia.bo/CGMES#" that makes it invalid URL
- `cim-urn-uuid.pl`: Convert CIMXML 
  under-defined URIs `rdf:ID="_<uuid>", rdf:about="#_<uuid>, rdf:resource="#_<uuid>` 
  to `urn:uuid:<uuid>`
- `cim-trig.pl`: Convert CIM XML file to Trig (Turtle with graphs). Invoke with option `-r` to call Jena riot
- `fix-datatypes-and-model.ru`:
  - Add datatypes to literals, so they can be properly compared and range searches can be faster
  - Convert `md,dm` to the newest `dcat:Dataset` metadata model, so it's the same as in

### Prerequisites
- make
- zip
- jena `riot` (used by `cim-trig.pl`)
- jena `update` (used by `fix-datatypes-and-model.ru`)
- perl and the following modules:
  - warnings
  - autodie
  - UUID
  - Getopt::Std
