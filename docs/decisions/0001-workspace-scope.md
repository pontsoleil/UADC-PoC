# Decision 0001: Workspace Scope

The PoC workspace uses OpenPeppol BIS Billing 3.0 upcoming UBL Invoice as the
input syntax. The first semantic definition is an EN 16931 CIUS Invoice LHM/HMD
CSV.

`../XBRL-GL-2026` remains a historical reference workspace for UN/CEFACT CCL to
FSM/BSM/LHM/taxonomy experiments. The PoC taxonomy generator required for
tests is now copied into `tools/taxonomy/`, so this repository has no runtime
dependency on the external XBRL-GL-2026 workspace.
