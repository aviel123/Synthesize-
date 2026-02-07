import numpy as np

def apply_compression(signal, sample_rate, threshold_db=-10.0, ratio=6.0, attack_ms=2.0, release_ms=150.0):
    """
    Step 5: Compression
    Attack: 1-5ms (lets transients through), Release: 100-200ms.
    Ratio: 4:1 - 8:1.
    """
    threshold = 10 ** (threshold_db / 20.0)

    # Envelope detection
    # We need a loop for signal-dependent attack/release
    # 0.5s is short enough for python loop

    # Abs signal for detection
    abs_signal = np.abs(signal)

    # Handle stereo signal (num_samples will be size of array, but if stereo, shape is (2, N))
    # If stereo, we should link channels or process separately.
    # Linking is better for kick (avoid stereo image shift).
    # We take max of abs(L, R) for detection.

    is_stereo = False
    if abs_signal.ndim == 2:
        is_stereo = True
        abs_signal_mono = np.max(abs_signal, axis=0)
        length = abs_signal.shape[1]
        envelope = np.zeros(length)
    else:
        abs_signal_mono = abs_signal
        length = len(abs_signal)
        envelope = np.zeros(length)

    # Attack/Release coefficients
    dt = 1.0 / sample_rate
    alpha_attack = np.exp(-dt / (attack_ms / 1000.0))
    alpha_release = np.exp(-dt / (release_ms / 1000.0))

    current_env = 0.0

    for i in range(length):
        in_val = abs_signal_mono[i]
        if in_val > current_env:
            current_env = alpha_attack * current_env + (1 - alpha_attack) * in_val
        else:
            current_env = alpha_release * current_env + (1 - alpha_release) * in_val
        envelope[i] = current_env

    # Calculate gain
    # If envelope > threshold, apply ratio

    env_db = 20 * np.log10(envelope + 1e-9)

    # Gain reduction in dB
    # Target = Threshold + (Input - Threshold) / Ratio
    # Reduction = Target - Input = (1/Ratio - 1) * (Input - Threshold)

    gr_db = np.zeros(length)
    mask = env_db > threshold_db
    gr_db[mask] = (env_db[mask] - threshold_db) * (1.0/ratio - 1.0)

    # Convert back to linear gain
    gr_linear = 10 ** (gr_db / 20.0)

    if is_stereo:
        # Broadcast to (2, N)
        compressed = signal * gr_linear
    else:
        compressed = signal * gr_linear

    # Makeup gain to peak at original level or -0.1dB
    # Let's normalize to peak of input or just 0dB?
    # Kick should be loud.
    max_val = np.max(np.abs(compressed))
    if max_val > 0:
        compressed = compressed / max_val * 0.95 # -0.5dB

    return compressed
