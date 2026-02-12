import os
import re


def validate_filename(filename):
    """
    Validates the filename to prevent path traversal and ensure it's a safe
    .wav file. Restricts saving to the current working directory (no path
    separators allowed).

    Args:
        filename (str): The filename to validate.

    Returns:
        str: A sanitized filename (guaranteed to end with .wav).

    Raises:
        ValueError: If the filename is invalid or contains path traversal
                    characters.
    """
    if not filename:
        raise ValueError("Filename cannot be empty.")

    # Strip whitespace
    filename = filename.strip()

    # Check for path separators
    if os.path.sep in filename or (
        os.path.altsep and os.path.altsep in filename
    ):
        raise ValueError(
            "Path separators are not allowed. "
            "Please save to the current directory."
        )

    # Check for path traversal characters
    if '..' in filename:
        raise ValueError("Path traversal ('..') is not allowed.")

    # Validate characters (whitelist)
    # Alphanumeric, underscore, dash, dot, space, comma, parenthesis
    if not re.match(r'^[a-zA-Z0-9_\-\.\ \(\)\,]+$', filename):
        raise ValueError(
            "Filename contains invalid characters. Use alphanumeric, dash, "
            "dot, underscore, space, comma, or parenthesis."
        )

    # Enforce .wav extension
    if not filename.lower().endswith('.wav'):
        filename += '.wav'

    return filename
