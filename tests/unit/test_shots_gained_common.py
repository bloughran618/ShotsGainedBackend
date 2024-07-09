import sys
import unittest

sys.path.append('../../python/shots_gained_common/layer/python/lib/python3.9/site-packages')

from shots_gained_common import lookup_shot_gained, get_shot_gained


class TestLambdaHandler(unittest.TestCase):

    def test_lookup_tee(self):
        self.assertEqual(lookup_shot_gained(450, 'tee'), 4.17)

    def test_lookup_fairway(self):
        self.assertEqual(lookup_shot_gained(115, 'fairway'), 2.84)

    def test_lookup_rough(self):
        self.assertEqual(lookup_shot_gained(199, 'rough'), 3.42)

    def test_lookup_sand(self):
        self.assertEqual(lookup_shot_gained(76, 'sand'), 3.24)

    def test_lookup_recovery(self):
        self.assertEqual(lookup_shot_gained(145.000001, 'recovery'), 3.8)

    def test_invalid_shot_type(self):
        with self.assertRaises(RuntimeError):
            lookup_shot_gained(55, 'House')

    def test_shots_table_has_none(self):
        with self.assertRaises(ValueError):
            lookup_shot_gained(15, 'tee')

    def test_tee_to_fairway_shotsgained(self):
        self.assertEqual(get_shot_gained(450, 'Tee', 115, 'Fairway'), 0.33)

    def test_fairway_to_green_shotsgained(self):
        self.assertEqual(get_shot_gained(115, 'fairway', 10, 'GREEN'), 0.23)

    def test_green_to_hole_shotsgained(self):
        self.assertEqual(get_shot_gained(10, 'Green', 0, 'asdf'), 0.61)

    def test_tee_to_recovery_shotsgained(self):
        self.assertEqual(get_shot_gained(299, 'tee', 196.0000001, 'recovery'), -1.16)

    def test_fairway_to_sand_shotsgained(self):
        self.assertEqual(get_shot_gained(246, 'fairway', 45, 'sand'), -0.38)

    def test_dunk(self):
        self.assertEqual(get_shot_gained(50, 'sand', 0, 'dunk'), 1.98)

    def test_shots_table_has_none_shotsgained(self):
        with self.assertRaises(ValueError):
            get_shot_gained(450, 'tee', 70, 'recovery')

