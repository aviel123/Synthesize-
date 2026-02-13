import re

def validate_filename(filename):
    """
    Validates a filename to prevent path traversal and restrict characters.
    Ensures filename ends with .wav and contains only safe characters.

    Args:
        filename (str): The filename to validate.

    Returns:
        str: The sanitized filename (always ends with .wav).

    Raises:
        ValueError: If the filename is invalid or unsafe.
    """
    if not filename:
        raise ValueError("Filename cannot be empty.")

    # 1. Explicit check for path separators (for clear error message)
    if '/' in filename or '\\' in filename:
        raise ValueError("Path traversal is not allowed. Please use a filename without folders.")

    # 2. Check against reserved names or dangerous patterns (before extension)
    if filename.strip() in ['.', '..']:
        raise ValueError("Invalid filename.")

    # 3. Ensure .wav extension
    if not filename.lower().endswith('.wav'):
        filename += '.wav'

    # 4. Whitelist check (alphanumeric, -, _, ., space, comma, parenthesis)
    # This ensures no shell meta-characters or other weirdness.
    if not re.match(r'^[\w\-\. \(\),]+$', filename):
        raise ValueError("Filename contains invalid characters. Use letters, numbers, -, _, ., space, comma, parenthesis.")

    return filename
