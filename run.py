import os
import logging
import random
import string
import subprocess
import config
from telebot import TeleBot, types

# Config
TOKEN = config.TOKEN
ADMIN_ID = config.ADMIN_ID
ALLOWED_USERS_FILE = config.ALLOWED_USERS_FILE
RUNNING_FILES = config.RUNNING_FILES
START_IMG = config.START_IMG

# Logger
logging.basicConfig(level=logging.INFO)

# Bot
bot = TeleBot(TOKEN)
allowed_users = set()


# Dosya işlemleri
def load_allowed_users():
    # allowed_users.py dosyasını içeri aktarmak için
    try:
        if os.path.exists(ALLOWED_USERS_FILE):
            # allowed_users.py dosyasını import et
            from allowed_users import allowed_users as users
            return set(users)  # Listeyi set'e dönüştür
    except Exception as e:
        logging.error(f"Hata: {e}")
    return set()

def save_allowed_user(user_id):
    with open(ALLOWED_USERS_FILE, 'a') as f:
        f.write(f"{user_id}\n")

def save_running_file(file_path):
    with open(RUNNING_FILES, 'a') as f:
        f.write(f"{file_path}\n")

def generate_random_filename(extension=".py"):
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    return f"{name}{extension}"


# Komutlar
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    caption = f"""
╔════════════════════╗
   🎩 HOŞGELDİN {name} 💚
╚════════════════════╝

🚀 BEN PYTHON SAAS HİZMET BOTUYUM.
🔥 POWERED BY OPEN AI
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("KURUCU", url="https://t.me/ViosCeo"))
    markup.add(types.InlineKeyboardButton("KULLANIM", callback_data="help"))
    markup.add(types.InlineKeyboardButton("FİYATLANDIRMA", callback_data="price"))
    bot.send_photo(message.chat.id, START_IMG, caption=caption, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_callback(call):
    bot.send_message(call.message.chat.id, " [1] ✅ PROJE AKTİF \n\n [ ÖRNEK CERENLOVELY.PY ] İLET VEYA GÖNDER ] \n\n [2] ✅ LİSTELEMEK \n\n [ /docs : AKTİF OLAN PROJELER LİSTELENİR ] \n\n [3] ✅ ÇÖP KUTUSU \n\n [ ÖRNEK /delete CERENLOVELY.PY ]")


@bot.callback_query_handler(func=lambda call: call.data == "price")
def price_callback(call):
    bot.send_message(call.message.chat.id, "🎲 FİYATLAR : \n\n [1] 💬 1 AY : [10 TRY] \n [2] 💬 2 AY : [20 TRY] \n [3] 💬 3 AY : [30 TRY] \n [4] 💬 5 AY : [50 TRY] \n\n NOT : ÖZEL BÜTÇELENDİRME VE PLAN TASSARUF İÇİN KURUCU İLE İLETİŞİME GEÇEBİLİRSİN ✓")


@bot.message_handler(commands=['authorize'])
def authorize_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            save_allowed_user(user_id)
            allowed_users.add(user_id)
            bot.send_message(message.chat.id, f"✅ Kullanıcı {user_id} yetkilendirildi.")
        except:
            bot.send_message(message.chat.id, "📛 HATA : \n\n KULLANIM [ /authorize 54490900 ]")
    else:
        bot.send_message(message.chat.id, "📛 HATA : \n\n BURAYI ALİ BABANIN ÇİFTLİĞİMİ SANDIN KANKİ")


@bot.message_handler(commands=['docs'])
def list_files(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "📛 HATA")
        return

    user_folder = f"run/{message.from_user.id}"
    if not os.path.exists(user_folder):
        bot.send_message(message.chat.id, "Henüz dosyan yok.")
        return

    files = os.listdir(user_folder)
    if not files:
        bot.send_message(message.chat.id, "Hiç dosya yok.")
        return

    bot.send_message(message.chat.id, "✅ BAŞARILI : \n\n AKTİF PROJELERİN :\n" + "\n".join(files))


@bot.message_handler(commands=['delete'])
def delete_file(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "Yetkin yok.")
        return

    try:
        filename = message.text.split()[1]
        filepath = f"run/{message.from_user.id}/{filename}"
        if os.path.exists(filepath):
            os.remove(filepath)
            bot.send_message(message.chat.id, f"{filename} silindi.")
        else:
            bot.send_message(message.chat.id, "Dosya bulunamadı.")
    except:
        bot.send_message(message.chat.id, "📛 HATALI : \n\n [ /delete cerenlovely.py ]")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "Yetkin yok.")
        return

    if not message.document.file_name.endswith('.py'):
        bot.send_message(message.chat.id, "📛 HATA : \n\n SADECE KABÜL EDİLEN DOSYA FORMATI .PY OLAMLIDIR")
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        user_folder = f"run/{message.from_user.id}"
        os.makedirs(user_folder, exist_ok=True)

        filename = generate_random_filename()
        filepath = os.path.join(user_folder, filename)

        with open(filepath, 'wb') as f:
            f.write(downloaded_file)

        save_running_file(filepath)
        subprocess.Popen(["python3", filepath])

        bot.send_message(message.chat.id, f"{filename} çalıştırılıyor.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Hata oluştu: {e}")


@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "📛 HATA \n\n TEHLİKELİ SULARDA YÜZÜYORSUN EVLAT")


# Başlatıcı
allowed_users = load_allowed_users()
bot.polling()
