import os

class InputValidator:
    """
    Validation utilities for user input to prevent security vulnerabilities.
    """

    @staticmethod
    def sanitize_filename(filename, ensure_extension='.wav'):
        """
        Sanitizes a filename to prevent path traversal and enforce extension.

        Args:
            filename (str): The input filename.
            ensure_extension (str): The required extension (default: '.wav').

        Returns:
            str: The sanitized filename (basename only).
        """
        # Strip directory components (prevents ../ or /etc/)
        safe_name = os.path.basename(filename)

        # Remove any leading/trailing whitespace
        safe_name = safe_name.strip()

        # Ensure it's not empty
        if not safe_name:
            safe_name = "output"

        # Ensure extension
        if not safe_name.lower().endswith(ensure_extension.lower()):
            safe_name += ensure_extension

        return safe_name
