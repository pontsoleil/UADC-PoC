import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/Users/nobuy/GitHub/WORK/UADC_PoC";
const baseOutputDir = `${root}/Specifications/UADC_Transformation_Examples`;
const hmdCopyDir = `${root}/docs/ChatGPT/202608/20260814/XBRL_GL_Next_HMD`;
const invoiceDir = `${baseOutputDir}/Invoice`;
const outputDir = `${baseOutputDir}/Journal_Entry`;
const previewDir = `${baseOutputDir}/_review_previews`;
const sourceWorkbookPath = `${root}/private/legacy_sources/accounting/pca/bindings/PCA_GL_Binding_v3_draft.xlsx`;
const sourceHmdPath = `${root}/private/legacy_sources/accounting/lhm/JP_LHM.csv`;
const sourceBindingSetPath = `${root}/private/legacy_sources/accounting/pca/bindings/binding_set.json`;
const xbrlGlDefinitionPath = `${root}/specs/XBRL-GL/xbrl-gl.csv`;
const xbrlGlNextRoot = "C:/Users/nobuy/GitHub/WORK/XBRL-GL-Next/semantic-model/LHM_for_taxonomy";
const corHmdSourcePath = `${xbrlGlNextRoot}/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`;
const btxHmdSourcePath = `${xbrlGlNextRoot}/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv`;
const mappingParametersPath = `${root}/private/legacy_sources/accounting/ledger_explorer/config/parameters.mapping.work.json`;
const explorerParametersPath = `${root}/private/legacy_sources/accounting/ledger_explorer/config/parameters.ledger_explorer.work.json`;

const names = {
  hmdCsv: "cor_Accounting_Entries_Journal_Entry_HMD_semantic_path_20260814.csv",
  hmdXlsx: "cor_Accounting_Entries_Journal_Entry_HMD_semantic_path_Part1_revised_20260814.xlsx",
  bindingCsv: "cor_Accounting_Entries_PCA_GL_flat_csv_semantic_path_binding_20260814.csv",
  bindingXlsx: "cor_Accounting_Entries_PCA_GL_flat_csv_semantic_path_binding_Part1_revised_20260814.xlsx",
  legacyCsv: "cor_Accounting_Entries_PCA_GL_legacy_semantic_path_crosswalk_20260814.csv",
  bindingSet: "cor_Accounting_Entries_PCA_GL_semantic_path_binding_set_20260814.json",
  mappingParams: "parameters.mapping.cor_accounting_entries.semantic_path.20260814.json",
  explorerParams: "parameters.ledger_explorer.cor_accounting_entries.semantic_path.20260814.json",
  manifest: "cor_Accounting_Entries_Journal_Entry_manifest_20260814.csv",
  readme: "README_cor_Accounting_Entries_Journal_Entry_20260814.md",
};

const canonicalSegmentOverrides = new Map([
  ["JP07a", "journalEntry"],
  ["JP08a", "journalEntryLine"],
  ["JP05a", "debitSubsidiaryLedgerAccount"],
  ["JP05b", "creditSubsidiaryLedgerAccount"],
]);

const D = '[cor_DebitCreditIndicator="D"]';
const C = '[cor_DebitCreditIndicator="C"]';
const corBase = "$.cor_AccountingEntries.cor_EntryHeader";
const debitDetail = `${corBase}.cor_EntryDetail${D}`;
const creditDetail = `${corBase}.cor_EntryDetail${C}`;
const corTargetById = new Map([
  ["JP07a", corBase],
  ["JP08a", `${corBase}.cor_EntryDetail`],
  ["JP07a_GL03_03", `${corBase}.cor_DatePosted`],
  ["JP07a_GL03_01", `${corBase}.cor_EntryID`],
  ["GE23c_01", `${corBase}.cor_TypeCode`],
  ["BS04fb", debitDetail],
  ["JP05a", debitDetail],
  ["BS04fc", creditDetail],
  ["JP05b", creditDetail],
  ["GE05ku_01", `${debitDetail}.cor_MonetaryAmount`],
  ["GE05kz_01", `${creditDetail}.cor_MonetaryAmount`],
  ["JP08a_GL04_03", `${corBase}.cor_EntryDetail.cor_DetailDescription`],
  ["GL05c_01", `${corBase}.cor_EntryOrigin`],
  ["GE09eR_01", `${corBase}.cor_HeaderEntryDate`],
]);

function normalizeModuleSemanticPath(value) {
  return text(value).split(".").map((segment) => {
    if (!segment || segment === "$") return segment;
    const predicateAt = segment.indexOf("[");
    const node = predicateAt >= 0 ? segment.slice(0, predicateAt) : segment;
    const predicate = predicateAt >= 0 ? segment.slice(predicateAt) : "";
    const separator = node.indexOf("_");
    if (separator < 0) return node.replace(/[\s_\/]+/g, "") + predicate;
    const moduleName = node.slice(0, separator);
    const elementName = node.slice(separator + 1).replace(/[\s_\/]+/g, "");
    return `${moduleName}_${elementName}${predicate}`;
  }).join(".");
}

const colors = {
  navy: "#1F4E78",
  blue: "#D9EAF7",
  teal: "#0F6B78",
  tealLight: "#DDEBF0",
  gold: "#F4B183",
  green: "#E2F0D9",
  red: "#FCE4D6",
  gray: "#E7E6E6",
  white: "#FFFFFF",
  text: "#1F2937",
};

