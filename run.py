import telebot
from telebot import types
import os
import logging
import subprocess
import config
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)

# config.py'den token'ı ve diğer ayarları alıyoruz
TOKEN = config.TOKEN
ADMIN_ID = config.ADMIN_ID
ALLOWED_USERS_FILE = config.ALLOWED_USERS_FILE
RUNNING_FILES = config.RUNNING_FILES

allowed_users = set()

def load_allowed_users():
    """Allowed users listesine dosyadan okuma yapar"""
    if os.path.exists(ALLOWED_USERS_FILE):
        with open(ALLOWED_USERS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_allowed_user(user_id):
    """Yeni bir kullanıcıyı izinli kullanıcı listesine ekler"""
    with open(ALLOWED_USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")

def save_running_file(file_path):
    """Çalışan dosyaları kaydeder"""
    with open(RUNNING_FILES, 'a') as file:
        file.write(f"{file_path}\n")

allowed_users = load_allowed_users()

# Botu başlatma
bot = telebot.TeleBot(TOKEN)

START_IMG = 'start_image.jpg'  # Başlangıç fotoğrafı
START = """ ๏ 𝗠𝗲𝗿𝗵𝗮𝗯𝗮 🌹
HEY PYTHON PROJELERİNİ ÇALIŞTIRABİLEN BİR BOTUM GENELDE TELEGRAM BOTLARI İÇİN TERCİH EDİYORLAR"""
SOURCE = "https://github.com/YourRepo"  # Kaynak kod linki

# Butonlar
MAIN = [
    [types.InlineKeyboardButton(text="sᴀʜɪᴘ", url="https://t.me/YourUsername")],
    [types.InlineKeyboardButton(text="ʙᴇɴɪ ɢʀᴜʙᴀ ᴇᴋʟᴇ", url="https://t.me/YourBotUsername?startgroup=true")],
    [types.InlineKeyboardButton(text="ʏᴀʀᴅıᴍ & ᴋᴏᴍᴜᴛʟᴀʀ", callback_data="HELP")]
]

HELP_READ = """**/run** İLE YANITLA SİSTEMDE ÇALIŞTIR
VİP FİYATLAR
AYLIK OLARAK HESAPLANIR"""

HELP_BACK = [
    [types.InlineKeyboardButton(text="VİP • ", url="t.me/ViosCeo")],
    [types.InlineKeyboardButton(text="⬅️", callback_data="HELP_BACK")]
]

SOURCE_BUTTONS = types.InlineKeyboardMarkup([[types.InlineKeyboardButton('sᴏᴜʀᴄᴇ', url=SOURCE)]])

# Start komutu
@bot.message_handler(commands=["start"])
def start(message):
    try:
        bot.send_message(message.chat.id, START, reply_markup=types.InlineKeyboardMarkup(MAIN))
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

# Yardım komutu
@bot.callback_query_handler(func=lambda call: call.data == "HELP")
def help_command(call):
    bot.edit_message_text(HELP_READ, call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup(HELP_BACK))

# Geri Yardım komutu
@bot.callback_query_handler(func=lambda call: call.data == "HELP_BACK")
def help_back_command(call):
    bot.edit_message_text(START, call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup(MAIN))

# Kullanıcıyı yetkilendir
@bot.message_handler(commands=['authorize'])
def authorize_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            save_allowed_user(user_id)
            allowed_users.add(user_id)
            bot.send_message(message.chat.id, f"Kullanıcı {user_id} yetkilendirildi.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Lütfen geçerli bir kullanıcı ID'si girin.")
    else:
        bot.send_message(message.chat.id, "Öncelikle Vip Erişim Elde Etmelisin.")

# Yüklü dosyaları listele
@bot.message_handler(commands=['list'])
def list_files(message):
    if message.from_user.id in allowed_users or message.from_user.id == ADMIN_ID:
        # Yüklü dosyaları listeleme mantığı
        pass  # Buraya uygun kodu ekleyin

# Dosya silme
@bot.message_handler(commands=['delete'])
def delete_file(message):
    if message.from_user.id in allowed_users or message.from_user.id == ADMIN_ID:
        # Dosya silme mantığı
        pass  # Buraya uygun kodu ekleyin

# Belge gönderildiğinde işlem yap
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "Bu komutu kullanma yetkiniz yok.")
        return

    try:
        if not message.document.file_name.endswith('.py'):
            bot.send_message(message.chat.id, "Lütfen sadece Python dosyaları (.py) gönderin.")
            return
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Dosyayı kaydetme
        file_path = message.document.file_name
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Kodu güvenli bir şekilde arka planda çalıştırma
        subprocess.Popen(["python3", file_path])
        bot.send_message(message.chat.id, f"{file_path} dosyası arka planda çalıştırılıyor.")
    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        bot.send_message(message.chat.id, f"Hata oluştu: {str(e)}")

# Bilinmeyen komutları yönet
@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.send_message(message.chat.id, "Bilinmeyen komut. Lütfen geçerli bir komut kullanın.")

# Bot başlatıldığında yetkilileri yükle
allowed_users = load_allowed_users()

bot.polling()
