import os
import re

class InputValidator:
    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitizes the filename to prevent path traversal and ensure it has a .wav extension.
        Restricts characters to alphanumeric, underscores, dashes, and dots.
        Forces the file to be saved in the current directory (or base name only).
        """
        if not filename:
            return "output.wav"

        # 1. Strip directory path (force to current directory)
        filename = os.path.basename(filename)

        # 2. Remove characters that are not alphanumeric, ., _, -, spaces, or parentheses
        filename = re.sub(r'[^a-zA-Z0-9._\- ()]', '', filename)

        # Strip whitespace
        filename = filename.strip()

        # 3. Ensure it's not empty after stripping
        if not filename:
            return "output.wav"

        # 4. Ensure .wav extension
        if not filename.lower().endswith('.wav'):
            filename += '.wav'

        return filename
