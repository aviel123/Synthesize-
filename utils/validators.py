import os
import re

class InputValidator:
    @staticmethod
    def sanitize_filename(filename, default="output.wav"):
        """
        Sanitizes the output filename to prevent path traversal and invalid characters.
        Enforces .wav extension.
        """
        if not filename:
            return default

        # 1. Strip directory components (prevent traversal)
        name = os.path.basename(filename)

        # 2. Allow only alphanumeric, underscores, dashes, dots
        # Replace invalid chars with empty string
        name = re.sub(r'[^a-zA-Z0-9_.-]', '', name)

        # 3. Ensure not empty after stripping
        if not name:
            return default

        # 4. Enforce .wav extension
        if not name.lower().endswith('.wav'):
            name += '.wav'

        return name
