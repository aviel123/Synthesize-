
import unittest
import numpy as np
from generators.kick_generator import TranceKickGenerator


class TestTranceKickGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = TranceKickGenerator(sample_rate=44100, duration=0.5)

    def test_generate_click_shape_mono(self):
        # Test default mono click
        click = self.generator.generate_click(
            level=1.0, decay_ms=10.0, width=0.0)
        self.assertEqual(click.shape, (self.generator.num_samples,))
        self.assertTrue(np.max(np.abs(click)) > 0)

    def test_generate_click_shape_stereo(self):
        # Test stereo click
        click = self.generator.generate_click(
            level=1.0, decay_ms=10.0, width=1.0)
        self.assertEqual(click.shape, (2, self.generator.num_samples))
        self.assertTrue(np.max(np.abs(click)) > 0)
        # Verify stereo content (L != R)
        self.assertFalse(np.allclose(click[0], click[1]))

    def test_generate_click_active_region(self):
        # Test that signal is present in active region and silent in inactive
        decay_ms = 10.0
        click = self.generator.generate_click(
            level=1.0, decay_ms=decay_ms, width=0.0)

        # Calculate samples (use ceil to cover all partial samples)
        # t < decay_time determines activity
        decay_samples = int(
            np.ceil(decay_ms / 1000.0 * self.generator.sample_rate))

        # Check active region has signal
        active_segment = click[:decay_samples]
        self.assertTrue(np.max(np.abs(active_segment)) > 0,
                        "Active region should have signal")

        # Check inactive region is silent
        # The current implementation zeros out strictly after decay_time
        inactive_segment = click[decay_samples:]
        self.assertTrue(np.all(inactive_segment == 0),
                        "Inactive region should be strictly zero")

    def test_generate_click_very_short_decay(self):
        # Test edge case with very short decay
        decay_ms = 1.0
        click = self.generator.generate_click(
            level=1.0, decay_ms=decay_ms, width=0.0)
        decay_samples = int(
            np.ceil(decay_ms / 1000.0 * self.generator.sample_rate))

        self.assertTrue(np.max(np.abs(click[:decay_samples])) > 0)
        self.assertTrue(np.all(click[decay_samples:] == 0))

    def test_generate_click_long_decay(self):
        # Test decay longer than duration (clamped)
        # If decay_ms > duration, active_samples > num_samples (clamped).

        decay_ms = 1000.0  # 1 second > 0.5s duration
        click = self.generator.generate_click(
            level=1.0, decay_ms=decay_ms, width=0.0)

        self.assertEqual(click.shape, (self.generator.num_samples,))
        # Should be non-zero throughout most of it
        self.assertTrue(np.max(np.abs(click)) > 0)


if __name__ == '__main__':
    unittest.main()
