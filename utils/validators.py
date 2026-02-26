import os

def validate_filename(filename):
    """
    Validates a filename to prevent path traversal and ensure safety.

    Args:
        filename (str): The filename to validate.

    Raises:
        ValueError: If the filename is invalid or unsafe.
    """
    if not filename:
        raise ValueError("Filename cannot be empty.")

    # Check for null bytes
    if '\0' in filename:
        raise ValueError("Filename contains null bytes.")

    # Check for path traversal attempts
    if '..' in filename:
        raise ValueError("Filename cannot contain path traversal sequences ('..').")

    # Check for directory separators (we want just a filename, not a path)
    if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
        raise ValueError(f"Filename cannot contain path separators ('{os.path.sep}'). Please use just a filename.")

    # Check for illegal characters (Windows/Linux common forbidden)
    illegal_chars = set('<>:"/\\|?*')
    if any(char in illegal_chars for char in filename):
        raise ValueError("Filename contains illegal characters.")

    return True
