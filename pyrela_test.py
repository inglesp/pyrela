import unittest
from pyrela import *

class SimpleRelationTest(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
