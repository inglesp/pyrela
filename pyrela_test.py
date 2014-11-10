import unittest
from pyrela import *


class PredicateTests(unittest.TestCase):
    def test_leaf_lhs_field_rhs_value(self):
        predicate = build_predicate_fn({'lhs': F('A'), 'rhs': 10})
        self.assertFalse(predicate({'A': 9}))
        self.assertTrue(predicate({'A': 10}))
        self.assertFalse(predicate({'A': 11}))


    def test_leaf_lhs_field_rhs_value_with_comparator(self):
        predicate = build_predicate_fn({'lhs': F('A'), 'rhs': 10, 'comparator': 'lt'})
        self.assertTrue(predicate({'A': 9}))
        self.assertFalse(predicate({'A': 10}))
        self.assertFalse(predicate({'A': 11}))


    def test_leaf_lhs_value_rhs_field(self):
        predicate = build_predicate_fn({'lhs': 10, 'rhs': F('A')})
        self.assertFalse(predicate({'A': 9}))
        self.assertTrue(predicate({'A': 10}))
        self.assertFalse(predicate({'A': 11}))


    def test_leaf_lhs_value_rhs_value(self):
        predicate = build_predicate_fn({'lhs': 10, 'rhs': 11})
        self.assertFalse(predicate({}))

        predicate = build_predicate_fn({'lhs': 10, 'rhs': 10})
        self.assertTrue(predicate({}))


    def test_leaf_lhs_field_rhs_field(self):
        predicate = build_predicate_fn({'lhs': F('A'), 'rhs': F('B')})
        self.assertTrue(predicate({'A': 10, 'B': 10}))
        self.assertFalse(predicate({'A': 10, 'B': 11}))


    def test_non_leaf_and_connector_not_negated(self):
        predicate = build_predicate_fn(
            {'lhs': F('A'), 'rhs': 10},
            {'lhs': F('B'), 'rhs': 10},
        )
        self.assertTrue(predicate({'A': 10, 'B': 10}))
        self.assertFalse(predicate({'A': 10, 'B': 11}))
        self.assertFalse(predicate({'A': 11, 'B': 10}))
        self.assertFalse(predicate({'A': 11, 'B': 11}))


    def test_non_leaf_and_connector_negated(self):
        predicate = build_predicate_fn(
            {'lhs': F('A'), 'rhs': 10},
            {'lhs': F('B'), 'rhs': 10},
            negated=True,
        )
        self.assertFalse(predicate({'A': 10, 'B': 10}))
        self.assertTrue(predicate({'A': 10, 'B': 11}))
        self.assertTrue(predicate({'A': 11, 'B': 10}))
        self.assertTrue(predicate({'A': 11, 'B': 11}))


    def test_non_leaf_or_connector_not_negated(self):
        predicate = build_predicate_fn(
            {'lhs': F('A'), 'rhs': 10},
            {'lhs': F('B'), 'rhs': 10},
            connector='OR',
        )
        self.assertTrue(predicate({'A': 10, 'B': 10}))
        self.assertTrue(predicate({'A': 10, 'B': 11}))
        self.assertTrue(predicate({'A': 11, 'B': 10}))
        self.assertFalse(predicate({'A': 11, 'B': 11}))


    def test_non_leaf_or_connector_negated(self):
        predicate = build_predicate_fn(
            {'lhs': F('A'), 'rhs': 10},
            {'lhs': F('B'), 'rhs': 10},
            connector='OR',
            negated=True,
        )
        self.assertFalse(predicate({'A': 10, 'B': 10}))
        self.assertFalse(predicate({'A': 10, 'B': 11}))
        self.assertFalse(predicate({'A': 11, 'B': 10}))
        self.assertTrue(predicate({'A': 11, 'B': 11}))


    def test_non_leaf_with_non_leaves(self):
        predicate = build_predicate_fn(
            (
                [
                    {'lhs': F('A'), 'rhs': 10},
                    {'lhs': F('A'), 'rhs': 11},
                ],
                dict(connector='OR')
            ),
            (
                [
                    {'lhs': F('B'), 'rhs': 10},
                    {'lhs': F('B'), 'rhs': 11},
                ],
                dict(connector='OR')
            ),
            connector='AND'
        )
        self.assertTrue(predicate({'A': 10, 'B': 10}))
        self.assertTrue(predicate({'A': 10, 'B': 11}))
        self.assertTrue(predicate({'A': 11, 'B': 10}))
        self.assertTrue(predicate({'A': 11, 'B': 11}))
        self.assertFalse(predicate({'A': 10, 'B': 12}))
        self.assertFalse(predicate({'A': 12, 'B': 10}))
        self.assertFalse(predicate({'A': 12, 'B': 12}))


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
        predicate = {'lhs': F('A'), 'rhs': 1}
        self.assertEqual(self.r1.select(predicate), r)


    def test_cross(self):
        ra = Relation(['A'], [[0], [1]])
        rb = Relation(['B'], [[0], [1]])

        self.assertEqual(cross(ra, rb), self.r1)


    def test_join(self):
        r1 = Relation(['A', 'B', 'C'], [[0, 0, 0], [0, 1, 1]])
        r2 = Relation(['B', 'C', 'D'], [[0, 0, 0], [1, 1, 0]])
        rj = Relation(['A', 'B', 'C', 'D'], [[0, 0, 0, 0], [0, 1, 1, 0]])
        self.assertEqual(join(r1, r2), rj)


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
        predicate = ({'lhs': F('age'), 'rhs': 18, 'comparator': 'lt'})
        computed = join(self.person.select(predicate), self.frequents).project(['pizzeria'])
        expected = Relation(['pizzeria'], [['Straw Hat'], ['New York Pizza'], ['Pizza Hut']])
        self.assertEqual(computed, expected)


    def test_b(self):
        # Find the names of all females who eat either mushroom or pepperoni
        # pizza (or both)
        predicates = [
            {'lhs': F('gender'), 'rhs': 'female'},
            (
                [
                    {'lhs': F('pizza'), 'rhs': 'mushroom'},
                    {'lhs': F('pizza'), 'rhs': 'pepperoni'},
                ],
                dict(connector='OR')
            )
        ]
        computed = join(self.person, self.eats).select(*predicates).project(['name'])
        expected = Relation(['name'], [['Amy'], ['Fay']])
        self.assertEqual(computed, expected)


    def test_c(self):
        # Find the names of all females who eat both mushroom and pepperoni
        # pizza
        mushroom_predicates =  [
            {'lhs': F('pizza'), 'rhs': 'mushroom'},
            {'lhs': F('gender'), 'rhs': 'female'},
        ]
        mushroom_rel = join(self.person, self.eats). \
            select(*mushroom_predicates). \
            project(['name'])

        pepperoni_predicates =  [
            {'lhs': F('pizza'), 'rhs': 'pepperoni'},
            {'lhs': F('gender'), 'rhs': 'female'},
        ]
        pepperoni_rel = join(self.person, self.eats). \
            select(*pepperoni_predicates). \
            project(['name'])

        computed = intersection(mushroom_rel, pepperoni_rel)
        expected = Relation(['name'], [['Amy']])
        self.assertEqual(computed, expected)

    def test_d(self):
        # Find all pizzerias that serve at least one pizza that Amy eats for
        # less than $10.00
        computed = join(
            self.eats.select({'lhs': F('name'), 'rhs': 'Amy'}),
            self.serves.select({'lhs': F('price'), 'rhs': 10, 'comparator': 'lt'}),
        ).project(['pizzeria'])

        expected = Relation(['pizzeria'], [['Little Caesars'], ['Straw Hat'], ['New York Pizza']])
        self.assertEqual(computed, expected)


    def test_e(self):
        # Find all pizzerias that are frequented by only females or only males
        female_rel = join(
            self.person.select({'lhs': F('gender'), 'rhs': 'female'}),
            self.frequents
        ).project(['pizzeria'])

        male_rel = join(
            self.person.select({'lhs': F('gender'), 'rhs': 'male'}),
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
            join(self.frequents, self.serves).project(['name', 'pizza'])
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
                join(self.eats, self.serves).project(['name', 'pizzeria'])
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
                join(self.eats, self.serves).project(['name', 'pizzeria']),
                self.frequents
            ).project(['name'])
        )

        expected = Relation(['name'], [['Fay']])
        self.assertEqual(computed, expected)


    def test_i(self):
        # Find the pizzeria serving the cheapest pepperoni pizza. In the case
        # of ties, return all of the cheapest-pepperoni pizzerias
        pepperoni_rel = self.serves.select({'lhs': F('pizza'), 'rhs': 'pepperoni'})

        computed = diff(
            pepperoni_rel.project(['pizzeria']),
            cross(
                pepperoni_rel.project(['pizzeria', 'price']),
                pepperoni_rel.project(['pizzeria', 'price']).rename(['pizzeria2', 'price2'])
            ).select({'lhs': F('price'), 'rhs': F('price2'), 'comparator': 'gt'}).project(['pizzeria'])
        )

        expected = Relation(['pizzeria'], [['Straw Hat'], ['New York Pizza']])
        self.assertEqual(computed, expected)

if __name__ == '__main__':
    unittest.main()
