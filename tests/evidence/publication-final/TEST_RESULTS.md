# Test results

Status: **PASS** (technical and publication gates).

- Deterministic publication generation: 2 runs, candidate payload SHA map equal.
- Taxonomy semantic delta: 70/70 XML artifacts identical after removal of added comments.
- Tuple DTS closure: 32 files, unresolved 0.
- OIM DTS closure: 26 files, unresolved 0.
- Old `http://www.xbrl.org/int/gl/` namespace in the 70 taxonomy XML artifacts: 0.
- XBRL GL NOTICE reference: 70/70 taxonomy XML artifacts.
- Taxonomy manifest: 70 rows, SHA mismatch 0.
- Arelle Tuple/OIM entry points and instances: error 0, warning 0 for all four targets.
- Clean clone: UBL → EN CSV → GL-BTX CSV/OIM → Tuple → GL-BTX → EN → GL-BTX; semantic/value/ordinal diff 0.
- UNCL 1001 D.24A member 380 QName retained; domain-member relationship/order unchanged.
- EntityParty declaration remains `0..1`; seller ordinal 1 and buyer ordinal 2 retained.
- EN definition and CII note remediation: all preserved columns unchanged; syntax output SHA unchanged (`5CB6C11C9E51B04BBB8702CEC6F531481348AD5787B6712C0741B342C992865B`).

Not rerun: existing 62-fact and selector unit suites, because mapping and semantic runtime bytes did not change.

Git publication is not executed because both Formal GIT repositories fail Git's dubious-ownership check in the current execution identity. Global `safe.directory` was not changed.
