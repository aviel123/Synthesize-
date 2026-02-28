import numpy as np


def apply_limiter(signal, ceiling_db=-0.3, lookahead_ms=2.0, release_ms=60.0, sample_rate=44100):
    """
    True lookahead limiter with smooth gain reduction.

    ceiling_db:   Output peak ceiling in dBFS (default -0.3 dB).
    lookahead_ms: How far ahead to look for peaks before they arrive (default 2ms).
    release_ms:   How quickly gain recovers after a peak (default 60ms).
    sample_rate:  Used to convert ms to samples.

    Algorithm:
      1. Compute the peak envelope of the absolute signal (smoothed with
         exponential release so gain reduction doesn't snap back too fast).
      2. Anywhere the envelope exceeds the ceiling, compute the required
         gain reduction.
      3. Apply the gain reduction to a version of the signal delayed by
         lookahead_ms so peaks are caught *before* they clip.
    """
    ceiling = 10 ** (ceiling_db / 20.0)

    # Work on mono envelope even for stereo input
    if signal.ndim == 2:
        abs_sig = np.max(np.abs(signal), axis=0)  # linked stereo detection
    else:
        abs_sig = np.abs(signal)

    n = len(abs_sig)

    # Release coefficient (exponential)
    dt = 1.0 / sample_rate
    alpha_release = np.exp(-dt / (release_ms / 1000.0))

    # Build peak envelope with release smoothing
    envelope = np.zeros(n)
    env = 0.0
    for i in range(n):
        peak = abs_sig[i]
        if peak > env:
            env = peak          # instant attack
        else:
            env = alpha_release * env + (1.0 - alpha_release) * peak
        envelope[i] = env

    # Gain reduction curve: where envelope > ceiling, reduce proportionally
    gain = np.where(envelope > ceiling, ceiling / np.maximum(envelope, 1e-9), 1.0)

    # Delay signal by lookahead so gain reduction arrives before the peak
    lookahead_samples = int(lookahead_ms * sample_rate / 1000.0)
    if signal.ndim == 2:
        delayed = np.zeros_like(signal)
        delayed[:, lookahead_samples:] = signal[:, :-lookahead_samples] if lookahead_samples else signal
        limited = delayed * gain
    else:
        delayed = np.zeros_like(signal)
        if lookahead_samples:
            delayed[lookahead_samples:] = signal[:-lookahead_samples]
        else:
            delayed = signal.copy()
        limited = delayed * gain

    return limited


def measure_loudness(signal, sample_rate=44100):
    """
    Returns (peak_db, rms_db) loudness measurements.
    Works with both mono (N,) and stereo (2, N) signals.
    """
    if signal.ndim == 2:
        data = np.mean(signal, axis=0)
    else:
        data = signal

    peak = np.max(np.abs(data))
    peak_db = 20 * np.log10(peak + 1e-9)

    rms = np.sqrt(np.mean(data ** 2))
    rms_db = 20 * np.log10(rms + 1e-9)

    return peak_db, rms_db
