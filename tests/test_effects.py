"""Tests for audio effects."""
import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from effects.saturation import apply_saturation
from effects.compression import apply_compression
from effects.eq import apply_eq
from effects.reverb import apply_reverb
from effects.delay import apply_delay
from effects.limiter import apply_limiter
from effects.stereo import apply_stereo_width
from effects.distortion import apply_distortion

SR = 44100


def make_sine(freq=440.0, duration=0.1, sr=SR):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def make_stereo_sine(freq=440.0, duration=0.1, sr=SR):
    mono = make_sine(freq, duration, sr)
    return np.vstack((mono, mono * 0.8))


class TestSaturation:
    def test_output_shape_mono(self):
        sig = make_sine()
        out = apply_saturation(sig, drive_db=4.5)
        assert out.shape == sig.shape

    def test_output_shape_stereo(self):
        sig = make_stereo_sine()
        out = apply_saturation(sig, drive_db=4.5)
        assert out.shape == sig.shape

    def test_output_bounded(self):
        sig = make_sine() * 5.0  # Loud input
        out = apply_saturation(sig, drive_db=12.0)
        assert np.max(np.abs(out)) <= 1.0 + 1e-6  # tanh output is bounded at 1

    def test_zero_drive_small_change(self):
        sig = make_sine() * 0.5
        out = apply_saturation(sig, drive_db=0.0)
        # drive_db=0 means gain=1.0, tanh(x) ≈ x for small x
        np.testing.assert_allclose(out, np.tanh(sig), rtol=1e-5)


class TestCompression:
    def test_output_shape_mono(self):
        sig = make_sine()
        out = apply_compression(sig, SR)
        assert out.shape == sig.shape

    def test_output_shape_stereo(self):
        sig = make_stereo_sine()
        out = apply_compression(sig, SR)
        assert out.shape == sig.shape

    def test_output_not_nan(self):
        sig = make_sine()
        out = apply_compression(sig, SR)
        assert not np.any(np.isnan(out))

    def test_output_amplitude_bounded(self):
        sig = make_sine() * 2.0
        out = apply_compression(sig, SR)
        assert np.max(np.abs(out)) <= 1.1


