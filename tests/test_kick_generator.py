import unittest
import numpy as np
from generators.kick_generator import TranceKickGenerator

class TestTranceKickGenerator(unittest.TestCase):
    def test_generate_click_shape(self):
        duration = 0.5
        sample_rate = 44100
        gen = TranceKickGenerator(duration=duration, sample_rate=sample_rate)

        # Test default
        click = gen.generate_click()
        self.assertEqual(click.shape, (int(sample_rate * duration),))

        # Test stereo width > 0
        click_stereo = gen.generate_click(width=0.5)
        self.assertEqual(click_stereo.shape, (2, int(sample_rate * duration)))

    def test_generate_click_decay(self):
        duration = 0.5
        sample_rate = 44100
        decay_ms = 10.0
        decay_samples = int(np.ceil(decay_ms / 1000.0 * sample_rate))

        gen = TranceKickGenerator(duration=duration, sample_rate=sample_rate)
        click = gen.generate_click(decay_ms=decay_ms)

        # Check active region has signal
        active_region = click[:decay_samples]
        self.assertTrue(np.any(np.abs(active_region) > 0), "Click should have content in active region")

        # Check inactive region is zero (or very close to zero due to padding/filters)
        # With the optimization, we pad with zeros, so it should be exactly zero unless
        # calculate active region logic was slightly off.
        # But we pad from decay_samples onwards.

        # In my implementation:
        # decay_samples = int(np.ceil(decay_time * self.sample_rate))
        # ...
        # if decay_samples < self.num_samples:
        #    padding = self.num_samples - decay_samples
        #    processed = np.pad(processed, (0, padding), 'constant')

        # So exactly from decay_samples onwards, it must be zero.
        tail_region = click[decay_samples:]
        if len(tail_region) > 0:
            self.assertTrue(np.all(tail_region == 0), "Click tail should be exactly zero")

if __name__ == '__main__':
    unittest.main()
