# ADR — XBRL_GL_Next prototype taxonomy reuse and publication

Date: 2026-09-19<br>
Status: Accepted for Canonical WORK; Formal GIT and GitHub publication remain separate gates

## Context

UADC-PoC uses accepted Business Transactions and Accounting Entries taxonomy
families and a Business Transactions taxonomy root HMD from the XBRL_GL_Next
project. The project owner is responsible for publication of both repositories
and has confirmed that XBRL_GL_Next is a prototype rather than an official
specification. UADC-PoC uses the taxonomy on that stated basis.

The predecessor publication authorization review established:

- Business Transactions taxonomy: 67/67 accepted exact bytes;
- Accounting Entries taxonomy: 58/58 accepted exact bytes;
- Business Transactions root HMD: accepted exact bytes;
- byte identity: 127/127 for the reviewed population, including the separately
  reviewed UADC baseline document;
- namespace consistency: 127/127; and
- unresolved publication HOLD or UNKNOWN: zero.

The review evidence is maintained under
`docs/Codex/2026/202609/20260919/20260919_091051/publication-hold-authorization-review/outputs/`
in WORK. That task-local evidence is not itself a publication artefact.

## Decision

1. UADC-PoC uses the accepted XBRL_GL_Next Business Transactions 67-file and
   Accounting Entries 58-file families without regenerating or rewriting them.
2. The accepted project namespace family is
   `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`. No namespace rename
   is performed in UADC-PoC.
3. Directory labels such as `gl-bus` and `gl-cor` are repository organization
   names. They are not XML namespace URIs, prefixes, QNames, or namespace
   authority declarations.
4. XBRL_GL_Next and its taxonomy are prototype project artefacts, not official
   XBRL International or XBRL Japan specifications. Namespace use does not
   imply approval, endorsement, recognition, or official publication.
5. UADC-PoC may reuse and publish the accepted exact-byte taxonomy families and
   identified Business Transactions root HMD under the project owner's stated
   publication responsibility, subject to all upstream copyright, licence,
   attribution, trademark, and disclaimer conditions.
6. The XBRL International source notice and original XBRL GL taxonomy link are
   preserved in `taxonomy/NOTICE_XBRL_GL.md` and `THIRD_PARTY_NOTICES.md`.
7. CC BY 4.0 applies only to identified XBRL_GL_Next project-authored
   documentation and artefact additions. It does not relicense upstream XBRL
   GL or other third-party material.
8. Formal GIT registration, branch creation, commit, and push require their own
   exact-path/SHA plans and explicit authorization. This decision does not
   perform or authorize those later operations by itself.

## Consequences

- UADC-PoC publication materials must retain the prototype and non-endorsement
  statements and the source/licence links.
- `LICENSE-SCOPE.md`, `THIRD_PARTY_NOTICES.md`, and the repository `README.md`
  distinguish UADC first-party licensing from the XBRL GL/XBRL_GL_Next family.
- Accepted taxonomy and HMD bytes remain unchanged; documentation registration
  alone does not authorize regeneration or namespace edits.
- Task-local `docs/Codex/**` evidence remains WORK-only unless an exact path is
  separately authorized for publication.

## References

- [XBRL GL source notice](../../taxonomy/NOTICE_XBRL_GL.md)
- [Licence scope](../../LICENSE-SCOPE.md)
- [Third-party notices](../../THIRD_PARTY_NOTICES.md)
- [Repository README](../../README.md)
- [Original XBRL GL 2017 Public Working Draft](https://www.xbrl.org/int/gl/2016-12-01/gl-framework-2017-PWD-2016-12-01.html)
- [XBRL_GL_Next source project](https://github.com/pontsoleil/XBRL_GL_Next)
