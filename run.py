import os
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid
from pyrogram.enums import ChatAction, ParseMode
from datetime import datetime
import logging

FORMAT = "[BOT] %(message)s"
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

StartTime = time.time()


    # Pyrogram Client (bot)
Mukesh = Client(
    "python-executor-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Başlangıç Mesajı
START = """
๏ 𝗠𝗲𝗿𝗵𝗮𝗯𝗮 🌹

Python dosyasını çalıştırmak için buradayım! Lütfen çalıştırmak istediğiniz Python dosyasını gönderin.
"""

# Yardım Mesajı
HELP_TEXT = """
**➻ 𝗞𝘂𝗹𝗹𝗮𝗻ı𝗺 :** 

Botu kullanarak istediğiniz Python dosyasını yükleyip çalıştırabilirsiniz. Python dosyasını göndermek için aşağıdaki talimatları takip edin:
1. Python dosyasını yükleyin.
2. Botun çalıştırmasını bekleyin.

**Bot Versiyonu:** v1.0
"""

# Start Komutu
@Mukesh.on_message(filters.command(["start", f"start@{BOT_USERNAME}"]))
async def start(client, m: Message):
    try:
        await m.reply_photo(
            photo=START_IMG,
            caption=START,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text="Yardım", callback_data="HELP")]
                ]
            ),
        )
    except Exception as e:
        await m.reply(str(e))


# Yardım Komutu
@Mukesh.on_callback_query(filters.regex("HELP"))
async def help_command(client, query):
    await query.message.edit_text(
        HELP_TEXT,
    )


# Python Dosyasını Çalıştırma
@Mukesh.on_message(filters.document)
async def handle_python_file(client, message: Message):
    if message.document.mime_type == "application/x-python":
        try:
            # Dosya indiriliyor
            file_name = f"{message.document.file_name}"
            file_path = f"./{file_name}"
            await message.download(file_path)
            
            # Python dosyasını çalıştırma
            process = await asyncio.create_subprocess_exec(
                "python3", file_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if stdout:
                result = stdout.decode()
                await message.reply(f"Python Script Output:\n```\n{result}\n```")
            if stderr:
                error = stderr.decode()
                await message.reply(f"Python Script Error:\n```\n{error}\n```")

            # Geçici dosyayı silme
            os.remove(file_path)

        except Exception as e:
            await message.reply(f"Bir hata oluştu: {str(e)}")

    else:
        await message.reply("Lütfen geçerli bir Python dosyası gönderin.")


# Ping Komutu
@Mukesh.on_message(filters.command(["ping", "alive"], prefixes=["+", "/", "-", "?", "$", "&", "."]))
async def ping(client, message: Message):
    start = datetime.now()
    t = "Bekleyiniz.."
    txxt = await message.reply(t)
    await asyncio.sleep(0.25)
    await txxt.edit_text("✦ Yᴜ̈ᴋʟᴇɴɪʏᴏʀ..")
    await asyncio.sleep(0.35)
    await txxt.delete()
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.reply(f"Bot Yanıt Süresi: `{ms}` ms")


# Botu başlatma
if __name__ == "__main__":
    print(f"{BOT_USERNAME} botu başlatılıyor...")
    try:
        Mukesh.start()
    except Exception as e:
        print(f"Bot başlatılamadı: {e}")
    print(f"Bot Çalışıyor...")
