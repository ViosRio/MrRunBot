import pyrogram
import telebot
import os
import logging
import subprocess
import config  # config.py dosyasını içe aktar

# Configure logging
logging.basicConfig(level=logging.INFO)

# config.py'den token'ı ve diğer ayarları alıyoruz
TOKEN = config.TOKEN
ADMIN_ID = config.ADMIN_ID
ALLOWED_USERS_FILE = config.ALLOWED_USERS_FILE
RUNNING_FILES = config.RUNNING_FILES

allowed_users = set()

def load_allowed_users():
    if os.path.exists(ALLOWED_USERS_FILE):
        with open(ALLOWED_USERS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_allowed_user(user_id):
    with open(ALLOWED_USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")

def save_running_file(file_path):
    with open(RUNNING_FILES, 'a') as file:
        file.write(f"{file_path}\n")

allowed_users = load_allowed_users()

# Botu başlatma
bot = telebot.TeleBot(TOKEN)

from telebot import types

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    
    # Butonları oluştur
    kurucu_button = types.InlineKeyboardButton("KURUCU", url="https://t.me/ViosCeo")
    kullanım_button = types.InlineKeyboardButton("KULLANIM", callback_data="help")
    
    # Butonları yerleştir
    markup.add(kurucu_button, kullanım_button)
    
    # Mesajı gönder
    bot.send_message(
        message.chat.id, 
        "MERHABA 💚\n\n"
        "BEN PYTHON PROJELERİNİZİ ÇALIŞTIRMAK İÇİN BİR BOTUM, GENELDE TELEGRAM BOTLARI İÇİN TERCİH EDİYORLAR.", 
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "/start - Botu başlat\n"
        "/help - Bu yardım mesajını göster\n"
        "/authorize <user_id> - Kullanıcıyı yetkilendir (sadece yönetici)\n"
        "/list - Yüklü dosyaları listele\n"
        "/delete <file_name> - Belirtilen dosyayı sil\n"
        "Python dosyası (.py) gönderin - Dosyayı yükler ve çalıştırır (sadece yetkilendirilmiş kullanıcılar)"
    )
    bot.send_message(message.chat.id, help_text)

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
        bot.send_message(message.chat.id, "Bu komutu kullanma yetkiniz yok.")

@bot.message_handler(commands=['list'])
def list_files(message):
    if message.from_user.id in allowed_users or message.from_user.id == ADMIN_ID:
        # Yüklü dosyaları listeleme mantığı
        pass  # Buraya uygun kodu ekleyin

@bot.message_handler(commands=['delete'])
def delete_file(message):
    if message.from_user.id in allowed_users or message.from_user.id == ADMIN_ID:
        # Dosya silme mantığı
        pass  # Buraya uygun kodu ekleyin

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

@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.send_message(message.chat.id, "Bilinmeyen komut. Lütfen geçerli bir komut kullanın.")

# Bot başlatıldığında yetkilileri yükle
allowed_users = load_allowed_users()

bot.polling()
