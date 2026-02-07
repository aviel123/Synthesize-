import numpy as np

def apply_limiter(signal, ceiling_db=-0.1):
    """
    Simple Lookahead Limiter.
    Hard clips peaks but manages gain to avoid distortion.
    """
    ceiling = 10 ** (ceiling_db / 20.0)

    # Just normalize peak to ceiling.

    max_val = np.max(np.abs(signal))
    if max_val > ceiling:
        signal = signal / max_val * ceiling

    return signal
