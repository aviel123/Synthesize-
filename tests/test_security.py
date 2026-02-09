
import unittest
import os
from utils.security import validate_filename

class TestSecurity(unittest.TestCase):
    def test_valid_filenames(self):
        valid_files = [
            "kick.wav",
            "my_kick.wav",
            "KICK-123.wav",
            "test.file.wav"
        ]
        for f in valid_files:
            try:
                self.assertEqual(validate_filename(f), f)
            except ValueError as e:
                self.fail(f"Valid filename '{f}' raised ValueError: {e}")

    def test_invalid_extension(self):
        invalid_files = [
            "kick.mp3",
            "kick.txt",
            "kick"
        ]
        for f in invalid_files:
            with self.assertRaises(ValueError):
                validate_filename(f)

    def test_path_traversal(self):
        invalid_files = [
            "../kick.wav",
            "subdir/kick.wav",
            "/etc/passwd",
            "./kick.wav" # technically valid path but contains ./ which dirname catches
        ]
        for f in invalid_files:
            with self.assertRaises(ValueError):
                validate_filename(f)

    def test_invalid_characters(self):
        invalid_files = [
            "kick!.wav",
            "kick space.wav",
            "kick(1).wav",
            "kick$.wav"
        ]
        for f in invalid_files:
            with self.assertRaises(ValueError):
                validate_filename(f)

if __name__ == '__main__':
    unittest.main()
