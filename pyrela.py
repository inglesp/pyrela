from decimal import Decimal, InvalidOperation
import csv

class Relation:
    def __init__(self, name, attrs, tuples):
        self.name = name
        self.attrs = tuple(attrs)
        self.tuples = set([tuple(t) for t in tuples])

    @staticmethod
    def from_csv(filename, attrs=None):
        f = open(filename)
        reader = csv.reader(f)

        if attrs is None:
            row = reader.next()
            attrs = [e.strip("'").strip('"') for e in row]

        tuples = []

        for row in reader:
            t = []
            for e in row:
                try:
                    e = Decimal(e)
                except InvalidOperation:
                    e = e.strip("'").strip('"')
                t.append(e)
            tuples.append(tuple(t))

        f.close()

        if filename.endswith('.csv'):
            name = filename[:-4]
        else:
            name = filename

        return Relation(name, attrs, tuples)

    def display(self):
        cols = range(len(self.attrs))
        widths = [1 + max([len(str(t[i])) for t in self.tuples] + [len(self.attrs[i])]) 
                  for i in cols]

        headings = [" " + self.attrs[i] + " " * (widths[i] - len(self.attrs[i]))
                    for i in cols]
 
        print "|".join(headings)

        print "+".join(["-" * (widths[i] + 1) for i  in cols])

        for t in self.tuples:
            row = []
            for i in cols:
                try:
                    Decimal(t[i])
                    e = " " * (widths[i] - len(str(t[i]))) + str(t[i]) + " "
                except InvalidOperation:
                    e = " " + t[i] + " " * (widths[i] - len(t[i]))
                row.append(e)

            print "|".join(row)


    def equal(self, other):
        return self.attrs == other.attrs and self.tuples == other.tuples

    def rename(self, new_attrs):
        return rename(new_attrs, self)

    def project(self, new_attrs):
        return project(new_attrs, self)

    def select(self, condition):
        return select(condition, self)

def project(new_attrs, rel):
    indices = [rel.attrs.index(a) for a in new_attrs]
    new_tuples = [[t[i] for i in indices] for t in rel.tuples]
    name = "Project[%s] %s" % (new_attrs, rel.name)
    return Relation(name, new_attrs, new_tuples)

def rename(new_attrs, rel):
    name = "Rename[%s] %s" % (new_attrs, rel.name)
    return Relation(name, new_attrs, rel.tuples)

def select(condition, rel):
    found_cmp = False
    for cmp in ['==', '<=', '>=', '<', '>']:
        if cmp in condition:
            found_cmp = True
            break

    if not found_cmp:
        raise SelectException

    attr, value = [token.strip() for token in condition.split(cmp)]

    try:
        ix = rel.attrs.index(attr)
    except IndexError:
        raise SelectException

    try:
        value = Decimal(value)
    except InvalidOperation:
        pass

    new_tuples = [t for t in rel.tuples if eval("t[ix] %s %s" % (cmp, value))]

    name = "Select[%s] %s" % (condition, rel.name)

    return Relation(name, rel.attrs, new_tuples)
    
def cross(rel1, rel2):
    new_attrs = rel1.attrs + rel2.attrs
    new_tuples = [t1 + t2 for t1 in rel1.tuples for t2 in rel2.tuples]
    name = "'%s' Cross '%s'" % (rel1.name, rel2.name)
    return Relation(name, new_attrs, new_tuples)

def join(rel1, rel2):
    common_attrs = set(rel1.attrs) & set(rel2.attrs)
    rel2_unique_attrs = tuple([a for a in rel2.attrs if a not in common_attrs])

    new_attrs = rel1.attrs + rel2_unique_attrs

    new_tuples = []

    for t in rel1.tuples:
        singleton_rel = Relation('_', rel1.attrs, [t])

        rel2_filtered = rel2
        for a in common_attrs:
            ix = rel1.attrs.index(a)
            condition = "%s == %s" % (a, t[ix])
            rel2_filtered = rel2_filtered.select(condition)

        projection = rel2_filtered.project(rel2_unique_attrs)
        cross_product = cross(singleton_rel, projection)

        new_tuples.extend(cross_product.tuples)

    name = "'%s' Join '%s" % (rel1.name, rel2.name)

    return Relation(name, new_attrs, new_tuples)

class RelationException(Exception): pass
class ProjectException(Exception): pass
class RenameException(Exception): pass
class SelectException(Exception): pass
class CrossException(Exception): pass
class JoinException(Exception): pass
