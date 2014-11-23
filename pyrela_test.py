import unittest
from pyrela import *


class PredicateTests(unittest.TestCase):
    def test_lhs_field_rhs_value(self):
        predicate = eq(F('A'), 10)
        self.assertFalse(predicate({'A': 9}))
        self.assertTrue(predicate({'A': 10}))
        self.assertFalse(predicate({'A': 11}))


    def test_lhs_value_rhs_field(self):
        predicate = eq(10, F('A'))
        self.assertFalse(predicate({'A': 9}))
        self.assertTrue(predicate({'A': 10}))
        self.assertFalse(predicate({'A': 11}))


    def test_lhs_value_rhs_value(self):
        predicate = eq(10, 11)
        self.assertFalse(predicate({}))

        predicate = eq(10, 10)
        self.assertTrue(predicate({}))


    def test_lhs_field_rhs_field(self):
        predicate = eq(F('A'), F('B'))
        self.assertTrue(predicate({'A': 10, 'B': 10}))
        self.assertFalse(predicate({'A': 10, 'B': 11}))


    def test_and(self):
        true_p = lambda record: True
        false_p = lambda record: False

        self.assertTrue(and_(true_p, true_p, true_p)({}))
        self.assertFalse(and_(false_p, true_p, true_p)({}))
        self.assertFalse(and_(true_p, false_p, true_p)({}))
        self.assertFalse(and_(true_p, true_p, false_p)({}))
        self.assertFalse(and_(false_p, false_p, true_p)({}))
        self.assertFalse(and_(false_p, true_p, false_p)({}))
        self.assertFalse(and_(true_p, false_p, false_p)({}))
        self.assertFalse(and_(false_p, false_p, false_p)({}))


    def test_or(self):
        true_p = lambda record: True
        false_p = lambda record: False

        self.assertTrue(or_(true_p, true_p, true_p)({}))
        self.assertTrue(or_(false_p, true_p, true_p)({}))
        self.assertTrue(or_(true_p, false_p, true_p)({}))
        self.assertTrue(or_(true_p, true_p, false_p)({}))
        self.assertTrue(or_(false_p, false_p, true_p)({}))
        self.assertTrue(or_(false_p, true_p, false_p)({}))
        self.assertTrue(or_(true_p, false_p, false_p)({}))
        self.assertFalse(or_(false_p, false_p, false_p)({}))


    def test_not(self):
        true_p = lambda record: True
        false_p = lambda record: False

        self.assertTrue(not_(false_p)({}))
        self.assertFalse(not_(true_p)({}))


class ComparatorTests(unittest.TestCase):
    def test_exact(self):
        fn = comparators['exact']
        self.assertTrue(fn(10, 10))
        self.assertFalse(fn(10, 11))
        self.assertTrue(fn('AAA', 'AAA'))
        self.assertFalse(fn('AAA', 'aaa'))


    def test_iexact(self):
        fn = comparators['iexact']
        self.assertTrue(fn('AAA', 'AAA'))
        self.assertTrue(fn('AAA', 'aaa'))
        self.assertFalse(fn('AAA', 'BBB'))


class AggregatorTests(unittest.TestCase):
    def setUp(self):
        self.group = [{'A': 1}, {'A': 3}, {'A': 6}]

    def test_count(self):
        aggregate = count('A')
        self.assertEqual(3, aggregate(self.group))


    def test_count_star(self):
        aggregate = count('*')
        self.assertEqual(3, aggregate(self.group))


    def test_sum(self):
        aggregate = sum_('A')
        self.assertEqual(10, aggregate(self.group))


    def test_avg(self):
        aggregate = avg('A')
        self.assertEqual(10.0 / 3, aggregate(self.group))


    def test_min(self):
        aggregate = min_('A')
        self.assertEqual(1, aggregate(self.group))


    def test_max(self):
        aggregate = max_('A')
        self.assertEqual(6, aggregate(self.group))


