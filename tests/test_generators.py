"""Tests for audio generators."""
import sys
import os
import numpy as np
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.kick_generator import TranceKickGenerator
from generators.clap_generator import ClapGenerator
from generators.advanced_noise_generator import AdvancedNoiseGenerator


class TestTranceKickGenerator:
    def setup_method(self):
        self.gen = TranceKickGenerator(sample_rate=44100, duration=0.5)

    def test_init(self):
        assert self.gen.sample_rate == 44100
        assert self.gen.duration == 0.5
        assert self.gen.num_samples == 22050

    def test_generate_punch_shape(self):
        punch = self.gen.generate_punch()
        assert punch.shape == (22050,)

    def test_generate_body_shape(self):
        body = self.gen.generate_body()
        assert body.shape == (22050,)

    def test_generate_click_mono(self):
        click = self.gen.generate_click(level=1.0, decay_ms=10.0, width=0.0)
        assert click.shape == (22050,)

    def test_generate_click_stereo(self):
        click = self.gen.generate_click(level=1.0, decay_ms=10.0, width=1.0)
        assert click.ndim == 2
        assert click.shape[0] == 2

    def test_generate_returns_audio(self):
        audio = self.gen.generate()
        assert audio is not None
        assert len(audio) > 0

    def test_generate_amplitude_bounded(self):
        audio = self.gen.generate()
        assert np.max(np.abs(audio)) <= 1.1  # Allow small overshoot before limiter

    def test_generate_stereo_when_click_width(self):
        audio = self.gen.generate(click_width=1.0)
        assert audio.ndim == 2
        assert audio.shape[0] == 2

    def test_generate_with_oversample(self):
        audio = self.gen.generate(oversample=2)
        assert audio is not None
        # After oversampling + decimation, length should match original duration
        assert self.gen.sample_rate == 44100

    def test_generate_bassline_shape(self):
        bass = self.gen.generate_bassline(freq=55.0, length_beats=4, bpm=138.0)
        expected_samples = int(4 * (60.0 / 138.0) * 44100)
        assert abs(len(bass) - expected_samples) <= 1

    def test_apply_sidechain_same_length(self):
        signal = np.ones(44100)
        result = self.gen.apply_sidechain(signal, bpm=138.0, depth=0.8)
        assert len(result) == len(signal)

    def test_apply_sidechain_zero_depth(self):
        signal = np.ones(44100)
        result = self.gen.apply_sidechain(signal, bpm=138.0, depth=0.0)
        np.testing.assert_array_equal(result, signal)


class TestClapGenerator:
    def setup_method(self):
        self.gen = ClapGenerator(sample_rate=44100)

    def test_init(self):
        assert self.gen.sample_rate == 44100
        assert self.gen.duration == 0.5
        assert self.gen.num_samples == 22050

    def test_generate_mono(self):
        audio = self.gen.generate(stereo_width=0.0)
        assert audio.ndim == 1
        assert len(audio) == 22050

    def test_generate_stereo(self):
        audio = self.gen.generate(stereo_width=0.8)
        assert audio.ndim == 2
        assert audio.shape[0] == 2
        assert audio.shape[1] == 22050

    def test_generate_amplitude_bounded(self):
        audio = self.gen.generate()
        assert np.max(np.abs(audio)) <= 1.1

    def test_haas_stereo_uses_correct_sample_rate(self):
        # At 44100, 12ms delay = 529 samples
        mono = np.zeros(22050)
        mono[0] = 1.0
        stereo = self.gen._apply_haas_stereo(mono, width=1.0)
        delay_samples = int(12.0 * 44100 / 1000.0)
        # With width=1 and M/S blending: at delay position, R channel gets the full impulse
        assert stereo[1, delay_samples] == pytest.approx(1.0, abs=0.01)

    def test_haas_stereo_respects_width(self):
        mono = np.ones(1000)
        # width=0 should give L=R (mid-heavy)
        stereo_narrow = self.gen._apply_haas_stereo(mono, width=0.0)
        # Both channels should be nearly equal at width=0
        np.testing.assert_allclose(stereo_narrow[0], stereo_narrow[1], atol=0.1)


class TestAdvancedNoiseGenerator:
    def setup_method(self):
        self.gen = AdvancedNoiseGenerator(sample_rate=44100)

    def test_white_noise_shape(self):
        noise = self.gen.generate_noise('white', duration=0.1)
        assert len(noise) == int(0.1 * 44100)

    def test_pink_noise_shape(self):
        noise = self.gen.generate_noise('pink', duration=0.1)
        assert len(noise) == int(0.1 * 44100)

    def test_brown_noise_shape(self):
        noise = self.gen.generate_noise('brown', duration=0.1)
        assert len(noise) == int(0.1 * 44100)

    def test_smoke_noise_shape(self):
        smoke = self.gen.smoke_noise(duration=0.5, density=0.6, character='soft')
        assert len(smoke) == int(0.5 * 44100)

    def test_smoke_envelope_shape(self):
        env = self.gen.create_smoke_envelope(
            duration=0.5, start_delay_ms=15, fade_in_ms=120, fade_out_ms=350
        )
        assert len(env) == int(0.5 * 44100)

    def test_smoke_envelope_starts_at_zero(self):
        env = self.gen.create_smoke_envelope(
            duration=0.5, start_delay_ms=15, fade_in_ms=120, fade_out_ms=350
        )
        # First samples (before start_delay) should be zero
        start_sample = int(15 * 44100 / 1000.0)
        assert np.all(env[:start_sample] == 0.0)

    def test_smoke_envelope_sustain_is_one(self):
        env = self.gen.create_smoke_envelope(
            duration=1.0, start_delay_ms=0, fade_in_ms=10, fade_out_ms=10
        )
        # Middle portion should be 1.0
        mid = len(env) // 2
        assert env[mid] == pytest.approx(1.0, abs=0.01)

    def test_smoke_envelope_ends_near_zero(self):
        env = self.gen.create_smoke_envelope(
            duration=0.5, start_delay_ms=0, fade_in_ms=10, fade_out_ms=200
        )
        # Last sample should be near zero
        assert env[-1] == pytest.approx(0.0, abs=0.1)

    def test_smoke_all_characters(self):
        for char in ('soft', 'harsh', 'analog', 'digital'):
            noise = self.gen.smoke_noise(duration=0.1, character=char)
            assert len(noise) > 0
            assert not np.any(np.isnan(noise))
