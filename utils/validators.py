import os
import re

class InputValidator:
    @staticmethod
    def sanitize_filename(filename, default_name="output.wav"):
        """
        Sanitizes the input filename to prevent path traversal and ensure it ends with .wav.
        Allows only alphanumeric characters, underscores, dashes, dots, spaces, and parentheses.
        Strips directory paths.
        """
        if not filename:
            return default_name

        # Strip directory path
        filename = os.path.basename(filename)

        # Whitelist characters (allow alphanumeric, -, _, ., space, parens)
        filename = re.sub(r'[^a-zA-Z0-9_\-\.\ \(\)]', '', filename)

        if not filename:
            return default_name

        if not filename.endswith('.wav'):
            filename += '.wav'

        return filename
