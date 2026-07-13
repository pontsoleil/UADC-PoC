# LHM Generation Documentation

This directory documents how the EN 16931 invoice LHM is generated and reviewed.

## Files

- **program_specification.md** - Defines the LHM generation program behavior, input layout, output layout, semantic path rules, element naming rules, and **lhm_level** derivation.
- **user_guide.md** - Gives operator steps for regenerating the LHM CSV, checking output, and troubleshooting common issues.

## Related Directories

- **../../specs/lhm/source/** - Editable source CSV for controlled LHM changes.
- **../../specs/lhm/** - Generated/current LHM CSV used by conversion and taxonomy generation.
- **../../tools/** - LHM maintenance scripts, including source rebuild, coverage audit, class/element normalization, and syntax sequence utilities.

The Excel workbook used for human review is local-only and ignored by Git.
