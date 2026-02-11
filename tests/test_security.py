import unittest
from utils.security import validate_filename


class TestSecurity(unittest.TestCase):
    def test_valid_filenames(self):
        self.assertEqual(validate_filename("kick.wav"), "kick.wav")
        self.assertEqual(validate_filename("my_kick.wav"), "my_kick.wav")
        self.assertEqual(validate_filename("kick-123.wav"), "kick-123.wav")
        self.assertEqual(validate_filename("Kick.wav"), "Kick.wav")
        self.assertEqual(validate_filename("my kick.wav"), "my kick.wav")
        self.assertEqual(validate_filename("kick (1).wav"), "kick (1).wav")
        self.assertEqual(
            validate_filename("kick, punch.wav"), "kick, punch.wav")

    def test_invalid_filenames(self):
        # Empty
        with self.assertRaises(ValueError):
            validate_filename("")

        # Path traversal
        with self.assertRaises(ValueError):
            validate_filename("../kick.wav")
        with self.assertRaises(ValueError):
            validate_filename("/etc/passwd")
        with self.assertRaises(ValueError):
            validate_filename("..\\kick.wav")

        # Wrong extension
        with self.assertRaises(ValueError):
            validate_filename("kick.mp3")
        with self.assertRaises(ValueError):
            validate_filename("kick")

        # Invalid characters
        with self.assertRaises(ValueError):
            validate_filename("kick!.wav")
        with self.assertRaises(ValueError):
            validate_filename("kick*.wav")
        with self.assertRaises(ValueError):
            validate_filename("kick;.wav")


if __name__ == "__main__":
    unittest.main()
