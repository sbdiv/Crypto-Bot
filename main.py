import telebot
from telebot import types
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

KEY = Fernet.generate_key()
cipher = Fernet(KEY)

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
    return (key * (len(text) // len(key))) + key[:len(text) % len(key)]

def vigenere_cipher(text, key):
    key = generate_vigenere_key(text, key)
    encrypted_text = ""
    for i in range(len(text)):
        if text[i].isalpha():
            shift = ord(key[i].lower()) - ord('a')
            encrypted_text += caesar_cipher(text[i], shift)
        else:
            encrypted_text += text[i]
    return encrypted_text

def vigenere_decipher(text, key):
    key = generate_vigenere_key(text, key)
    decrypted_text = ""
    for i in range(len(text)):
        if text[i].isalpha():
            shift = ord(key[i].lower()) - ord('a')
            decrypted_text += caesar_cipher(text[i], -shift)
        else:
            decrypted_text += text[i]
    return decrypted_text

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
    msg = bot.send_message(message.chat.id, "Введіть текст для шифрування:")
    bot.register_next_step_handler(msg, lambda msg: process_encryption(msg, method))

def process_encryption(message, method):
    if method == "AES":
        encrypted_text = cipher.encrypt(message.text.encode()).decode()
    elif method == "Caesar":
        encrypted_text = caesar_cipher(message.text, 3)
    elif method == "Vigenere":
        encrypted_text = vigenere_cipher(message.text, "SECRET")
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
    msg = bot.send_message(message.chat.id, "Введіть текст для розшифрування:")
    bot.register_next_step_handler(msg, lambda msg: process_decryption(msg, method))

def process_decryption(message, method):
    try:
        if method == "AES":
            decrypted_text = cipher.decrypt(message.text.encode()).decode()
        elif method == "Caesar":
            decrypted_text = caesar_decipher(message.text, 3)
        elif method == "Vigenere":
            decrypted_text = vigenere_decipher(message.text, "SECRET")
        else:
            bot.send_message(message.chat.id, "Невідомий метод розшифрування.")
            return
        bot.send_message(message.chat.id, f"Розшифрований текст ({method}): {decrypted_text}")
    except Exception as e:
        bot.send_message(message.chat.id, "Помилка! Невірний формат або ключ.")
    return_to_main_menu(message.chat.id)

bot.polling(none_stop=True)