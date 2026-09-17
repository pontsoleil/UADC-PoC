import sys, unittest
from pathlib import Path
from decimal import Decimal
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/uadc'))
import aggregate_pairing as a
import flat_csv as f

def facts(n, side, value, tax=0):
    rows=[dict(source_row=str(n), occurrence=side,binding_path=side+'Amount', semantic_path='$.cor_MonetaryAmount',value=str(value))]
    if tax: rows.append(dict(source_row=str(n),occurrence=side,binding_path=side+'Tax',semantic_path='$.cor_AmountofTaxes',value=str(tax)))
    return rows

def run(d,c,tax=0):
    details={}
    for side, entries in [('D',d),('C',c)]:
        for n,v in entries:
            details.setdefault(('voucher',n),[]).extend(facts(n,side,v,tax if side=='C' else 0))
    return a.materialize(details,None,lambda _:('D','C','DAmount','CAmount'),f._decimal_amount,f._copy_with_amount,f.ConversionError)

class AggregateTests(unittest.TestCase):
    def check_ok(self,d,c,rows,tax=0):
        out,count=run(d,c,tax)
        self.assertEqual(len(out),rows)
        sums={'D':Decimal(0),'C':Decimal(0)}
        for _,records in out:
            pair={s:f._decimal_amount(records,s+'Amount')[0] for s in sums}
            self.assertEqual(pair['D'],pair['C'])
            for s in sums:sums[s]+=pair[s]
        self.assertEqual(sums['D'],sum(Decimal(v) for _,v in d))
        self.assertEqual(sums['C'],sum(Decimal(v) for _,v in c))
        self.assertEqual(out,run(d,c,tax)[0])
    def error(self,d,c,code,tax=0):
        with self.assertRaises(f.ConversionError) as ctx:run(d,c,tax)
        self.assertEqual(ctx.exception.kind,code)
    def test_single(self):self.check_ok([(1,300)],[(1,300)],1)
    def test_n1(self):self.check_ok([(1,100),(2,200)],[(1,300)],2)
    def test_1n(self):self.check_ok([(1,300)],[(1,100),(2,200)],2)
    def test_32(self):self.check_ok([(1,100),(2,200),(3,400)],[(1,300),(3,400)],3)
    def test_42_multiple(self):self.check_ok([(1,100),(2,200),(3,400),(4,800)],[(1,300),(3,1200)],4)
    def test_53(self):self.check_ok([(1,100),(2,200),(3,400),(4,800),(5,1600)],[(1,300),(3,1200),(5,1600)],5)
    def test_mirror(self):self.check_ok([(1,300),(3,1200)],[(1,100),(2,200),(3,400),(4,800)],4)
    def test_paired_repeated(self):self.check_ok([(1,100),(2,100)],[(1,100),(2,100)],2)
    def test_ambiguous(self):self.error([(1,100),(2,100),(3,200),(4,200)],[(1,300),(2,300)],'AMBIGUOUS_AGGREGATE_SPLIT')
    def test_insufficient(self):self.error([(1,100),(2,200)],[(1,200),(2,100)],'UNMATCHED_RESIDUAL_AMOUNT')
    def test_total(self):self.error([(1,100)],[(1,200)],'COMPOUND_AMOUNT_MISMATCH')
    def test_residual(self):self.error([(1,100),(2,200),(3,400)],[(1,200),(3,500)],'UNMATCHED_RESIDUAL_AMOUNT')
    def test_empty(self):self.error([(1,100)],[],'EMPTY_ACTIVE_SIDE')
    def test_negative_paired(self):self.check_ok([(1,-100)],[(1,-100)],1)
    def test_negative_split(self):self.check_ok([(1,-100),(2,-200)],[(1,-300)],2)
    def test_mixed_signed_split(self):self.check_ok([(1,500),(2,-200)],[(1,300)],2)
    def test_nonzero_tax(self):self.error([(1,100),(2,200)],[(1,300)],'TAX_ALLOCATION_UNRESOLVED',30)
    def test_description_owned_by_receiver(self):
        details={('voucher',1):facts(1,'D',100)+facts(1,'C',300),('voucher',2):facts(2,'D',200)}
        details[('voucher',1)].append(dict(source_row='1',occurrence='C',binding_path='CDesc',semantic_path='$.cor_DetailDescription',value='first'))
        details[('voucher',2)].append(dict(source_row='2',occurrence='C',binding_path='CDesc',semantic_path='$.cor_DetailDescription',value='second'))
        out,_=a.materialize(details,None,lambda _:('D','C','DAmount','CAmount'),f._decimal_amount,f._copy_with_amount,f.ConversionError)
        self.assertEqual([next(r['value'] for r in rows if r['binding_path']=='CDesc')for _,rows in out],['first','second'])
    def test_occupied_receiver(self):
        details={('voucher',1):facts(1,'D',100)+facts(1,'C',300),('voucher',2):facts(2,'D',200)}
        details[('voucher',2)].append(dict(source_row='2',occurrence='C',binding_path='CAccount',semantic_path='$.cor_AccountNumber',value='occupied'))
        with self.assertRaises(f.ConversionError) as ctx:a.materialize(details,None,lambda _:('D','C','DAmount','CAmount'),f._decimal_amount,f._copy_with_amount,f.ConversionError)
        self.assertEqual(ctx.exception.kind,'INSUFFICIENT_BLANK_DETAIL_ROWS')
    def test_decimal(self):self.check_ok([(1,'0.1'),(2,'0.2')],[(1,'0.3')],2)
if __name__=='__main__':unittest.main()
