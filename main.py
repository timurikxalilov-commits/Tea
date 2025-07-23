from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import asyncio

# 🔧 Твои данные
MASTER_CHAT_ID = 5225197085
TOKEN = "7436013012:AAHq7FIRs5kJhaRIPkwV0bTF83-WdMPe4LY"

# 💾 Хранилище отзывов (10 последних)
last_reviews = []

# 📌 Состояния
NAME, DATE, PLACE, COMMENTS, PHONE, REVIEW, REMIND, NOTE = range(8)

# ▶️ Старт
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
        "🌿 Добро пожаловать в «Гвозди и Листья» — пространство для глубины, покоя и присутствия:\n\n"
        "🔩 Стояние на гвоздях — через боль к свободе\n"
        "🍵 Китайский чай (пуэр, улун, да хун пао) — как медитация\n"
        "🔥 Банки — древняя телесная практика\n"
        "🌀 Душевные разговоры — по-настоящему\n"
        "🏕 Выездные церемонии в лесу или на природе\n\n"
        "Ты можешь записаться, оставить записку или просто побыть рядом 🌿"
    )

# 📅 Заявка
async def sign_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как тебя зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Когда удобно провести сессию? (дата/время)")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date'] = update.message.text
    await update.message.reply_text("Где провести? (дома, на природе или у меня в гостях?)")
    return PLACE

async def get_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['place'] = update.message.text
    await update.message.reply_text("Есть пожелания или вопросы?")
    return COMMENTS

async def get_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['comments'] = update.message.text
    await update.message.reply_text("Оставь, пожалуйста, номер телефона для связи 📱")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    user = update.message.from_user

    text = (
        f"📥 *Новая заявка:*\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"📅 Время: {context.user_data['date']}\n"
        f"📍 Место: {context.user_data['place']}\n"
        f"💬 Пожелания: {context.user_data['comments']}\n"
        f"📱 Телефон: {context.user_data['phone']}\n"
        f"Telegram: @{user.username or 'нет'}"
    )
    await context.bot.send_message(chat_id=MASTER_CHAT_ID, text=text, parse_mode="Markdown")
    await update.message.reply_text("Заявка отправлена! Я скоро с тобой свяжусь 🙌")
    return ConversationHandler.END

# 💬 Отзывы
async def reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["✍️ Оставить отзыв", "👀 Посмотреть отзывы"],
        ["🔙 Назад"]
    ]
    await update.message.reply_text(
        "Выбери, что хочешь сделать с отзывами:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def review_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пришли свой отзыв: текст, фото или видео 🙏")
    return REVIEW

async def receive_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = f"✍️ Новый отзыв от @{user.username or 'аноним'}"
    if update.message.photo:
        fid = update.message.photo[-1].file_id
        await context.bot.send_photo(MASTER_CHAT_ID, fid, caption=caption)
        last_reviews.append(('photo', fid, caption))
    elif update.message.video:
        fid = update.message.video.file_id
        await context.bot.send_video(MASTER_CHAT_ID, fid, caption=caption)
        last_reviews.append(('video', fid, caption))
    elif update.message.text:
        await context.bot.send_message(MASTER_CHAT_ID, f"{caption}\n\n{update.message.text}")
        last_reviews.append(('text', update.message.text, caption))
    else:
        await update.message.reply_text("Формат не поддерживается 😢")
        return ConversationHandler.END

    if len(last_reviews) > 10:
        last_reviews.pop(0)
    await update.message.reply_text("Спасибо за отзыв! 🌟")
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
        "📲 Перевод по номеру: *+7 912 852-81-81*\n"
        "_Сбербанк / Т-Банк_ ну или за чайной церемонией 🐲",
        parse_mode="Markdown"
    )

# ✉️ Оставить записку
async def note_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши свою записку мастеру, и я передам её лично 📬")
    return NOTE

async def receive_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text or "[Нет текста]"
    msg = f"📩 *Записка от @{user.username or 'аноним'}:*\n\n{text}"
    await context.bot.send_message(chat_id=MASTER_CHAT_ID, text=msg, parse_mode="Markdown")
    await update.message.reply_text("Спасибо, записка отправлена! 🙏")
    return ConversationHandler.END

# ⏰ Напоминание
async def reminder_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Через сколько минут напомнить тебе попить чай или сделать выдох? 🫖")
    return REMIND

async def reminder_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = int(update.message.text)
        await update.message.reply_text(f"⏳ Ок, напомню через {m} минут 🍵")
        await asyncio.sleep(m * 60)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🍵 Время на чай или глубокий выдох ☁️")
    except:
        await update.message.reply_text("Пожалуйста, укажи число минут.")
    return ConversationHandler.END

# 🔙 Назад
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start(update, context)

# ❓ Неизвестные
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял тебя 🙃 Нажми кнопку ниже!")

# ▶️ Главная
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    signup_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Записаться") | filters.Regex("📅 Записаться"), sign_up)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_place)],
            COMMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comments)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[]
    )

    review_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("✍️ Оставить отзыв"), review_entry)],
        states={ REVIEW: [MessageHandler(filters.ALL, receive_review)] },
        fallbacks=[]
    )

    note_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("✉️ Оставить записку"), note_entry)],
        states={ NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_note)] },
        fallbacks=[]
    )

    remind_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("⏰ Напоминание"), reminder_set)],
        states={ REMIND: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_wait)] },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(signup_conv)
    app.add_handler(review_conv)
    app.add_handler(note_conv)
    app.add_handler(remind_conv)

    app.add_handler(MessageHandler(filters.Regex("🧘 О практике"), practice))
    app.add_handler(MessageHandler(filters.Regex("💬 Отзывы"), reviews))
    app.add_handler(MessageHandler(filters.Regex("👀 Посмотреть отзывы"), show_reviews))
    app.add_handler(MessageHandler(filters.Regex("🤝 Поддержать проект"), support))
    app.add_handler(MessageHandler(filters.Regex("✉️ Оставить записку"), note_entry))
    app.add_handler(MessageHandler(filters.Regex("🔙 Назад"), back_to_menu))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.add_handler(MessageHandler(filters.TEXT, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()
