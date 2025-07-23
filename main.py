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
TOKEN = "7436013012:AAFyD5YEYS7toek2quD8P7N71lmiYz_RwtY"

# 📜 Цитаты чайного пьяницы
TEA_QUOTES = [
    "🍵 «Пей чай, и всё само расставится по местам.»",
    "🍵 «Чай не решает проблемы, но делает их теплее.»",
    "🍵 «Когда не знаешь, что делать — завари чай.»",
    "🍵 «Чай не торопит. В нём вечность на кончике пиалы.»",
    "🍵 «Даже молчание со вкусом чая становится разговором.»",
    "🍵 «Ум успокаивается, когда в руках горячая пиала.»",
    "🍵 «Жизнь не в суете. Жизнь в чае.»",
    "🍵 «Каждая церемония — возвращение домой.»",
    "🍵 «Тот, кто пьёт чай, уже не спешит.»",
    "🍵 «Чайный пьяница — тот, кто трезво видит с закрытыми глазами.»",
    "🍵 «Пей чай, пока мысли не растворятся, как осадок в глине.»",
    "🍵 «Гвозди под ногами, чай в ладонях, и ты в себе.»",
    "🍵 «Тишина – это тоже вкус, просто редкий.»",
    "🍵 «Ушёл в пуэр — не ищите.»",
    "🍵 «В этом мире больше вкусов, чем решений.»",
    "🍵 «Тот, кто чувствует чай, не нуждается в словах.»"
]

# 🧘 Состояния
NAME, DATE, PLACE, COMMENTS, PHONE, REMIND = range(6)

# 🌐 Flask сервер
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running"
def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ▶️ Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.send_message(
        chat_id=MASTER_CHAT_ID,
        text=f"👋 @{user.username or 'гость'} запустил бота."
    )
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

# 🌿 О практике
async def practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 «Гвозди и Листья» — это пространство, где ты можешь:\n\n"
        "🔩 Постоять на гвоздях — почувствовать себя\n"
        "🍵 Выпить редкий китайский чай в тишине\n"
        "💆 Поставить банки — мягко отдать напряжение\n"
        "🧘 Поболтать о важном или помолчать о главном\n"
        "🏕 Приехать на выездную церемонию в лесу"
    )

# 📅 Запись
async def sign_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как тебя зовут?")
    return NAME
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Когда удобно? (дата/время)")
    return DATE
async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    await update.message.reply_text("Где удобно? (у меня / у тебя / природа)")
    return PLACE
async def get_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text
    await update.message.reply_text("Есть пожелания или мысли?")
    return COMMENTS
async def get_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comments"] = update.message.text
    await update.message.reply_text("Оставь номер телефона для связи 📱")
    return PHONE
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
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
    await context.bot.send_message(chat_id=MASTER_CHAT_ID, text=text, parse_mode="Markdown")
    await update.message.reply_text("Спасибо, скоро свяжусь 🙌")
    return ConversationHandler.END

# ⏰ Напоминание
async def reminder_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Через сколько минут напомнить тебе сделать вдох или попить чай? 🍵")
    return REMIND
async def send_later(chat_id, delay, bot):
    await asyncio.sleep(delay)
    await bot.send_message(chat_id=chat_id, text="🍵 Время на чай или выдох ☁️")
async def reminder_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        minutes = int(update.message.text)
        await update.message.reply_text(f"⏳ Окей, напомню через {minutes} минут 🍵")
        asyncio.create_task(send_later(update.effective_chat.id, minutes * 60, context.bot))
    except:
        await update.message.reply_text("Пожалуйста, укажи число минут 🙏")
    return ConversationHandler.END

# 💌 Записка
async def note_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши записку — я передам её Тимуру 📬")
    return 5
async def receive_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    note = update.message.text
    await context.bot.send_message(
        MASTER_CHAT_ID,
        f"📩 Записка от @{user.username or 'аноним'}:\n\n{note}"
    )
    await update.message.reply_text("Записка отправлена 🙏")
    return ConversationHandler.END

# 🍵 Цитата
async def tea_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(TEA_QUOTES)
    await update.message.reply_text(quote)

# 🤝 Поддержка
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💚 Хочешь поддержать проект?\n\n"
        "📲 Перевод: *+7 912 852‑81‑81*\n"
        "_Сбербанк / Т-Банк_ или приходи на чайную церемонию 🐉",
        parse_mode="Markdown"
    )

# ❓ Неизвестное
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я не понял 🤔 Нажми кнопку ниже")

# ▶️ Запуск
def main():
    threading.Thread(target=run_flask).start()
    app_ = ApplicationBuilder().token(TOKEN).build()

    app_.add_handler(CommandHandler("start", start))

    # Запись
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

    # Напоминание
    app_.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("⏰ Напоминание"), reminder_set)],
        states={REMIND: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_wait)]},
        fallbacks=[]
    ))

    # Записка
    app_.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("💌 Оставить записку"), note_entry)],
        states={5: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_note)]},
        fallbacks=[]
    ))

    app_.add_handler(MessageHandler(filters.Regex("🧘 О практике"), practice))
    app_.add_handler(MessageHandler(filters.Regex("🍵 Цитата дня от чайного пьяницы"), tea_quote))
    app_.add_handler(MessageHandler(filters.Regex("🤝 Поддержать проект"), support))
    app_.add_handler(MessageHandler(filters.COMMAND, unknown))
    app_.add_handler(MessageHandler(filters.TEXT, unknown))

    app_.run_polling()

if __name__ == "__main__":
    main()
