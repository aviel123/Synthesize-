import unittest
from utils.validators import InputValidator

class TestInputValidator(unittest.TestCase):
    def test_sanitize_filename(self):
        # Basic
        self.assertEqual(InputValidator.sanitize_filename("test.wav"), "test.wav")

        # Path Traversal
        self.assertEqual(InputValidator.sanitize_filename("../../test.wav"), "test.wav")
        self.assertEqual(InputValidator.sanitize_filename("/etc/passwd"), "passwd.wav")
        self.assertEqual(InputValidator.sanitize_filename("folder/file.wav"), "file.wav")

        # Invalid Characters
        self.assertEqual(InputValidator.sanitize_filename("invalid*?.wav"), "invalid.wav")
        self.assertEqual(InputValidator.sanitize_filename("bad|pipe.wav"), "badpipe.wav")

        # Missing Extension
        self.assertEqual(InputValidator.sanitize_filename("test"), "test.wav")
        self.assertEqual(InputValidator.sanitize_filename("my kick"), "my kick.wav")

        # Empty / Weird
        self.assertEqual(InputValidator.sanitize_filename(""), "output.wav")
        self.assertEqual(InputValidator.sanitize_filename("   "), "output.wav")
        self.assertEqual(InputValidator.sanitize_filename(".wav"), "output.wav")

        # Case
        self.assertEqual(InputValidator.sanitize_filename("TEST.WAV"), "TEST.WAV")
        self.assertEqual(InputValidator.sanitize_filename("TEST"), "TEST.wav")

if __name__ == "__main__":
    unittest.main()
