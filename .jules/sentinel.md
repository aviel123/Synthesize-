## 2025-02-09 - Missing Security Utilities & Path Traversal

**Vulnerability:** The CLI for `kick_generator.py` allowed direct path injection (e.g., `../file.wav`) into `scipy.io.wavfile.write`, enabling arbitrary file overwrite outside the intended scope.

**Learning:** The memory context referenced `utils.security.validate_filename`, but the file `utils/security.py` did not exist in the codebase. This gap between assumed security infrastructure and actual implementation creates critical vulnerabilities.

**Prevention:** Always verify the existence of imported security modules. Implement strict filename validation (restrict to current directory and safe characters) for all user-controllable file outputs, especially when wrapping external I/O libraries.
