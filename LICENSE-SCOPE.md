# UADC-PoC License Scope

UADC-PoC uses separate licenses for executable logic and original semantic
content. A file's format or extension does not by itself determine the license;
the nature and source of the material do.

## Executable program logic — MIT License

The MIT License in [LICENSE-CODE](LICENSE-CODE) applies to first-party
executable program logic, including Python conversion, validation, generation,
input/output, command-line, and test-support logic. It also applies to
first-party executable logic in other formats, such as browser-side utility
code.

## Original semantic content — CC BY-SA 4.0

The terms in [LICENSE-CONTENT](LICENSE-CONTENT) apply to original first-party
meaning-bearing content, including:

- LHM definitions and Structured CSV schemas;
- syntax bindings, semantic bindings, join tables, relationship tables, and
  field mappings;
- transformation rules and semantic definitions;
- labels and translation dictionaries;
- original public samples; and
- documentation, diagrams, tables, and explanatory text.

This boundary follows the material into mixed files. Original semantic content
stored in Python constants, dictionaries, lists, tables, comments, or docstrings
is CC BY-SA 4.0; the executable logic around it remains MIT-licensed. The same
principle applies to generated source files that mix executable logic and
meaning-bearing definitions.

## Third-party material — original terms

No UADC-PoC license relicenses third-party material. This includes ISO standards
text, reproduced portions of EN 16931, AICPA ADS material, XBRL and XBRL GL
specifications or taxonomy material, OASIS UBL specifications or schemas,
OpenPeppol specifications or samples, and third-party code lists. Notices
shipped with third-party files remain controlling for those files.

### XBRL GL and XBRL GL Next prototype taxonomy

The accepted files under `taxonomy/business-transactions/`,
`taxonomy/accounting-entries/`, and the Business Transactions taxonomy root
HMD at
`models/gl-bus/business-transactions/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv`
are exact-byte copies from the accepted XBRL_GL_Next prototype family. They
are not relicensed as ordinary UADC-PoC CC BY-SA 4.0 content.

- Upstream XBRL GL-derived material remains subject to the XBRL International
  copyright, licence, attribution, trademark, and disclaimer conditions linked
  from [taxonomy/NOTICE_XBRL_GL.md](taxonomy/NOTICE_XBRL_GL.md).
- Identified XBRL_GL_Next project-authored documentation and artefact additions
  are licensed under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This grant does
  not extend to upstream XBRL GL material or other third-party content.
- These taxonomy and HMD files are published as prototype project artefacts,
  not as official XBRL International or XBRL Japan specifications.
- The XBRL Japan namespace URIs identify the accepted project namespace
  family; they do not imply organizational approval or endorsement.

The operative source and status notice is
[taxonomy/NOTICE_XBRL_GL.md](taxonomy/NOTICE_XBRL_GL.md), and the publication
decision is recorded in
[docs/decisions/ADR-XBRL-GL-NEXT-PROTOTYPE-TAXONOMY-PUBLICATION.md](docs/decisions/ADR-XBRL-GL-NEXT-PROTOTYPE-TAXONOMY-PUBLICATION.md).

## Classification by artefact type

| Artefact type | Applicable scope |
|---|---|
| First-party executable code | MIT under `LICENSE-CODE` |
| First-party documentation | CC BY-SA 4.0 under `LICENSE-CONTENT`, unless a file states different terms |
| First-party semantic definition CSV and bindings | CC BY-SA 4.0 under `LICENSE-CONTENT`, subject to third-party components and notices |
| HMD | Source-sensitive: UADC-authored HMD content follows `LICENSE-CONTENT`; the identified XBRL_GL_Next Business Transactions root HMD follows the XBRL GL/XBRL_GL_Next notice above |
| Generated or derived taxonomy | Inherits source rights; the accepted XBRL_GL_Next families follow `taxonomy/NOTICE_XBRL_GL.md` and are not wholly relicensed by UADC-PoC |
| Upstream XBRL GL material | XBRL International source terms, notice, attribution, trademark, and disclaimer conditions |
| Identified XBRL_GL_Next original additions | CC BY 4.0, without extending that licence to upstream or other third-party material |

Original UADC-PoC identifiers, annotations, cross-references, and mappings may
be CC BY-SA 4.0 even when they point to third-party material. That license covers
only the original selection, arrangement, annotation, or mapping; it does not
change the rights in the referenced standard text, definition, schema, code
list entry, or sample. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Samples and generated outputs

An original sample created for public demonstration is first-party content and
is covered by CC BY-SA 4.0. A third-party sample retains its original terms,
including when copied into a test fixture or transformed into another format.

Files under `out/`, generated PDFs, generated CSV files, generated XML/XBRL,
and other rendered artifacts inherit the rights and restrictions of their
inputs. Regeneration does not create a new license or remove an existing one.
Before publishing an output, identify whether it is:

1. mechanically regenerated from first-party sources;
2. an original public sample;
3. derived from third-party material; or
4. derived from non-public or restricted data.

Only the first two categories are intended for public release under the project
licenses, and only to the extent that they contain no third-party material with
different terms. Generated artifacts derived from third-party inputs must retain
applicable notices and restrictions.

## Private and restricted data

Real transaction data, personal data, confidential or secret information,
credentials, private keys, access tokens, certificates, machine-specific
configuration, and purchased or otherwise restricted standards text are not
public project content and are not licensed for publication. They must not be
placed in public samples, generated review artifacts, documentation, or release
packages.

## Resolving uncertainty

When material combines sources or its provenance is unclear, do not assume that
MIT or CC BY-SA 4.0 applies to the whole file. Preserve existing notices, consult
the source terms, and exclude the material from publication until its status is
resolved.
