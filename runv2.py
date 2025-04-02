import sys
import telebot
import os
import logging
import subprocess
import config
import random
import string
from datetime import datetime

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)

# config.py'den token'ı ve diğer ayarları alıyoruz
TOKEN = config.TOKEN
ADMIN_ID = int(config.ADMIN_ID)
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
# /start komutu
@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name
    username = message.from_user.username  # Kullanıcı adı
    welcome_text = f"""
╔════════════════════╗
     🎩 SELAMLAR 🎩  
╚════════════════════╝

🎨 HOŞGELDİN {first_name} 💚

🚀 BEN BİR PROJE SANAT BOTUYUM 
❤️ GENELDE BENİ TELEGRAM BOTLARIM İÇİN İDARE EDİYORLAR,

🔥 POWERED BY OPEN Aİ
    """

    # Ana Sayfaya Dön butonunu ekliyoruz
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("KURUCU", url="https://t.me/ViosCeo"))
    markup.add(types.InlineKeyboardButton("KULLANIM", callback_data="help"))
    markup.add(types.InlineKeyboardButton("FİYATLANDIRMA", callback_data="price"))
    markup.add(types.InlineKeyboardButton("KAYIT", callback_data="register"))
    markup.add(types.InlineKeyboardButton("DESTEK", callback_data="support"))

    # Hoşgeldin mesajı ile fotoğrafı gönderiyoruz
    bot.send_photo(message.chat.id, config.START_IMG, caption=welcome_text, parse_mode="Markdown", reply_markup=markup)

# Callback işlemleri
@bot.callback_query_handler(func=lambda call: call.data == "help")
def callback_help(call):
    help_text = """
✅ KULLANIM TALİMATLARI:

2️⃣ /docs - Aktif olan dosyalar listelenecektir
3️⃣ /delete <dosya_adı>** - Dosya silme komutu

Ekstra bilgiler için bize her zaman yazabilirsiniz!
    """
    # Yardım mesajını gönderirken geri dön butonu ekliyoruz
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Ana Sayfaya Dön", callback_data="back_home"))
    bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

# Ana sayfaya dönme callback işlemi
@bot.callback_query_handler(func=lambda call: call.data == "back_home")
def callback_back_home(call):
    start(call.message)  # Ana sayfa fonksiyonunu tekrar çağırıyoruz


# Yetkilendirme komutu
@bot.message_handler(commands=['new'])
def authorize_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            save_allowed_user(user_id)
            bot.send_message(message.chat.id, f"✅ DURUM : \n\n {user_id} BAŞARIYLA YETKİLENDİRİLDİ.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "⚠️ HATA : \n\n ÖNCELİKLE CHAT İD BELİRTİNİZ")
    else:
        bot.send_message(message.chat.id, "📛 UYARI : \n\n BU KOMUTU KULLANIM YETKİNİZ YOKTUR")

# Yetkilendirilmiş kullanıcıları listeleme
@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        users = "\n".join(str(user) for user in allowed_users) if allowed_users else "📛UYARI :\n HENÜZ ADMİN ERİŞİMİ OLAN KULLANICI DEĞİLSİN"
        bot.send_message(message.chat.id, f"✅ BAŞARILI:\n{users}")
    else:
        bot.send_message(message.chat.id, "📛 UYARI : \n\n BU KOMUTU KULLANIM YETKİNİZ YOKTUR.")

# Modül yükleme fonksiyonu
def install_modules():
    required_modules = ['telebot']
    for module in required_modules:
        try:
            subprocess.check_call([sys.executable, "pip", "install", module])
        except subprocess.CalledProcessError:
            print(f"Modül yüklenemedi: {module}")

# Rastgele dosya adı oluşturma fonksiyonu
def generate_random_filename(extension=".py"):
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    return f"{random_string}{extension}"

# Bot başlatma komutuyla önce modülleri yükle
install_modules()

# Dosya yükleme ve çalıştırma komutu
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "📛 UYARI : \n\n CLOUD SAAS HİZMETLERİ ERİŞİM İÇİN VİP ERİŞİM ELDE ETMELİSİN.")
        return

    try:
        if not message.document.file_name.endswith('.py'):
            bot.send_message(message.chat.id, "📛 UYARI : \n\n LÜTFEN PROJELERİNİZ [ .py ] KAYNAK OLMALIDIR.")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Kullanıcının chat_id'sine özel dizini oluştur
        user_chat_id = message.from_user.id
        user_folder = f"run/{user_chat_id}"

        # Kullanıcıya ait dizin yoksa oluştur
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # Yeni dosya adını rastgele oluştur
        random_filename = generate_random_filename()

        # Dosyayı kullanıcının dizinine kaydet
        file_path = os.path.join(user_folder, random_filename)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Python dosyasını çalıştırmadan önce modülleri kontrol et
        install_modules()

        subprocess.Popen(["python3", file_path])
        bot.send_message(message.chat.id, f"{file_path} \n\n ✅ BAŞARILI : \n\n UYGULAMANIZ BAŞARILI BİR ŞEKİLDE ÇALIŞMAKTA.")

    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        bot.send_message(message.chat.id, f"Hata oluştu: {str(e)}")

