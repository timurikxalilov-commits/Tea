from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import asyncio
import random

# 🔧 Конфигурация
MASTER_CHAT_ID = 5225197085
TOKEN = "7436013012:AAFmxpR03fQC_VOj_pWKhyfaK43FohaPNoE"

# 📂 Состояния
NAME, DATE, PLACE, COMMENTS, PHONE, NOTE, REMIND = range(7)

# 🍵 Цитаты
tea_quotes = [
    "Чай — это тишина, завёрнутая в аромат.",
    "Пей чай так, как будто ты разговариваешь с пустотой.",
    "Вода знает путь, чай показывает суть.",
    "Настоящий вкус чая — это вкус твоего настроения.",
    "Чашка чая может быть целой вселенной.",
    "Чай — не напиток. Это разговор с духом времени.",
    "Время замедляется, когда пьёшь хороший чай.",
    "Не спеши. Горячая вода любит терпение.",
    "Каждая пьялка — как первое вдохновение.",
    "Чай — это искусство растворяться в простом.",
    # Добавь свои до 100...
]

# 🟢 Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🧘 О практике", "📅 Записаться"],
        ["🍵 Цитата дня от чайного пьяницы"],
        ["⏰ Напоминание", "💌 Оставить записку"],
        ["🤝 Поддержать проект"]
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
    # Уведомление мастеру о запуске
    user = update.effective_user
    await context.bot.send_message(MASTER_CHAT_ID, f"👤 @{user.username or 'Без ника'} запустил бота.")

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

# 💌 Оставить записку
async def note_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оставь записку, и она будет передана лично 📬")
    return NOTE

async def receive_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = f"📩 *Записка от @{user.username or 'аноним'}:*\n\n{update.message.text}"
    await context.bot.send_message(MASTER_CHAT_ID, msg, parse_mode="Markdown")
    await update.message.reply_text("Спасибо, записка доставлена 🙏")
    return ConversationHandler.END

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

# 🍵 Цитата дня
async def tea_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(tea_quotes)
    await update.message.reply_text(f"🧙‍♂️ Чайный пьяница говорит:\n\n“{quote}”")

# ❓ Неизвестное
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял тебя 🙃 Лучше нажми кнопку ниже")

# ▶️ MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Запись
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

    # Записка
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("💌 Оставить записку"), note_entry)],
        states={NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_note)]},
        fallbacks=[]
    ))

    # Напоминание
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("⏰ Напоминание"), reminder_set)],
        states={REMIND: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_wait)]},
        fallbacks=[]
    ))

    app.add_handler(MessageHandler(filters.Regex("🧘 О практике"), practice))
    app.add_handler(MessageHandler(filters.Regex("🍵 Цитата дня от чайного пьяницы"), tea_quote))
    app.add_handler(MessageHandler(filters.Regex("🤝 Поддержать проект"), lambda u, c: u.message.reply_text(
        "💚 Хочешь поддержать проект?\n\n📲 Перевод: *+7 912 852-81-81*\n_Сбербанк / Т-Банк_\n\nили приходи на чайную церемонию 🐉",
        parse_mode="Markdown"
    )))

    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.add_handler(MessageHandler(filters.TEXT, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()
