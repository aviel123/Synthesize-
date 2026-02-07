import numpy as np

def apply_reverb(signal, sample_rate, amount=0.3):
    """
    Simple Reverb/Delay Simulation for "Euphoria" feel.
    Uses a comb filter or delay network.
    """
    if amount <= 0.0:
        return signal

    # Create a simple delay line
    delay_ms = 40.0 # Short room/plate
    feedback = 0.4

    delay_samples = int(delay_ms * sample_rate / 1000.0)

    # Add delay
    # This is a very crude FIR/IIR mix
    # Let's just add a delayed version with decay

    wet_signal = np.zeros_like(signal)

    if signal.ndim == 2:
        wet_signal[:, delay_samples:] = signal[:, :-delay_samples] * feedback
        # Add a second tap
        delay_samples2 = int(delay_ms * 1.5 * sample_rate / 1000.0)
        if delay_samples2 < signal.shape[1]:
            wet_signal[:, delay_samples2:] += signal[:, :-delay_samples2] * (feedback * 0.7)
    else:
        wet_signal[delay_samples:] = signal[:-delay_samples] * feedback
        # Add a second tap
        delay_samples2 = int(delay_ms * 1.5 * sample_rate / 1000.0)
        if delay_samples2 < len(signal):
            wet_signal[delay_samples2:] += signal[:-delay_samples2] * (feedback * 0.7)

    # Mix
    return signal * (1.0 - amount * 0.5) + wet_signal * amount
