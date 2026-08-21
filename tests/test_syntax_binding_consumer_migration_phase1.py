import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import syntax_binding  # noqa: E402


class ConsumerMigrationPhase1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.taxonomy = self.root / "taxonomy"
        self.metadata = self.root / "output" / "metadata.json"
        self.binding = self.root / "binding.csv"

        oim_directory = self.taxonomy / "oim" / "en16931_Invoice"
        oim_directory.mkdir(parents=True)
        (self.taxonomy / "en16931").mkdir(parents=True)
        (self.taxonomy / "plt").mkdir(parents=True)
        for name in (
            "en16931-all-oim-2025-01-01.xsd",
            "en16931-all-oim-2026-07-05.xsd",
            "en16931-all-dim-2026-07-05.xml",
        ):
            (oim_directory / name).touch()
        (self.taxonomy / "en16931" / "en16931-oim-2026-07-05.xsd").touch()
        # A newer legacy-layout file must not affect Canonical entry-point selection.
        (self.taxonomy / "plt" / "en16931-oim-2099-01-01.xsd").touch()

        with self.binding.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=["type", "structured_csv_column", "module", "datatype"],
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "type": "C",
                        "structured_csv_column": "InvoiceLine",
                        "module": "en16931",
                        "datatype": "Text",
                    },
                    {
                        "type": "A",
                        "structured_csv_column": "InvoiceNumber",
                        "module": "en16931",
                        "datatype": "Identifier",
                    },
                    {
                        "type": "C",
                        "structured_csv_column": "OtherClass",
                        "module": "cor",
                        "datatype": "Text",
                    },
                    {
                        "type": "A",
                        "structured_csv_column": "OtherAmount",
                        "module": "cor",
                        "datatype": "Amount",
                    },
                ]
            )

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_canonical_entry_point_is_selected_deterministically(self) -> None:
        entrypoints = syntax_binding.taxonomy_entrypoints(self.taxonomy, self.metadata)

        self.assertTrue(
            entrypoints["xbrlCsvSchema"].endswith(
                "oim/en16931_Invoice/en16931-all-oim-2026-07-05.xsd"
            )
        )
        self.assertNotIn("en16931-oim-2099-01-01.xsd", entrypoints["xbrlCsvSchema"])
        self.assertTrue(
            entrypoints["definitionLinkbase"].endswith(
                "oim/en16931_Invoice/en16931-all-dim-2026-07-05.xml"
            )
        )

    def test_qname_namespace_separation_and_other_family_compatibility(self) -> None:
        columns = syntax_binding.binding_column_metadata(self.binding, "utf-8")

        self.assertEqual(
            "plt:d_en16931_InvoiceLine",
            columns["dInvoiceLine"]["taxonomyConcept"],
        )
        self.assertEqual(
            "en16931:p_en16931_InvoiceLine",
            columns["dInvoiceLine"]["primaryItem"],
        )
        self.assertEqual(
            "en16931:InvoiceNumber",
            columns["InvoiceNumber"]["taxonomyConcept"],
        )
        self.assertEqual(
            "en16931:d_cor_OtherClass",
            columns["dOtherClass"]["taxonomyConcept"],
        )
        self.assertEqual(
            "en16931:p_cor_OtherClass",
            columns["dOtherClass"]["primaryItem"],
        )
        self.assertEqual("cor:OtherAmount", columns["OtherAmount"]["taxonomyConcept"])

    def test_metadata_contains_new_entry_point_and_namespace_contract(self) -> None:
        syntax_binding.write_csv_metadata(
            self.metadata,
            self.root / "invoice.csv",
            self.root / "invoice.xml",
            self.binding,
            ["dInvoiceLine", "InvoiceNumber"],
            1,
            self.taxonomy,
            "utf-8",
        )

        metadata = json.loads(self.metadata.read_text(encoding="utf-8"))
        document_info = metadata["documentInfo"]
        self.assertEqual(1, len(document_info["taxonomy"]))
        self.assertTrue(
            document_info["taxonomy"][0].endswith(
                "oim/en16931_Invoice/en16931-all-oim-2026-07-05.xsd"
            )
        )
        self.assertEqual(
            "http://www.xbrl.org/int/gl/en16931/2026-07-05",
            document_info["namespaces"]["en16931"],
        )
        self.assertEqual(
            "http://www.xbrl.org/int/gl/plt/2026-07-05",
            document_info["namespaces"]["plt"],
        )
        dimensions = metadata["tableTemplates"]["structured"]["dimensions"]
        self.assertEqual("$dInvoiceLine", dimensions["plt:d_en16931_InvoiceLine"])
        columns = metadata["tableTemplates"]["structured"]["columns"]
        self.assertEqual(
            "en16931:InvoiceNumber",
            columns["InvoiceNumber"]["dimensions"]["concept"],
        )


if __name__ == "__main__":
    unittest.main()
