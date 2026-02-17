import os
import re


class InputValidator:
    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitizes filename to prevent path traversal and ensure safe chars.
        Enforces .wav extension.
        """
        # 1. Strip path information (prevent traversal)
        name = os.path.basename(filename)

        # 2. Limit characters (alphanumeric, dot, dash, underscore)
        # Remove any suspicious characters
        name = re.sub(r'[^a-zA-Z0-9_.-]', '', name)

        # 3. Handle empty result or just dots
        if not name or name.replace('.', '') == '':
            name = "output"

        # 4. Ensure .wav extension
        if not name.endswith('.wav'):
            name += '.wav'

        return name
