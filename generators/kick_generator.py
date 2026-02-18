import numpy as np
from scipy.io import wavfile
import argparse

from effects.saturation import apply_saturation
from effects.compression import apply_compression
from effects.eq import apply_eq
from effects.reverb import apply_reverb
from effects.delay import apply_delay
from effects.limiter import apply_limiter
from effects.stereo import apply_stereo_width
from generators.advanced_noise_generator import AdvancedNoiseGenerator

class TranceKickGenerator:
    def __init__(self, sample_rate=44100, duration=0.5):
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_samples = int(sample_rate * duration)

    def generate_punch(self, phase_deg=0.0):
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

        # Add start phase offset
        phase_offset = phase_deg * np.pi / 180.0
        signal = np.sin(phase + phase_offset)

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

    def generate_body(self, phase_deg=0.0):
        """
        Step 2: Kick Body
        Sine wave at 60-80Hz for depth.
        ADSR: A=0, D=200-400ms, S=0, R=50-100ms.
        """
        body_freq = 70.0  # ~F2
        decay_time = 0.300 # 300ms

        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)

        # Signal
        phase_offset = phase_deg * np.pi / 180.0
        signal = np.sin(2 * np.pi * body_freq * t + phase_offset)

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

    def generate_click(self, level=1.0, decay_ms=10.0, width=0.0):
        """
        Step 3: Click/Transient (Modified for Euphoria - More Noise)
        White Noise short burst.
        Filter: High-pass @ 2kHz+.
        Envelope: Attack 0ms, Decay 5-15ms (Adjustable).
        width: 0.0 (Mono) to 1.0 (Full Stereo Width) or more.
        """
        from scipy.signal import butter, lfilter

        # Generate white noise (Stereo if width > 0)
        # Actually generate mono first, then stereoize?
        # Or generate two uncorrelated noise sources

        if width > 0.001:
            # Stereo Noise
            noise_L = np.random.uniform(-1, 1, self.num_samples)
            noise_R = np.random.uniform(-1, 1, self.num_samples)

            # Mix towards mono based on width inverse?
            # Actually, standard is: Width 0 = L+R/2 (Mono), Width 1 = L, R uncorrelated
            # Let's just interpolate between Mono (L=R=Noise1) and Stereo (L=Noise1, R=Noise2)

            # Better approach for controlled width:
            # Mid = Noise1
            # Side = Noise2 * width
            # L = M + S, R = M - S

            mid = np.random.uniform(-1, 1, self.num_samples)
            side = np.random.uniform(-1, 1, self.num_samples) * width

            noise_L = mid + side
            noise_R = mid - side

            # Normalize approx
            noise = np.vstack((noise_L, noise_R)) # Shape (2, N)
        else:
            noise = np.random.uniform(-1, 1, self.num_samples)
            # 1D array

        # High-pass filter at 2500Hz
        cutoff = 2500
        nyquist = 0.5 * self.sample_rate
        normal_cutoff = cutoff / nyquist
        b, a = butter(2, normal_cutoff, btype='high', analog=False)

        if noise.ndim == 2:
            filtered_noise = lfilter(b, a, noise, axis=1)
        else:
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

    def generate(self, click_level=1.0, click_decay_ms=10.0, drive_db=4.5, reverb_amount=0.0, delay_amount=0.0, generate_bass=False, bass_freq=55.0, sc_depth=0.8, oversample=1, click_width=0.0, phase_deg=0.0, smoke_params=None):
        """
        Generate the kick.
        oversample: 1 (Standard) or 2 (High Quality). Runs processing at 2x sample rate.
        """
        original_rate = self.sample_rate

        if oversample > 1:
            self.sample_rate = original_rate * oversample
            self.num_samples = int(self.sample_rate * self.duration)

        # 1. Generate Layers
        punch = self.generate_punch(phase_deg=phase_deg)
        body = self.generate_body(phase_deg=phase_deg)
        click = self.generate_click(level=click_level, decay_ms=click_decay_ms, width=click_width)

        # Smoke Layer
        smoke_layer = None
        if smoke_params and smoke_params.get("enabled", False):
            try:
                noise_gen = AdvancedNoiseGenerator(self.sample_rate)
                # Generate base smoke
                smoke = noise_gen.smoke_noise(
                    duration=self.duration,
                    density=smoke_params.get("density", 60.0) / 100.0,
                    character=smoke_params.get("character", "soft"),
                    hp_freq=smoke_params.get("hp_freq", 6000.0),
                    lp_freq=smoke_params.get("lp_freq", 16000.0)
                )

                # Apply envelope
                env = noise_gen.create_smoke_envelope(
                    duration=self.duration,
                    start_delay_ms=smoke_params.get("delay", 15.0),
                    fade_in_ms=smoke_params.get("fade_in", 120.0),
                    fade_out_ms=smoke_params.get("fade_out", 350.0)
                )
                smoke = smoke * env

                # Apply Level
                level_db = smoke_params.get("level", -12.0)
                gain = 10 ** (level_db / 20.0)
                smoke = smoke * gain

                # Apply Stereo Width
                width = smoke_params.get("width", 85.0) / 100.0
                smoke_layer = apply_stereo_width(smoke, width)

            except Exception as e:
                print(f"Error generating smoke layer: {e}")

        # 2. Mix
        # Handle stereo mixing if click or smoke is stereo
        is_stereo = False
        if click.ndim == 2 or (smoke_layer is not None and smoke_layer.ndim == 2):
            is_stereo = True
            # Expand punch/body to stereo
            if punch.ndim == 1: punch = np.vstack((punch, punch))
            if body.ndim == 1: body = np.vstack((body, body))
            if click.ndim == 1: click = np.vstack((click, click)) # Should be handled by gen but strictly ensuring

        mix = (punch * 0.7) + (body * 0.8) + (click * 0.5)

        if smoke_layer is not None:
            # Ensure smoke matches mix dimensions
            if is_stereo and smoke_layer.ndim == 1:
                smoke_layer = np.vstack((smoke_layer, smoke_layer))

            # If mix is mono but smoke is stereo, mix is already promoted above?
            # Yes, if smoke_layer was stereo, is_stereo is True, so mix components promoted.

            mix = mix + smoke_layer

        # 3. Apply Effects Chain
        # Saturation (benefit most from oversampling)
        processed = apply_saturation(mix, drive_db=drive_db)

        # Reverb
        processed = apply_reverb(processed, self.sample_rate, amount=reverb_amount)

        # Delay
        processed = apply_delay(processed, self.sample_rate, amount=delay_amount)

        # Compression
        processed = apply_compression(processed, self.sample_rate, threshold_db=-12.0, ratio=4.0, attack_ms=3.0, release_ms=150.0)

        # EQ
        processed = apply_eq(processed, self.sample_rate)

        # Downsample if needed
        if oversample > 1:
            # Simple decimation with low-pass filter to prevent aliasing
            from scipy.signal import decimate
            # decimate applies a low-pass filter (chebyshev type I) and downsamples
            # Handle stereo decimation
            if processed.ndim == 2:
                processed = decimate(processed, oversample, axis=1, ftype='fir', zero_phase=True)
            else:
                processed = decimate(processed, oversample, ftype='fir', zero_phase=True)

            # Restore original rate state
            self.sample_rate = original_rate
            self.num_samples = int(self.sample_rate * self.duration)

        return self._finalize_generation(processed, generate_bass, bass_freq, bpm=138.0, sc_depth=sc_depth)

    def _finalize_generation(self, processed, generate_bass, bass_freq, bpm, sc_depth):
        # Final Limiting
        processed = apply_limiter(processed)

        # Bassline Generation (Optional)
        if generate_bass:
            # Generate bass loop
            beat_len = 60.0 / bpm
            samples_beat = int(beat_len * self.sample_rate)

            # Create 1 bar loop
            one_bar_samples = samples_beat * 4

            if processed.ndim == 2:
                 loop_kick = np.zeros((2, one_bar_samples))
            else:
                 loop_kick = np.zeros(one_bar_samples)

            # Place kick on beats
            kick_len = processed.shape[-1] if processed.ndim == 2 else len(processed)

            for i in range(4):
                start = i * samples_beat
                end = start + kick_len
                if end > one_bar_samples: end = one_bar_samples

                if processed.ndim == 2:
                     loop_kick[:, start:end] += processed[:, :end-start]
                else:
                     loop_kick[start:end] += processed[:end-start]

            # Generate bass
            bass = self.generate_bassline(freq=bass_freq, length_beats=4, bpm=bpm)

            # Sidechain Bass
            bass_sc = self.apply_sidechain(bass, bpm=bpm, depth=sc_depth, release_ms=150.0)

            # Mix
            # Ensure stereo bass if kick is stereo
            if processed.ndim == 2 and bass_sc.ndim == 1:
                bass_sc = np.vstack((bass_sc, bass_sc))

            # Truncate
            length = min(loop_kick.shape[-1], bass_sc.shape[-1])
            if processed.ndim == 2:
                 loop_kick = loop_kick[:, :length]
                 bass_sc = bass_sc[:, :length]
            else:
                 loop_kick = loop_kick[:length]
                 bass_sc = bass_sc[:length]

            mix_loop = loop_kick + bass_sc * 0.6

            # Normalize loop
            max_loop = np.max(np.abs(mix_loop))
            if max_loop > 0:
                mix_loop = mix_loop / max_loop * 0.95

            return mix_loop

        return processed

    def save(self, filename, audio_data):
        # Convert float32 to int16 PCM
        # Transpose if stereo (scipy wavfile expects (N, 2))
        if audio_data.ndim == 2:
            audio_data = audio_data.T

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

    from utils.validators import InputValidator
    safe_output = InputValidator.sanitize_filename(args.output)

    generator.save(safe_output, audio)
    print(f"Generated trance kick (or loop) to {safe_output}")
