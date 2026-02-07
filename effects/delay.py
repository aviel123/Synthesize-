import numpy as np

def apply_delay(signal, sample_rate, amount=0.3, time_ms=250.0):
    """
    Simple Stereo Ping-Pong Delay.
    """
    if amount <= 0.0:
        return signal

    delay_samples = int(time_ms * sample_rate / 1000.0)
    feedback = 0.5

    wet_signal = np.zeros_like(signal)

    if signal.ndim == 2:
        # Stereo signal
        # Ping Pong often implies Left -> Right -> Left
        # Here we just do a simple tap delay
        wet_signal[:, delay_samples:] = signal[:, :-delay_samples] * feedback

        # Add a second tap
        delay_samples2 = int(time_ms * 1.5 * sample_rate / 1000.0)
        if delay_samples2 < signal.shape[1]:
            wet_signal[:, delay_samples2:] += signal[:, :-delay_samples2] * (feedback * 0.5)

    else:
        # Mono signal
        wet_signal[delay_samples:] = signal[:-delay_samples] * feedback

        # Add a second tap
        delay_samples2 = int(time_ms * 1.5 * sample_rate / 1000.0)
        if delay_samples2 < len(signal):
            wet_signal[delay_samples2:] += signal[:-delay_samples2] * (feedback * 0.5)

    return signal * (1.0 - amount * 0.3) + wet_signal * amount
