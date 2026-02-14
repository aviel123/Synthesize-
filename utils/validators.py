class InputValidator:
    """
    Validates user input parameters to prevent security issues like Denial of Service (DoS)
    via resource exhaustion (huge memory allocation).
    """
    MAX_DURATION = 30.0  # seconds
    MAX_SAMPLE_RATE = 192000  # Hz (192kHz)

    @staticmethod
    def validate_audio_params(duration=None, sample_rate=None):
        """
        Validates audio parameters. Raises ValueError if invalid.
        """
        if duration is not None:
            if duration <= 0:
                raise ValueError("Duration must be positive")
            if duration > InputValidator.MAX_DURATION:
                raise ValueError(f"Duration exceeds maximum allowed ({InputValidator.MAX_DURATION}s)")

        if sample_rate is not None:
            if sample_rate <= 0:
                raise ValueError("Sample rate must be positive")
            if sample_rate > InputValidator.MAX_SAMPLE_RATE:
                raise ValueError(f"Sample rate exceeds maximum allowed ({InputValidator.MAX_SAMPLE_RATE}Hz)")
