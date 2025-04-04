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

# START MESAJ V2
@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name
    welcome_text = f"""
╔════════════════════╗
   🎩 HOŞGELDİN {first_name} 💚
╚════════════════════╝

🚀 BEN PYTHON SAAS HİZMET BOTUYUM KESİNTİSİZ DESTEK İÇİN BURADAYIM \n\n  
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
    bot.send_message(call.message.chat.id, "[1] ✅ PROJE AKTİF \n\n [ ÖRNEK CERENLOVELY.PY ] İLET VEYA GÖNDER ] \n\n [2] ✅ LİSTELEMEK \n\n [ /docs : AKTİF OLAN PROJELER LİSTELENİR ] \n\n [3] ✅ ÇÖP KUTUSU \n\n [ ÖRNEK /delete CERENLOVELY.PY ]")

@bot.callback_query_handler(func=lambda call: call.data == "price")
def callback_price(call):
    bot.send_message(call.message.chat.id, "🎲 FİYATLAR : \n\n [1] 💬 1 AY : [10 TRY] \n [2] 💬 2 AY : [20 TRY] \n [3] 💬 3 AY : [30 TRY] \n [4] 💬 5 AY : [50 TRY] \n\n NOT : ÖZEL BÜTÇELENDİRME VE PLAN TASSARUF İÇİN KURUCU İLE İLETİŞİME GEÇEBİLİRSİN ✓")


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
