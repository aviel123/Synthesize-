## 2025-02-08 - Path Traversal in Audio Generators
**Vulnerability:** The application accepted raw user input for filenames in both CLI (`kick_generator.py`) and GUI (`kick_tab.py`, `clap_tab.py`, `combo_tab.py`), allowing path traversal (`../`) and arbitrary file overwrite.
**Learning:** Python's `open()` and `scipy.io.wavfile.write()` do not sanitize paths. Even in a local desktop app, this can be dangerous if the app is run with high privileges or if users are tricked into overwriting critical files.
**Prevention:** Implemented `utils.security.validate_filename` to strictly enforce `os.path.basename` (stripping directories) and an allowlist of characters (alphanumeric, `_`, `-`, `.`), ensuring files are only written to the intended directory.
