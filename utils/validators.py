import os
import re

class InputValidator:
    """
    Validator class for user inputs to ensure security.
    """

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitizes a filename to prevent path traversal and ensure safe characters.

        Security measures:
        1. Strips directory traversal characters using os.path.basename.
        2. Restricts characters to alphanumeric, underscores, dashes, dots, spaces, parentheses.
        3. Enforces .wav extension.

        Args:
            filename (str): The input filename.

        Returns:
            str: The sanitized filename (basename only).

        Raises:
            ValueError: If the filename is empty or invalid.
        """
        if not filename or not isinstance(filename, str):
            raise ValueError("Filename must be a non-empty string.")

        # 1. Path Traversal Protection: Use basename only
        # This strips "subdir/" or "../../" components
        clean_name = os.path.basename(filename).strip()

        if not clean_name:
            raise ValueError("Filename cannot be empty or just path separators.")

        # 2. Enforce .wav extension (case-insensitive check, append lowercase)
        if not clean_name.lower().endswith('.wav'):
            clean_name += '.wav'

        # 3. Character Whitelisting (Alphanumeric, _ - . ( ) space)
        safe_pattern = re.compile(r'[^a-zA-Z0-9_\-\.\(\) ]')
        clean_name = safe_pattern.sub('', clean_name)

        # Check if empty after cleaning (e.g. if input was "@@@")
        # But we appended .wav, so it will at least be ".wav".
        if clean_name == '.wav':
             raise ValueError("Filename contains no valid characters.")

        return clean_name
