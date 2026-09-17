# ADR — EN CIUS common semantic model and syntax-specific selector binding

Date: 2026-08-24<br>
Status: Accepted; repeatable composite Attributes use technical occurrence Classes and syntax-specific Class aliases

## Context

UBL 2.1 and UN/CEFACT CII D16B are physical syntaxes for the same EN 16931 semantic identities. Creating a syntax-specific HMD would duplicate BG/BT identities and would make Structured CSV unsuitable as a syntax-neutral interchange model.

CEN/TS 16931-3-3 also maps some single Business Terms to multiple CII locations. Blank ID cells continuing a preceding Table 2 row do not create a new Business Term.

## Decision

1. The EN CIUS Canonical HMD is the common authoritative semantic model for UBL and CII bindings.
2. Syntax-specific XML names, attributes, predicates, and selection rules remain in UBL or CII Syntax Binding tables and are not added to the HMD.
3. Existing EN identifiers are retained. Supplementary components use the CEN identifiers `BT-NN-1` and `BT-NN-2`; local alternatives such as `BT-NN-01` and `BT-NN-02` are not new semantic identities.
4. A CEN/TS Table 2 row with a blank ID is a continuation mapping of the preceding BG/BT unless other normative evidence establishes a separate semantic identity.
5. When one semantic fact has multiple physical representations, the binding may contain multiple rows with the same BT ID. Each row has one physical path and one XSD-derived `syntax_sequence`.
6. Syntax selection is represented in `semantic_path`, not in a new selector column. Removing the selector must resolve to exactly one canonical HMD `semantic_path`.
7. `[schemeIdentifier]` means that the paired Scheme identifier supplementary fact exists in the same technical-Class occurrence. `[not(schemeIdentifier)]` means that it is absent from that same technical-Class occurrence.
8. UBL does not require an identifier-path selector merely because `@schemeID` is present: the identifier value remains on the same `cbc:ID` element.
9. CII `GlobalID` is selected for an occurrence with a Scheme identifier and `ID` for an occurrence without one.

## Class-level syntax alias contract

A canonical semantic Class MAY have multiple syntax-specific Class Binding rows when a syntax provides alternative physical representations of the same semantic Class.

A **Class-level syntax alias** is one of two or more syntax-specific Binding rows representing alternative physical realisations of the same canonical semantic Class. The rows share the same selector-stripped canonical `semantic_path`, but may differ in selector, `syntax_path`, and `syntax_sequence`.

- An alias is not a new semantic identity and does not create a new BG or BT.
- One Binding row continues to represent exactly one `syntax_path` and one `syntax_sequence`; union syntax paths are prohibited.
- Multiple `type=C` Binding rows may resolve to the same canonical Class path.
- Canonical semantic Class identity is the selector-stripped canonical `semantic_path`.
- Binding row identity is `type + full semantic_path + syntax_path + syntax_sequence`; `semantic_path` alone is not a unique key for Class Binding rows.

Syntax variant selection is syntax-neutral. It is determined from the presence or absence of the corresponding semantic supplementary fact within the same canonical technical Class occurrence, not directly from an XML element name or attribute.

`[schemeIdentifier]` means that the applicable `BT-NN-1` Scheme identifier fact exists in the same technical Class occurrence. `[not(schemeIdentifier)]` means that this fact is absent from that occurrence. Neither selector may be evaluated at Party, Invoice, document, or row-adjacency scope.

For CIUS-to-syntax transformation, exactly one alias must match the semantic occurrence. A matching `schemeIdentifier` selects the CII `GlobalID` alias and its `@schemeID`; absence selects the CII `ID` alias. For syntax-to-CIUS transformation, alternative physical nodes are resolved into the canonical Class structure by the Binding selection rule. When both `GlobalID` and `ID` are present for the same Party in the selected CII profile, the `GlobalID` variant is selected and the `ID` node is not automatically added as another semantic occurrence.

Alias match cardinality is strict: one match is valid, zero matches is a transformation error, and more than one match is an ambiguity error. First-match, row-order, and implicit-priority fallbacks are prohibited.

Child Attribute Binding rows are evaluated relative to the selected or resolved parent Class alias occurrence. Consequently, an identifier value and its Scheme identifier attribute are extracted from or created on the same physical alias node.

## gl-btx Header Identifier Reference discriminator contract

The UADC Semantic Binding uses the XBRL GL Next Business Transactions `Header Identifier Reference` structure through three independent axes:

- `Identifier Type` is the entity or party-role discriminator;
- `Identifier Purpose` is the optional identifier-kind discriminator;
- `Registered Identifier / ID` is the identifier value, while `Registered Identifier / Identification Scheme` is the identifier scheme.

When `Identifier Purpose` is absent, the Registered Identifier represents the default or general identifier for the entity or role identified by `Identifier Type`. The EN CIUS mappings are:

- `IdentifierType="vendor"` and absent `IdentifierPurpose` → `BT-29` / `BT-29-1`;
- `IdentifierType="customer"` and absent `IdentifierPurpose` → `BT-46` / `BT-46-1`.

Special-purpose identifiers use an explicit `Identifier Purpose` within the same `Header Identifier Reference` occurrence:

- `vendor + legalRegistration` → `BT-30` / `BT-30-1`;
- `vendor + VAT` → `BT-31`;
- `vendor + taxRegistration` → `BT-32`.

