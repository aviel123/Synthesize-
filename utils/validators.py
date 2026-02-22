import os
import re

class InputValidator:
    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitizes a filename to prevent path traversal and remove invalid characters.
        Enforces .wav extension.
        """
        if not filename:
            return "output.wav"

        # 1. Strip whitespace
        filename = filename.strip()

        # 2. Get basename to prevent path traversal
        filename = os.path.basename(filename)

        # 3. Remove invalid characters (keep alphanumeric, _, -, ., spaces, parens)
        # Using regex to replace anything NOT in the allowed set with empty string
        filename = re.sub(r'[^a-zA-Z0-9_\-\.\s\(\)]', '', filename)

        # 4. Ensure .wav extension
        if not filename.lower().endswith('.wav'):
            filename += '.wav'

        # 5. Handle empty filename after sanitization
        if filename == '.wav':
            return "output.wav"

        return filename
