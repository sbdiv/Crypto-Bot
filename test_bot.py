import unittest
from cryptography.fernet import Fernet
from main import caesar_cipher, caesar_decipher, vigenere_cipher, vigenere_decipher, is_english


KEY = Fernet.generate_key()
cipher = Fernet(KEY)
class TestCipherFunctions(unittest.TestCase):

    def test_caesar_cipher(self):
        self.assertEqual(caesar_cipher("abc", 3), "def")
        self.assertEqual(caesar_cipher("ABC", 3), "DEF")
        self.assertEqual(caesar_cipher("xyz", 3), "abc")
        self.assertEqual(caesar_cipher("Hello, World!", 5), "Mjqqt, Btwqi!")

    def test_caesar_decipher(self):
        self.assertEqual(caesar_decipher("def", 3), "abc")
        self.assertEqual(caesar_decipher("DEF", 3), "ABC")
        self.assertEqual(caesar_decipher("abc", 3), "xyz")
        self.assertEqual(caesar_decipher("Mjqqt, Btwqi!", 5), "Hello, World!")

    def test_vigenere_cipher(self):
        self.assertEqual(vigenere_cipher("HELLO WORLD", "key"), "RIJVS UYVJN")
        self.assertEqual(vigenere_cipher("hello world", "key"), "rijvs uyvjn")
        self.assertEqual(vigenere_cipher("Hello, World!", "key"), "Rijvs, Uyvjn!")

    def test_vigenere_decipher(self):
        self.assertEqual(vigenere_decipher("RIJVS UYVJN", "key"), "HELLO WORLD")
        self.assertEqual(vigenere_decipher("rijvs uyvjn", "key"), "hello world")
        self.assertEqual(vigenere_decipher("Rijvs, Uyvjn!", "key"), "Hello, World!")

    def test_fernet_encryption(self):
        # Тест для шифрування та дешифрування за допомогою Fernet
        text = "Test encryption!"
        encrypted = cipher.encrypt(text.encode())
        decrypted = cipher.decrypt(encrypted).decode()
        self.assertEqual(text, decrypted)

    def test_is_english(self):
        self.assertTrue(is_english("Hello world"))
        self.assertFalse(is_english("Привіт світ"))
        self.assertFalse(is_english("こんにちは世界"))
        self.assertTrue(is_english("Good morning!"))

if __name__ == "__main__":
    unittest.main()