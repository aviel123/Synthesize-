## 2025-02-18 - Path Traversal in GUI Inputs
**Vulnerability:** The GUI allowed users to specify arbitrary file paths (e.g., `../../file.wav`) in the filename entry field, which were passed directly to `scipy.io.wavfile.write`, creating a path traversal/file overwrite risk.
**Learning:** Even in local desktop applications, user input fields labeled "Filename" can be exploited to overwrite system files if not sanitized, especially if the underlying library functions (like `wavfile.write`) accept full paths.
**Prevention:** Implemented strict filename validation (`utils.validators.validate_filename`) that rejects path separators and `..`, enforcing that files are saved only in the application's working directory when using the GUI.
