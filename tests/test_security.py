import unittest
import os
import sys

# Ensure 'utils' module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.security import validate_filename  # noqa: E402


class TestSecurity(unittest.TestCase):

    def test_valid_filename(self):
        self.assertEqual(validate_filename("test.wav"), "test.wav")
        self.assertEqual(validate_filename("My_Song_1.wav"), "My_Song_1.wav")
        self.assertEqual(validate_filename("kick-drum.wav"), "kick-drum.wav")
        self.assertEqual(validate_filename("loop (1).wav"), "loop (1).wav")

    def test_adds_extension(self):
        self.assertEqual(validate_filename("test"), "test.wav")
        self.assertEqual(validate_filename("My Song"), "My Song.wav")

    def test_empty_filename(self):
        with self.assertRaises(ValueError):
            validate_filename("")
        with self.assertRaises(ValueError):
            validate_filename("   ")

    def test_path_traversal(self):
        with self.assertRaises(ValueError):
            validate_filename("../test.wav")
        with self.assertRaises(ValueError):
            validate_filename("..\\test.wav")
        with self.assertRaises(ValueError):
            validate_filename("/etc/passwd")
        with self.assertRaises(ValueError):
            validate_filename("C:\\Windows\\System32")

    def test_invalid_characters(self):
        with self.assertRaises(ValueError):
            validate_filename("test*.wav")
        with self.assertRaises(ValueError):
            validate_filename("test?.wav")
        with self.assertRaises(ValueError):
            validate_filename("test;.wav")
        with self.assertRaises(ValueError):
            validate_filename("test|.wav")
        with self.assertRaises(ValueError):
            validate_filename("test>.wav")


if __name__ == '__main__':
    unittest.main()
