"""Unique aggregate partition; source slots and original occurrence ownership are retained."""
from collections import Counter
from decimal import Decimal


def materialize(details, definition, semantics, amount, copy_amount, error):
    dv, cv, dp, cp = semantics(definition)
    entries = {}
    for (key, number), rows in details.items():
        entries.setdefault(key, []).append((number, rows))
    output, counts = [], Counter()
    for key, groups in sorted(entries.items(), key=lambda x: min(n for n, _ in x[1])):
        groups.sort()
        sides = {}
        for v, path in [(dv, dp), (cv, cp)]:
            sides[v] = [(n, [r for r in rows if r['occurrence'] == v]) for n, rows in groups
                        if any(r['occurrence'] == v and r['binding_path'] == path and r['value'].strip() for r in rows)]
        d, c = sides[dv], sides[cv]
        if not d or not c:
            raise error('EMPTY_ACTIVE_SIDE', 'a voucher lacks an active side')
        da, ca = [amount(r, dp) for _, r in d], [amount(r, cp) for _, r in c]
        if any(not x.is_finite() for x, _ in da + ca):
            raise error('COMPOUND_AMOUNT_INVALID', 'aggregate pairing requires finite non-negative amounts')
        if sum((a for a, _ in da), Decimal(0)) != sum((a for a, _ in ca), Decimal(0)):
            raise error('COMPOUND_AMOUNT_MISMATCH', 'voucher totals differ')
        # A fully paired and balanced source layout needs no allocation inference.
        if len(d) == len(c) and [n for n, _ in d] == [n for n, _ in c] and [a for a, _ in da] == [a for a, _ in ca]:
            output.extend(((key, dn), [*dr, *cr]) for (dn, dr), (_, cr) in zip(d, c))
            counts['1:1' if len(d) == 1 else 'N:M-preserved'] += 1
            continue
        if len(d) >= len(c):
            many, few, ma, fa, fp, fv = d, c, da, ca, cp, cv
        else:
            many, few, ma, fa, fp, fv = c, d, ca, da, dp, dv
        many_rows = {n: i for i, (n, _) in enumerate(many)}
        occupied = {n for n, _ in few}
        # A receiving side may contain only its default indicator, not existing business facts.
        eligible = set()
        for n, rows in groups:
            if n not in many_rows or n in occupied:
                continue
            blank_facts = [r for r in rows if r['occurrence'] == fv and r['value'].strip()
                           and not r['semantic_path'].lower().endswith(('debitcreditindicator', 'detaildescription'))]
            if not blank_facts:
                eligible.add(many_rows[n])
        if len(many) - len(few) > len(eligible):
            raise error('INSUFFICIENT_BLANK_DETAIL_ROWS', 'aggregate expansion lacks eligible blank positions')
        budget = [0]
        solutions = []
        candidate_cache = {}
        def tick():
            budget[0] += 1
            if budget[0] > 1000000:
                raise error('AGGREGATE_SEARCH_LIMIT', 'uniqueness could not be established within the search budget')
        def solve(pos, used, allocation):
            tick()
            if len(solutions) > 1:
                return
            if pos == len(few):
                if len(used) == len(many): solutions.append(allocation)
                return
            anchor, _ = few[pos]
            fixed = many_rows.get(anchor)
            full_allowed = eligible | ({fixed} if fixed is not None else set())
            allowed = sorted(full_allowed - used)
            target = fa[pos][0]
            if fixed is not None and fixed not in allowed:
                return
            if pos == len(few) - 1:
                remaining = set(range(len(many))) - used
                if remaining and remaining.issubset(allowed) and sum((ma[i][0] for i in remaining), Decimal(0)) == target:
                    solve(pos + 1, used | remaining, allocation + [tuple(sorted(remaining))])
                return
            # Meet-in-the-middle exact subset sums support signed detail amounts.
            # No absolute-value normalization or arbitrary allocation is performed.
            if pos in candidate_cache:
                for picked in candidate_cache[pos]:
                    if not used.intersection(picked): solve(pos + 1, used | set(picked), allocation + [picked])
                    if len(solutions) > 1: return
                return
            optional = [i for i in sorted(full_allowed) if i != fixed]
            fixed_set = [fixed] if fixed is not None else []
            residual = target - (ma[fixed][0] if fixed is not None else Decimal(0))
            mid = len(optional) // 2
            def sums(indices):
                values = [(Decimal(0), ())]
                for i in indices:
                    new = []
                    for value, subset in values:
                        tick(); new.append((value + ma[i][0], subset + (i,)))
                    values += new
                return values
            right = {}
            for value, subset in sums(optional[mid:]):
                right.setdefault(value, []).append(subset)
            matches = []
            for value, left in sums(optional[:mid]):
                for r in right.get(residual - value, []):
                    tick()
                    picked = tuple(fixed_set) + left + r
                    if picked: matches.append(picked)
            candidate_cache[pos] = matches
            for picked in matches:
                if not used.intersection(picked): solve(pos + 1, used | set(picked), allocation + [picked])
                if len(solutions) > 1: return
        solve(0, set(), [])
        if not solutions:
            raise error('UNMATCHED_RESIDUAL_AMOUNT', 'no complete source-compatible allocation exists')
        if len(solutions) != 1:
            raise error('AMBIGUOUS_AGGREGATE_SPLIT', 'multiple complete occurrence allocations exist')
        by_slot = dict(groups)
        parts = []
        for (_, original), subset in zip(few, solutions[0]):
            if len(subset) > 1 and any(r['semantic_path'].lower().endswith('amountoftaxes') and Decimal(r['value'] or '0') != 0 for r in original):
                raise error('TAX_ALLOCATION_UNRESOLVED', 'nonzero aggregate tax requires a defined allocation policy')
            if sum((ma[i][0] for i in subset), Decimal(0)) != amount(original, fp)[0]:
                raise error('COMPOUND_AMOUNT_MISMATCH', 'aggregate amount was not conserved')
            for i in subset:
                n, records = many[i]
                split = copy_amount(original, fp, ma[i][1])
                # Description is local to the receiving source detail. Preserve it.
                local = {r['binding_path']: r for r in by_slot[n] if r['occurrence'] == fv
                         and r['semantic_path'].lower().endswith('detaildescription') and r['value']}
                if local:
                    split = [r for r in split if r['binding_path'] not in local]
                    split.extend(dict(r) for r in local.values())
                parts.append(((key, n), [*records, *split]))
        output.extend(sorted(parts, key=lambda p: p[0][1]))
        counts['1:1' if len(d) == len(c) == 1 else '1:N' if len(d) == 1 else 'N:1' if len(c) == 1 else 'N:M-aggregate'] += 1
    return output, counts
