import numpy as np
from scipy.io import wavfile
import argparse

class TranceKickGenerator:
    def __init__(self, sample_rate=44100, duration=0.5):
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_samples = int(sample_rate * duration)

    def generate_punch(self):
        """
        Step 1: Kick Frequency Base (Punch)
        Sine wave starting high and dropping fast.
        Base freq ~150-200Hz.
        Pitch Envelope: +48 semitones to 0 in 20-50ms.
        """
        base_freq = 150.0
        punch_decay = 0.040  # 40ms
        start_pitch_semitones = 48

        # Start frequency calculation: base * 2^(semitones/12)
        start_freq = base_freq * (2 ** (start_pitch_semitones / 12.0))

        # Generate envelope for pitch
        # We want the pitch to drop from start_freq to base_freq over punch_decay seconds
        # Using an exponential decay for pitch usually sounds best

        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)

        # Pitch envelope: 1 at t=0, 0 at t=punch_decay (normalized)
        # But we want frequency.
        # Let's model frequency decay exponentially from start_freq to base_freq.
        # After punch_decay, it stays at base_freq (or fades out via amplitude envelope).

        # Create a frequency array
        freq_envelope = np.zeros_like(t)

        # Active region for the sweep
        active_indices = t < punch_decay
        t_active = t[active_indices]

        # Exponential interpolation
        # f(t) = start_freq * (base_freq/start_freq)^(t/decay)
        freq_envelope[active_indices] = start_freq * ((base_freq / start_freq) ** (t_active / punch_decay))
        freq_envelope[~active_indices] = base_freq

        # Generate phase by integrating frequency
        phase = 2 * np.pi * np.cumsum(freq_envelope) / self.sample_rate

        signal = np.sin(phase)

        # Amplitude Envelope for the punch
        # The prompt doesn't strictly specify amplitude envelope for the punch layer specifically,
        # but implies it's short ("punch").
        # Step 2 talks about Body Decay.
        # I will apply a short amplitude decay to the punch layer so it doesn't drone on at 150Hz.
        # Let's say it follows the pitch envelope duration roughly.

        amp_env = np.zeros_like(t)
        # Linear decay for amplitude matching the pitch drop duration + a bit of release
        decay_samples = int(punch_decay * self.sample_rate)
        release_samples = int(0.01 * self.sample_rate) # 10ms release

        total_len = decay_samples + release_samples
        if total_len > self.num_samples:
            total_len = self.num_samples

        # 1.0 to 0.0
        amp_env[:decay_samples] = np.linspace(1.0, 0.5, decay_samples) # Decay to half
        amp_env[decay_samples:total_len] = np.linspace(0.5, 0.0, release_samples) # Quick release

        return signal * amp_env

    def generate_body(self):
        """
        Step 2: Kick Body
        Sine wave at 60-80Hz for depth.
        ADSR: A=0, D=200-400ms, S=0, R=50-100ms.
        """
        body_freq = 70.0  # ~F2
        decay_time = 0.300 # 300ms

        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)

        # Signal
        signal = np.sin(2 * np.pi * body_freq * t)

        # Amplitude Envelope
        # Attack is 0, so start at 1.0
        # Decay to 0 over decay_time (exponentially)

        amp_env = np.zeros_like(t)
        decay_samples = int(decay_time * self.sample_rate)

        if decay_samples > self.num_samples:
            decay_samples = self.num_samples

        # Exponential decay: e^(-k * t)
        # We want envelope to drop to near zero (~-60dB) by decay_time.
        # e^-7 is approx 0.001 (-60dB).
        k = 7.0 / decay_time

        active_indices = t < decay_time
        t_active = t[active_indices]

        amp_env[active_indices] = np.exp(-k * t_active)
        amp_env[~active_indices] = 0.0

        return signal * amp_env

    def generate_click(self, level=1.0, decay_ms=10.0):
        """
        Step 3: Click/Transient (Modified for Euphoria - More Noise)
        White Noise short burst.
        Filter: High-pass @ 2kHz+.
        Envelope: Attack 0ms, Decay 5-15ms (Adjustable).
        """
        from scipy.signal import butter, lfilter

        # Generate white noise
        noise = np.random.uniform(-1, 1, self.num_samples)

        # High-pass filter at 2500Hz
        cutoff = 2500
        nyquist = 0.5 * self.sample_rate
        normal_cutoff = cutoff / nyquist
        b, a = butter(2, normal_cutoff, btype='high', analog=False)
        filtered_noise = lfilter(b, a, noise)

        # Envelope: Decay adjustable
        decay_time = decay_ms / 1000.0

        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)
        amp_env = np.zeros_like(t)

        decay_samples = int(decay_time * self.sample_rate)
        if decay_samples > self.num_samples:
            decay_samples = self.num_samples

        # Exponential decay for crispness
        # For Euphoria, maybe a slightly longer tail?
        # k = 7.0 / decay_time -> standard -60dB point.
        # If user wants "more noise", we can make the decay curve shallower?
        # Let's keep exponential but scale amplitude by level.

        k = 7.0 / decay_time
        active_indices = t < decay_time
        t_active = t[active_indices]

        amp_env[active_indices] = np.exp(-k * t_active)
        amp_env[~active_indices] = 0.0

        return filtered_noise * amp_env * level

    def apply_saturation(self, signal, drive_db=4.5):
        """
        Step 4: Saturation and Harmonics
        Add Saturator/Overdrive to the kick body.
        Drive: 3-6dB.
        """
        # Convert dB to linear gain
        drive_gain = 10 ** (drive_db / 20.0)

        # Soft clipping using tanh
        # This creates harmonics
        saturated_signal = np.tanh(signal * drive_gain)

        # We might want to normalize or recover gain, but saturation naturally compresses dynamics.

        return saturated_signal

    def apply_compression(self, signal, threshold_db=-10.0, ratio=6.0, attack_ms=2.0, release_ms=150.0):
        """
        Step 5: Compression
        Attack: 1-5ms (lets transients through), Release: 100-200ms.
        Ratio: 4:1 - 8:1.
        """
        threshold = 10 ** (threshold_db / 20.0)

        # Envelope detection
        # We need a loop for signal-dependent attack/release
        # 0.5s is short enough for python loop

        num_samples = len(signal)
        gain_reduction = np.ones(num_samples)

        # Attack/Release coefficients
        # alpha = exp(-1 / (time * sample_rate))
        # Actually standard formula is exp(-1 / (time_in_seconds * sample_rate))?
        # Or time constant tau? t = -1/ln(alpha) -> alpha = exp(-1/t).
        # Usually defined as time to reach 63% or similar.

        dt = 1.0 / self.sample_rate
        alpha_attack = np.exp(-dt / (attack_ms / 1000.0))
        alpha_release = np.exp(-dt / (release_ms / 1000.0))

        current_env = 0.0

        # Abs signal for detection
        abs_signal = np.abs(signal)

        # Envelope follower
        envelope = np.zeros(num_samples)
        for i in range(num_samples):
            in_val = abs_signal[i]
            if in_val > current_env:
                current_env = alpha_attack * current_env + (1 - alpha_attack) * in_val
            else:
                current_env = alpha_release * current_env + (1 - alpha_release) * in_val
            envelope[i] = current_env

        # Calculate gain
        # If envelope > threshold, apply ratio

        # We work in linear domain or log?
        # Let's use log for ratio calculation

        env_db = 20 * np.log10(envelope + 1e-9)

        # Gain reduction in dB
        # gain_db = (threshold - env) * (1 - 1/ratio) if env > threshold else 0
        # Wait.
        # Target = Threshold + (Input - Threshold) / Ratio
        # Reduction = Target - Input = (1/Ratio - 1) * (Input - Threshold)

        gr_db = np.zeros(num_samples)
        mask = env_db > threshold_db
        gr_db[mask] = (env_db[mask] - threshold_db) * (1.0/ratio - 1.0)

        # Convert back to linear gain
        gr_linear = 10 ** (gr_db / 20.0)

        compressed = signal * gr_linear

        # Makeup gain to peak at original level or -0.1dB
        # Let's normalize to peak of input or just 0dB?
        # Kick should be loud.
        max_val = np.max(np.abs(compressed))
        if max_val > 0:
            compressed = compressed / max_val * 0.95 # -0.5dB

        return compressed

    def _design_peaking_eq(self, freq, gain_db, Q=1.0):
        # RBJ Cookbook Peaking EQ
        A = 10 ** (gain_db / 40.0)
        w0 = 2 * np.pi * freq / self.sample_rate
        alpha = np.sin(w0) / (2 * Q)
        cos_w0 = np.cos(w0)

        b0 = 1 + alpha * A
        b1 = -2 * cos_w0
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * cos_w0
        a2 = 1 - alpha / A

        return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0

    def apply_eq(self, signal):
        """
        Step 6: EQ Design
        Cut < 30Hz
        Boost 60-80Hz
        Dip 200-400Hz
        Boost 3-5kHz
        """
        from scipy.signal import butter, lfilter

        # 1. High-pass > 30Hz
        b_hp, a_hp = butter(2, 30.0 / (0.5 * self.sample_rate), btype='high')
        signal = lfilter(b_hp, a_hp, signal)

        # 2. Boost 70Hz (+2dB)
        b_peak1, a_peak1 = self._design_peaking_eq(70.0, 2.0, Q=2.0)
        signal = lfilter(b_peak1, a_peak1, signal)

        # 3. Dip 300Hz (-3dB)
        b_dip, a_dip = self._design_peaking_eq(300.0, -3.0, Q=1.0)
        signal = lfilter(b_dip, a_dip, signal)

        # 4. Boost 4000Hz (+2dB) -> Euphoria Style: Boost Highs more!
        b_pres, a_pres = self._design_peaking_eq(4000.0, 3.5, Q=1.0)
        signal = lfilter(b_pres, a_pres, signal)

        return signal

    def apply_reverb(self, signal, amount=0.3):
        """
        Simple Reverb/Delay Simulation for "Euphoria" feel.
        Uses a comb filter or delay network.
        """
        if amount <= 0.0:
            return signal

        # Create a simple delay line
        delay_ms = 40.0 # Short room/plate
        feedback = 0.4

        delay_samples = int(delay_ms * self.sample_rate / 1000.0)
        output = np.copy(signal)

        # Add delay
        # This is a very crude FIR/IIR mix
        # Let's just add a delayed version with decay

        wet_signal = np.zeros_like(signal)
        wet_signal[delay_samples:] = signal[:-delay_samples] * feedback

        # Add a second tap
        delay_samples2 = int(delay_ms * 1.5 * self.sample_rate / 1000.0)
        if delay_samples2 < len(signal):
            wet_signal[delay_samples2:] += signal[:-delay_samples2] * (feedback * 0.7)

        # Mix
        return signal * (1.0 - amount * 0.5) + wet_signal * amount

    def apply_delay(self, signal, amount=0.3, time_ms=250.0):
        """
        Simple Stereo Ping-Pong Delay.
        """
        if amount <= 0.0:
            return signal

        delay_samples = int(time_ms * self.sample_rate / 1000.0)
        feedback = 0.5

        # Create stereo-ish effect by slightly offsetting or just summing
        # For mono signal, let's just do a simple feedback delay

        wet_signal = np.zeros_like(signal)
        wet_signal[delay_samples:] = signal[:-delay_samples] * feedback

        # Add a second tap
        delay_samples2 = int(time_ms * 1.5 * self.sample_rate / 1000.0)
        if delay_samples2 < len(signal):
            wet_signal[delay_samples2:] += signal[:-delay_samples2] * (feedback * 0.5)

        return signal * (1.0 - amount * 0.3) + wet_signal * amount

    def generate_bassline(self, freq=55.0, length_beats=4, bpm=138.0):
        """
        Generates a simple offbeat trance bass loop.
        Sawtooth wave.
        """
        beat_duration = 60.0 / bpm
        total_duration = length_beats * beat_duration
        num_samples = int(self.sample_rate * total_duration)
        t = np.linspace(0, total_duration, num_samples, endpoint=False)

        # Sawtooth wave
        # Use simple additive synthesis or just modulo
        phase = 2 * np.pi * freq * t
        bass_signal = (phase % (2 * np.pi)) / np.pi - 1.0

        # Filter (Low-pass)
        from scipy.signal import butter, lfilter
        b, a = butter(2, 400.0 / (0.5 * self.sample_rate), btype='low')
        bass_signal = lfilter(b, a, bass_signal)

        return bass_signal

    def apply_sidechain(self, signal, bpm=138.0, depth=0.8, release_ms=100.0):
        """
        Applies volume ducking (sidechain compression) triggered on every beat.
        """
        if depth <= 0.0:
            return signal

        beat_duration = 60.0 / bpm
        samples_per_beat = int(beat_duration * self.sample_rate)

        # Create ducking envelope for one beat
        # Starts at 1-depth, rises to 1.0 over release_ms
        env_beat = np.ones(samples_per_beat)

        release_samples = int(release_ms * self.sample_rate / 1000.0)
        if release_samples > samples_per_beat:
            release_samples = samples_per_beat

        # Linear or exponential rise
        # Let's do exponential rise
        t_rel = np.linspace(0, 1, release_samples)
        curve = 1.0 - np.exp(-5.0 * t_rel) # Fast rise

        # Scale curve: 0 -> 1 becomes (1-depth) -> 1
        ducking_curve = (1.0 - depth) + (depth * curve)

        env_beat[:release_samples] = ducking_curve

        # Tile envelope to match signal length
        num_beats = int(np.ceil(len(signal) / samples_per_beat))
        full_env = np.tile(env_beat, num_beats)[:len(signal)]

        return signal * full_env

    def save_sidechain_trigger(self, filename="sidechain_trigger.wav"):
        """
        Exports a short click track for sidechain key input in DAWs.
        """
        duration = 0.05 # 50ms click
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        click = np.sin(2 * np.pi * 1000.0 * t) * np.exp(-t * 100.0)
        self.save(filename, click)

    def generate(self, click_level=1.0, click_decay_ms=10.0, drive_db=4.5, reverb_amount=0.0, delay_amount=0.0, generate_bass=False, bass_freq=55.0, sc_depth=0.8):
        # 1. Generate Layers
        punch = self.generate_punch()
        body = self.generate_body()
        click = self.generate_click(level=click_level, decay_ms=click_decay_ms)

        # 2. Mix
        # Adjust levels based on typical trance kick balance
        # Punch provides the initial thud
        # Body provides the low end tail
        # Click provides the top end snap
        # Increased click mix slightly for "more noise" capability
        mix = (punch * 0.7) + (body * 0.8) + (click * 0.5) # Default click higher, scalable by level

        # 3. Apply Effects Chain
        # Saturation to glue and add harmonics
        processed = self.apply_saturation(mix, drive_db=drive_db)

        # Reverb (Euphoria Style) - Applied before compression?
        # Usually reverb is after compression, but for a "big room" kick effect where the tail is compressed up,
        # sometimes it's before. Let's put it before compression to smash the reverb tail up.
        processed = self.apply_reverb(processed, amount=reverb_amount)

        # Delay (FX)
        processed = self.apply_delay(processed, amount=delay_amount)

        # Compression to tighten and bring out transient
        processed = self.apply_compression(processed, threshold_db=-12.0, ratio=4.0, attack_ms=3.0, release_ms=150.0)

        # EQ to sculpt the final tone
        processed = self.apply_eq(processed)

        # Final Normalization / Limiting
        max_val = np.max(np.abs(processed))
        if max_val > 0:
            processed = processed / max_val * 0.95

        # Bassline Generation (Optional)
        if generate_bass:
            # Generate bass loop
            # Calculate length to match kick duration or beats?
            # Kick duration is usually short (0.5s), but loop needs beats.
            # Let's assume we tile the kick or just return a longer loop containing the kick on beat 1?
            # Usually users want the kick sound, so maybe "generate bass" just appends a sidechained bass tail?
            # Or better: Create a 4-beat loop with Kick on 1, 2, 3, 4 and Bass offbeat.

            bpm = 138.0
            beat_len = 60.0 / bpm
            samples_beat = int(beat_len * self.sample_rate)

            # Create 1 bar loop
            one_bar_samples = samples_beat * 4
            loop_kick = np.zeros(one_bar_samples)

            # Place kick on beats
            kick_len = len(processed)
            for i in range(4):
                start = i * samples_beat
                end = start + kick_len
                if end > one_bar_samples: end = one_bar_samples
                loop_kick[start:end] += processed[:end-start]

            # Generate bass
            bass = self.generate_bassline(freq=bass_freq, length_beats=4, bpm=bpm)

            # Sidechain Bass
            bass_sc = self.apply_sidechain(bass, bpm=bpm, depth=sc_depth, release_ms=150.0)

            # Ensure lengths match
            min_len = min(len(loop_kick), len(bass_sc))
            loop_kick = loop_kick[:min_len]
            bass_sc = bass_sc[:min_len]

            # Mix
            # Bass usually lower volume
            mix_loop = loop_kick + bass_sc * 0.6

            # Normalize loop
            max_loop = np.max(np.abs(mix_loop))
            if max_loop > 0:
                mix_loop = mix_loop / max_loop * 0.95

            return mix_loop

        return processed

    def save(self, filename, audio_data):
        # Convert float32 to int16 PCM
        scaled = np.int16(audio_data * 32767)
        wavfile.write(filename, self.sample_rate, scaled)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trance Kick Generator in the style of Armin van Buuren")
    parser.add_argument("--duration", type=float, default=0.5, help="Duration of the kick in seconds")
    parser.add_argument("--output", type=str, default="trance_kick.wav", help="Output filename")
    parser.add_argument("--click-level", type=float, default=1.0, help="Click/Noise Level (default: 1.0)")
    parser.add_argument("--click-decay", type=float, default=10.0, help="Click/Noise Decay in ms (default: 10.0)")
    parser.add_argument("--drive", type=float, default=4.5, help="Saturation Drive in dB (default: 4.5)")
    parser.add_argument("--reverb", type=float, default=0.0, help="Reverb Amount 0.0-1.0 (default: 0.0)")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay Amount 0.0-1.0 (default: 0.0)")
    parser.add_argument("--bass", action="store_true", help="Generate Bassline Loop")
    parser.add_argument("--bass-freq", type=float, default=55.0, help="Bass Frequency (default: 55.0)")
    parser.add_argument("--sc-depth", type=float, default=0.8, help="Sidechain Depth 0.0-1.0 (default: 0.8)")
    parser.add_argument("--export-trigger", action="store_true", help="Export sidechain trigger file")
    args = parser.parse_args()

    generator = TranceKickGenerator(duration=args.duration)

    if args.export_trigger:
        generator.save_sidechain_trigger("sidechain_trigger.wav")
        print("Exported sidechain_trigger.wav")

    audio = generator.generate(
        click_level=args.click_level,
        click_decay_ms=args.click_decay,
        drive_db=args.drive,
        reverb_amount=args.reverb,
        delay_amount=args.delay,
        generate_bass=args.bass,
        bass_freq=args.bass_freq,
        sc_depth=args.sc_depth
    )
    generator.save(args.output, audio)
    print(f"Generated trance kick (or loop) to {args.output}")
