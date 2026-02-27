import numpy as np


def generate_lfo(num_samples, sample_rate, rate_hz=2.0,
                 waveform='sine', depth=0.5, phase_deg=0.0):
    """
    Generate a normalised LFO array in the range [-depth, +depth].

    Parameters
    ----------
    num_samples  : int   – length of the output array
    sample_rate  : int   – samples per second
    rate_hz      : float – oscillation frequency in Hz (0.05 – 20 Hz typical)
    waveform     : str   – 'sine' | 'square' | 'saw' | 'triangle'
    depth        : float – amplitude (0.0 = no modulation, 1.0 = full)
    phase_deg    : float – starting phase in degrees

    Returns
    -------
    numpy array of shape (num_samples,), values in [-depth, +depth]
    """
    t     = np.arange(num_samples) / sample_rate
    phase = 2.0 * np.pi * rate_hz * t + np.deg2rad(phase_deg)

    if waveform == 'square':
        raw = np.sign(np.sin(phase))
    elif waveform == 'saw':
        # Sawtooth: ramp from -1 to +1 each cycle
        raw = 2.0 * (rate_hz * t % 1.0) - 1.0
    elif waveform == 'triangle':
        raw = 2.0 * np.abs(2.0 * (rate_hz * t % 1.0) - 1.0) - 1.0
    else:  # default: sine
        raw = np.sin(phase)

    return raw * depth
