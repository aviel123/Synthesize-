import unittest
from utils.validators import validate_filename

class TestValidators(unittest.TestCase):
    def test_valid_filename(self):
        """Test simple valid filenames."""
        self.assertEqual(validate_filename("kick.wav"), "kick.wav")
        self.assertEqual(validate_filename("my_kick.wav"), "my_kick.wav")
        self.assertEqual(validate_filename("kick-123.wav"), "kick-123.wav")

    def test_appends_extension(self):
        """Test that .wav is appended if missing."""
        self.assertEqual(validate_filename("kick"), "kick.wav")
        self.assertEqual(validate_filename("my_kick"), "my_kick.wav")

    def test_path_traversal(self):
        """Test that directory traversal attempts are neutralized."""
        self.assertEqual(validate_filename("../kick.wav"), "kick.wav")
        self.assertEqual(validate_filename("../../etc/passwd"), "passwd.wav")
        self.assertEqual(validate_filename("/root/secret.wav"), "secret.wav")

    def test_invalid_characters(self):
        """Test that invalid characters raise ValueError."""
        with self.assertRaises(ValueError):
            validate_filename("kick!.wav")
        with self.assertRaises(ValueError):
            validate_filename("kick*.wav")
        with self.assertRaises(ValueError):
            validate_filename("kick?.wav")
        with self.assertRaises(ValueError):
            validate_filename("kick|.wav")

    def test_empty_filename(self):
        """Test that empty filename raises ValueError."""
        with self.assertRaises(ValueError):
            validate_filename("")
        with self.assertRaises(ValueError):
            validate_filename("   ")

    def test_just_dots(self):
        """Test that filenames consisting only of dots are rejected."""
        with self.assertRaises(ValueError):
            validate_filename(".")
        with self.assertRaises(ValueError):
            validate_filename("..")
        with self.assertRaises(ValueError):
            validate_filename("...")

if __name__ == "__main__":
    unittest.main()
