"""Exercise governed four-fact selection independently of D/C placement."""
import sys, unittest
from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/uadc'))
import flat_csv as f
R=Path(__file__).resolve().parents[1]
P='EPSON_ZaimuKaikeiR4_43col_NTA_Fallback'
PREFIX='$.cor_AccountingEntries.cor_EntryHeader.cor_EntryDetail'
def facts(side,classification,typ,cat,rate):
    rows=[]
    for suffix,value in [(f.TAX_TYPE_SUFFIX,typ),(f.TAX_TRANSACTION_CLASSIFICATION_SUFFIX,classification),(f.TAX_CATEGORY_SUFFIX,cat),(f.TAX_RATE_SUFFIX,rate)]:
        if value:
            rows.append(dict(entry_key='voucher',source_row='1',occurrence=side,semantic_path=PREFIX+suffix,binding_path=PREFIX+suffix,value=value))
    return rows
class TaxCombinationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rules=f.load_standard_tax_mapping(R/f'bindings/flat-csv/{P}/{P}_STANDARD_TAX_MAPPING.csv')
    def reverse(self,rows,rules=None,mode='policy_regenerated',traces=()):
        definition=SimpleNamespace(rows=[SimpleNamespace(path=PREFIX+f.TAX_RATE_SUFFIX)])
        return f._apply_standard_tax_reverse(rows,rules or self.rules,P,mode,traces,definition)[0]
    def test_official_combinations_both_sides(self):
        cases=[('Sales','VAT','S','0.10','01','10'),('Purchase','VAT','S','0.10','31','10'),('Purchase','VAT','AA','0.08','31','K8.0'),('Sales','VAT','E','','20',''),('Purchase','VAT','E','','30',''),('','VAT','O','','00','')]
        for side in ['D','C']:
            for cls,typ,cat,rate,code,out_rate in cases:
                with self.subTest(side=side,classification=cls,category=cat):
                    out=self.reverse(facts(side,cls,typ,cat,rate))
                    self.assertEqual(next(r['value']for r in out if r['semantic_path'].endswith(f.TAX_CATEGORY_SUFFIX)),code)
                    self.assertEqual(next((r['value']for r in out if r['semantic_path'].endswith(f.TAX_RATE_SUFFIX)),''),out_rate)
    def test_missing_type_stops(self):
        with self.assertRaises(f.ConversionError)as e:self.reverse(facts('D','Sales','','S','0.10'))
        self.assertEqual(e.exception.kind,'MISSING_TAX_INFORMATION')
    def test_wrong_type_cannot_match_vat(self):
        with self.assertRaises(f.ConversionError)as e:self.reverse(facts('D','Sales','OTH','S','0.10'))
        self.assertEqual(e.exception.kind,'TAX_POLICY_UNRESOLVED')
    def test_type_selects_between_equal_category_rate_classification(self):
        vat=next(r for r in self.rules if r.application_tax_code=='01')
        other=replace(vat,tax_type='OTH',application_tax_code='TEST_OTHER',line_number=999)
        out=self.reverse(facts('C','Sales','OTH','S','0.10'),[vat,other])
        self.assertEqual(next(r['value']for r in out if r['semantic_path'].endswith(f.TAX_CATEGORY_SUFFIX)),'TEST_OTHER')
    def test_missing_sales_purchase_cannot_guess_from_side(self):
        for side in ['D','C']:
            with self.assertRaises(f.ConversionError)as e:self.reverse(facts(side,'','VAT','S','0.10'))
            self.assertEqual(e.exception.kind,'TAX_POLICY_UNRESOLVED')
    def test_source_trace_rejects_changed_type_or_classification(self):
        trace=dict(source_record_key='voucher',source_row='1',source_occurrence_side='D',source_application=P,output_tax_category='S',output_tax_rate_ratio='0.10',output_tax_type='VAT',output_transaction_classification='Sales',source_tax_code='01',source_tax_rate_lexical='10')
        for cls,typ in [('Sales','OTH'),('Purchase','VAT')]:
            with self.assertRaises(f.ConversionError)as e:self.reverse(facts('D',cls,typ,'S','0.10'),mode='source_restored',traces=[trace])
            self.assertEqual(e.exception.kind,'TAX_TRACE_OUTPUT_MISMATCH')
if __name__=='__main__':unittest.main()
