import telebot
from telebot import types
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
from langdetect import detect, LangDetectException

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

KEY = Fernet.generate_key()
cipher = Fernet(KEY)

def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False

def caesar_cipher(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            shift_amount = shift % 26
            new_char = chr(((ord(char.lower()) - ord('a') + shift_amount) % 26) + ord('a'))
            result += new_char.upper() if char.isupper() else new_char
        else:
            result += char
    return result

def caesar_decipher(text, shift):
    return caesar_cipher(text, -shift)

def generate_vigenere_key(text, key):
    key = key.lower()
    key_extended = []
    key_index = 0

    for char in text:
        if char.isalpha():
            key_extended.append(key[key_index % len(key)])
            key_index += 1
        else:
            key_extended.append(char)

    return "".join(key_extended)

def vigenere_cipher(text, key):
    key_extended = generate_vigenere_key(text, key)
    result = ""

    for i in range(len(text)):
        if text[i].isalpha():
            shift_base = 65 if text[i].isupper() else 97
            key_shift = ord(key_extended[i].lower()) - 97
            result += chr((ord(text[i]) - shift_base + key_shift) % 26 + shift_base)
        else:
            result += text[i]

    return result

def vigenere_decipher(text, key):
    key_extended = generate_vigenere_key(text, key)
    result = ""

    for i in range(len(text)):
        if text[i].isalpha():
            shift_base = 65 if text[i].isupper() else 97
            key_shift = ord(key_extended[i].lower()) - 97
            result += chr((ord(text[i]) - shift_base - key_shift) % 26 + shift_base)
        else:
            result += text[i]

    return result

def return_to_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Шифрування", "Розшифрування")
    bot.send_message(chat_id, "Виберіть одну з опцій:", reply_markup=markup)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    return_to_main_menu(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "Шифрування")
def choose_encryption_method(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("AES", "Caesar", "Vigenere")
    msg = bot.send_message(message.chat.id, "Виберіть метод шифрування:", reply_markup=markup)
    bot.register_next_step_handler(msg, encrypt_text)

def encrypt_text(message):
    method = message.text
    if method in ["Caesar", "Vigenere"]:
        msg = bot.send_message(message.chat.id, "Введіть ключ для шифрування:")
        bot.register_next_step_handler(msg, lambda msg: get_encryption_key(msg, method))
    else:
        msg = bot.send_message(message.chat.id, "Введіть текст для шифрування:")
        bot.register_next_step_handler(msg, lambda msg: process_encryption(msg, method))

def get_encryption_key(message, method):
    key = message.text
    if not is_english(key):
        bot.send_message(message.chat.id, "Ключ повинен містити лише англійські літери.")
        return_to_main_menu(message.chat.id)
        return
    msg = bot.send_message(message.chat.id, "Введіть текст для шифрування:")
    bot.register_next_step_handler(msg, lambda msg: process_encryption(msg, method, key))

def process_encryption(message, method, key=None):
    if not is_english(message.text):
        bot.send_message(message.chat.id, "Будь ласка, введіть текст англійською мовою.")
        return_to_main_menu(message.chat.id)
        return
    
    if method == "AES":
        encrypted_text = cipher.encrypt(message.text.encode()).decode()
    elif method == "Caesar":
        try:
            shift = int(key)
            encrypted_text = caesar_cipher(message.text, shift)
        except ValueError:
            bot.send_message(message.chat.id, "Ключ для шифрування Цезаря повинен бути числом.")
            return
    elif method == "Vigenere":
        encrypted_text = vigenere_cipher(message.text, key)
    else:
        bot.send_message(message.chat.id, "Невідомий метод шифрування.")
        return
    
    bot.send_message(message.chat.id, f"Зашифрований текст ({method}): {encrypted_text}")
    return_to_main_menu(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "Розшифрування")
def choose_decryption_method(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("AES", "Caesar", "Vigenere")
    msg = bot.send_message(message.chat.id, "Виберіть метод розшифрування:", reply_markup=markup)
    bot.register_next_step_handler(msg, decrypt_text)

def decrypt_text(message):
    method = message.text
    if method in ["Caesar", "Vigenere"]:
        msg = bot.send_message(message.chat.id, "Введіть ключ для розшифрування:")
        bot.register_next_step_handler(msg, lambda msg: get_decryption_key(msg, method))
    else:
        msg = bot.send_message(message.chat.id, "Введіть текст для розшифрування:")
        bot.register_next_step_handler(msg, lambda msg: process_decryption(msg, method))

def get_decryption_key(message, method):
    key = message.text
    if not is_english(key):
        bot.send_message(message.chat.id, "Ключ повинен містити лише англійські літери.")
        return_to_main_menu(message.chat.id)
        return
    msg = bot.send_message(message.chat.id, "Введіть текст для розшифрування:")
    bot.register_next_step_handler(msg, lambda msg: process_decryption(msg, method, key))

def process_decryption(message, method, key=None):
    if not is_english(message.text):
        bot.send_message(message.chat.id, "Будь ласка, введіть текст англійською мовою.")
        return_to_main_menu(message.chat.id)
        return
    
    try:
        if method == "AES":
            decrypted_text = cipher.decrypt(message.text.encode()).decode()
        elif method == "Caesar":
            try:
                shift = int(key)
                decrypted_text = caesar_decipher(message.text, shift)
            except ValueError:
                bot.send_message(message.chat.id, "Ключ для розшифрування Цезаря повинен бути числом.")
                return
        elif method == "Vigenere":
            decrypted_text = vigenere_decipher(message.text, key)
        else:
            bot.send_message(message.chat.id, "Невідомий метод розшифрування.")
            return
        
        bot.send_message(message.chat.id, f"Розшифрований текст ({method}): {decrypted_text}")
    except Exception as e:
        bot.send_message(message.chat.id, "Помилка! Невірний формат або ключ.")
    
    return_to_main_menu(message.chat.id)

if __name__ == "__main__":
    bot.polling(none_stop=True)