# /docs komutu ile aktif dosyaların listelenmesi ve kategorilere ayıran yapı
@bot.message_handler(commands=['docs'])
def list_user_files(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "📛 UYARI : \n\n Bu komut yalnızca yetkili kullanıcılar içindir.")
        return

    try:
        # Kullanıcının Chat ID'sini alalım
        user_chat_id = message.from_user.id
        
        # Kullanıcıya özel bir klasör belirleyelim
        user_folder = f"run/{user_chat_id}"

        # Eğer kullanıcıya ait dosya klasörü varsa
        if os.path.exists(user_folder):
            user_files = os.listdir(user_folder)
            active_files = []
            sleeping_files = []
            suspicious_files = []

            # Dosyaları kategorilere ayıralım
            for file in user_files:
                file_path = os.path.join(user_folder, file)
                if file.endswith('.py'):
                    try:
                        # Dosyanın içeriğine göre durumunu kontrol et
                        with open(file_path, 'r') as f:
                            content = f.read()
                        # Aktif dosyayı belirleme basit kontrolü
                        if "active" in content:
                            active_files.append(file)
                        else:
                            sleeping_files.append(file)
                    except Exception as e:
                        suspicious_files.append(file)
            
            # Kullanıcıya özel mesajı hazırlayalım
            response_message = "✅ AKTİF DOSYALAR :\n"
            if active_files:
                response_message += "\n".join(active_files) + "\n"
            else:
                response_message += "📛 Aktif dosya bulunmamaktadır.\n"

            response_message += "\n💹 UYKU DURUMUNDAKİ DOSYALAR :\n"
            if sleeping_files:
                response_message += "\n".join(sleeping_files) + "\n"
            else:
                response_message += "📛 Uyku durumundaki dosya bulunmamaktadır.\n"

            response_message += "\n⚠️ ŞÜPHELİ DOSYALAR :\n"
            if suspicious_files:
                response_message += "\n".join(suspicious_files) + "\n"
            else:
                response_message += "📛 Şüpheli dosya bulunmamaktadır.\n"

            bot.send_message(message.chat.id, response_message)
        else:
            bot.send_message(message.chat.id, "📛 UYARI : \n\n Bu kullanıcıya ait dosyalar bulunamadı.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Hata oluştu: {str(e)}")

# Kullanıcının yüklediği dosyayı silme komutu
@bot.message_handler(commands=['delete'])
def delete_user_file(message):
    try:
        file_name = message.text.split()[1]  # Silinecek dosyanın adını al
        file_path = f"./{file_name}"

        if not os.path.exists(file_path):
            bot.send_message(message.chat.id, f"⚠️ {file_name} adlı dosya bulunamadı.")
            return

        # Admin veya yetkilendirilmiş kullanıcı, sadece kendi yüklediği dosyayı silebilir
        if message.from_user.id == ADMIN_ID or (message.from_user.id in allowed_users and file_name.startswith(str(message.from_user.id))):
            os.remove(file_path)
            bot.send_message(message.chat.id, f"✅ {file_name} başarıyla silindi.")
        else:
            bot.send_message(message.chat.id, "📛 Sadece kendi yüklediğiniz dosyaları silebilirsiniz.")

    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "⚠️ Lütfen silmek istediğiniz dosya adını belirtin: `/delete CERENLOVELY.PY`")

# Bilinmeyen komutları yakalama
@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.send_message(message.chat.id, "Bilinmeyen komut. Lütfen geçerli bir komut kullanın.")

# BOTU ÇALIŞTIR
print("Bot çalışıyor...")
bot.polling()
