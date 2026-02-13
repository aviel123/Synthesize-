import unittest
from utils.security import validate_filename

class TestSecurity(unittest.TestCase):
    def test_valid_filename(self):
        self.assertEqual(validate_filename("test.wav"), "test.wav")
        self.assertEqual(validate_filename("test"), "test.wav")
        self.assertEqual(validate_filename("My_Song_1.wav"), "My_Song_1.wav")
        self.assertEqual(validate_filename("track (1).wav"), "track (1).wav")

    def test_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "Path traversal"):
            validate_filename("../test.wav")
        with self.assertRaisesRegex(ValueError, "Path traversal"):
            validate_filename("folder/test.wav")
        with self.assertRaisesRegex(ValueError, "Path traversal"):
            validate_filename("..\\test.wav")
        with self.assertRaisesRegex(ValueError, "Path traversal"):
            validate_filename("C:\\Windows\\System32\\test.wav")

    def test_invalid_characters(self):
        with self.assertRaisesRegex(ValueError, "Filename contains invalid characters"):
            validate_filename("test*.wav")
        with self.assertRaisesRegex(ValueError, "Filename contains invalid characters"):
            validate_filename("test?.wav")
        with self.assertRaisesRegex(ValueError, "Filename contains invalid characters"):
            validate_filename("test;.wav")
        with self.assertRaisesRegex(ValueError, "Filename contains invalid characters"):
            validate_filename("test|.wav")

    def test_reserved_names(self):
        with self.assertRaisesRegex(ValueError, "Invalid filename"):
            validate_filename(".")
        with self.assertRaisesRegex(ValueError, "Invalid filename"):
            validate_filename("..")

    def test_empty_filename(self):
        with self.assertRaisesRegex(ValueError, "Filename cannot be empty"):
            validate_filename("")

if __name__ == '__main__':
    unittest.main()
