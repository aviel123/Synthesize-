import unittest
import os
from utils.security import validate_filename

class TestSecurity(unittest.TestCase):

    def test_valid_filename(self):
        """Test simple valid filenames."""
        valid, msg = validate_filename("kick.wav")
        self.assertTrue(valid, f"Should be valid: {msg}")
        self.assertEqual(msg, "")

        valid, msg = validate_filename("my_kick_123.wav")
        self.assertTrue(valid, f"Should be valid: {msg}")

        valid, msg = validate_filename("Test File.wav")
        self.assertTrue(valid, f"Should be valid: {msg}")

    def test_empty_filename(self):
        """Test empty filenames."""
        valid, msg = validate_filename("")
        self.assertFalse(valid)
        self.assertEqual(msg, "Filename cannot be empty.")

        valid, msg = validate_filename("   ")
        self.assertFalse(valid)
        self.assertEqual(msg, "Filename cannot be empty.")

    def test_path_traversal(self):
        """Test path traversal attempts."""
        valid, msg = validate_filename("../secret.wav")
        self.assertFalse(valid)
        self.assertIn("directory traversal", msg)

        valid, msg = validate_filename("..")
        self.assertFalse(valid)
        self.assertIn("directory traversal", msg)

        valid, msg = validate_filename("folder/../file.wav")
        self.assertFalse(valid)
        self.assertIn("directory traversal", msg)

    def test_directories_disallowed(self):
        """Test that directory separators are disallowed (enforcing CWD)."""
        valid, msg = validate_filename("subdir/file.wav")
        self.assertFalse(valid)
        self.assertIn("Directories are not allowed", msg)

        # Windows style
        # Note: On Linux, backslash might be treated as char, but validate_filename checks for it explicitly in invalid_chars or logic
        # Our invalid_chars includes \
        valid, msg = validate_filename("subdir\\file.wav")
        self.assertFalse(valid)
        # Message might be "invalid characters" or "directories not allowed" depending on which check hits first
        # In our implementation:
        # os.path.dirname("subdir\\file.wav") might be "" on Linux
        # But check for invalid_chars hits \
        self.assertTrue("invalid characters" in msg or "Directories are not allowed" in msg)

    def test_absolute_paths(self):
        """Test absolute paths are disallowed."""
        # On Linux
        if os.name == 'posix':
            valid, msg = validate_filename("/etc/passwd")
            self.assertFalse(valid)
            self.assertTrue("Absolute paths" in msg or "Directories are not allowed" in msg)

        # Mocking or generic check?
        # validate_filename uses os.path.isabs
        # and os.path.dirname

        # /tmp/test.wav -> isabs=True on Linux
        # C:\test.wav -> isabs=True on Windows

    def test_invalid_characters(self):
        """Test invalid characters."""
        # <>:"/\|?*
        for char in '<>:"/\\|?*':
            valid, msg = validate_filename(f"test{char}file.wav")
            self.assertFalse(valid, f"Should fail for char: {char}")
            if char in "/\\":
                self.assertTrue("Directories are not allowed" in msg or "invalid characters" in msg, f"Msg was: {msg}")
            else:
                self.assertIn("invalid characters", msg)

if __name__ == '__main__':
    unittest.main()
