import unittest
import numpy as np
from unittest.mock import patch, MagicMock
from utils.security import validate_filename
from generators.kick_generator import TranceKickGenerator

class TestSecurity(unittest.TestCase):
    def test_validate_filename_valid(self):
        """Test valid filenames."""
        self.assertEqual(validate_filename("kick.wav"), "kick.wav")
        self.assertEqual(validate_filename("my_kick-v2.wav"), "my_kick-v2.wav")
        self.assertEqual(validate_filename("TRANCE.wav"), "TRANCE.wav")
        self.assertEqual(validate_filename("my kick.wav"), "my kick.wav")

    def test_validate_filename_invalid_chars(self):
        """Test invalid characters."""
        with self.assertRaises(ValueError):
            validate_filename("kick!.wav")
        with self.assertRaises(ValueError):
            validate_filename("kick*.wav")

    def test_validate_filename_path_traversal(self):
        """Test path traversal attempts."""
        with self.assertRaises(ValueError):
            validate_filename("../kick.wav")
        with self.assertRaises(ValueError):
            validate_filename("dir/kick.wav")
        with self.assertRaises(ValueError):
            validate_filename("/etc/passwd")

    def test_validate_filename_extension(self):
        """Test invalid extensions."""
        with self.assertRaises(ValueError):
            validate_filename("kick.mp3")
        with self.assertRaises(ValueError):
            validate_filename("kick.exe")
        with self.assertRaises(ValueError):
            validate_filename("kick")

    @patch('generators.kick_generator.wavfile.write')
    def test_generator_save_security(self, mock_write):
        """Test that generator.save uses validation."""
        gen = TranceKickGenerator()
        audio = np.zeros(100)

        # Valid save
        gen.save("safe.wav", audio)
        mock_write.assert_called()

        # Invalid save
        with self.assertRaises(ValueError):
            gen.save("../unsafe.wav", audio)

if __name__ == '__main__':
    unittest.main()
