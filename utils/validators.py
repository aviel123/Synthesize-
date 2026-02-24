import re
import os

def validate_filename(filename):
    """
    Validates that the filename is safe and does not contain path traversal characters.
    Returns the sanitized filename or raises ValueError.
    """
    # Check for empty
    if not filename:
        raise ValueError("Filename cannot be empty")

    # Check for path traversal
    if ".." in filename:
        raise ValueError("Path traversal ('..') is not allowed")

    # Check for directory separators (enforce current directory for GUI)
    if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
        raise ValueError("Filename must not contain path separators")

    # Check for illegal characters (Windows/Linux common)
    # < > : " / \ | ? *
    if re.search(r'[<>:"/\\|?*]', filename):
        raise ValueError("Filename contains illegal characters")

    return filename
