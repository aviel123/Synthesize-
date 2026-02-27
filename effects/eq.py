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


def _apply_filter(signal, b, a):
    if signal.ndim == 2:
        return lfilter(b, a, signal, axis=1)
    return lfilter(b, a, signal)


def apply_eq(signal, sample_rate):
    """
    Buzzism-tuned EQ chain for professional trance kick:
      1. High-pass  30Hz      - removes sub-rumble
      2. Boost     +4dB @65Hz - emphasises the deep sub punch
      3. Cut       -4dB @250Hz- removes boxiness/mud
      4. Boost     +4dB @4500Hz- presence/attack snap
      5. Boost     +2dB @8000Hz- air and high-end shimmer
    """
    # 1. High-pass at 30Hz
    b_hp, a_hp = butter(2, 30.0 / (0.5 * sample_rate), btype='high')
    signal = _apply_filter(signal, b_hp, a_hp)

    # 2. Sub boost: +4dB at 65Hz, tight Q
    b, a = _design_peaking_eq(sample_rate, 65.0, 4.0, Q=2.5)
    signal = _apply_filter(signal, b, a)

    # 3. Mud cut: -4dB at 250Hz
    b, a = _design_peaking_eq(sample_rate, 250.0, -4.0, Q=1.0)
    signal = _apply_filter(signal, b, a)

    # 4. Presence boost: +4dB at 4500Hz
    b, a = _design_peaking_eq(sample_rate, 4500.0, 4.0, Q=1.2)
    signal = _apply_filter(signal, b, a)

    # 5. Air boost: +2dB at 8000Hz
    b, a = _design_peaking_eq(sample_rate, 8000.0, 2.0, Q=1.0)
    signal = _apply_filter(signal, b, a)

    return signal
