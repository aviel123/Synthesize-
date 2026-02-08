import os
import re

def validate_filename(filename, allowed_extension=".wav"):
    """
    Validates and sanitizes a filename to prevent path traversal and ensure
    it only contains safe characters.

    Args:
        filename (str): The filename to validate.
        allowed_extension (str): The required file extension (e.g., ".wav").

    Returns:
        str: The sanitized filename (basename only).

    Raises:
        ValueError: If the filename is empty after sanitization.
    """
    # 1. Strip directory path (prevent traversal)
    filename = os.path.basename(filename)

    # 2. Enforce allowed characters (alphanumeric, underscore, dash, dot)
    # Replace unsafe characters with underscores
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

    # 3. Prevent hidden files (leading dot) - optional but good practice
    # If the filename starts with a dot, prepend an underscore
    if filename.startswith('.'):
        filename = '_' + filename

    # 4. Ensure filename is not empty
    if not filename:
        # Fallback
        filename = "output"

    # 5. Enforce extension
    if not filename.endswith(allowed_extension):
        filename += allowed_extension

    return filename
