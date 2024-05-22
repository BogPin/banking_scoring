import unittest
import numpy as np
from scoring import voronin_scoring, format_integro_text

class TestScoring(unittest.TestCase):
    
    def test_voronin_scoring(self):
        normalized_data = np.array([[0.1, 0.2], [0.3, 0.4]])
        n = 2
        num_persons = 2
        integro, canvas, ax, fig, line1 = voronin_scoring(normalized_data, n, num_persons)
        self.assertEqual(len(integro), 2)
    
    def test_format_integro_text(self):
        integro_scores = np.array([1.0, 2.0])
        formatted_text = format_integro_text(integro_scores)
        self.assertIn("1: 1.000000000000000000e+00", formatted_text)
        self.assertIn("2: 2.000000000000000000e+00", formatted_text)

if __name__ == '__main__':
    unittest.main()
