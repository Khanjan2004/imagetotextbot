import os
import telebot
import requests

# Environment variablesdan tokenlarni olish
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
OCR_API_KEY = os.getenv("OCR_API_KEY")

if not BOT_TOKEN or not OCR_API_KEY:
    raise ValueError("TELEGRAM_TOKEN yoki OCR_API_KEY environment variables topilmadi!")

bot = telebot.TeleBot(BOT_TOKEN)

# /start komandasi
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Salom! Menga rasm yuboring, men matnni chiqarib beraman 📄")

# Faqat rasm qabul qilish
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        # OCR.Space API'ga so'rov
        payload = {
            'apikey': OCR_API_KEY,
            'url': file_url,
            'language': 'eng',  # 'eng' o‘rniga 'uzb' ham qo‘yishingiz mumkin
        }
        r = requests.post("https://api.ocr.space/parse/image", data=payload)
        result = r.json()

        if result.get("IsErroredOnProcessing"):
            bot.reply_to(message, "❌ OCR xatolik yuz berdi.")
        else:
            parsed_text = result["ParsedResults"][0]["ParsedText"]
            if parsed_text.strip():
                bot.reply_to(message, f"📜 Aniqlangan matn:\n\n{parsed_text}")
            else:
                bot.reply_to(message, "📭 Matn topilmadi.")
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

# Botni polling rejimida ishga tushirish
if __name__ == "__main__":
    bot.polling(none_stop=True)
