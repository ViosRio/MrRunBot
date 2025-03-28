import telebot
import os
import logging
import subprocess
import config  # config.py dosyasını içe aktar

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)

# config.py'den token'ı ve diğer ayarları alıyoruz
TOKEN = config.TOKEN
ADMIN_ID = int(config.ADMIN_ID)  # Eğer string olarak tanımlıysa int'e çeviriyoruz
ALLOWED_USERS_FILE = config.ALLOWED_USERS_FILE
RUNNING_FILES = config.RUNNING_FILES
START_IMG = config.START_IMG

allowed_users = set()

# Yetkilendirilmiş kullanıcıları yükleme
def load_allowed_users():
    if os.path.exists(ALLOWED_USERS_FILE):
        with open(ALLOWED_USERS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_allowed_user(user_id):
    with open(ALLOWED_USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")
    allowed_users.add(user_id)  # Belleğe de ekle

allowed_users = load_allowed_users()

# Bot başlatma
bot = telebot.TeleBot(TOKEN)
from telebot import types

# /start komutu
@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name
    welcome_text = f"""
╔════════════════════╗
   🎩 HOŞGELDİN {first_name} 💚
╚════════════════════╝

🚀 BEN BİR PROJE SANAT BOTUYUM \n\n  
❤️ GENELDE BENİ TELEGRAM BOTLARIM İÇİN İDARE EDİYORLAR, 

🔥 POWERED BY OPEN Aİ
    """

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("KURUCU", url="https://t.me/ViosCeo"))
    markup.add(types.InlineKeyboardButton("KULLANIM", callback_data="help"))
    markup.add(types.InlineKeyboardButton("FİYATLANDIRMA", callback_data="price"))

    bot.send_photo(message.chat.id, config.START_IMG, caption=welcome_text, parse_mode="Markdown", reply_markup=markup)

# Callback işlemleri
@bot.callback_query_handler(func=lambda call: call.data == "help")
def callback_help(call):
    bot.send_message(call.message.chat.id, "KULLANIM : \n\n CERENLOVELY.PY ° İLET VEYA GÖNDER")

@bot.callback_query_handler(func=lambda call: call.data == "price")
def callback_price(call):
    bot.send_message(call.message.chat.id, "📅 FİYATLAR 📅\n\n📅 1 AY : 10 TRY\n📅 2 AY : 20 TRY\n📅 3 AY : 30 TRY\n📅 12 AY : 50 TRY\n\nABONELİK İŞLEMLERİ İÇİN KURUCU İLE İLETİŞİME GEÇİN!")

# Yetkilendirme komutu
@bot.message_handler(commands=['new'])
def authorize_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            save_allowed_user(user_id)
            bot.send_message(message.chat.id, f"Kullanıcı {user_id} yetkilendirildi.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Lütfen geçerli bir kullanıcı ID'si girin.")
    else:
        bot.send_message(message.chat.id, "Bu komutu kullanma yetkiniz yok.")

# Yetkilendirilmiş kullanıcıları listeleme
@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        users = "\n".join(str(user) for user in allowed_users) if allowed_users else "Henüz yetkilendirilmiş kullanıcı yok."
        bot.send_message(message.chat.id, f"Yetkili Kullanıcılar:\n{users}")
    else:
        bot.send_message(message.chat.id, "Bu komutu kullanma yetkiniz yok.")

import subprocess
import sys

# Modül yükleme fonksiyonu
def install_modules():
    required_modules = ['telebot', 'beautifulsoup4', 'bs4']
    for module in required_modules:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        except subprocess.CalledProcessError:
            print(f"Modül yüklenemedi: {module}")

# Bot başlatma komutuyla önce modülleri yükle
install_modules()

# Dosya yükleme ve çalıştırma komutu
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

        file_path = f"./{message.document.file_name}"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Python dosyasını çalıştırmadan önce modülleri kontrol et
        install_modules()

        subprocess.Popen(["python3", file_path])
        bot.send_message(message.chat.id, f"{file_path} dosyası arka planda çalıştırılıyor.")

    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        bot.send_message(message.chat.id, f"Hata oluştu: {str(e)}")

# Dosya yükleme ve çalıştırma komutu
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

        file_path = f"./{message.document.file_name}"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        subprocess.Popen(["python3", file_path])
        bot.send_message(message.chat.id, f"{file_path} dosyası arka planda çalıştırılıyor.")

    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        bot.send_message(message.chat.id, f"Hata oluştu: {str(e)}")

# Bilinmeyen komutları yakalama
@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.send_message(message.chat.id, "Bilinmeyen komut. Lütfen geçerli bir komut kullanın.")

# BOTU ÇALIŞTIR
print("Bot çalışıyor...")
bot.polling()