class OperatorTests(unittest.TestCase):
    def setUp(self):
        self.r1 = Relation(['A', 'B'], [[0, 0], [1, 0], [0, 1], [1, 1]])
        self.r2 = Relation(['B', 'C'], [[0, 0], [1, 0], [0, 1], [1, 1]])
        self.r3 = Relation(['A', 'B'], [[1, 2], [3, 4]])
        self.r4 = Relation(['A', 'B'], [[3, 4], [5, 6]])


    def test_project(self):
        r = Relation(['A'], [[0], [1]])
        self.assertEqual(self.r1.project(['A']), r)


    def test_rename(self):
        self.assertEqual(self.r1.rename(['B', 'C']), self.r2)


    def test_select(self):
        r = Relation(['A', 'B'], [[1, 0], [1, 1]])
        predicate = eq(F('A'), 1)
        self.assertEqual(self.r1.select(predicate), r)


    def test_group_by(self):
        r = Relation(['A', 'B'], [[0, 0], [1, 0], [1, 1]])
        rg = Relation(['A', 'count(B)', 'sum(B)'], [[0, 1, 0], [1, 2, 1]])

        aggregations = [count('B'), sum_('B')]
        self.assertEqual(r.group_by(['A'], aggregations), rg)


    def test_cross(self):
        ra = Relation(['A'], [[0], [1]])
        rb = Relation(['B'], [[0], [1]])

        self.assertEqual(cross(ra, rb), self.r1)


    def test_natural_join(self):
        r1 = Relation(['A', 'B', 'C'], [[0, 0, 0], [0, 1, 1]])
        r2 = Relation(['B', 'C', 'D'], [[0, 0, 0], [1, 1, 0]])
        rj = Relation(['A', 'B', 'C', 'D'], [[0, 0, 0, 0], [0, 1, 1, 0]])
        self.assertEqual(natural_join(r1, r2), rj)


    def test_inner_join(self):
        r1 = Relation(['A', 'B', 'C'], [[0, 0, 0], [0, 1, 1]])
        r2 = Relation(['D', 'E', 'F'], [[0, 0, 1], [0, 1, 0]])
        rj = Relation(['A', 'B', 'C', 'D', 'E', 'F'], [[0, 0, 0, 0, 0, 1], [0, 1, 1, 0, 1, 0]])
        self.assertEqual(inner_join(r1, r2, ('A', 'D'), ('B', 'E')), rj)


    def test_diff(self):
        r = Relation(['A', 'B'], [[1, 2]])
        self.assertEqual(diff(self.r3, self.r4), r)


    def test_union(self):
        r = Relation(['A', 'B'], [[1, 2], [3, 4], [5, 6]])
        self.assertEqual(union(self.r3, self.r4), r)


    def test_intersection(self):
        r = Relation(['A', 'B'], [[3, 4]])
        self.assertEqual(intersection(self.r3, self.r4), r)


