import re


def validate_filename(filename):
    """
    Validates the filename to prevent path traversal and ensure it's a safe
    .wav file.

    Args:
        filename (str): The filename to validate.

    Returns:
        str: The validated filename.

    Raises:
        ValueError: If the filename is invalid.
    """
    if not filename:
        raise ValueError("Filename cannot be empty.")

    # Check for path traversal characters explicitly (defense in depth)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError(
            "Invalid filename: Path traversal characters not allowed.")

    # Check extension
    if not filename.lower().endswith(".wav"):
        raise ValueError("Invalid filename: Must be a .wav file.")

    # Check for allowed characters
    # Allow alphanumeric, underscore, dash, dot, space, parens, comma
    if not re.match(r"^[a-zA-Z0-9_\-\. (),]+$", filename):
        raise ValueError("Invalid filename: Contains invalid characters.")

    return filename
