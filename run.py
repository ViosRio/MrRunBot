import os
import logging
import subprocess
import asyncio
import config  # config.py dosyasını içe aktar
from datetime import datetime
from random import choice
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import telebot

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)

# Config dosyasından verileri çekiyoruz
TOKEN = config.TOKEN
ADMIN_ID = config.ADMIN_ID
ALLOWED_USERS_FILE = config.ALLOWED_USERS_FILE
RUNNING_FILES = config.RUNNING_FILES

allowed_users = set()

def load_allowed_users():
    """Yetkili kullanıcıları dosyadan yükler."""
    if os.path.exists(ALLOWED_USERS_FILE):
        with open(ALLOWED_USERS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_allowed_user(user_id):
    """Yeni yetkili kullanıcıyı dosyaya kaydeder."""
    with open(ALLOWED_USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")

def save_running_file(file_path):
    """Çalışan Python dosyalarını kaydeder."""
    with open(RUNNING_FILES, 'a') as file:
        file.write(f"{file_path}\n")

allowed_users = load_allowed_users()

# Telebot başlatma
bot = telebot.TeleBot(TOKEN)

# START Mesajı
START = """ 
๏ 𝗠𝗲𝗿𝗵𝗮𝗯𝗮 🌹

𝗣𝘆𝘁𝗵𝗼𝗻 𝗱𝗼𝘀𝘆𝗮𝗹𝗮𝗿ı𝗻ı 𝗰̧𝗮𝗹ı𝘀̧tır𝗮𝗯𝗶𝗹𝗲𝗻 𝗯𝗶𝗿 𝗯𝗼𝘁𝘂𝗺! 
𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺 𝗯𝗼𝘁𝗹𝗮𝗿ı 𝗶ç𝗶𝗻 ç𝗼𝗸 𝘁𝗲𝗿𝗰𝗶𝗵 𝗲𝗱𝗶𝗹𝗶𝘆𝗼𝗿! 🚀
"""

# Butonlar
MAIN_BUTTONS = [
    [InlineKeyboardButton(text="👤 Sahip", url="https://t.me/ViosCeo")],
    [InlineKeyboardButton(text="➕ Beni Gruba Ekle", url=f"https://t.me/{config.BOT_USERNAME}?startgroup=true")],
    [InlineKeyboardButton(text="🆘 Yardım & Komutlar", callback_data="HELP")],
]

HELP_TEXT = """
**Komutlar:**  
- `/run` → Yanıtladığınız `.py` dosyasını çalıştırır  
- `/list` → Çalışan dosyaları listeler  
- `/delete` → Çalışan bir dosyayı siler  

🔹 *VIP erişim için adminle iletişime geçin!*
"""

# /start komutu
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_photo(message.chat.id, "https://example.com/start_img.jpg", caption=START, reply_markup=InlineKeyboardMarkup(MAIN_BUTTONS))

# /help komutu
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, HELP_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data="HELP_BACK")]]))

# Callback işleme
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "HELP":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=HELP_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data="HELP_BACK")]]))
    elif call.data == "HELP_BACK":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=START, reply_markup=InlineKeyboardMarkup(MAIN_BUTTONS))

# Kullanıcı yetkilendirme
@bot.message_handler(commands=['authorize'])
def authorize_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            save_allowed_user(user_id)
            allowed_users.add(user_id)
            bot.send_message(message.chat.id, f"✅ Kullanıcı {user_id} yetkilendirildi!")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "⚠️ Geçerli bir kullanıcı ID'si girin.")
    else:
        bot.send_message(message.chat.id, "⛔ Öncelikle VIP erişim almalısın!")

# Çalışan dosyaları listeleme
@bot.message_handler(commands=['list'])
def list_files(message):
    if message.from_user.id in allowed_users or message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Şu an çalışan dosyalar listelenecek...")

# Dosya silme
@bot.message_handler(commands=['delete'])
def delete_file(message):
    if message.from_user.id in allowed_users or message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Bir dosya silinecek...")

# Python dosyası yükleme
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "⛔ Bu komutu kullanma yetkiniz yok.")
        return
    
    try:
        if not message.document.file_name.endswith('.py'):
            bot.send_message(message.chat.id, "⚠️ Lütfen sadece `.py` uzantılı dosyalar gönderin!")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = message.document.file_name
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Dosyayı arka planda çalıştır
        subprocess.Popen(["python3", file_path])
        save_running_file(file_path)
        bot.send_message(message.chat.id, f"✅ `{file_path}` arka planda çalıştırılıyor!")

    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        bot.send_message(message.chat.id, f"⚠️ Hata oluştu: {str(e)}")

# Bilinmeyen komut
@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.send_message(message.chat.id, "❌ Bilinmeyen komut. Lütfen geçerli bir komut kullanın.")

# Yetkilileri yükle
allowed_users = load_allowed_users()

# Botu başlat
bot.polling()
