import unittest
import numpy as np
from generators.kick_generator import TranceKickGenerator

class TestKickGenerator(unittest.TestCase):
    def test_generate_punch(self):
        gen = TranceKickGenerator(duration=0.5)
        punch = gen.generate_punch()
        self.assertEqual(len(punch), gen.num_samples)
        self.assertTrue(np.max(np.abs(punch)) > 0)

    def test_generate_body(self):
        gen = TranceKickGenerator(duration=0.5)
        body = gen.generate_body()
        self.assertEqual(len(body), gen.num_samples)
        self.assertTrue(np.max(np.abs(body)) > 0)

    def test_generate_click(self):
        gen = TranceKickGenerator(duration=0.5)
        click = gen.generate_click()
        self.assertEqual(len(click), gen.num_samples)
        self.assertTrue(np.max(np.abs(click)) > 0)

    def test_generate_full(self):
        gen = TranceKickGenerator(duration=0.5)
        kick = gen.generate()
        self.assertEqual(len(kick), gen.num_samples)
        self.assertTrue(np.max(np.abs(kick)) > 0)

if __name__ == '__main__':
    unittest.main()
