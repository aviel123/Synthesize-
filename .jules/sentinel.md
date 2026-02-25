## 2024-02-12 - Path Traversal in File Exports
**Vulnerability:** User input from `tk.Entry` (filename) was used directly in `wavfile.write` without validation, allowing path traversal (e.g., `../../etc/passwd`).
**Learning:** Tkinter-based desktop apps often overlook input sanitization for file paths, assuming local user trust, but this can be dangerous if the app is exposed or if users are tricked.
**Prevention:** Always use a strict whitelist validator (`utils.validators.validate_filename`) for any user-supplied filename before file operations.
