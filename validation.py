"""
Parameter validation for audio generators.

Raises ValueError with a clear, user-readable message when a parameter is
out of its safe operating range.  Call validate_kick_params() before passing
any values to TranceKickGenerator.generate().
"""

_KICK_RULES: list[tuple] = [
    # (param_name, min_val, max_val, unit)
    ("body_freq",        20.0,   200.0, "Hz"),
    ("punch_semitones",  1,      48,    "semitones"),
    ("punch_decay_ms",   1.0,    500.0, "ms"),
    ("body_decay_ms",    50.0,   3000.0,"ms"),
    ("duration",         0.1,    5.0,   "s"),
    ("click_level",      0.0,    5.0,   ""),
    ("click_decay_ms",   0.5,    200.0, "ms"),
    ("click_width",      0.0,    4.0,   ""),
    ("drive_db",         0.0,    30.0,  "dB"),
    ("reverb_amount",    0.0,    1.0,   ""),
    ("delay_amount",     0.0,    1.0,   ""),
    ("distortion_amount",0.0,    1.0,   ""),
    ("lfo_rate_hz",      0.0,    50.0,  "Hz"),
    ("lfo_depth",        0.0,    1.0,   ""),
    ("bass_freq",        20.0,   500.0, "Hz"),
    ("sc_depth",         0.0,    1.0,   ""),
    ("oversample",       1,      8,     ""),
]

_VALID_DISTORTION_MODES = {"hard_clip", "foldback", "wavefolder", "bitcrush"}
_VALID_LFO_TARGETS      = {"none", "body_freq", "drive"}
_VALID_LFO_WAVEFORMS    = {"sine", "square", "saw", "triangle"}


def validate_kick_params(**kwargs) -> None:
    """
    Validate kick generator parameters.

    Raises ValueError with a descriptive message on the first invalid value.
    Missing keys are silently ignored (uses generator defaults).
    """
    for name, lo, hi, unit in _KICK_RULES:
        if name not in kwargs:
            continue
        val = kwargs[name]
        try:
            numeric = float(val)
        except (TypeError, ValueError):
            raise ValueError(f"'{name}' must be a number, got {val!r}")
        if not (lo <= numeric <= hi):
            suffix = f" {unit}" if unit else ""
            raise ValueError(
                f"'{name}' must be between {lo}{suffix} and {hi}{suffix}, "
                f"got {numeric}{suffix}"
            )

    if "distortion_mode" in kwargs:
        mode = kwargs["distortion_mode"]
        if mode not in _VALID_DISTORTION_MODES:
            raise ValueError(
                f"'distortion_mode' must be one of "
                f"{sorted(_VALID_DISTORTION_MODES)}, got {mode!r}"
            )

    if "lfo_target" in kwargs:
        target = kwargs["lfo_target"]
        if target not in _VALID_LFO_TARGETS:
            raise ValueError(
                f"'lfo_target' must be one of "
                f"{sorted(_VALID_LFO_TARGETS)}, got {target!r}"
            )

    if "lfo_waveform" in kwargs:
        wf = kwargs["lfo_waveform"]
        if wf not in _VALID_LFO_WAVEFORMS:
            raise ValueError(
                f"'lfo_waveform' must be one of "
                f"{sorted(_VALID_LFO_WAVEFORMS)}, got {wf!r}"
            )
