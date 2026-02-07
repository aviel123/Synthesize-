import numpy as np

def apply_stereo_width(signal, width=0.0):
    """
    Apply stereo width to a signal.
    width: 0.0 (Mono) to 1.0 (Standard) to >1.0 (Wide).

    If signal is Mono, it creates a fake stereo spread (Mid=Signal, Side=Signal*width?).
    No, Mono signal has no side information.
    To widen mono, we need to create decorrelated channels (e.g. slight delay or filter).

    If signal is already Stereo (2, N):
    M = (L+R)/2
    S = (L-R)/2
    New S = S * width
    New L = M + New S
    New R = M - New S
    """
    if width < 0: width = 0.0

    if signal.ndim == 1:
        # Mono input
        if width > 0.001:
            # Create pseudo stereo?
            # For now, just return mono as stereo L=R if width is low,
            # or try to synthesize width (e.g. for noise layers this is done at generation).
            # This function assumes signal already has stereo content if we want to widen it.
            # If we pass mono here, we just duplicate it.
            return np.vstack((signal, signal))
        else:
            return signal

    # Stereo Input
    # Mid-Side processing
    L = signal[0]
    R = signal[1]

    M = (L + R) * 0.5
    S = (L - R) * 0.5

    S_new = S * width

    L_new = M + S_new
    R_new = M - S_new

    return np.vstack((L_new, R_new))
