import numpy as np
from scipy.signal import butter, lfilter

def _design_peaking_eq(sample_rate, freq, gain_db, Q=1.0):
    # RBJ Cookbook Peaking EQ
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * freq / sample_rate
    alpha = np.sin(w0) / (2 * Q)
    cos_w0 = np.cos(w0)

    b0 = 1 + alpha * A
    b1 = -2 * cos_w0
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * cos_w0
    a2 = 1 - alpha / A

    return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0

def apply_eq(signal, sample_rate):
    """
    Step 6: EQ Design
    Cut < 30Hz
    Boost 60-80Hz
    Dip 200-400Hz
    Boost 3-5kHz
    """
    # 1. High-pass > 30Hz
    b_hp, a_hp = butter(2, 30.0 / (0.5 * sample_rate), btype='high')

    # Handle stereo processing if needed for lfilter
    # lfilter works on last axis by default, which is correct for (2, N) or (N,)
    if signal.ndim == 2:
        signal = lfilter(b_hp, a_hp, signal, axis=1)
    else:
        signal = lfilter(b_hp, a_hp, signal)

    # 2. Boost 70Hz (+2dB)
    b_peak1, a_peak1 = _design_peaking_eq(sample_rate, 70.0, 2.0, Q=2.0)
    if signal.ndim == 2:
        signal = lfilter(b_peak1, a_peak1, signal, axis=1)
    else:
        signal = lfilter(b_peak1, a_peak1, signal)

    # 3. Dip 300Hz (-3dB)
    b_dip, a_dip = _design_peaking_eq(sample_rate, 300.0, -3.0, Q=1.0)
    if signal.ndim == 2:
        signal = lfilter(b_dip, a_dip, signal, axis=1)
    else:
        signal = lfilter(b_dip, a_dip, signal)

    # 4. Boost 4000Hz (+3.5dB) -> Euphoria Style: Boost Highs more!
    b_pres, a_pres = _design_peaking_eq(sample_rate, 4000.0, 3.5, Q=1.0)
    if signal.ndim == 2:
        signal = lfilter(b_pres, a_pres, signal, axis=1)
    else:
        signal = lfilter(b_pres, a_pres, signal)

    return signal
