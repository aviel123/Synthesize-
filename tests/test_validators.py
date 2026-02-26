import unittest
import sys
import os

# Ensure we can import utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.validators import validate_filename

class TestValidators(unittest.TestCase):
    def test_valid_filenames(self):
        """Test that safe filenames pass validation."""
        valid_names = [
            "kick_01",
            "my-sound.wav",
            "track 1",
            "final_mix_v2",
            "just_a_name"
        ]
        for name in valid_names:
            try:
                self.assertTrue(validate_filename(name))
            except ValueError as e:
                self.fail(f"Valid filename '{name}' raised ValueError: {e}")

    def test_empty_filename(self):
        """Test that empty filename fails."""
        with self.assertRaises(ValueError):
            validate_filename("")
        with self.assertRaises(ValueError):
            validate_filename(None)

    def test_path_traversal(self):
        """Test that path traversal attempts fail."""
        invalid_names = [
            "../kick",
            "..\\kick",
            "dir/../file",
            "....",
            "..",
            "./file" # Even explicit current dir can be considered path manipulation
        ]
        for name in invalid_names:
            with self.assertRaises(ValueError):
                validate_filename(name)

    def test_absolute_paths(self):
        """Test that absolute paths fail (we only want filenames)."""
        invalid_names = [
            "/tmp/kick.wav",
            "C:\\Windows\\System32\\kick.wav",
            "/etc/passwd"
        ]
        for name in invalid_names:
            with self.assertRaises(ValueError):
                validate_filename(name)

    def test_illegal_characters(self):
        """Test characters that are illegal in filenames on common OSs."""
        invalid_names = [
            "kick?.wav",
            "kick*.wav",
            "kick<1>.wav",
            "kick|pipe.wav",
            'kick"quote".wav',
            "kick:time.wav"
        ]
        for name in invalid_names:
            with self.assertRaises(ValueError):
                validate_filename(name)

    def test_null_bytes(self):
        """Test null byte injection."""
        with self.assertRaises(ValueError):
            validate_filename("kick.wav\0")

if __name__ == '__main__':
    unittest.main()
