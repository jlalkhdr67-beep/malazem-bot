from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN

keyboard = [
    ["📘 الرياضيات", "📗 الفيزياء"],
    ["🧪 الكيمياء", "🧬 الأحياء"],
    ["📖 العربي", "🇬🇧 الإنكليزي"],
    ["🌍 الاجتماعيات", "☪️ الإسلامية"],
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 أهلاً بك في بوت ملازم السادس الإعدادي\n\nاختر المادة:",
        reply_markup=reply_markup,
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    await update.message.reply_text(
        f"لقد اخترت: {text}\n\nسيتم إضافة ملفات PDF لهذه المادة لاحقًا."
    )

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))

print("Bot Started...")

app.run_polling()
