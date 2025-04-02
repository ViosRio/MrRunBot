# DENEME AMAÇLIDIR HEMEN ZIPLAMA SAĞLAM OLANI run.py | DİR

import telebot import os import logging import subprocess import config  # config.py dosyasını içe aktar

Logging yapılandırması

logging.basicConfig(level=logging.INFO)

config.py'den token'ı ve diğer ayarları alıyoruz

TOKEN = config.TOKEN ADMIN_ID = int(config.ADMIN_ID)  # Eğer string olarak tanımlıysa int'e çeviriyoruz ALLOWED_USERS_FILE = config.ALLOWED_USERS_FILE START_IMG = config.START_IMG

allowed_users = set()

Yetkilendirilmiş kullanıcıları yükleme

def load_allowed_users(): if os.path.exists(ALLOWED_USERS_FILE): with open(ALLOWED_USERS_FILE, 'r') as file: return set(line.strip() for line in file) return set()

def save_allowed_user(user_id): with open(ALLOWED_USERS_FILE, 'a') as file: file.write(f"{user_id}\n") allowed_users.add(user_id)  # Belleğe de ekle

allowed_users = load_allowed_users()

Bot başlatma

bot = telebot.TeleBot(TOKEN) from telebot import types

/start komutu

@bot.message_handler(commands=['start']) def start(message): first_name = message.from_user.first_name welcome_text = f""" 🎩 HOŞGELDİN {first_name} 💚

🚀 BEN BİR PROJE SANAT BOTUYUM \n\n  
❤️ GENELDE BENİ TELEGRAM BOTLARIM İÇİN İDARE EDİYORLAR, 

🔥 POWERED BY OPEN AI
"""

markup = types.InlineKeyboardMarkup()
markup.add(types.InlineKeyboardButton("KURUCU", url="https://t.me/ViosCeo"))
markup.add(types.InlineKeyboardButton("KULLANIM", callback_data="help"))
markup.add(types.InlineKeyboardButton("FİYATLANDIRMA", callback_data="price"))

bot.send_photo(message.chat.id, START_IMG, caption=welcome_text, parse_mode="Markdown", reply_markup=markup)

Modül yükleme fonksiyonu

def install_modules(): required_modules = ['telebot'] for module in required_modules: try: subprocess.check_call(["python3", "-m", "pip", "install", module]) except subprocess.CalledProcessError: logging.error(f"Modül yüklenemedi: {module}")

Dosya yükleme ve çalıştırma komutu

@bot.message_handler(content_types=['document']) def handle_document(message): if message.from_user.id not in allowed_users: bot.send_message(message.chat.id, "📛 UYARI : \n\n CLOUD SAAS HİZMETLERİ ERİŞİM İÇİN VİP ERİŞİM ELDE ETMELİSİN.") return

try:
    if not message.document.file_name.endswith('.py'):
        bot.send_message(message.chat.id, "📛 UYARI : \n\n LÜTFEN PROJELERİNİZ [ .py ] KAYNAK OLMALIDIR.")
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    file_path = f"./{message.document.file_name}"
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    install_modules()
    subprocess.Popen(["python3", file_path])
    bot.send_message(message.chat.id, f"✅ {file_path} başarıyla çalıştırıldı.")

except Exception as e:
    logging.error(f"Hata oluştu: {e}")
    bot.send_message(message.chat.id, f"Hata oluştu: {str(e)}")

bot.polling(none_stop=True)

