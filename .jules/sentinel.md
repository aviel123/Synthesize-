## 2025-05-18 - Path Traversal in File Output
**Vulnerability:** The `TranceKickGenerator.save` method accepted arbitrary filenames without validation, allowing path traversal (e.g., `../etc/passwd`).
**Learning:** Audio generation tools often focus on signal processing and neglect standard security practices like input validation, especially when originally designed as CLI tools. When these tools are exposed via web interfaces (as planned with `index.html`), this becomes a critical vulnerability.
**Prevention:** Enforce strict filename validation using an allowlist (alphanumeric, dots, dashes, spaces) and reject any path separators. Always validate inputs at the boundary, even in internal helper methods if they deal with file I/O.
