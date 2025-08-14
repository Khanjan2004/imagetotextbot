import telebot
import requests

# Token va API kalitni to‘g‘ridan-to‘g‘ri kod ichida belgilaymiz
TOKEN = "7936808066:AAEaHwNRfhAk-JwRPPW7CO-gg0It9vTXRN0"
OCR_API_KEY = "K86869459388957"

# Bot obyektini yaratamiz
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def greet_user(message):
    """
    Foydalanuvchi birinchi marta /start yozganda ishga tushadi.
    Xabar ichida qisqacha tushuntirish va admin tugmasi bo‘ladi.
    """
    markup = telebot.types.InlineKeyboardMarkup()
    admin_button = telebot.types.InlineKeyboardButton(
        text="👤 Admin",
        url="tg://resolve?domain=ubaydulloxoshimjonov"
    )
    markup.add(admin_button)

    welcome_text = (
        "🖼 Menga rasm yuboring — ichidagi matnni siz uchun ajratib beraman.\n"
        "Matnni o‘z holicha qaytarishga harakat qilaman."
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


@bot.message_handler(content_types=['photo'])
def process_photo(message):
    """
    Foydalanuvchi rasm yuborganda ishga tushadi.
    Rasm Telegram serveridan yuklab olinadi va OCR.Space xizmatiga yuboriladi.
    Natija matn ko‘rinishida foydalanuvchiga qaytariladi.
    """
    try:
        # Telegram serveridan rasmni yuklab olish
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        image_data = requests.get(file_url).content

        # OCR.Space API orqali matnni ajratish
        payload = {
            'apikey': OCR_API_KEY,
            'language': 'eng'  # Zarurat bo‘lsa boshqa tillarni ham qo‘shish mumkin
        }
        files = {'filename': image_data}

        response = requests.post('https://api.ocr.space/parse/image', data=payload, files=files)
        result = response.json()

        if result.get("ParsedResults"):
            extracted_text = result["ParsedResults"][0].get("ParsedText", "").strip()
            if extracted_text:
                bot.reply_to(message, f"📄 Ajratilgan matn:\n\n{extracted_text}")
            else:
                bot.reply_to(message, "⚠️ Rasm ichida matn topilmadi.")
        else:
            bot.reply_to(message, "❌ Matnni ajratib olishda xatolik yuz berdi.")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Kutilmagan xatolik yuz berdi: {str(e)}")


if __name__ == "__main__":
    print("✅ Bot ishga tushdi. Kutish rejimida...")
    bot.polling(none_stop=True)
