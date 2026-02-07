import os

def validate_filename(filename):
    """
    Validates that the filename is safe to use.

    This function checks if the filename:
    1. Is not empty.
    2. Does not contain directory traversal sequences ('..').
    3. Is not an absolute path.
    4. Does not contain directory separators (enforces saving to the current directory).
    5. Does not contain invalid filename characters.

    Args:
        filename (str): The filename to validate.

    Returns:
        tuple: (bool, str) - (True, "") if valid, (False, error_message) if invalid.
    """
    if not filename or not filename.strip():
        return False, "Filename cannot be empty."

    # Path traversal check
    if '..' in filename:
        return False, "Filename contains directory traversal ('..')."

    # Absolute path check
    if os.path.isabs(filename):
        return False, "Absolute paths are not allowed. Please use a local filename."

    # Directory separator check (to enforce local directory)
    if os.path.dirname(filename):
         return False, "Directories are not allowed in filename. Please save to the current directory."

    # Check for invalid characters (Windows restrictions mostly, plus / and \)
    # < > : " / \ | ? *
    invalid_chars = '<>:"/\\|?*'
    if any(char in filename for char in invalid_chars):
        return False, f"Filename contains invalid characters: {invalid_chars}"

    return True, ""
