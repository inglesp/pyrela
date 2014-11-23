from copy import copy
import json


class Relation:
    def __init__(self, attrs, tuples):
        n = len(attrs)
        assert all(t for t in tuples if len(t) == n)

        self.attrs = tuple(attrs)
        self.tuples = {tuple(t) for t in tuples}


    @staticmethod
    def from_json(filename):
        with open(filename) as f:
            data = json.load(f)

        return Relation(data['attrs'], data['tuples'])


    def __repr__(self):
        cols = range(len(self.attrs))

        headings = [str(attr) for attr in self.attrs]

        widths = [1 + max([len(str(t[i])) for t in self.tuples] + [len(headings[i])])
                  for i in cols]

        lines = []

        row = []
        for i in cols:
            e = ' ' + headings[i] + ' ' * (widths[i] - len(headings[i]))
            row.append(e)

        lines.append('|'.join(row))

        lines.append('+'.join(['-' * (widths[i] + 1) for i  in cols]))

        for t in self.tuples:
            row = []
            for i in cols:
                e = ' ' + str(t[i]) + ' ' * (widths[i] - len(str(t[i])))
                row.append(e)

            lines.append('|'.join(row))

        return '\n'.join([''] + lines + [''])


    def __eq__(self, other):
        return self.attrs == other.attrs and self.tuples == other.tuples


    def __len__(self):
        return len(self.tuples)


    def rename(self, new_attrs):
        assert len(new_attrs) == len(self.attrs)
        return Relation(new_attrs, self.tuples)


    def project(self, attrs):
        assert set(attrs) <= set(self.attrs)

        indices = [self.attrs.index(a) for a in attrs]
        new_tuples = [[t[i] for i in indices] for t in self.tuples]
        return Relation(attrs, new_tuples)


    def select(self, predicate):
        dicts = [dict(zip(self.attrs, t)) for t in self.tuples]
        selected_dicts = [d for d in dicts if predicate(d)]
        selected_tuples = {tuple(d[k] for k in self.attrs) for d in selected_dicts}
        return Relation(self.attrs, selected_tuples)


def cross(rel1, rel2):
    assert not set(rel1.attrs) & set(rel2.attrs)

    new_attrs = rel1.attrs + rel2.attrs
    new_tuples = [t1 + t2 for t1 in rel1.tuples for t2 in rel2.tuples]
    return Relation(new_attrs, new_tuples)


def natural_join(rel1, rel2):
    common_attrs = set(rel1.attrs) & set(rel2.attrs)
    assert common_attrs

    rel1a_attrs = [(1, attr) for attr in rel1.attrs]
    rel2a_attrs = [(2, attr) for attr in rel2.attrs]
    rel2a_only_attrs = [attr for attr in rel2a_attrs if attr[1] not in common_attrs]
    joined_attrs = rel1a_attrs + rel2a_only_attrs
    renamed_attrs = [attr[1] for attr in joined_attrs]

    rel1a = rel1.rename(rel1a_attrs)
    rel2a = rel2.rename(rel2a_attrs)

    cross_rel = cross(rel1a, rel2a)

    predicate = and_(*[eq(F((1, attr)), F((2, attr))) for attr in common_attrs])

    join_rel = cross_rel.select(predicate)
    return join_rel.project(joined_attrs).rename(renamed_attrs)


def inner_join(rel1, rel2, *attr_pairs):
    cross_rel = cross(rel1, rel2)
    predicate = and_(*[eq(F(attr1), F(attr2)) for attr1, attr2 in attr_pairs])
    return cross_rel.select(predicate)



def diff(rel1, rel2):
    assert rel1.attrs == rel2.attrs

    new_tuples = rel1.tuples - rel2.tuples
    return Relation(rel1.attrs, new_tuples)


def union(rel1, rel2):
    assert rel1.attrs == rel2.attrs

    new_tuples = rel1.tuples | rel2.tuples
    return Relation(rel1.attrs, new_tuples)


def intersection(rel1, rel2):
    assert rel1.attrs == rel2.attrs

    new_tuples = rel1.tuples & rel2.tuples
    return Relation(rel1.attrs, new_tuples)


comparators = {
    'exact': lambda lhs, rhs: lhs == rhs,
    'iexact': lambda lhs, rhs: lhs.lower() == rhs.lower(),
    'contains': lambda lhs, rhs: rhs in lhs,
    'icontains': lambda lhs, rhs: rhs.lower() in lhs.lower(),
    'gt': lambda lhs, rhs: lhs > rhs,
    'gte': lambda lhs, rhs: lhs >= rhs,
    'lt': lambda lhs, rhs: lhs < rhs,
    'lte': lambda lhs, rhs: lhs <= rhs,
    'startswith': lambda lhs, rhs: lhs.startswith(rhs),
    'endswith': lambda lhs, rhs: lhs.endswith(rhs),
    'istartswith': lambda lhs, rhs: lhs.lower().startswith(rhs.lower()),
    'iendswith': lambda lhs, rhs: lhs.lower().endswith(rhs.lower()),
    'year': lambda lhs, rhs: lhs.year == rhs,
    'month': lambda lhs, rhs: lhs.month == rhs,
    'day': lambda lhs, rhs: lhs.day == rhs,
}


