import math
import unittest

import numpy as np

from packages.ai_engine.python.cosine import cosine_similarity, similarity_to_percentage


class TestCosineSimilarity(unittest.TestCase):
    def test_identical_vectors(self):
        vector = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(cosine_similarity(vector, vector), 1.0)

    def test_orthogonal_vectors(self):
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)

    def test_opposite_vectors(self):
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [-1.0, 0.0]), -1.0)

    def test_normalized_dot_product(self):
        left = np.array([0.6, 0.8])
        right = np.array([0.8, 0.6])
        expected = float(np.dot(left, right))
        self.assertAlmostEqual(cosine_similarity(left, right), expected)

    def test_empty_vector_raises(self):
        with self.assertRaises(ValueError):
            cosine_similarity([], [1.0])

    def test_shape_mismatch_raises(self):
        with self.assertRaises(ValueError):
            cosine_similarity([1.0, 2.0], [1.0])

    def test_similarity_to_percentage_bounds(self):
        self.assertEqual(similarity_to_percentage(0.0), 0)
        self.assertEqual(similarity_to_percentage(0.5), 50)
        self.assertEqual(similarity_to_percentage(1.0), 100)

    def test_similarity_to_percentage_clamps(self):
        self.assertEqual(similarity_to_percentage(1.5), 100)
        self.assertEqual(similarity_to_percentage(-0.5), 0)


if __name__ == '__main__':
    unittest.main()
