import unittest
from pyrela import *

class OperatorTests(unittest.TestCase):
    def setUp(self):
        self.r1 = Relation('r1', ['A', 'B'],
                           [[0, 0],
                            [1, 0],
                            [0, 1],
                            [1, 1]])
        self.r2 = Relation('r2', ['B', 'C'],
                           [[0, 0],
                            [1, 0],
                            [0, 1],
                            [1, 1]])
        self.r3 = Relation('r3', ['I', 'S'],
                           [[0, 'a'],
                            [1, 'a'],
                            [0, 'b'],
                            [1, 'b']])

        self.r4 = Relation('r4', ['A', 'B'],
                           [[1, 2], [3, 4]])

        self.r5 = Relation('r4', ['A', 'B'],
                           [[3, 4], [5, 6]])

    def test_project(self):
        r = Relation('r', ['A'], [[0], [1]])
        self.assertTrue(self.r1.project(['A']).equal(r))

    def test_rename(self):
        self.assertTrue(self.r1.rename(['B', 'C']).equal(self.r2))

    def test_select_on_integer_eq(self):
        r = Relation('r', ['I', 'S'],
                     [[0, 'a'],
                      [0, 'b']])
        self.assertTrue(self.r3.select("I == 0").equal(r))

    def test_select_on_integer_lt(self):
        r = Relation('r', ['I', 'S'],
                     [[0, 'a'],
                      [0, 'b']])
        self.assertTrue(self.r3.select("I < 1").equal(r))

    def test_select_on_integer_gte(self):
        self.assertTrue(self.r3.select("I >= 0").equal(self.r3))

    def test_select_on_string_eq(self):
        r = Relation('r', ['I', 'S'],
                     [[0, 'a'],
                      [1, 'a']])
        self.assertTrue(self.r3.select("S == 'a'").equal(r))
        
    def test_select_on_string_gt(self):
        r = Relation('r', ['I', 'S'],
                     [[0, 'b'],
                      [1, 'b']])
        self.assertTrue(self.r3.select("S > 'a'").equal(r))

    def test_select_on_string_lte(self):
        self.assertTrue(self.r3.select("S <= 'b'").equal(self.r3))

    def test_cross(self):
        ra = Relation('ra', ['A'], [[0], [1]])
        rb = Relation('rb', ['B'], [[0], [1]])

        self.assertTrue(cross(ra, rb).equal(self.r1))

    def test_join(self):
        rj = Relation('rj', ['A', 'B', 'C'],
                      [[0, 0, 0],
                       [0, 0, 1],
                       [1, 0, 0],
                       [1, 0, 1],
                       [0, 1, 0],
                       [0, 1, 1],
                       [1, 1, 0],
                       [1, 1, 1]])
        self.assertTrue(join(self.r1, self.r2).equal(rj))

class ErrorTests(unittest.TestCase):
    def setUp(self):
        self.person = Relation.from_csv('person.csv', ['name', 'age', 'gender'])
        self.frequents = Relation.from_csv('frequents.csv', ['name', 'pizzeria'])
        self.eats = Relation.from_csv('eats.csv', ['name', 'pizza'])
        self.serves = Relation.from_csv('serves.csv', ['pizzeria', 'pizza', 'price'])
    
    def test_project_error(self):
        self.assertRaises(ProjectException, self.person.project, ['pizza'])

    def test_rename_error(self):
        self.assertRaises(RenameException, self.frequents.rename, ['age'])

    def test_select_error_1(self):
        self.assertRaises(SelectException, self.eats.select, "name")

    def test_select_error_2(self):
        self.assertRaises(SelectException, self.serves.select, "gender == 'male'")

    def test_cross_error(self):
        self.assertRaises(CrossException, cross, self.person, self.frequents)

    def test_join_error(self):
        self.assertRaises(JoinException, join, self.person, self.serves)

class PizzaTests(unittest.TestCase):
    def setUp(self):
        self.person = Relation.from_csv('person.csv', ['name', 'age', 'gender'])
        self.frequents = Relation.from_csv('frequents.csv', ['name', 'pizzeria'])
        self.eats = Relation.from_csv('eats.csv', ['name', 'pizza'])
        self.serves = Relation.from_csv('serves.csv', ['pizzeria', 'pizza', 'price'])

    def test_1(self):
        # Find all pizzerias frequented by at least one person under the age of 18
        computed = join(self.person.select('age < 18'), self.frequents).project(['pizzeria'])
        expected = Relation("", ["pizzeria"], [["Straw Hat"], ["New York Pizza"], ["Pizza Hut"]])
        self.assertTrue(computed.equal(expected))

if __name__ == '__main__':
    unittest.main()
