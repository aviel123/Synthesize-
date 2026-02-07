import numpy as np
from scipy.signal import butter, lfilter

class AdvancedNoiseGenerator:
    """
    Advanced Noise Generator with physical models and spectral shaping.
    Supports various noise colors and specific 'smoke' textures for trance.
    """

    def __init__(self, sample_rate=44100):
        self.sr = sample_rate

    def _highpass_filter(self, data, cutoff):
        nyquist = 0.5 * self.sr
        norm_cutoff = cutoff / nyquist
        if norm_cutoff >= 1.0: return np.zeros_like(data)
        b, a = butter(2, norm_cutoff, btype='high', analog=False)
        return lfilter(b, a, data)

    def _lowpass_filter(self, data, cutoff):
        nyquist = 0.5 * self.sr
        norm_cutoff = cutoff / nyquist
        if norm_cutoff >= 1.0: return data
        b, a = butter(2, norm_cutoff, btype='low', analog=False)
        return lfilter(b, a, data)

    def _highshelf(self, data, freq, gain_db):
        # Basic High Shelf EQ implementation (RBJ)
        A = 10 ** (gain_db / 40.0)
        w0 = 2 * np.pi * freq / self.sr
        alpha = np.sin(w0) / 2 * np.sqrt((A + 1/A) * (1/1 - 1)) if A != 1 else 0 # Simplified Q=0.707 approx
        # Actually, let's use a simpler implementation or standard library if possible.
        # Since we don't have a library for shelving easily, let's stick to a simple gain scaling for high frequencies
        # using a crossover filter.

        hp = self._highpass_filter(data, freq)
        lp = data - hp
        return lp + hp * (10 ** (gain_db / 20.0))

    def generate_noise(self, noise_type, duration):
        """
        Generates basic noise colors.
        """
        num_samples = int(duration * self.sr)

        if noise_type == 'white':
            return np.random.randn(num_samples)

        elif noise_type == 'pink':
            # 1/f noise approximation (Voss-McCartney or simple filter)
            # Simple filter: -3dB/oct
            white = np.random.randn(num_samples)
            # 10Hz to Nyquist
            b, a = butter(1, 10 / (0.5 * self.sr), btype='low') # Not quite pink
            # Better approximation:
            uneven = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
            # ... this is complex. Let's strictly filter white noise with a -3dB slope or just sum octaves.
            # Fast approximation:
            cols = 16
            array = np.empty((cols, num_samples))
            array.fill(np.nan)
            array[0, :] = np.random.randn(num_samples)
            for i in range(1, cols):
                # Sample and hold
                arr = np.random.randn(int(np.ceil(num_samples / (2**i))))
                expanded = np.repeat(arr, 2**i)[:num_samples]
                array[i, :] = expanded
            return np.sum(array, axis=0)

        elif noise_type == 'brown':
            # 1/f^2 - Integration of white noise
            white = np.random.randn(num_samples)
            return np.cumsum(white)

        elif noise_type == 'blue':
            # +3dB/oct - Differentiation of white noise
            white = np.random.randn(num_samples)
            return np.diff(white, prepend=0)

        elif noise_type == 'violet':
            # +6dB/oct - Diff of Blue? Or Highpass.
            # Approx as diff of diff
            white = np.random.randn(num_samples)
            return np.diff(np.diff(white, prepend=0), prepend=0)

        elif noise_type == 'velvet':
            # Sparse pulses
            noise = np.zeros(num_samples)
            # Density of pulses
            density = 0.05 # 5%
            indices = np.random.choice(num_samples, int(num_samples * density), replace=False)
            noise[indices] = np.random.choice([-1, 1], size=len(indices))
            return noise

        else:
            return np.random.randn(num_samples)

    def smoke_noise(self, duration, density=0.5, character='soft', hp_freq=6000, lp_freq=16000):
        """
        Trance 'Smoke' Noise generator.
        """
        num_samples = int(duration * self.sr)

        # Base: White Noise
        noise = np.random.randn(num_samples)

        # Filtering
        noise = self._highpass_filter(noise, cutoff=hp_freq)

        if character == 'analog':
            # Add crackle (sparse high amplitude spikes)
            crackle = np.zeros_like(noise)
            mask = np.random.rand(len(noise)) < 0.001 # Very sparse
            crackle[mask] = np.random.choice([-1, 1], size=np.sum(mask)) * 2.0
            noise = noise + crackle
            # Saturation
            noise = np.tanh(noise * 1.2)

        elif character == 'soft':
            # Gentle roll-off
            noise = self._lowpass_filter(noise, cutoff=lp_freq)

        elif character == 'harsh':
            # Boost highs
            noise = self._highshelf(noise, freq=10000, gain_db=6)

        elif character == 'digital':
            # Bitcrush / Quantize effect
            steps = 16
            noise = np.round(noise * steps) / steps

        # Density Control (Gating/Masking)
        # Random amplitude modulation
        if density < 1.0:
            # Create a smooth random mask? Or strictly binary?
            # Binary mask creates "sputtering", smooth is better for smoke.
            # Let's use low-passed noise as a modulator
            modulator = np.random.rand(len(noise))
            # Smooth it
            modulator = self._lowpass_filter(modulator, cutoff=50) # Slow varying
            # Threshold
            # Normalize modulator 0-1
            modulator = (modulator - np.min(modulator)) / (np.max(modulator) - np.min(modulator))
            # Map density to threshold: High density = Low threshold (pass more)
            threshold = 1.0 - density
            mask = modulator > threshold
            noise = noise * mask

        return noise

    def create_smoke_envelope(self, duration, start_delay_ms, fade_in_ms, fade_out_ms):
        """
        Custom envelope for smoke layer.
        """
        samples = int(duration * self.sr)
        envelope = np.zeros(samples)

        start_sample = int(start_delay_ms * self.sr / 1000.0)
        fade_in_samples = int(fade_in_ms * self.sr / 1000.0)
        fade_out_samples = int(fade_out_ms * self.sr / 1000.0)

        if start_sample >= samples:
            return envelope

        # Fade In
        end_fade_in = start_sample + fade_in_samples
        if end_fade_in > samples: end_fade_in = samples

        for i in range(start_sample, end_fade_in):
            rel_pos = (i - start_sample) / fade_in_samples
            envelope[i] = rel_pos ** 2 # Convex fade in

        # Sustain
        sustain_end = samples - fade_out_samples
        if sustain_end < end_fade_in: sustain_end = end_fade_in

        envelope[end_fade_in:sustain_end] = 1.0

        # Fade Out
        for i in range(sustain_end, samples):
            rel_pos = (i - sustain_end) / fade_out_samples
            envelope[i] = 1.0 - (rel_pos ** 0.5) # Concave fade out

        return envelope
