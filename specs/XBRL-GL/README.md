# XBRL GL Specifications

This directory contains the XBRL GL tuple taxonomy definition table used by the
UADC PoC.

## Files

- `xbrl-gl.csv` - XBRL GL definition table aligned with
  `XBRL-GL-PWD-2016-12-01/gl/plt/case-c-b-m-u-e-t-s/gl-plt-all-2016-12-01.xsd`
  and the imported `gl-cor`, `gl-bus`, `gl-muc`, `gl-ehm`, `gl-taf`, `gl-srcd`,
  and `gl-usk` modules.

The table preserves existing English and Japanese labels where available, but
the sequence, module names, cardinalities, type names, and parent-child order
are normalized from the selected XBRL GL taxonomy profile.

The `XPath` column records the absolute tuple/fact path from `xbrli:xbrl`.
It is generated from the taxonomy parent-child tree so binding tables can point
directly to the target XBRL GL location without carrying internal row IDs.