def build_predicate_fn(fn):
    def predicate_fn(lhs, rhs):
        def predicate(record):
            if isinstance(lhs, dict):
                lhsv = record[lhs['field']]
            else:
                lhsv = lhs

            if isinstance(rhs, dict):
                rhsv = record[rhs['field']]
            else:
                rhsv = rhs

            return fn(lhsv, rhsv)

        return predicate
    return predicate_fn




for key, fn in comparators.items():
    locals()[key] = build_predicate_fn(fn)


eq = exact


def and_(*ps):
    return lambda record: all(p(record) for p in ps)


def or_(*ps):
    return lambda record: any(p(record) for p in ps)


def not_(p):
    return lambda record: not p(record)


def F(fieldname):
    return {'field': fieldname}


class Table:
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs
        self.rel = Relation(attrs, set())
        self.last_id = 0


    def get_next_id(self):
        self.last_id += 1
        return self.last_id


    def insert(self, record):
        assert set(record) | set(['id']) == set(self.attrs)
        record = copy(record)
        record['id'] = self.get_next_id()
        tpl = tuple(record[attr] for attr in self.attrs)
        self.rel = union(self.rel, Relation(self.attrs, [tpl]))
        return record['id']


    def delete(self, predicate):
        self.rel = self.rel.select(not_(predicate))


    # This will need to be more sophisticated!
    def update(self, predicate, attr, value):
        assert attr in self.attrs
        to_update = self.rel.select(predicate)
        to_not_update = self.rel.select(not_(predicate))

        ix = self.attrs.index(attr)
        updated_tuples = [tpl[:ix] + (value,) + tpl[ix+1:] for tpl in to_update.tuples]
        updated_rel = Relation(self.attrs, updated_tuples)
        self.rel = union(updated_rel, to_not_update)


    def __len__(self):
        return len(self.rel)


    def select(self, predicate=None, order=None, offset=None, limit=None):
        if predicate is not None:
            rel = self.rel.select(predicate)
        else:
            rel = self.rel

        if order is not None:
            order = [((self.name, attr), direction) for attr, direction in order]

        attrs = [(self.name, attr) for attr in self.attrs]
        rel = rel.rename(attrs)
        return Selection(rel, order=order, offset=offset, limit=limit)


class InnerJoin:
    def __init__(self, lhs, rhs, *attr_pairs):
        lhs_attrs = [(lhs.name, attr) for attr in lhs.attrs]
        rhs_attrs = [(rhs.name, attr) for attr in rhs.attrs]

        lhs_rel = lhs.rel.rename(lhs_attrs)
        rhs_rel = rhs.rel.rename(rhs_attrs)

        attr_pairs = [((lhs.name, lhs_attr), (rhs.name, rhs_attr)) for lhs_attr, rhs_attr in attr_pairs]

        self.rel = inner_join(lhs_rel, rhs_rel, *attr_pairs)


    def select(self, predicate=None, order=None, offset=None, limit=None):
        if predicate is not None:
            rel = self.rel.select(predicate)
        else:
            rel = self.rel

        return Selection(rel, order=order, offset=offset, limit=limit)


class Selection:
    def __init__(self, rel, order=None, offset=None, limit=None):
        if order is None:
            assert offset is None and limit is None

        self.attrs = rel.attrs
        self.tuples = list(rel.tuples)

        if order is not None:
            for attr, direction in order[::-1]:
                ix = self.attrs.index(attr)
                assert direction in ['asc', 'desc']

                self.tuples = sorted(
                    self.tuples,
                    key=lambda t: t[ix],
                    reverse=(direction == 'desc')
                )

        if offset is None:
            low = 0
        else:
            low = offset

        if limit is None:
            high = len(self.tuples)
        else:
            high = low + limit

        self.tuples = self.tuples[low:high]


    def records(self):
        return [dict(zip(self.attrs, t)) for t in self.tuples]


    def records_for_alias(self, alias):
        # This duplicates .project and .rename.
        indices = [i for i in range(len(self.attrs)) if self.attrs[i][0] == alias]
        new_tuples = [[t[i] for i in indices] for t in self.tuples]

        attrs = [attr[1] for attr in self.attrs if attr[0] == alias]
        return [dict(zip(attrs, t)) for t in new_tuples]

