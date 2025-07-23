from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import asyncio
from flask import Flask
import threading
import time

# 🔧 Конфигурация
MASTER_CHAT_ID = 5225197085
TOKEN = "7436013012:AAFmxpR03fQC_VOj_pWKhyfaK43FohaPNoE"

# Flask веб-сервер для хостинга (чтобы слушать порт)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 📂 Память отзывов
last_reviews = []
NAME, DATE, PLACE, COMMENTS, PHONE, REVIEW, NOTE, REMIND = range(8)

# 🟢 Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🧘 О практике", "📅 Записаться"],
        ["💬 Отзывы", "🤝 Поддержать проект"],
        ["⏰ Напоминание", "✉️ Оставить записку"]
    ]
    await update.message.reply_text(
        "🛠️ Добро пожаловать в пространство *«Гвозди и Листья»* 🍃\n\n"
        "🔩 Стояние на гвоздях\n"
        "🍵 Чайные церемонии\n"
        "💆 Банки\n"
        "🏕 Выездные практики в природе\n\n"
        "👇 Выбери действие:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )

# 🌿 О практике
async def practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 «Гвозди и Листья» — это место для тех, кто хочет вернуться к себе:\n\n"
        "🔩 Стояние на гвоздях — практика внимания и принятия\n"
        "🍵 Чай — как ритуал тишины и вкуса\n"
        "💨 Душевные разговоры — просто по-человечески\n"
        "💆 Банки — бережная телесная работа\n"
        "🏕 Выезды на природу — церемонии под открытым небом"
    )

# 📅 Запись
async def sign_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как тебя зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Когда удобно провести сессию? (дата/время)")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date'] = update.message.text
    await update.message.reply_text("Где провести? (дома, на природе или у меня?)")
    return PLACE

async def get_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['place'] = update.message.text
    await update.message.reply_text("Есть пожелания или мысли?")
    return COMMENTS

async def get_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['comments'] = update.message.text
    await update.message.reply_text("И пожалуйста, оставь номер телефона для связи 📱")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    user = update.message.from_user
    text = (
        f"📥 *Новая заявка:*\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"📅 Когда: {context.user_data['date']}\n"
        f"📍 Где: {context.user_data['place']}\n"
        f"💬 Мысли: {context.user_data['comments']}\n"
        f"📱 Телефон: {context.user_data['phone']}\n"
        f"Telegram: @{user.username or 'нет'}"
    )
    await context.bot.send_message(MASTER_CHAT_ID, text, parse_mode="Markdown")
    await update.message.reply_text("Спасибо, скоро свяжусь с тобой 🙌")
    return ConversationHandler.END

# ✉️ Оставить записку
async def note_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оставь записку, и она будет передана лично 📬")
    return NOTE

async def receive_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = f"📩 *Записка от @{user.username or 'аноним'}:*\n\n{update.message.text}"
    await context.bot.send_message(MASTER_CHAT_ID, msg, parse_mode="Markdown")
    await update.message.reply_text("Спасибо, записка доставлена 🙏")
    return ConversationHandler.END

# 💬 Отзывы
async def reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✍️ Оставить отзыв", "👀 Посмотреть отзывы"], ["🔙 Назад"]]
    await update.message.reply_text("Что хочешь сделать с отзывами:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def review_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пришли текст, фото или видео отзыва 🙏")
    return REVIEW

async def receive_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = f"✍️ Отзыв от @{user.username or 'аноним'}"
    if update.message.photo:
        fid = update.message.photo[-1].file_id
        await context.bot.send_photo(MASTER_CHAT_ID, fid, caption=caption)
        last_reviews.append(('photo', fid, caption))
    elif update.message.video:
        fid = update.message.video.file_id
        await context.bot.send_video(MASTER_CHAT_ID, fid, caption=caption)
        last_reviews.append(('video', fid, caption))
    elif update.message.text:
        last_reviews.append(('text', update.message.text, caption))
        await context.bot.send_message(MASTER_CHAT_ID, f"{caption}\n\n{update.message.text}")
    else:
        await update.message.reply_text("Формат не поддерживается 😢")
        return ConversationHandler.END
    if len(last_reviews) > 10:
        last_reviews.pop(0)
    await update.message.reply_text("Спасибо за отзыв 🌟")
    return ConversationHandler.END

async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not last_reviews:
        await update.message.reply_text("Пока нет отзывов. Будь первым!")
        return
    await update.message.reply_text("🗂 Это крайние 10 отзывов:")
    for kind, content, caption in last_reviews:
        if kind == 'photo':
            await update.message.reply_photo(content, caption=caption)
        elif kind == 'video':
            await update.message.reply_video(content, caption=caption)
        elif kind == 'text':
            await update.message.reply_text(f"{caption}\n\n{content}")

# 🤝 Поддержка
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💚 Хочешь поддержать проект?\n\n"
        "📲 Перевод: *+7 912 852-81-81*\n"
        "_Сбербанк / Т-Банк_\n\n"
        "или приходи на чайную церемонию 🐉",
        parse_mode="Markdown"
    )

# ⏰ Напоминание
async def reminder_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Через сколько минут напомнить тебе сделать выдох или попить чай? 🍵")
    return REMIND

async def send_later(chat_id, delay, bot):
    await asyncio.sleep(delay)
    await bot.send_message(chat_id=chat_id, text="🍵 Время на чай или глубокий выдох ☁️")

async def reminder_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = int(update.message.text)
        await update.message.reply_text(f"⏳ Хорошо, напомню через {m} минут 🍵")
        asyncio.create_task(send_later(update.effective_chat.id, m * 60, context.bot))
    except:
        await update.message.reply_text("Укажи число минут, пожалуйста 🙏")
    return ConversationHandler.END

# 🔙 Назад
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start(update, context)

# ❓ Неизвестные
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял тебя 🙃 Лучше нажми кнопку ниже")

# ▶️ MAIN
def main():
    # Запускаем Flask сервер в отдельном потоке, чтобы слушать порт 8080
    threading.Thread(target=run_flask).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Записаться") | filters.Regex("📅 Записаться"), sign_up)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_place)],
            COMMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comments)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("✍️ Оставить отзыв"), review_entry)],
        states={REVIEW: [MessageHandler(filters.ALL, receive_review)]},
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("✉️ Оставить записку"), note_entry)],
        states={NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_note)]},
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("⏰ Напоминание"), reminder_set)],
        states={REMIND: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_wait)]},
        fallbacks=[]
    ))

    app.add_handler(MessageHandler(filters.Regex("🧘 О практике"), practice))
    app.add_handler(MessageHandler(filters.Regex("💬 Отзывы"), reviews))
    app.add_handler(MessageHandler(filters.Regex("👀 Посмотреть отзывы"), show_reviews))
    app.add_handler(MessageHandler(filters.Regex("🤝 Поддержать проект"), support))
    app.add_handler(MessageHandler(filters.Regex("🔙 Назад"), back_to_menu))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.add_handler(MessageHandler(filters.TEXT, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()
