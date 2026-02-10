import re

def validate_filename(filename):
    """
    Validates the filename to prevent path traversal and ensure it's safe.
    Allows only alphanumeric characters, underscores, dashes, dots, and spaces.
    Enforces that the file is saved in the current working directory.
    """
    if not filename:
        raise ValueError("Filename cannot be empty")

    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
         raise ValueError("Invalid filename: Path traversal characters are not allowed")

    # Allow alphanumeric, underscore, dash, dot, space
    if not re.match(r'^[\w\-\. ]+$', filename):
        raise ValueError("Invalid filename: Only alphanumeric, underscore, dash, dot, and space are allowed")

    # Ensure extension is .wav
    if not filename.lower().endswith('.wav'):
        raise ValueError("Invalid filename: Must end with .wav")

    return filename