The same generic contract applies to other party roles. For example, `customer + legalRegistration` represents `BT-47` / `BT-47-1` when those source facts are present.

Identifier scheme values such as `0188` and `0296` SHALL NOT be carried in `Identifier Purpose`. They belong to `Registered Identifier / Identification Scheme` in the same Registered Identifier occurrence as the applicable ID.

The selector `[not(btx_IdentifierPurpose)]` is a same-occurrence absence condition. It means that the selected `Header Identifier Reference` occurrence has no `btx_IdentifierPurpose` fact; it does not mean that all Header Identifier Reference occurrences lack a purpose.

Extensible `Identifier Type` value domains SHALL use XBRL Extensible Enumerations 1.0 (EE1). EE2 SHALL NOT be used in this UADC / Structured CSV transformation architecture. The current Seller and Buyer mappings use the existing `vendor` and `customer` values. Future values such as `payee`, `invoicer`, `taxRepresentative`, and `deliverTo` require an EE1 extension decision before use.

This is a UADC Semantic Binding discriminator contract. It neither adds an EN 16931 Business Term nor changes the EN CIUS HMD semantic identities. Selector literals are Binding data and SHALL NOT be embedded as BT-, EN-, CII-, or party-specific runtime conditionals.

## Repeatable composite Attribute occurrence contract

A repeatable Business Term whose semantic datatype has supplementary components is represented by a repeatable technical Class. The technical Class provides binding-neutral occurrence identity only and does not introduce a new EN BG/BT semantic identity.

The original Business Term and its supplementary components remain Attributes within the technical Class and retain their existing `BT-NN`, `BT-NN-1`, and `BT-NN-2` source identities. The value Attribute is mandatory once the technical Class occurrence exists. Supplementary Attributes retain their EN multiplicities within that occurrence.

The Structured CSV/OIM occurrence identity is the occurrence key generated for the repeatable technical Class. Pairing must not be inferred from row adjacency or an implicit syntax-specific link.

The reviewed 216-row HMD candidate contains three binding-neutral technical occurrence Classes:

- Seller Identifier;
- Buyer Identifier;
- Item Classification Identifier.

These Classes do not introduce new EN BG/BT semantic identities. The original semantic identities remain:

- `BT-29` and `BT-29-1`;
- `BT-46` and `BT-46-1`;
- `BT-158`, `BT-158-1`, and `BT-158-2`.

The technical Classes provide occurrence identity for repeatable composite semantic values. The generated OIM occurrence keys are:

- `plt:d_en16931_SellerIdentifier`;
- `plt:d_en16931_BuyerIdentifier`;
- `plt:d_en16931_ItemClassificationIdentifier`.

The repeatable composite occurrence contract is also applied to Buyer Identifier. The Buyer Identifier technical Class is repeatable and contains BT-46 as its mandatory Identifier Attribute and BT-46-1 as its optional Scheme identifier Attribute. It provides occurrence identity only and does not introduce a new EN BG/BT semantic identity.

The mixed-occurrence OIM proofs passed and confirmed that multiple Seller Identifier, Buyer Identifier, and Item Classification Identifier occurrences can be represented independently without row-adjacency inference. Scheme identifier facts remain associated with the applicable technical-Class occurrence. The previous repeatable-Attribute occurrence blocker is therefore resolved for these reviewed structures.

The reviewed 216-row HMD candidate is the authoritative task input for subsequent UBL/CII Binding and transformation validation. It is not yet promoted to the production/canonical HMD.

The generated taxonomy remains task-local until separately reviewed and promoted.

## Consequences

The occurrence-identity architecture gate is resolved for Seller Identifier, Buyer Identifier, and Item Classification Identifier. The gl-btx Header Identifier Reference discriminator contract is also fixed for general, legal-registration, VAT, and tax-registration identifiers. Subsequent work may proceed with UBL/CII binding materialisation, `semantic_path` selector implementation, cross-syntax transformation tests, and gl-btx roundtrip using the reviewed 216-row HMD candidate as the task input. Production promotion remains subject to successful completion of those validations.

## CEN/TS formal CII authority and generic runtime promotion (2026-08-26)

- CEN/TS 16931-3-3:2020 Table 2 is the authoritative source for the CII D16B Syntax Binding. Table 3 is an inverse and coverage reference and does not override Table 2.
- The formally reviewed corrected Binding has 237 rows and SHA-256 `B529F2585CA2A5FBFDAF673A6F96B98135CE274B8B022C1B791FF9863C23BD23` at `specs/bindings/syntax/EN16931_CII_D16B_Invoice_Syntax_Binding.csv`.
- All 237 rows and all 13 corrections passed formal review. Selector-stripped paths and supplementary components resolve to one existing EN HMD BG/BT identity; they do not extend the EN semantic model.
- Syntax-only F rows, required empty containers, fixed and nested predicate materialisation, alias-relative child paths, named transformations, XSD-derived child ordering and strict ambiguity errors are generic Binding/runtime capabilities. CII-specific physical structures remain declarative Binding data.
- The approved generic runtime SHA-256 is `4D9A163D157C223DCF5FDC68924A08D2BF9CF1AC745AA24D288E57ECF6FF7E3F` at `src/syntax_binding.py`.