function text(value) {
  return value === null || value === undefined ? "" : String(value);
}

async function readJsonAnyEncoding(filePath) {
  const bytes = await fs.readFile(filePath);
  let decoded;
  if (bytes[0] === 0xFF && bytes[1] === 0xFE) decoded = bytes.subarray(2).toString("utf16le");
  else if (bytes[0] === 0xFE && bytes[1] === 0xFF) throw new Error(`UTF-16BE JSON is not supported: ${filePath}`);
  else decoded = bytes.toString("utf8").replace(/^\uFEFF/, "");
  return JSON.parse(decoded);
}

function lowerCamelCaseConcatenated(term) {
  const words = text(term).match(/[A-Za-z0-9]+/g) ?? [];
  if (!words.length) return "unnamed";
  const first = words[0].toLowerCase();
  const rest = words.slice(1).map((word) => word.slice(0, 1).toUpperCase() + word.slice(1).toLowerCase());
  let value = first + rest.join("");
  if (/^[0-9]/.test(value)) value = `n${value.slice(0, 1).toUpperCase()}${value.slice(1)}`;
  return value;
}

function terminalBusinessTerm(semanticPath, fallback) {
  const source = text(semanticPath).replace(/^\$\./, "");
  const parts = [];
  let current = "";
  let depth = 0;
  for (const char of source) {
    if (char === "(" ) depth += 1;
    if (char === ")" && depth > 0) depth -= 1;
    if (char === "." && depth === 0) {
      parts.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  if (current) parts.push(current);
  return parts.at(-1) || fallback;
}

function csvEscape(value) {
  const s = text(value);
  return /[",\r\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

function toCsv(headers, rows) {
  return [headers, ...rows.map((row) => headers.map((header) => row[header] ?? ""))]
    .map((row) => row.map(csvEscape).join(","))
    .join("\r\n") + "\r\n";
}

function rowsFromMatrix(matrix) {
  const headers = matrix[0].map(text);
  return matrix.slice(1).map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
}

function colName(index) {
  let result = "";
  for (let n = index + 1; n > 0; n = Math.floor((n - 1) / 26)) result = String.fromCharCode(65 + ((n - 1) % 26)) + result;
  return result;
}

function setTableStyle(sheet, rowCount, colCount, widths = {}) {
  const end = colName(colCount - 1);
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  sheet.getRange(`A1:${end}1`).format = {
    fill: colors.navy,
    font: { bold: true, color: colors.white, typeface: "Aptos Display", fontSize: 10 },
    wrapText: true,
    verticalAlignment: "center",
    borders: { bottom: { style: "medium", color: colors.navy } },
  };
  sheet.getRange(`A1:${end}${rowCount}`).format.font = { typeface: "Aptos", fontSize: 9, color: colors.text };
  sheet.getRange(`A2:${end}${rowCount}`).format.borders = {
    insideHorizontal: { style: "thin", color: "#E5E7EB" },
  };
  sheet.getRange(`A1:${end}${rowCount}`).format.wrapText = false;
  sheet.getRange(`A1:${end}1`).format.rowHeight = 32;
  for (const [column, width] of Object.entries(widths)) sheet.getRange(`${column}:${column}`).format.columnWidth = width;
}

function makeReadmeSheet(workbook, title, subtitle, facts, notes) {
  const sheet = workbook.worksheets.add("README");
  sheet.showGridLines = false;
  sheet.getRange("A1:H2").merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1:H2").format = {
    fill: colors.navy,
    font: { bold: true, color: colors.white, typeface: "Aptos Display", fontSize: 18 },
    verticalAlignment: "center",
  };
  sheet.getRange("A3:H3").merge();
  sheet.getRange("A3").values = [[subtitle]];
  sheet.getRange("A3:H3").format = { fill: colors.blue, font: { italic: true, color: colors.text }, wrapText: true };
  sheet.getRange("A5:B5").values = [["Property", "Value"]];
  sheet.getRange(`A6:B${5 + facts.length}`).values = facts;
  sheet.getRange("A5:B5").format = { fill: colors.teal, font: { bold: true, color: colors.white } };
  sheet.getRange(`A5:B${5 + facts.length}`).format.borders = { insideHorizontal: { style: "thin", color: "#D1D5DB" } };
  const noteStart = 7 + facts.length;
  sheet.getRange(`A${noteStart}:H${noteStart}`).merge();
  sheet.getRange(`A${noteStart}`).values = [["Conformance and handling notes"]];
  sheet.getRange(`A${noteStart}:H${noteStart}`).format = { fill: colors.tealLight, font: { bold: true, color: colors.text } };
  notes.forEach((note, i) => {
    const row = noteStart + 1 + i;
    sheet.getRange(`A${row}:H${row}`).merge();
    sheet.getRange(`A${row}`).values = [[`• ${note}`]];
    sheet.getRange(`A${row}:H${row}`).format = { wrapText: true, verticalAlignment: "top" };
    sheet.getRange(`A${row}:H${row}`).format.rowHeight = 30;
  });
  sheet.getRange("A:A").format.columnWidth = 25;
  sheet.getRange("B:B").format.columnWidth = 70;
  sheet.getRange("C:H").format.columnWidth = 14;
  return sheet;
}

function addDataSheet(workbook, name, headers, rows, tableName, widths = {}) {
  const sheet = workbook.worksheets.add(name);
  const matrix = [headers, ...rows.map((row) => headers.map((header) => row[header] ?? ""))];
  sheet.getRangeByIndexes(0, 0, matrix.length, headers.length).values = matrix;
  setTableStyle(sheet, matrix.length, headers.length, widths);
  sheet.tables.add(`A1:${colName(headers.length - 1)}${matrix.length}`, true, tableName).style = "TableStyleMedium2";
  return sheet;
}

async function renderWorkbook(workbook, workbookStem, sheetRanges) {
  await fs.mkdir(previewDir, { recursive: true });
  for (const [sheetName, range] of Object.entries(sheetRanges)) {
    const preview = await workbook.render({
      sheetName,
      range,
      autoCrop: "all",
      scale: 0.8,
      format: "png",
    });
    await fs.writeFile(`${previewDir}/${workbookStem}_${sheetName}.png`, new Uint8Array(await preview.arrayBuffer()));
  }
}

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(hmdCopyDir, { recursive: true });
await fs.copyFile(corHmdSourcePath, `${hmdCopyDir}/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`);
await fs.copyFile(btxHmdSourcePath, `${hmdCopyDir}/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv`);
await fs.writeFile(`${hmdCopyDir}/README_XBRL_GL_Next_HMD_copies_20260814.md`, `# XBRL GL Next HMD copies

These are unchanged review copies from the private XBRL-GL-Next WORK tree:

- \`XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv\` — \`cor\` / Accounting Entries
- \`XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv\` — \`btx\` / Business Transactions

The copied source HMDs preserve their original semantic paths. The UADC example package normalizes spaces, underscores inside element terms, and punctuation according to the current Part 1 naming discussion; module-to-element separation remains a single underscore (for example, \`cor_EntryHeader\`).
`, "utf8");

// Read the original HMD with artifact-tool so quoting and embedded commas are preserved.
const hmdSourceWorkbook = await Workbook.fromCSV((await fs.readFile(sourceHmdPath, "utf8")).replace(/^\uFEFF/, ""), { sheetName: "HMD" });
const hmdSourceMatrix = hmdSourceWorkbook.worksheets.getItem("HMD").getUsedRange(true).values;
const originalHmdRows = rowsFromMatrix(hmdSourceMatrix);

const segmentById = new Map(originalHmdRows.map((row) => [
  text(row.id),
  canonicalSegmentOverrides.get(text(row.id)) ?? lowerCamelCaseConcatenated(terminalBusinessTerm(row.semantic_path, row.name)),
]));
const canonicalById = new Map();
const canonicalByAbbreviation = new Map();
const allCanonicalHmdRows = originalHmdRows.map((row) => {
  const identifiers = text(row.path).split("/").filter(Boolean);
  const segments = identifiers.map((identifier) => segmentById.get(identifier)).filter(Boolean);
  const localPath = (segments.length ? segments : [lowerCamelCaseConcatenated(row.name)]).join(".");
  const semanticPath = text(row.path).startsWith("/JP07a")
    ? `$.jp_AccountingEntries.${localPath}`
    : `$.${localPath}`;
  canonicalById.set(text(row.id), semanticPath);
  canonicalByAbbreviation.set(text(row.abbreviation_path), semanticPath);
  return {
    sequence: row.sequence,
    level: row.level,
    type: row.type,
    identifier: row.identifier,
    name: row.name,
    datatype: row.datatype,
    multiplicity: row.multiplicity,
    domain_name: row.domain_name,
    definition: row.definition,
    module: row.module,
    table: row.table,
    class_term: row.class_term,
    id: row.id,
    path: row.path,
    semantic_path: semanticPath,
    legacy_semantic_path: row.semantic_path,
    abbreviation_path: row.abbreviation_path,
  };
});
let hmdRows = allCanonicalHmdRows.filter((row) => text(row.path).startsWith("/JP07a"));
for (const row of originalHmdRows) {
  if (corTargetById.has(text(row.id))) {
    canonicalById.set(text(row.id), corTargetById.get(text(row.id)));
    canonicalByAbbreviation.set(text(row.abbreviation_path), corTargetById.get(text(row.id)));
  }
}

// Canonical HMD rows come from the authoritative XBRL GL Next Accounting Entries HMD.
const corHmdWorkbook = await Workbook.fromCSV((await fs.readFile(corHmdSourcePath, "utf8")).replace(/^\uFEFF/, ""), { sheetName: "COR_HMD" });
const corHmdRows = rowsFromMatrix(corHmdWorkbook.worksheets.getItem("COR_HMD").getUsedRange(true).values);
const requiredBsmIds = new Set(["CO23", "CO23-03", "CO22-01", "CO22-05", "CO22-09", "CO22-12", "CO22-13", "CO22-39", "CO21-01", "CO21-13", "CO21-20", "CO21-21", "CO21-24"]);
hmdRows = corHmdRows.filter((row) => requiredBsmIds.has(text(row.source_bsm_id))).map((row) => ({
  sequence: row.sequence,
  level: row.level,
  type: row.type,
  identifier: row.identifier,
  name: row.name,
  datatype: row.datatype,
  multiplicity: row.multiplicity,
  domain_name: row.association_role,
  definition: row.definition,
  module: row.module,
  table: "",
  class_term: row.class_term,
  id: row.source_bsm_id,
  path: row.xpath,
  semantic_path: normalizeModuleSemanticPath(row.semantic_path),
  legacy_semantic_path: row.xpath,
  abbreviation_path: row.local_name,
}));

function canonicalizeSelector(selector) {
  let value = text(selector);
  if (!value) return "";
  const candidates = [...canonicalByAbbreviation.keys()].filter(Boolean).sort((a, b) => b.length - a.length);
  for (const abbreviation of candidates) {
    if (value.includes(abbreviation)) value = value.replaceAll(abbreviation, canonicalByAbbreviation.get(abbreviation));
  }
  return value;
}

// Read the original multi-sheet mapping workbook with artifact-tool.
const sourceWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(sourceWorkbookPath));
const sourceRows = rowsFromMatrix(sourceWorkbook.worksheets.getItem("v3_sources").getUsedRange(true).values);
const hierarchySourceRows = rowsFromMatrix(sourceWorkbook.worksheets.getItem("v3_hierarchy").getUsedRange(true).values);
const bindingSourceRows = rowsFromMatrix(sourceWorkbook.worksheets.getItem("v3_semantic_binding").getUsedRange(true).values);
const joinSourceRows = rowsFromMatrix(sourceWorkbook.worksheets.getItem("v3_joins").getUsedRange(true).values);
const legacySourceRows = rowsFromMatrix(sourceWorkbook.worksheets.getItem("Current_bindingPCA_GL").getUsedRange(true).values);

const hierarchyRows = hierarchySourceRows.map((row) => {
  const hierarchyHmd = originalHmdRows.find((item) => text(item.abbreviation_path) === text(row.semanticPath));
  const semanticPath = corTargetById.get(text(hierarchyHmd?.id)) ?? "";
  const parentHmd = originalHmdRows.find((item) => text(item.abbreviation_path) === text(row.parentSemanticPath));
  return {
    sequence: row.sequence,
    source_key: row.sourceKey,
    group_column: row.groupColumn,
    name: row.name,
    multiplicity: row.multiplicity,
    id: hierarchyHmd?.id ?? "",
    semantic_path: semanticPath,
    occurrence_mode: text(row.groupColumn) === "dColumn2" || text(row.groupColumn) === "dColumn27" ? "keyed_rows" : "single",
    group_key: text(row.groupColumn) === "dColumn2" ? '["Column2"]' : text(row.groupColumn) === "dColumn27" ? '["Column2","__source_row__"]' : "",
    row_role: text(row.groupColumn) === "dColumn27" ? "driver" : "context",
    parent_semantic_path: corTargetById.get(text(parentHmd?.id)) ?? "",
    enabled: row.enabled,
    migration_note: semanticPath ? "Migrated to the module-qualified XBRL GL Next semantic path; any predicate is encoded directly in semantic_path." : row.migrationNote,
  };
});

const bindingRows = bindingSourceRows.map((row) => {
  const old = text(row.semanticPath);
  const mappedId = text(originalHmdRows.find((item) => text(item.abbreviation_path) === old)?.id);
  const semanticPath = corTargetById.get(mappedId) ?? "";
  const hmd = originalHmdRows.find((item) => text(item.abbreviation_path) === old);
  const mappedStatus = semanticPath ? "mapped" : old ? "extension_required" : "unmapped";
  return {
    column: row.column,
    source_ordinal: row.sourceOrdinal,
    source_column_letter: row.sourceColumnLetter,
    name: row.name,
    multiplicity: row.multiplicity,
    datatype: row.Representation,
    semantic_sort: row.semSort,
    id: hmd?.id ?? "",
    path: hmd?.path ?? "",
    semantic_path: semanticPath,
    structured_csv_column: semanticPath ? semanticPath.split(".").at(-1) : "",
    fixed_value: row.fixedValue,
    mapping_status: mappedStatus,
    migration_note: mappedStatus === "extension_required" ? "No corresponding element was confirmed in the current XBRL GL Next Accounting Entries HMD; define a JP extension or revise the mapping." : row.migrationNote,
  };
});

const joinRows = joinSourceRows.map((row) => ({
  join_key: row.joinKey,
  parent_source_key: row.parentSourceKey,
  child_source_key: row.childSourceKey,
  parent_key_expression: row.parentKeyExpression,
  child_key_expression: row.childKeyExpression,
  cardinality: row.cardinality,
  output_semantic_path: canonicalByAbbreviation.get(text(row.outputSemanticPath)) ?? "",
  enabled: row.enabled,
  note: row.note,
}));

const legacyRows = legacySourceRows.map((row) => ({
  column: row.column,
  name: row.name,
  multiplicity: row.multiplicity,
  datatype: row.Representation,
  semantic_sort: row.semSort,
  id: row.id,
  path: row.path,
  semantic_path: corTargetById.get(text(row.id)) ?? "",
  legacy_selector: canonicalizeSelector(row.value || row.line),
  fixed_value: row.fixedValue,
  legacy_sem_path: row.semPath,
  legacy_label_path: row.term,
  mapping_status: corTargetById.get(text(row.id)) ? "mapped" : text(row.id) ? "extension_required" : "unmapped",
  note: row.migrationNote || "",
}));

const sourceRowsCanonical = sourceRows.map((row) => ({
  source_key: row.sourceKey,
  role: row.role,
  file_pattern: row.filePattern,
  encoding: row.encoding,
  delimiter: row.delimiter,
  header_rows: row.headerRows,
  record_selector: row.recordSelector,
  description: row.description,
  enabled: row.enabled,
}));

const hmdHeaders = ["sequence", "level", "type", "identifier", "name", "datatype", "multiplicity", "domain_name", "definition", "module", "table", "class_term", "id", "path", "semantic_path", "legacy_semantic_path", "abbreviation_path"];
const bindingHeaders = ["column", "source_ordinal", "source_column_letter", "name", "multiplicity", "datatype", "semantic_sort", "id", "path", "semantic_path", "structured_csv_column", "fixed_value", "mapping_status", "migration_note"];
const hierarchyHeaders = ["sequence", "source_key", "group_column", "name", "multiplicity", "id", "semantic_path", "occurrence_mode", "group_key", "row_role", "parent_semantic_path", "enabled", "migration_note"];
const legacyHeaders = ["column", "name", "multiplicity", "datatype", "semantic_sort", "id", "path", "semantic_path", "legacy_selector", "fixed_value", "legacy_sem_path", "legacy_label_path", "mapping_status", "note"];

await fs.writeFile(`${outputDir}/${names.hmdCsv}`, "\ufeff" + toCsv(hmdHeaders, hmdRows), "utf8");
await fs.writeFile(`${outputDir}/${names.bindingCsv}`, "\ufeff" + toCsv(bindingHeaders, bindingRows), "utf8");
await fs.writeFile(`${outputDir}/${names.legacyCsv}`, "\ufeff" + toCsv(legacyHeaders, legacyRows), "utf8");

const hmdWorkbook = Workbook.create();
makeReadmeSheet(
  hmdWorkbook,
  "cor / Accounting Entries — Journal Entry HMD",
  "Part 1 semantic_path review copy extracted from the XBRL GL Next Accounting Entries HMD; paths preserve module-qualified names such as cor_AccountingEntries.",
  [
    ["Status", "Framework-aligned review copy"],
    ["Canonical key", "semantic_path"],
    ["Canonical pattern", "$.cor_AccountingEntries.cor_EntryHeader.cor_EntryDetail"],
    ["Source", "XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv (copied unchanged under ../../XBRL_GL_Next_HMD)"],
    ["Generated", "2026-08-14"],
  ],
  [
    "semantic_path is copied from the XBRL GL Next HMD and normalized so the underscore separates module and element only; spaces, embedded underscores, and punctuation within an element term are removed.",
    "legacy_semantic_path preserves the source XPath and abbreviation_path preserves the source local_name as traceability references; semantic_path is the canonical binding key.",
  "Definitions and third-party terminology retain their original rights; this review copy does not relicense referenced standards.",
    "No accounting instance data, master data, credentials, or purchased standards text is included.",
  ],
);
const hmdSheet = addDataSheet(hmdWorkbook, "HMD", hmdHeaders, hmdRows, "JPAccountingHMD", { A: 10, B: 7, C: 7, D: 12, E: 28, F: 15, G: 12, H: 20, I: 50, J: 10, K: 8, L: 35, M: 22, N: 38, O: 70, P: 70, Q: 55 });
hmdSheet.freezePanes.freezeColumns(5);
const hmdValidation = hmdWorkbook.worksheets.add("Validation");
hmdValidation.showGridLines = false;
hmdValidation.getRange("A1:D1").merge();
hmdValidation.getRange("A1").values = [["HMD conformance checks"]];
hmdValidation.getRange("A1:D1").format = { fill: colors.navy, font: { bold: true, color: colors.white, fontSize: 15 } };
hmdValidation.getRange("A3:C7").values = [
  ["Check", "Result", "Expected"],
  ["Rows", "", hmdRows.length],
  ["Blank semantic_path", "", 0],
  ["Non-Part-1 prefix", "", 0],
  ["Duplicate semantic_path", "", 0],
];
hmdValidation.getRange("B4").formulas = [[`=COUNTA(HMD!A2:A${hmdRows.length + 1})`]];
hmdValidation.getRange("B5").formulas = [[`=COUNTBLANK(HMD!O2:O${hmdRows.length + 1})`]];
hmdValidation.getRange("B6").values = [[hmdRows.filter((row) => !text(row.semantic_path).startsWith("$.cor_AccountingEntries")).length]];
hmdValidation.getRange("B7").values = [[hmdRows.length - new Set(hmdRows.map((row) => text(row.semantic_path))).size]];
hmdValidation.getRange("A3:C3").format = { fill: colors.teal, font: { bold: true, color: colors.white } };
hmdValidation.getRange("A3:C7").format.borders = { insideHorizontal: { style: "thin", color: "#D1D5DB" } };
hmdValidation.getRange("A:A").format.columnWidth = 30;
hmdValidation.getRange("B:C").format.columnWidth = 16;

const bindingWorkbook = Workbook.create();
makeReadmeSheet(
  bindingWorkbook,
  "cor / Accounting Entries — PCA GL semantic-path binding",
  "Taxonomy Framework Part 1 module-qualified naming edition. Canonical paths use $.cor_AccountingEntries.cor_EntryHeader, and debit/credit predicates are encoded directly in semantic_path.",
  [
    ["Table type", "Flat CSV semantic path binding"],
    ["Canonical key", "semantic_path ($.cor_AccountingEntries.cor_EntryHeader…)"],
    ["HMD", names.hmdCsv],
    ["Source", "private/legacy_sources/accounting/pca/bindings/PCA_GL_Binding_v3_draft.xlsx"],
    ["Generated", "2026-08-14"],
  ],
  [
    "semantic_path and parent_semantic_path follow Part 1 lowerCamelCase hierarchy naming; deprecated short paths are confined to Legacy_Crosswalk.",
    "Selection predicates are encoded directly in semantic_path. The PCA journal-line occurrence uses the declared profile coordinate __source_row__ with Column2 as its parent voucher key.",
    "Unmapped PCA columns remain visible and are not assigned speculative semantics.",
    "The legacy example column was deliberately omitted because it contained instance-like values; no accounting data or master data is included.",
  ],
);
addDataSheet(bindingWorkbook, "Sources", Object.keys(sourceRowsCanonical[0]), sourceRowsCanonical, "PCASources", { A: 18, B: 15, C: 18, D: 18, E: 10, F: 12, G: 35, H: 35, I: 10 });
addDataSheet(bindingWorkbook, "Hierarchy", hierarchyHeaders, hierarchyRows, "PCAHierarchy", { A: 9, B: 14, C: 16, D: 24, E: 12, F: 22, G: 70, H: 18, I: 30, J: 12, K: 70, L: 10, M: 55 });
const bindingSheet = addDataSheet(bindingWorkbook, "Semantic_Binding", bindingHeaders, bindingRows, "PCASemanticBinding", { A: 12, B: 12, C: 12, D: 28, E: 12, F: 15, G: 12, H: 22, I: 38, J: 70, K: 30, L: 18, M: 14, N: 55 });
bindingSheet.freezePanes.freezeColumns(4);
const statusCol = bindingHeaders.indexOf("mapping_status");
bindingSheet.getRangeByIndexes(1, statusCol, bindingRows.length, 1).conditionalFormats.add("containsText", { text: "mapped", format: { fill: colors.green, font: { color: "#385723" } } });
bindingSheet.getRangeByIndexes(1, statusCol, bindingRows.length, 1).conditionalFormats.add("containsText", { text: "unmapped", format: { fill: colors.red, font: { color: "#9C0006" } } });
addDataSheet(bindingWorkbook, "Joins", Object.keys(joinRows[0]), joinRows, "PCAJoins", { A: 25, B: 22, C: 22, D: 30, E: 30, F: 12, G: 60, H: 10, I: 55 });
addDataSheet(bindingWorkbook, "Legacy_Crosswalk", legacyHeaders, legacyRows, "PCALegacyCrosswalk", { A: 14, B: 28, C: 12, D: 15, E: 12, F: 22, G: 38, H: 70, I: 70, J: 16, K: 38, L: 60, M: 14, N: 45 });
const validation = bindingWorkbook.worksheets.add("Validation");
validation.showGridLines = false;
validation.getRange("A1:D1").merge();
validation.getRange("A1").values = [["Binding conformance checks"]];
validation.getRange("A1:D1").format = { fill: colors.navy, font: { bold: true, color: colors.white, fontSize: 15 } };
validation.getRange("A3:C9").values = [
  ["Check", "Result", "Expected / disposition"],
  ["Physical fields", "", bindingRows.length],
  ["Mapped fields", "", "Review"],
  ["Unmapped fields", "", "No source semantic assignment"],
  ["Extension-required fields", "", "Explicit; no speculative cor mapping"],
  ["Blank canonical paths on mapped rows", "", 0],
  ["Legacy example values copied", 0, 0],
];
validation.getRange("B4").formulas = [[`=COUNTA(Semantic_Binding!A2:A${bindingRows.length + 1})`]];
validation.getRange("B5").formulas = [[`=COUNTIF(Semantic_Binding!M2:M${bindingRows.length + 1},"mapped")`]];
validation.getRange("B6").formulas = [[`=COUNTIF(Semantic_Binding!M2:M${bindingRows.length + 1},"unmapped")`]];
validation.getRange("B7").formulas = [[`=COUNTIF(Semantic_Binding!M2:M${bindingRows.length + 1},"extension_required")`]];
validation.getRange("B8").formulas = [[`=COUNTIFS(Semantic_Binding!M2:M${bindingRows.length + 1},"mapped",Semantic_Binding!J2:J${bindingRows.length + 1},"")`]];
validation.getRange("A3:C3").format = { fill: colors.teal, font: { bold: true, color: colors.white } };
validation.getRange("A3:C9").format.borders = { insideHorizontal: { style: "thin", color: "#D1D5DB" } };
validation.getRange("A:A").format.columnWidth = 34;
validation.getRange("B:B").format.columnWidth = 16;
validation.getRange("C:C").format.columnWidth = 28;

const hmdExport = await SpreadsheetFile.exportXlsx(hmdWorkbook);
await hmdExport.save(`${outputDir}/${names.hmdXlsx}`);
const bindingExport = await SpreadsheetFile.exportXlsx(bindingWorkbook);
await bindingExport.save(`${outputDir}/${names.bindingXlsx}`);

const bindingSetSource = await readJsonAnyEncoding(sourceBindingSetPath);
const revisedBindingSet = {
  profile: "cor_Accounting_Entries_PCA_GL_flat_csv_semantic_path_20260814",
  xbrl_gl_next_module: { prefix: "cor", element: "accountingEntries", label: "Accounting Entries" },
  framework: "XBRL GL Next Taxonomy Framework Part 1 — semantic_path naming",
  canonical_semantic_path_pattern: "$.cor_AccountingEntries.cor_EntryHeader.cor_EntryDetail[cor_DebitCreditIndicator=\"D\"].cor_MonetaryAmount",
  hmd: { file: names.hmdCsv, semantic_path_column: "semantic_path", compatibility_columns: ["legacy_semantic_path", "abbreviation_path"] },
  binding: { file: names.bindingCsv, type: "flat_csv_semantic_path", semantic_path_column: "semantic_path" },
  sources: sourceRowsCanonical,
  hierarchy: hierarchyRows,
  joins: joinRows,
  migration: {
    source_profile: bindingSetSource.profile ?? "legacy",
    legacy_crosswalk: names.legacyCsv,
    deprecated_keys: ["semPath", "semanticPath", "abbreviation_path"],
    note: "Deprecated path forms are retained only for cross-reference. New processing shall bind on semantic_path.",
  },
  privacy: "No source instance, master, generated accounting output, or example-value column is included.",
};
await fs.writeFile(`${outputDir}/${names.bindingSet}`, JSON.stringify(revisedBindingSet, null, 2) + "\n", "utf8");

async function reviseParameters(sourcePath, outputName) {
  const parameters = await readJsonAnyEncoding(sourcePath);
  delete parameters.LHM_path;
  parameters.HMD_path = names.hmdCsv;
  parameters.semantic_path_column = "semantic_path";
  parameters.semantic_binding_path = names.bindingCsv;
  parameters.binding_set_path = names.bindingSet;
  parameters.profile_note = "Review copy: runtime data/master paths still point to private workspace locations and are not included in this package.";
  await fs.writeFile(`${outputDir}/${outputName}`, JSON.stringify(parameters, null, 2) + "\n", "utf8");
}
await reviseParameters(mappingParametersPath, names.mappingParams);
await reviseParameters(explorerParametersPath, names.explorerParams);

const manifestRows = [
  { file: names.hmdCsv, role: "Canonical Part 1 HMD CSV", source: "private/legacy_sources/accounting/lhm/JP_LHM.csv", public_data: "No instance data" },
  { file: names.hmdXlsx, role: "Review workbook for canonical HMD", source: names.hmdCsv, public_data: "No instance data" },
  { file: names.bindingCsv, role: "Operational flat CSV semantic-path binding", source: "PCA_GL_Binding_v3_draft.xlsx", public_data: "No example values" },
  { file: names.bindingXlsx, role: "Review workbook for binding", source: names.bindingCsv, public_data: "No example values" },
  { file: names.legacyCsv, role: "Deprecated-to-canonical path crosswalk", source: "bindingPCA_GL.csv / current binding sheet", public_data: "No example values" },
  { file: names.bindingSet, role: "Binding-set manifest", source: "binding_set.json", public_data: "Definitions only" },
  { file: names.mappingParams, role: "LedgerExplorer mapping parameters", source: "parameters.mapping.work.json", public_data: "Definitions and private path references only" },
  { file: names.explorerParams, role: "LedgerExplorer run parameters", source: "parameters.ledger_explorer.work.json", public_data: "Definitions and private path references only" },
];
await fs.writeFile(`${outputDir}/${names.manifest}`, "\ufeff" + toCsv(["file", "role", "source", "public_data"], manifestRows), "utf8");

const readme = `# cor / Accounting Entries — PCA GL Journal Entry package

This folder contains the PCA GL example interpreted as an XBRL GL Next \`cor\` / \`Accounting Entries\` Journal Entry, with its semantic-path binding and the extracted JP Journal Entry HMD subtree.

## Part 1 naming rule

The canonical key is \`semantic_path\`. It begins with \`$.\` and joins lowerCamelCase hierarchy elements with dots, for example:

\`$.cor_AccountingEntries.cor_EntryHeader.cor_EntryDetail[cor_DebitCreditIndicator="D"].cor_MonetaryAmount\`

The previous label-style path and abbreviated path are compatibility references only. New bindings and selectors use the canonical \`semantic_path\`. The HMD in this package contains only the JP07a Journal Entry subtree; unrelated JP HMD roots are not presented as Accounting Entries.

## Included files

See \`${names.manifest}\`. The two principal review tables are \`${names.hmdXlsx}\` and \`${names.bindingXlsx}\`; CSV companions support machine processing.

## Data boundary

The package does not include PCA accounting input/output, LedgerExplorer outputs, master data, credentials, purchased standards text, or the legacy example-value column. Parameter files retain references to private workspace paths but do not copy those files.

## Mapping status

Unmapped physical PCA fields remain explicitly marked \`unmapped\`. They must not receive guessed semantic paths. \`__source_row__\` is a declared profile coordinate used to distinguish journal-line occurrences where the legacy flat CSV has no physical line identifier.
`;
await fs.writeFile(`${outputDir}/${names.readme}`, readme, "utf8");

// Organize the Invoice example from existing public/example assets; do not invent PCA invoice data.
await fs.mkdir(invoiceDir, { recursive: true });
const invoiceFiles = [
  ["btx_Business_Transactions_Invoice_OpenPeppol_UBL_input.xml", `${root}/samples/input/openpeppol_ubl_invoice_minimal.xml`, "Syntax input example (third-party-derived sample; original conditions apply)", "copy"],
  ["btx_Business_Transactions_Invoice_HMD_semantic_path_20260814.csv", `${root}/specs/lhm/EN16931_CIUS_Invoice_LHM.csv`, "Invoice HMD/LHM with Business Transactions semantic_path root", "semantic_path"],
  ["btx_Business_Transactions_Invoice_UBL_Syntax_Binding_semantic_path_20260814.csv", `${root}/specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv`, "UBL syntax-path to Business Transactions semantic_path binding", "semantic_path"],
];
for (const [file, source, , mode] of invoiceFiles) {
  if (mode === "semantic_path") {
    const content = await fs.readFile(source, "utf8");
    await fs.writeFile(`${invoiceDir}/${file}`, content.replaceAll("$.invoice", "$.btx_BusinessTransactions.btx_Invoice"), "utf8");
  } else {
    await fs.copyFile(source, `${invoiceDir}/${file}`);
  }
}
const invoiceManifest = invoiceFiles.map(([file, source, role]) => ({
  file,
  role,
  source: path.relative(root, source).replaceAll("\\", "/"),
  example_type: "Invoice",
}));
await fs.writeFile(`${invoiceDir}/Invoice_example_manifest_20260814.csv`, "\ufeff" + toCsv(["file", "role", "source", "example_type"], invoiceManifest), "utf8");
await fs.writeFile(`${invoiceDir}/README_Invoice_example_20260814.md`, `# UADC transformation example: Invoice

The Invoice example starts from the existing OpenPeppol UBL invoice and uses the EN 16931 HMD plus UBL syntax binding. In this example-set classification it corresponds to XBRL GL Next \`btx\` / \`Business Transactions\`; the module-qualified profile root is \`$.btx_BusinessTransactions.btx_Invoice\`.

Included files are listed in \`Invoice_example_manifest_20260814.csv\`. Third-party standards, schemas, terminology, and sample material retain their original rights and are not relicensed by this package.
`, "utf8");

await fs.writeFile(`${baseOutputDir}/README_UADC_Transformation_Examples_20260814.md`, `# UADC transformation examples

The examples are organized by business document semantics:

1. **Invoice** — XBRL GL Next \`btx\` / **Business Transactions**. OpenPeppol UBL input, EN 16931 HMD, syntax binding, and expected UADC Structured CSV. Module-qualified example root: \`$.btx_BusinessTransactions.btx_Invoice\`.
2. **Journal Entry** — XBRL GL Next \`cor\` / **Accounting Entries**. PCA accounting flat CSV interpreted as entry-header and selected entry-detail semantics, Accounting Entries HMD extract, semantic-path binding, and LedgerExplorer-related configuration. Root: \`$.cor_AccountingEntries.cor_EntryHeader\`.

PCA accounting does not contain an Invoice document. It is therefore not placed under \`btx\` / Business Transactions and is not mapped to the Invoice profile. Private PCA instance data, master data, and generated accounting outputs are excluded.
`, "utf8");

const hmdInspect = await hmdWorkbook.inspect({ kind: "workbook,sheet,table,formula", maxChars: 10000, tableMaxRows: 5, tableMaxCols: 8, options: { maxResults: 50 } });
const bindingInspect = await bindingWorkbook.inspect({ kind: "workbook,sheet,table,formula", maxChars: 12000, tableMaxRows: 5, tableMaxCols: 8, options: { maxResults: 80 } });
console.log(hmdInspect.ndjson ?? hmdInspect);
console.log(bindingInspect.ndjson ?? bindingInspect);

const formulaErrorsHmd = await hmdWorkbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, maxChars: 5000 });
const formulaErrorsBinding = await bindingWorkbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, maxChars: 5000 });
console.log(`HMD FORMULA ERRORS\n${formulaErrorsHmd.ndjson ?? formulaErrorsHmd}`);
console.log(`BINDING FORMULA ERRORS\n${formulaErrorsBinding.ndjson ?? formulaErrorsBinding}`);

await renderWorkbook(hmdWorkbook, "HMD", { README: "A1:H16", HMD: "A1:Q24", Validation: "A1:C8" });
await renderWorkbook(bindingWorkbook, "PCA", { README: "A1:H16", Sources: "A1:I8", Hierarchy: "A1:N10", Semantic_Binding: "A1:O24", Joins: "A1:I6", Legacy_Crosswalk: "A1:N24", Validation: "A1:C10" });

console.log(JSON.stringify({
  hmd_rows: hmdRows.length,
  hmd_unique_ids: new Set(hmdRows.map((row) => text(row.id))).size,
  binding_rows: bindingRows.length,
  mapped: bindingRows.filter((row) => row.mapping_status === "mapped").length,
  unmapped: bindingRows.filter((row) => row.mapping_status === "unmapped").length,
  extension_required: bindingRows.filter((row) => row.mapping_status === "extension_required").length,
  outputs: Object.values(names),
}, null, 2));