class PizzaTests(unittest.TestCase):
    '''These come from Prof Jennifer Widom's Stanford Databases MOOC.

    See http://cs.stanford.edu/people/widom/DB-mooc.html and
    https://class.stanford.edu/c4x/DB/RA/asset/opt-rel-algebra.html.
    '''

    @classmethod
    def setUpClass(cls):
        cls.person = Relation.from_json('test_data/person.json')
        cls.frequents = Relation.from_json('test_data/frequents.json')
        cls.eats = Relation.from_json('test_data/eats.json')
        cls.serves = Relation.from_json('test_data/serves.json')


    def test_a(self):
        # Find all pizzerias frequented by at least one person under the age of
        # 18
        predicate = lt(F('age'), 18)
        computed = natural_join(self.person.select(predicate), self.frequents).project(['pizzeria'])
        expected = Relation(['pizzeria'], [['Straw Hat'], ['New York Pizza'], ['Pizza Hut']])
        self.assertEqual(computed, expected)


    def test_b(self):
        # Find the names of all females who eat either mushroom or pepperoni
        # pizza (or both)
        predicate = and_(
            eq(F('gender'), 'female'),
            or_(
                eq(F('pizza'), 'mushroom'),
                eq(F('pizza'), 'pepperoni'),
            )
        )
        computed = natural_join(self.person, self.eats).select(predicate).project(['name'])
        expected = Relation(['name'], [['Amy'], ['Fay']])
        self.assertEqual(computed, expected)


    def test_c(self):
        # Find the names of all females who eat both mushroom and pepperoni
        # pizza
        mushroom_predicate = and_(
            eq(F('pizza'), 'mushroom'),
            eq(F('gender'), 'female')
        )
        mushroom_rel = natural_join(self.person, self.eats). \
            select(mushroom_predicate). \
            project(['name'])

        pepperoni_predicate = and_(
            eq(F('pizza'), 'pepperoni'),
            eq(F('gender'), 'female')
        )
        pepperoni_rel = natural_join(self.person, self.eats). \
            select(pepperoni_predicate). \
            project(['name'])

        computed = intersection(mushroom_rel, pepperoni_rel)
        expected = Relation(['name'], [['Amy']])
        self.assertEqual(computed, expected)

    def test_d(self):
        # Find all pizzerias that serve at least one pizza that Amy eats for
        # less than $10.00
        computed = natural_join(
            self.eats.select(eq(F('name'), 'Amy')),
            self.serves.select(lt(F('price'), 10))
        ).project(['pizzeria'])

        expected = Relation(['pizzeria'], [['Little Caesars'], ['Straw Hat'], ['New York Pizza']])
        self.assertEqual(computed, expected)


    def test_e(self):
        # Find all pizzerias that are frequented by only females or only males
        female_rel = natural_join(
            self.person.select(eq(F('gender'), 'female')),
            self.frequents
        ).project(['pizzeria'])

        male_rel = natural_join(
            self.person.select(eq(F('gender'), 'male')),
            self.frequents
        ).project(['pizzeria'])

        computed = union(diff(female_rel, male_rel), diff(male_rel, female_rel))
        expected = Relation(['pizzeria'], [['Little Caesars'], ['New York Pizza'], ['Chicago Pizza']])
        self.assertEqual(computed, expected)


    def test_f(self):
        # For each person, find all pizzas the person eats that are not served
        # by any pizzeria the person frequents. Return all such person (name) /
        # pizza pairs
        computed = diff(
            self.eats,
            natural_join(self.frequents, self.serves).project(['name', 'pizza'])
        )

        expected = Relation(['name', 'pizza'], [['Amy', 'mushroom'], ['Dan', 'mushroom'], ['Gus', 'mushroom']])
        self.assertEqual(computed, expected)


    def test_g(self):
        # Find the names of all people who frequent only pizzerias serving at
        # least one pizza they eat
        computed = diff(
            self.person.project(['name']),
            diff(
                self.frequents,
                natural_join(self.eats, self.serves).project(['name', 'pizzeria'])
            ).project(['name'])
        )

        expected = Relation(['name'], [['Amy'], ['Ben'], ['Dan'], ['Eli'], ['Fay'], ['Gus'], ['Hil']])
        self.assertEqual(computed, expected)
                


    def test_h(self):
        # Find the names of all people who frequent every pizzeria serving at
        # least one pizza they eat
        computed = diff(
            self.person.project(['name']),
            diff(
                natural_join(self.eats, self.serves).project(['name', 'pizzeria']),
                self.frequents
            ).project(['name'])
        )

        expected = Relation(['name'], [['Fay']])
        self.assertEqual(computed, expected)


    def test_i(self):
        # Find the pizzeria serving the cheapest pepperoni pizza. In the case
        # of ties, return all of the cheapest-pepperoni pizzerias
        pepperoni_rel = self.serves.select(eq(F('pizza'), 'pepperoni'))

        computed = diff(
            pepperoni_rel.project(['pizzeria']),
            cross(
                pepperoni_rel.project(['pizzeria', 'price']),
                pepperoni_rel.project(['pizzeria', 'price']).rename(['pizzeria2', 'price2'])
            ).select(gt(F('price'), F('price2'))).project(['pizzeria'])
        )

        expected = Relation(['pizzeria'], [['Straw Hat'], ['New York Pizza']])
        self.assertEqual(computed, expected)


