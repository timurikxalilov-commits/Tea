from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import asyncio
from flask import Flask
import threading
import random

# 🔧 Конфигурация
MASTER_CHAT_ID = 5225197085
TOKEN = "7436013012:AAFmxpR03fQC_VOj_pWKhyfaK43FohaPNoE"

# Flask сервер для Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running"
def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 🔢 Состояния
NAME, DATE, PLACE, COMMENTS, PHONE, NOTE, REMIND = range(7)

# 🍵 Цитаты
TEA_QUOTES = [
    "Когда кипяток встречает чай — тишина говорит громче слов.",
    "Пей чай так, будто времени нет.",
    "Настоящий вкус приходит не к тем, кто спешит.",
    "Чашка — портал в другой мир.",
    "Мир не нужно понимать, достаточно налить ещё одну пиалу.",
    "Смотри, как чай танцует — и стань водой.",
    "Время — это просто температура заварки.",
    "Отрешись от суеты, как чаинки от пакетика.",
    "Даже сильный ветер не остудит чайного сердца.",
    "Чай не задаёт вопросов. Он просто лечит.",
    # добавь сюда ещё 90 по желанию
] + [f"🫖 Мудрость #{i}: будь как чай, не как кофе." for i in range(11, 101)]

# ▶️ Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🧘 О практике", "📅 Записаться"],
        ["🍵 Цитата дня от чайного пьяницы", "⏰ Напоминание"],
        ["✉️ Оставить записку", "🤝 Поддержать проект"]
    ]
    await context.bot.send_message(
        chat_id=MASTER_CHAT_ID,
        text=f"👤 @{update.effective_user.username or 'пользователь'} запустил бота!"
    )
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

# ✉️ Записка
async def note_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оставь записку, и она будет передана лично 📬")
    return NOTE
async def receive_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = f"📩 *Записка от @{user.username or 'аноним'}:*\n\n{update.message.text}"
    await context.bot.send_message(MASTER_CHAT_ID, msg, parse_mode="Markdown")
    await update.message.reply_text("Спасибо, записка доставлена 🙏")
    return ConversationHandler.END

# 🤝 Поддержка
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💚 Хочешь поддержать проект?\n\n"
        "📲 Перевод: *+7 912 852-81-81*\n"
        "_Сбербанк / Т-Банк_\n\n"
        "или приходи на чайную церемонию 🐉",
        parse_mode="Markdown"
    )

# 🍵 Цитата дня
async def tea_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(TEA_QUOTES)
    await update.message.reply_text(f"🍵 Цитата дня от чайного пьяницы:\n\n“{quote}”")

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

# Неизвестное
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял тебя 🙃 Лучше нажми кнопку ниже")

# ▶️ MAIN
def main():
    threading.Thread(target=run_flask).start()
    app_ = ApplicationBuilder().token(TOKEN).build()

    app_.add_handler(CommandHandler("start", start))
    app_.add_handler(MessageHandler(filters.Regex("🧘 О практике"), practice))
    app_.add_handler(MessageHandler(filters.Regex("🤝 Поддержать проект"), support))
    app_.add_handler(MessageHandler(filters.Regex("🍵 Цитата дня от чайного пьяницы"), tea_quote))

    # Заявка
    app_.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("📅 Записаться"), sign_up)],
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
    app_.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("✉️ Оставить записку"), note_entry)],
        states={NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_note)]},
        fallbacks=[]
    ))

    # Напоминание
    app_.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("⏰ Напоминание"), reminder_set)],
        states={REMIND: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_wait)]},
        fallbacks=[]
    ))

    app_.add_handler(MessageHandler(filters.COMMAND, unknown))
    app_.add_handler(MessageHandler(filters.TEXT, unknown))

    app_.run_polling()

if __name__ == "__main__":
    main()
