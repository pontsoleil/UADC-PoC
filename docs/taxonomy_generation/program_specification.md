# Program Specification: Taxonomy Generation

## 1. Purpose

This document specifies the taxonomy generation program used by the UADC Proof of Concept.

All paths in this document are relative to the repository root after the repository is pushed or cloned. The taxonomy generator is included in this repository; it no longer depends on an external `XBRL-GL-2026` checkout.

## 2. Scope

Input LHM:

```text
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

Taxonomy generator:

```text
tools/taxonomy/xBRLGL_TaxonomyGenerator.py
```

Output directory:

```text
out/taxonomy/
```

The output directory is generated local output and is not intended to be pushed to GitHub.

## 3. Component

Program:

```text
tools/taxonomy/xBRLGL_TaxonomyGenerator.py
```

Responsibilities:

- read the UADC LHM CSV layout through `csv.DictReader`;
- normalize UADC LHM records into the internal XBRL-GL generator layout;
- generate module taxonomy schema files;
- generate an xBRL-CSV dimensional taxonomy schema;
- generate label, presentation, definition linkbase, JSON metadata, and CSV skeleton files.

The generator accepts UADC LHM CSV headers directly. It also supports older XBRL-GL LHM layouts where compatible.

## 4. Input Contract

The generator consumes the generated LHM CSV:

```text
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

Required fields include:

```text
sequence
level
lhm_level
type
name
datatype
multiplicity
definition
module
class_term
id
path
semantic_path
element
xpath
```

Important interpretation rules:

- `module` becomes the module namespace prefix, currently `en16931`.
- `element` becomes the concept name.
- `type` controls whether a row is treated as a field or group for dimensional modeling.
- `multiplicity` is used for dimensional modeling.
- `level`, `path`, and `semantic_path` preserve the logical LHM hierarchy.
- `lhm_level` defines the effective hierarchy for xBRL-CSV taxonomy generation.
- BG rows with blank `lhm_level` are retained as semantic groupings but are not emitted as hypercube, dimension, or primary item concepts.
- BT rows are attached to the cube of the nearest ancestor BG with an `lhm_level`.

Allowed `multiplicity` values are `0..1`, `0..*`, `1..1`, and `1..*`. The LHM generation step normalizes source values such as `0..n` and `1..n` before taxonomy generation.

## 5. Taxonomy Output

The EN 16931 PoC output includes:

```text
out/taxonomy/en16931/en16931-2026-07-05.xsd
out/taxonomy/en16931/en16931-2026-07-05-presentation.xml
out/taxonomy/en16931/lang/en16931-2026-07-05-label.xml
out/taxonomy/en16931/lang/en16931-2026-07-05-label-ja.xml
out/taxonomy/gen/gl-gen-2026-07-05.xsd
out/taxonomy/plt/plt-def-2026-07-05.xml
out/taxonomy/plt/plt-oim-2026-07-05.xsd
```

### 5.1 Module schema

File pattern:

```text
out/taxonomy/<module>/<module>-<version>.xsd
```

For this PoC:

```text
out/taxonomy/en16931/en16931-2026-07-05.xsd
```

Responsibilities:

- declare item concepts for LHM Field rows;
- assign `xbrli:periodType="instant"` to `substitutionGroup="xbrli:item"` elements.
- import the GL generic type schema from `../gen/gl-gen-<version>.xsd` when a GL generic type is used.

### 5.2 Omitted tuple/content schemas

No XBRL 2.1 tuple taxonomy entry point or tuple/content schema is generated for this Structured CSV PoC. In particular, these files are not defined:

- `out/taxonomy/plt/plt-all-<version>.xsd`
- `out/taxonomy/plt/<module>-content-<version>.xsd`

### 5.3 GL generic type schema

File pattern:

```text
out/taxonomy/gen/gl-gen-<version>.xsd
```

Responsibilities:

- provide reusable GL item types such as `gen:amountItemType` and `gen:emailAddressItemType`;
- use the same version namespace as the generated taxonomy;
- be referenced from module schemas as `../gen/gl-gen-<version>.xsd`.

### 5.4 xBRL-CSV taxonomy schema

File pattern:

```text
out/taxonomy/plt/plt-oim-<version>.xsd
```

Responsibilities:

- define `h_*` hypercube concepts using `xbrldt:hypercubeItem`;
- define `d_*` dimension concepts using `xbrldt:dimensionItem`;
- define `p_*` primary item concepts using `xbrli:item`;
- define the typed dimension domain element `_v`;
- define role types used by the xBRL-CSV definition linkbase.

Restrictions:

- `plt-oim` must not define tuple-supporting `complexType`.
- `plt-oim` must not define `xbrli:tuple` concepts.
- `plt-oim` must not import the module content schema.

### 5.5 Definition linkbase

File pattern:

```text
out/taxonomy/plt/plt-def-<version>.xml
```

Responsibilities:

- reference `plt-oim` role types and dimensional concepts;
- connect primary items, hypercubes, and dimensions;
- represent BG-to-BG hierarchy using dimensional relationships for xBRL-CSV.

The definition linkbase locators for dimensional relationships point to `plt-oim`.

## 6. Validation Rules

The taxonomy regression checks verify that:

- `plt-oim` contains hypercube, dimension, and primary item definitions;
- `plt-oim` contains no `xbrli:tuple`;
- `plt-oim` contains no `complexType`;
- `plt-oim` does not import `en16931-content`;
- `plt-all` is not generated;
- `en16931-content` is not generated;
- module schemas import `../gen/gl-gen-<version>.xsd`;
- `xbrli:item` elements generated in `plt-oim` have `xbrli:periodType="instant"`.

## 7. Dependencies

Required:

- Python 3.10 or later.

## 8. Non-Goals

The taxonomy generation program does not:

- update LHM source CSV files;
- publish generated `out/` files to GitHub;
- validate the generated DTS with an external XBRL processor;
- validate xBRL-CSV instances beyond the regression checks.