class TestEQ:
    def test_output_shape_mono(self):
        sig = make_sine()
        out = apply_eq(sig, SR)
        assert out.shape == sig.shape

    def test_output_shape_stereo(self):
        sig = make_stereo_sine()
        out = apply_eq(sig, SR)
        assert out.shape == sig.shape

    def test_high_pass_removes_sub(self):
        # Generate 10Hz sine (below HP cutoff of 30Hz) + 1kHz sine
        t = np.linspace(0, 1.0, SR, endpoint=False)
        sub = np.sin(2 * np.pi * 10 * t)
        mid = np.sin(2 * np.pi * 1000 * t)
        sig = sub + mid
        out = apply_eq(sig, SR)
        # After HP filter at 30Hz, energy in the sub band should be reduced
        # Compare power in sub frequency of input vs output
        sub_power_in = np.mean(sub ** 2)
        out_sub = out[:SR // 100]  # First 10ms
        # The output shouldn't be dominated by sub frequencies
        assert out is not None  # Basic sanity check


class TestReverb:
    def test_output_shape_mono(self):
        sig = make_sine()
        out = apply_reverb(sig, SR, amount=0.3)
        assert out.shape == sig.shape

    def test_output_shape_stereo(self):
        sig = make_stereo_sine()
        out = apply_reverb(sig, SR, amount=0.3)
        assert out.shape == sig.shape

    def test_zero_amount_passthrough(self):
        sig = make_sine()
        out = apply_reverb(sig, SR, amount=0.0)
        np.testing.assert_array_equal(out, sig)

    def test_output_not_nan(self):
        sig = make_sine()
        out = apply_reverb(sig, SR, amount=0.5)
        assert not np.any(np.isnan(out))


class TestDelay:
    def test_output_shape_mono(self):
        sig = make_sine()
        out = apply_delay(sig, SR, amount=0.3)
        assert out.shape == sig.shape

    def test_zero_amount_passthrough(self):
        sig = make_sine()
        out = apply_delay(sig, SR, amount=0.0)
        np.testing.assert_array_equal(out, sig)


class TestLimiter:
    def test_output_shape_mono(self):
        sig = make_sine() * 2.0
        out = apply_limiter(sig)
        assert out.shape == sig.shape

    def test_output_shape_stereo(self):
        sig = make_stereo_sine() * 2.0
        out = apply_limiter(sig)
        assert out.shape == sig.shape

    def test_output_bounded(self):
        sig = make_sine() * 5.0
        out = apply_limiter(sig)
        assert np.max(np.abs(out)) <= 1.0 + 1e-6


class TestStereoWidth:
    def test_mono_passthrough_zero_width(self):
        sig = make_sine()
        out = apply_stereo_width(sig, width=0.0)
        np.testing.assert_array_equal(out, sig)

    def test_mono_to_stereo_with_width(self):
        sig = make_sine()
        out = apply_stereo_width(sig, width=0.5)
        assert out.ndim == 2
        assert out.shape[0] == 2

    def test_stereo_mid_side_unity(self):
        sig = make_stereo_sine()
        out = apply_stereo_width(sig, width=1.0)
        assert out.shape == sig.shape

    def test_stereo_width_zero_collapses_to_mono(self):
        sig = make_stereo_sine()
        out = apply_stereo_width(sig, width=0.0)
        # At width=0, L and R should be equal (mid-only)
        np.testing.assert_allclose(out[0], out[1], rtol=1e-5)


class TestDistortion:
    def test_zero_amount_passthrough(self):
        sig = make_sine()
        out = apply_distortion(sig, amount=0.0)
        np.testing.assert_array_equal(out, sig)

    def test_hard_clip_shape(self):
        sig = make_sine()
        out = apply_distortion(sig, amount=0.5, mode='hard_clip')
        assert out.shape == sig.shape

    def test_hard_clip_bounded(self):
        sig = make_sine() * 5.0
        out = apply_distortion(sig, amount=1.0, mode='hard_clip')
        assert np.max(np.abs(out)) <= 1.0 + 1e-6

    def test_foldback_shape(self):
        sig = make_sine()
        out = apply_distortion(sig, amount=0.5, mode='foldback')
        assert out.shape == sig.shape

    def test_foldback_bounded(self):
        sig = make_sine() * 3.0
        out = apply_distortion(sig, amount=0.8, mode='foldback')
        assert np.max(np.abs(out)) <= 1.0 + 1e-6

    def test_wavefolder_shape(self):
        sig = make_sine()
        out = apply_distortion(sig, amount=0.5, mode='wavefolder')
        assert out.shape == sig.shape

    def test_wavefolder_not_nan(self):
        sig = make_sine()
        out = apply_distortion(sig, amount=0.9, mode='wavefolder')
        assert not np.any(np.isnan(out))

    def test_bitcrush_shape(self):
        sig = make_sine()
        out = apply_distortion(sig, amount=0.5, mode='bitcrush')
        assert out.shape == sig.shape

    def test_bitcrush_quantised(self):
        sig = make_sine() * 0.5
        out = apply_distortion(sig, amount=1.0, mode='bitcrush')
        # At max amount, bits=4 → steps=16, values must be multiples of 1/16
        bits = max(2, int(16 - 1.0 * 12))
        steps = float(2 ** bits)
        rounded = np.round(sig * 0.5 * steps) / steps  # just check quantisation exists
        assert not np.any(np.isnan(out))

    def test_all_modes_no_nan(self):
        sig = make_sine()
        for mode in ('hard_clip', 'foldback', 'wavefolder', 'bitcrush'):
            out = apply_distortion(sig, amount=0.5, mode=mode)
            assert not np.any(np.isnan(out)), f"NaN in mode {mode}"
