import os
import re

class InputValidator:
    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitizes a filename to prevent path traversal and shell injection.
        Allows spaces and alphanumeric characters.
        """
        # 1. Strip directory path (force to current dir)
        filename = os.path.basename(filename)

        # 2. Allow alphanumeric, underscores, dashes, dots, and SPACES
        filename = re.sub(r'[^a-zA-Z0-9_.\- ]', '', filename)

        # 3. Ensure not empty
        if not filename or filename.strip() == "":
            filename = "output.wav"

        # 4. Ensure .wav extension
        if not filename.endswith('.wav'):
            filename += '.wav'

        return filename
