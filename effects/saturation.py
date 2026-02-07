import numpy as np

def apply_saturation(signal, drive_db=4.5):
    """
    Step 4: Saturation and Harmonics
    Add Saturator/Overdrive to the kick body.
    Drive: 3-6dB.
    """
    # Convert dB to linear gain
    drive_gain = 10 ** (drive_db / 20.0)

    # Soft clipping using tanh
    # This creates harmonics
    saturated_signal = np.tanh(signal * drive_gain)

    # We might want to normalize or recover gain, but saturation naturally compresses dynamics.

    return saturated_signal
