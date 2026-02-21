import unittest
from utils.validators import InputValidator

class TestInputValidator(unittest.TestCase):

    def test_sanitize_filename_valid(self):
        """Test valid filename sanitization."""
        self.assertEqual(InputValidator.sanitize_filename("valid.wav"), "valid.wav")
        self.assertEqual(InputValidator.sanitize_filename("my-file.wav"), "my-file.wav")
        self.assertEqual(InputValidator.sanitize_filename("my_file (1).wav"), "my_file (1).wav")

    def test_sanitize_filename_missing_extension(self):
        """Test adding .wav extension if missing."""
        self.assertEqual(InputValidator.sanitize_filename("test"), "test.wav")
        self.assertEqual(InputValidator.sanitize_filename("test_file"), "test_file.wav")
        # Preserves case for the base part, but .wav check is case-insensitive
        # If input is "TEST", it doesn't end with .wav, so "TEST.wav"
        self.assertEqual(InputValidator.sanitize_filename("TEST"), "TEST.wav")

    def test_sanitize_filename_path_traversal(self):
        """Test path traversal prevention."""
        # basename of ../../etc/passwd is passwd. Doesn't end with .wav -> passwd.wav
        self.assertEqual(InputValidator.sanitize_filename("../../etc/passwd"), "passwd.wav")
        self.assertEqual(InputValidator.sanitize_filename("subdir/test.wav"), "test.wav")
        self.assertEqual(InputValidator.sanitize_filename("../hidden/secret.wav"), "secret.wav")
        self.assertEqual(InputValidator.sanitize_filename("/absolute/path/to/file.wav"), "file.wav")

    def test_sanitize_filename_whitespace(self):
        """Test whitespace stripping."""
        self.assertEqual(InputValidator.sanitize_filename("  test.wav  "), "test.wav")
        self.assertEqual(InputValidator.sanitize_filename("  spaces  "), "spaces.wav")

    def test_sanitize_filename_invalid_chars(self):
        """Test removal of invalid characters."""
        self.assertEqual(InputValidator.sanitize_filename("bad*file?.wav"), "badfile.wav")
        self.assertEqual(InputValidator.sanitize_filename("weird$name!.wav"), "weirdname.wav")
        self.assertEqual(InputValidator.sanitize_filename("file<name>.wav"), "filename.wav")

    def test_sanitize_filename_empty(self):
        """Test empty filename handling."""
        with self.assertRaises(ValueError):
            InputValidator.sanitize_filename("")
        with self.assertRaises(ValueError):
            InputValidator.sanitize_filename("   ")
        with self.assertRaises(ValueError):
            InputValidator.sanitize_filename(None)

if __name__ == '__main__':
    unittest.main()
