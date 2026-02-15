class InputValidator:
    MAX_DURATION = 30.0
    MAX_SAMPLE_RATE = 192000

    @staticmethod
    def validate_audio_params(duration, sample_rate):
        """
        Validates audio generation parameters to prevent Denial of Service
        (DoS) via memory exhaustion.
        """
        if duration <= 0 or duration > InputValidator.MAX_DURATION:
            raise ValueError(
                f"Duration must be between 0 and "
                f"{InputValidator.MAX_DURATION} seconds."
            )

        if sample_rate <= 0 or sample_rate > InputValidator.MAX_SAMPLE_RATE:
            raise ValueError(
                f"Sample rate must be between 0 and "
                f"{InputValidator.MAX_SAMPLE_RATE} Hz."
            )

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitizes the output filename to prevent path traversal attacks.
        Ensures the file has a .wav extension.
        """
        # prevent path traversal
        if '..' in filename:
            raise ValueError(
                "Filename cannot contain traversal characters ('..')."
            )

        # enforce .wav extension
        if not filename.lower().endswith('.wav'):
            filename += '.wav'

        return filename
