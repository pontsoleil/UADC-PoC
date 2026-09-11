# Third-Party Notices

UADC-PoC implements, references, tests against, or transforms material associated
with the following standards and organizations. These references are provided
for identification and interoperability. The UADC-PoC MIT and CC BY-SA 4.0
licenses do not relicense third-party specifications, schemas, taxonomies, code
lists, samples, or excerpts.

| Third-party source | Use in this project | Rights statement |
|---|---|---|
| ISO standards, including ISO 21378 | Referenced by identifiers and used to design ADC target mappings | ISO standard text and purchased material remain subject to ISO and the applicable distributor's terms. Do not publish the standard text unless separately authorized. |
| EN 16931 | Business terms, groups, identifiers, and some definitions are referenced by the invoice LHM and mappings | Reproduced standard text remains subject to the rights and terms of the relevant standards bodies or authorized source. Original UADC-PoC mappings do not relicense that text. |
| AICPA Audit Data Standards (ADS) | Referenced by ADS definition tables and Phase 2 PSV/XBRL GL mappings | AICPA-provided documents, definitions, tables, and samples remain under AICPA's applicable terms. |
| XBRL International and XBRL GL | Specifications, namespaces, taxonomy structures, and referenced or generated XBRL artifacts | Third-party specifications and taxonomy components retain their published notices and license terms. Original UADC-PoC generator logic is MIT; original mappings and explanations are CC BY-SA 4.0. |
| OASIS Universal Business Language (UBL) | UBL Invoice syntax bindings, schemas, namespaces, and schema validation | OASIS specifications and schema files retain their OASIS notices and terms. Cached or copied schemas are not relicensed by this project. |
| OpenPeppol / Peppol BIS Billing | Profile rules, identifiers, and invoice examples used for conversion and regression testing | OpenPeppol specifications and samples retain their original terms and notices. Transformed test artifacts derived from those samples retain the same third-party status. |
| Third-party code lists | Currency and other controlled values used or referenced by bindings and validation | Each code list remains subject to its publisher's applicable conditions. Original project cross-references do not relicense the list. |
| W3C and other schema dependencies | XML, XML Schema, XML Signature, namespaces, or bundled dependencies referenced by UBL/XBRL artifacts | The corresponding specifications, schemas, and software licenses continue to apply. Preserve notices included with the material. |

## Repository handling

- Keep third-party copyright and license notices with the relevant material.
- Prefer links, reproducible acquisition instructions, or local caches over
  redistributing large or restricted source documents.
- Treat `out/cache/` and similar downloaded dependency locations as
  third-party caches, not as CC BY-SA 4.0 project content.
- Do not publish real data, confidential data, credentials, personal data, or
  purchased standards text.
- Review generated outputs by provenance: conversion or rendering does not
  replace the input material's license.

The absence of a row from this summary is not a grant of rights. Consult the
notice shipped with a specific file and the rightsholder's current terms before
redistribution.
