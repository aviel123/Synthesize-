import numpy as np


def apply_distortion(signal, amount=0.5, mode='hard_clip'):
    """
    Multi-mode distortion effect for aggressive electronic music production.

    amount: 0.0 = clean, 1.0 = maximum distortion
    mode:
      'hard_clip'  – Gain then hard-clip at ±1.0. Classic rock/techno crunch.
                     Adds odd harmonics, very aggressive.
      'foldback'   – When signal exceeds threshold it folds back (mirrors).
                     Extremely rich harmonic content; industrial / acid sounds.
      'wavefolder' – Sinusoidal shaping that folds the wave multiple times.
                     Metallic, complex timbres; used in modular synthesis.
      'bitcrush'   – Reduces bit depth (16 → 4 bits). Lo-fi digital crunch.
    """
    if amount <= 0.001:
        return signal

    if mode == 'hard_clip':
        # Drive up then hard-clip symmetrically.
        # At amount=1.0 the signal is boosted 11× before clipping → very clipped.
        gain = 1.0 + amount * 10.0
        return np.clip(signal * gain, -1.0, 1.0)

    elif mode == 'foldback':
        # Threshold shrinks as amount increases (more of the wave folds).
        # Up to 3 fold iterations for extreme but controlled distortion.
        threshold = max(0.05, 1.0 - amount * 0.85)
        out = signal.copy()
        for _ in range(3):
            mask_pos = out > threshold
            mask_neg = out < -threshold
            if not (np.any(mask_pos) or np.any(mask_neg)):
                break
            out[mask_pos] = 2.0 * threshold - out[mask_pos]
            out[mask_neg] = -2.0 * threshold - out[mask_neg]
        return np.clip(out, -1.0, 1.0)

    elif mode == 'wavefolder':
        # Sinusoidal shaper: sin(driven * π/2)
        # When driven ≤ 1 it's a normal soft-clipper; above 1 it folds back.
        gain = 1.0 + amount * 6.0
        return np.sin(signal * gain * np.pi * 0.5)

    elif mode == 'bitcrush':
        # Reduce effective bit depth from 16 to 4 bits as amount goes 0→1.
        bits = max(2, int(16 - amount * 12))
        steps = float(2 ** bits)
        return np.round(signal * steps) / steps

    return signal
