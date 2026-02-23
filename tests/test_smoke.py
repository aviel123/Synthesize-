
import unittest
import numpy as np
from generators.kick_generator import TranceKickGenerator

class TestKickGenerator(unittest.TestCase):
    def test_smoke_generation(self):
        """
        Smoke test to ensure the generator runs without crashing.
        """
        gen = TranceKickGenerator(sample_rate=44100, duration=0.5)
        audio = gen.generate(
            click_level=1.0,
            click_decay_ms=10.0,
            drive_db=4.5,
            reverb_amount=0.0,
            delay_amount=0.0,
            generate_bass=False,
            bass_freq=55.0,
            sc_depth=0.8
        )
        self.assertEqual(len(audio), int(44100 * 0.5))
        self.assertTrue(np.max(np.abs(audio)) > 0)

    def test_oversampling_smoke(self):
        """
        Test oversampling mode (runs 2x sample rate).
        """
        gen = TranceKickGenerator(sample_rate=44100, duration=0.5)
        audio = gen.generate(oversample=2)
        self.assertEqual(len(audio), int(44100 * 0.5))

    def test_stereo_smoke(self):
        """
        Test stereo click (width > 0).
        """
        gen = TranceKickGenerator(sample_rate=44100, duration=0.5)
        audio = gen.generate(click_width=1.0)
        # Should be stereo? generate returns 1D if everything else is mono?
        # generate() logic:
        # mix = (punch * 0.7) + (body * 0.8) + (click * 0.5)
        # punch/body start mono. click is stereo.
        # click expands others.
        # So output should be (2, N)
        self.assertEqual(audio.ndim, 2)
        self.assertEqual(audio.shape[1], int(44100 * 0.5))

if __name__ == '__main__':
    unittest.main()
