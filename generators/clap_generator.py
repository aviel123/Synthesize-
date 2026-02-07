import numpy as np
from scipy.signal import butter, lfilter
from effects.stereo import apply_stereo_width

def apply_stereo_width(signal, width=0.0):
    """
    Local simplified stereo widener if import fails or for custom behavior.
    Decorrelates L/R by delaying one channel.
    """
    if width <= 0.001:
        return signal

    # Mono to Pseudo Stereo
    # Delay Right Channel by 10-20ms
    delay_ms = 12.0
    sr = 44100
    delay_samples = int(delay_ms * sr / 1000.0)

    L = signal
    R = np.zeros_like(signal)

    # R is delayed version
    if len(signal) > delay_samples:
        R[delay_samples:] = signal[:-delay_samples]

    # Mix
    # Width 0 = Mono (L=R=Signal)
    # Width 1 = Hard Pan (L=Signal, R=Delayed)

    # Actually standard widener:
    # Mid = Signal
    # Side = (L-R) -> Here L=Sig, R=Sig_Delayed -> Side = Comb Filtered

    # Let's just return L/R array
    return np.vstack((L, R))


class ClapGenerator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.duration = 0.5 # Default duration
        self.num_samples = int(sample_rate * self.duration)

    def _create_reflections(self, num_reflections=5, spacing_ms=8.0):
        """
        Creates the 'machine clap' effect using spaced impulses/noise bursts.
        """
        # Reflections are typically noise bursts played in rapid succession

        spacing_samples = int(spacing_ms * self.sample_rate / 1000.0)
        total_len = spacing_samples * num_reflections + 1000 # buffer

        # Create single burst
        burst_len_ms = 4.0
        burst_samples = int(burst_len_ms * self.sample_rate / 1000.0)
        burst_env = np.linspace(1.0, 0.0, burst_samples)

        # Bandpass noise for burst
        noise = np.random.uniform(-1, 1, burst_samples)
        nyquist = 0.5 * self.sample_rate
        low = 900.0 / nyquist
        high = 4000.0 / nyquist
        b, a = butter(2, [low, high], btype='band')
        filtered_burst = lfilter(b, a, noise) * burst_env

        # Arrange bursts
        output = np.zeros(self.num_samples)

        for i in range(num_reflections):
            start = i * spacing_samples
            end = start + len(filtered_burst)

            # Amplitude decay for reflections
            amp = 1.0 - (i / (num_reflections + 1)) # Linear decay

            if end < self.num_samples:
                output[start:end] += filtered_burst * amp

        return output

    def _create_transient(self, decay_ms=5.0):
        """
        Creates the initial sharp attack using filtered noise + sine burst.
        """
        # Noise burst
        noise = np.random.uniform(-1, 1, self.num_samples)

        # Bandpass filter for "snap" (1kHz - 5kHz)
        nyquist = 0.5 * self.sample_rate
        low = 1000.0 / nyquist
        high = 5000.0 / nyquist
        b, a = butter(2, [low, high], btype='band')
        filtered_noise = lfilter(b, a, noise)

        # Short envelope
        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)
        decay_samples = int(decay_ms * self.sample_rate / 1000.0)

        env = np.zeros_like(t)
        if decay_samples > 0:
            env[:decay_samples] = np.linspace(1.0, 0.0, decay_samples)

        return filtered_noise * env

    def _create_tail(self, length_ms=150.0):
        """
        Creates the main body/tail of the clap using pink/white noise.
        """
        # Pink noise approximation (1/f)
        white = np.random.normal(0, 1, self.num_samples)
        # Simple 1/f filter: -3dB/octave? Or just lowpass white noise.
        # Let's use white noise with a specific filter for "clap" character

        # Bandpass 800Hz - 8000Hz
        nyquist = 0.5 * self.sample_rate
        low = 800.0 / nyquist
        high = 8000.0 / nyquist
        b, a = butter(2, [low, high], btype='band')
        filtered = lfilter(b, a, white)

        # Envelope: Exponential decay
        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)
        decay_samples = int(length_ms * self.sample_rate / 1000.0)

        env = np.zeros_like(t)
        if decay_samples > 0:
            # Exponential decay
            k = 5.0 / (length_ms / 1000.0)
            env[:decay_samples] = np.exp(-k * t[:decay_samples])

        return filtered * env

    def generate(self, transient_level=1.0, tail_length_ms=100.0, reflections=5, spacing_ms=8.0, stereo_width=0.0):
        # 1. Transient (Attack)
        transient = self._create_transient() * transient_level

        # 2. Reflections (Body)
        reflections_audio = self._create_reflections(num_reflections=reflections, spacing_ms=spacing_ms)

        # 3. Tail (Sustain)
        tail = self._create_tail(length_ms=tail_length_ms)

        # Combine
        mix = transient + reflections_audio * 0.8 + tail * 0.7

        # Normalize Mono First
        max_val = np.max(np.abs(mix))
        if max_val > 0:
            mix = mix / max_val * 0.95

        # Apply Stereo Width
        # If width > 0, we need to create stereo content.
        # The simple Apply Stereo Width assumes stereo input or just duplicates mono.
        # To truly widen a clap, we can pan reflections or delay channels slightly.

        if stereo_width > 0.001:
            # Create decorrelated tail/reflections
            # Simple Haasz effect or delay L/R

            # Use utility from effects
            mix = apply_stereo_width(mix, width=stereo_width)

            # Or better: Pan reflections alternating L/R?
            # That's complex for now. Let's stick to the utility which handles basic widening.

        return mix
