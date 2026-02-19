import unittest
from utils.validators import InputValidator

class TestInputValidator(unittest.TestCase):

    def test_sanitize_filename_basic(self):
        self.assertEqual(InputValidator.sanitize_filename("test.wav"), "test.wav")
        self.assertEqual(InputValidator.sanitize_filename("my_kick.wav"), "my_kick.wav")

    def test_sanitize_filename_traversal(self):
        # Should strip directory components
        self.assertEqual(InputValidator.sanitize_filename("../../etc/passwd"), "passwd.wav")
        self.assertEqual(InputValidator.sanitize_filename("/var/lib/secret.wav"), "secret.wav")

    def test_sanitize_filename_extension(self):
        # Should append .wav if missing
        self.assertEqual(InputValidator.sanitize_filename("kick"), "kick.wav")
        self.assertEqual(InputValidator.sanitize_filename("my.file.txt"), "my.file.txt.wav")

    def test_sanitize_filename_special_chars(self):
        # Should remove invalid chars
        self.assertEqual(InputValidator.sanitize_filename("bad$name!.wav"), "badname.wav")
        self.assertEqual(InputValidator.sanitize_filename("spaces are bad.wav"), "spacesarebad.wav")

    def test_sanitize_filename_empty(self):
        # Should return default if empty
        self.assertEqual(InputValidator.sanitize_filename(""), "output.wav")
        self.assertEqual(InputValidator.sanitize_filename(None), "output.wav")
        # If sanitization results in empty string (e.g. only special chars)
        self.assertEqual(InputValidator.sanitize_filename("$$$"), "output.wav")

if __name__ == '__main__':
    unittest.main()
