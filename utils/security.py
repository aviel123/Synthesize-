import os
import re

def validate_filename(filename):
    """
    Validates that the filename is safe to use.
    - Must end with .wav
    - Must not contain path traversal characters (..) or directory separators
    - Must only contain safe characters (alphanumeric, -, _, .)
    """
    # 1. Check extension
    if not filename.lower().endswith('.wav'):
        raise ValueError("Filename must end with .wav")

    # 2. Check for path traversal or directory components
    if os.path.dirname(filename):
        raise ValueError("Filename must not contain path information (must be in current directory)")

    # 3. Check for invalid characters
    # Allow a-z, A-Z, 0-9, -, _, .
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
        raise ValueError("Filename contains invalid characters. Only alphanumeric, -, _, and . are allowed.")

    return filename
