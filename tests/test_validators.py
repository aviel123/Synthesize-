import unittest
from utils.validators import InputValidator

class TestInputValidator(unittest.TestCase):
    def test_sanitize_filename_valid(self):
        self.assertEqual(InputValidator.sanitize_filename("test.wav"), "test.wav")
        self.assertEqual(InputValidator.sanitize_filename("my_kick.wav"), "my_kick.wav")
        self.assertEqual(InputValidator.sanitize_filename("KICK-123.wav"), "KICK-123.wav")

    def test_sanitize_filename_adds_extension(self):
        self.assertEqual(InputValidator.sanitize_filename("test"), "test.wav")
        self.assertEqual(InputValidator.sanitize_filename("my_kick"), "my_kick.wav")

    def test_sanitize_filename_path_traversal(self):
        self.assertEqual(InputValidator.sanitize_filename("../../etc/passwd"), "passwd.wav")
        self.assertEqual(InputValidator.sanitize_filename("/var/www/html/index.php"), "index.php.wav")
        self.assertEqual(InputValidator.sanitize_filename("../hidden/secret.txt"), "secret.txt.wav")

    def test_sanitize_filename_special_chars(self):
        # Spaces and parentheses should be preserved
        self.assertEqual(InputValidator.sanitize_filename("my kick.wav"), "my kick.wav")
        self.assertEqual(InputValidator.sanitize_filename("kick (1).wav"), "kick (1).wav")
        self.assertEqual(InputValidator.sanitize_filename("kick@home!.wav"), "kickhome.wav")

    def test_sanitize_filename_empty(self):
        self.assertEqual(InputValidator.sanitize_filename(""), "output.wav")
        self.assertEqual(InputValidator.sanitize_filename(None), "output.wav")
        self.assertEqual(InputValidator.sanitize_filename("   "), "output.wav")

if __name__ == "__main__":
    unittest.main()
