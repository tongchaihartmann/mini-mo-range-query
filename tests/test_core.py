"""Tests for MoRangeQuery focusing on distinct-sum range queries."""

import unittest

from mini_mo_range_query import MoRangeQuery


def make_callbacks(data):
    """Build add/remove/get_answer callbacks tracking distinct element count."""

    counts = {}

    def add(i, c=counts, d=data):
        v = d[i]
        c[v] = c.get(v, 0) + 1

    def remove(i, c=counts, d=data):
        v = d[i]
        c[v] -= 1
        if c[v] == 0:
            del c[v]

    def get_answer(c=counts):
        return len(c)

    return add, remove, get_answer


class TestMoRangeQuery(unittest.TestCase):
    def test_basic_single_query(self):
        data = [1, 1, 2, 3, 2]
        mo = MoRangeQuery(data)
        mo.add_query(0, 5)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [3])

    def test_empty_range_query(self):
        data = [1, 2, 3]
        mo = MoRangeQuery(data)
        mo.add_query(1, 1)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [0])

    def test_single_element_query(self):
        data = [5, 7, 9]
        mo = MoRangeQuery(data)
        mo.add_query(1, 2)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [1])

    def test_multiple_queries_with_overlap(self):
        data = [1, 2, 1, 3, 2, 1, 4]
        mo = MoRangeQuery(data)
        mo.add_query(0, 7)
        mo.add_query(2, 5)
        mo.add_query(0, 3)
        mo.add_query(4, 7)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers[0], 4)
        self.assertEqual(mo.answers[1], 3)
        self.assertEqual(mo.answers[2], 2)
        self.assertEqual(mo.answers[3], 3)

    def test_answers_in_registration_order(self):
        data = [1, 2, 3, 4, 5]
        mo = MoRangeQuery(data)
        mo.add_query(0, 5)
        mo.add_query(0, 1)
        mo.add_query(4, 5)
        mo.add_query(0, 5)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [5, 1, 1, 5])

    def test_no_queries(self):
        data = [1, 2, 3]
        mo = MoRangeQuery(data)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [])

    def test_empty_data_no_queries(self):
        mo = MoRangeQuery([])
        add, rem, get = make_callbacks([])
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [])

    def test_single_element_data(self):
        data = [42]
        mo = MoRangeQuery(data)
        mo.add_query(0, 1)
        mo.add_query(0, 0)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [1, 0])

    def test_all_same_values(self):
        data = [7, 7, 7, 7]
        mo = MoRangeQuery(data)
        mo.add_query(0, 4)
        mo.add_query(1, 3)
        mo.add_query(0, 0)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [1, 1, 0])

    def test_invalid_query_indices(self):
        data = [1, 2, 3]
        mo = MoRangeQuery(data)
        with self.assertRaises(ValueError):
            mo.add_query(-1, 2)
        with self.assertRaises(ValueError):
            mo.add_query(0, 4)
        with self.assertRaises(ValueError):
            mo.add_query(3, 2)

    def test_invalid_data_type(self):
        with self.assertRaises(TypeError):
            MoRangeQuery("not a list")

    def test_tuple_data(self):
        data = (1, 2, 3, 2, 1)
        mo = MoRangeQuery(data)
        mo.add_query(0, 5)
        mo.add_query(1, 4)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [3, 2])

    def test_full_range_on_large_input(self):
        n = 100
        data = list(range(n))
        mo = MoRangeQuery(data)
        mo.add_query(0, n)
        mo.add_query(0, n // 2)
        mo.add_query(n // 2, n)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [n, n // 2, n // 2])

    def test_interleaved_queries_force_cursor_movement(self):
        data = list(range(10))
        mo = MoRangeQuery(data)
        # Deliberately interleave far-apart ranges so the Mo cursor must travel.
        mo.add_query(0, 1)
        mo.add_query(9, 10)
        mo.add_query(0, 1)
        mo.add_query(9, 10)
        mo.add_query(0, 10)
        add, rem, get = make_callbacks(data)
        mo.run(add, rem, get)
        self.assertEqual(mo.answers, [1, 1, 1, 1, 10])


if __name__ == "__main__":
    unittest.main()
