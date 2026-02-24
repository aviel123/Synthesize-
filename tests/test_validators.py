import unittest
import os
from utils.validators import validate_filename

class TestValidators(unittest.TestCase):
    def test_valid_filename(self):
        self.assertEqual(validate_filename("output.wav"), "output.wav")
        self.assertEqual(validate_filename("my_kick.wav"), "my_kick.wav")
        self.assertEqual(validate_filename("clean-file.wav"), "clean-file.wav")

    def test_empty_filename(self):
        with self.assertRaises(ValueError):
            validate_filename("")

    def test_path_traversal(self):
        with self.assertRaises(ValueError):
            validate_filename("../output.wav")
        with self.assertRaises(ValueError):
            validate_filename("..")
        with self.assertRaises(ValueError):
            validate_filename("folder/../file.wav")

    def test_separators(self):
        with self.assertRaises(ValueError):
            validate_filename("folder/file.wav")
        with self.assertRaises(ValueError):
            validate_filename("/tmp/file.wav")

        # Test backslash if on Windows or generally
        with self.assertRaises(ValueError):
            validate_filename("folder\\file.wav")

    def test_illegal_chars(self):
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in illegal_chars:
            with self.assertRaises(ValueError):
                validate_filename(f"file{char}.wav")

if __name__ == '__main__':
    unittest.main()
