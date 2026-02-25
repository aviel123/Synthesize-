import os
import re

def validate_filename(filename):
    """
    Validates and sanitizes a filename for security.

    Ensures the filename:
    1. Contains only alphanumeric characters, underscores, dashes, and dots.
    2. Does not contain path separators (no directory traversal).
    3. Is not empty.
    4. Ends with .wav (appends if missing).

    Returns the sanitized filename (basename only) if valid.
    Raises ValueError if invalid.
    """
    if not filename:
        raise ValueError("Filename cannot be empty.")

    # 1. Strip directory path (basename only) to prevent traversal
    # If the user provided a path, we strip it and use only the filename.
    # This effectively neutralizes ../../ attacks.
    clean_filename = os.path.basename(filename)

    if not clean_filename:
        raise ValueError("Filename cannot be empty.")

    # 2. Check for allowed characters
    # Allow a-z, A-Z, 0-9, _, -, .
    if not re.match(r'^[\w.-]+$', clean_filename):
        raise ValueError("Filename contains invalid characters. Use only letters, numbers, underscores, dashes, and dots.")

    # 3. Ensure it's not just dots (e.g., ".", "..", "...")
    if all(c == '.' for c in clean_filename):
         raise ValueError("Filename cannot be just dots.")

    # 4. Enforce .wav extension
    if not clean_filename.lower().endswith('.wav'):
        clean_filename += '.wav'

    return clean_filename
