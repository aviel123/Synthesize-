## 2024-05-23 - Path Traversal in Audio Export
**Vulnerability:** User input for filenames was passed directly to `scipy.io.wavfile.write`, allowing directory traversal (e.g. `../../etc/passwd`).
**Learning:** Libraries like `scipy.io.wavfile` do not sanitize paths; they behave like standard file I/O.
**Prevention:** Use `os.path.basename` to strip directory components if the intent is to save to a specific directory, or validate the path against an allowlist of directories. Implemented `InputValidator.sanitize_filename` in `utils/validators.py`.