class TableTests(unittest.TestCase):
    def setUp(self):
        self.t = Table('t', ['id', 'A'])
        for a in [9, 10, 11]:
            self.t.insert({'A': a})


    def test_insert(self):
        id = self.t.insert({'A': 12})
        self.assertEqual(4, id)
        self.assertEqual(Relation(['id', 'A'], [[1, 9], [2, 10], [3, 11], [4, 12]]), self.t.rel)


    def test_delete(self):
        self.t.delete(lt(F('A'), 10))

        self.assertEqual(Relation(['id', 'A'], [[2, 10], [3, 11]]), self.t.rel)


    def test_update(self):
        self.t.update(lt(F('A'), 10), 'A', 100)

        self.assertEqual(Relation(['id', 'A'], [[1, 100], [2, 10], [3, 11]]), self.t.rel)


    def test_select_with_no_predicate(self):
        selection = self.t.select(order=[('A', 'asc')])

        self.assertEqual(
            [{'id': 1, 'A': 9}, {'id': 2, 'A': 10}, {'id': 3, 'A': 11}],
            selection.records_for_alias('t')
        )


    def test_select_with_predicate(self):
        selection = self.t.select(lte(F('A'), 10), order=[('A', 'asc')])

        self.assertEqual(
            [{'id': 1, 'A': 9}, {'id': 2, 'A': 10}],
            selection.records_for_alias('t')
        )


class InnerJoinTests(unittest.TestCase):
    def setUp(self):
        t1 = Table('t1', ['id', 'A'])
        t1.insert({'A': 9})
        t1.insert({'A': 10})

        t2 = Table('t2', ['id', 't1_id', 'B'])
        t2.insert({'t1_id': 1, 'B': 19})
        t2.insert({'t1_id': 1, 'B': 20})
        t2.insert({'t1_id': 2, 'B': 21})

        self.j = InnerJoin(t1, t2, ('id', 't1_id'))


    def test_select_with_no_predicate(self):
        self.assertEqual(
            [
                {('t1', 'id'): 1, ('t1', 'A'): 9, ('t2', 'id'): 1, ('t2', 't1_id'): 1, ('t2', 'B'): 19},
                {('t1', 'id'): 1, ('t1', 'A'): 9, ('t2', 'id'): 2, ('t2', 't1_id'): 1, ('t2', 'B'): 20},
                {('t1', 'id'): 2, ('t1', 'A'): 10, ('t2', 'id'): 3, ('t2', 't1_id'): 2, ('t2', 'B'): 21},

            ],
            self.j.select(order=[(('t2', 'id'), 'asc')]).records()
        )


    def test_select_with_predicate(self):
        self.assertEqual(
            [
                {('t1', 'id'): 1, ('t1', 'A'): 9, ('t2', 'id'): 2, ('t2', 't1_id'): 1, ('t2', 'B'): 20},
                {('t1', 'id'): 2, ('t1', 'A'): 10, ('t2', 'id'): 3, ('t2', 't1_id'): 2, ('t2', 'B'): 21},

            ],
            self.j.select(gt(F(('t2', 'B')), 19), order=[(('t2', 'id'), 'asc')],).records()
        )


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.rel = Relation(['A'], [[11], [9], [10]])


    def test_with_no_options(self):
        selection = Selection(self.rel)
        self.assertEqual(
            [[('A', a)] for a in [9, 10, 11]],
            sorted(list(record.items()) for record in selection.records())
        )


    def test_offset_with_no_order(self):
        with self.assertRaises(AssertionError):
            Selection(self.rel, offset=1)


    def test_limit_with_no_order(self):
        with self.assertRaises(AssertionError):
            Selection(self.rel, limit=1)


    def test_offset(self):
        selection = Selection(self.rel, order=[('A', 'asc')], offset=1)
        self.assertEqual([{'A': 10}, {'A': 11}], selection.records())


    def test_limit(self):
        selection = Selection(self.rel, order=[('A', 'asc')], limit=1)
        self.assertEqual([{'A': 9}], selection.records())


    def test_offset_and_limit(self):
        selection = Selection(self.rel, order=[('A', 'asc')], offset=1, limit=1)
        self.assertEqual([{'A': 10}], selection.records())


    def test_order(self):
        rel = Relation(['A', 'B', 'C'], [[1, 2, 3], [1, 2, 1], [1, 3, 2]])
        selection = Selection(rel, order=[('A', 'asc'), ('B', 'desc'), ('C', 'asc')])

        self.assertEqual(
            [
                {'A': 1, 'B': 3, 'C': 2},
                {'A': 1, 'B': 2, 'C': 1},
                {'A': 1, 'B': 2, 'C': 3},
            ],
            selection.records()
        )


if __name__ == '__main__':
    unittest.main()

