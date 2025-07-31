import logging
import json
import random
import asyncio
import os
import sys
import re
from datetime import datetime
import pytz

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# === Конфигурация ===
BOT_TOKEN = "8276571944:AAF3ypIPxV-IPJYW-Rr6PiEql8vUONzEGeE"
GROUP_CHAT_ID = -1002444770684
THREAD_ID = 2
ADMIN_ID = 1118647995
REMINDER_HOUR = 20
REMINDER_MINUTE = 50
MSK = pytz.timezone("Europe/Moscow")
USER_DATA_FILE = "subscribers.json"

# === Логи ===
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# === Пользователи ===
def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return []
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

subscribers = load_users()

def escape(text):
    return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', str(text))

# === Шутки ===
JOKES = [
    "⚠️ Скрин актива — это твоя ответственность. Сделай сейчас.",
    "🔔 20:50 МСК. Время скринов. Не пропусти.",
    "🕒 Скрин должен быть сделан точно по времени. Без задержек.",
    "📋 Не забудь: актив фиксируется только сейчас. Сделай скрин.",
    "⏳ Времени мало. Сделай скрин до обновления списка.",
    "📷 Это важно — скрин актива обязателен. Не откладывай.",
    "💡 Ответственность начинается с простого действия. Скринь.",
    "✅ Сделал скрин? Молодец. Пропустил? Никто не узнает, что ты был.",
    "🚨 Скрин — подтверждение твоей активности. Не упусти момент.",
    "📎 Один скрин = одно доказательство. Сейчас важно.",
    "🔍 Никто не заскринит за тебя. Сделай это сам.",
    "📆 Скрин делается не 'когда удобно', а 'когда надо'. Сейчас надо.",
    "🧭 Скрин — ориентир твоей ответственности. Проверь себя.",
    "🕹 Не выключай голову — скринь в нужное время.",
    "🗂 Твоя активность — это твоя репутация. Скрин за неё отвечает.",
    "📣 Тебе напомнили. Осталось только заскринить. Делай.",
    "📶 Связь есть. Telegram работает. Значит, можешь сделать скрин.",
    "📌 Не проспи. Скринить нужно сейчас.",
    "⏰ Уведомление пришло не просто так. Делай скрины.",
    "📤 Скрин — это отчёт, а не формальность.",
    "📑 Без скрина — ты как будто не участвовал.",
    "🧱 Строй доверие — с каждого скрина.",
    "🧾 Скрин — квитанция о твоей активности.",
    "🧨 Отложишь — забудешь. Сделай скрин сразу.",
    "📊 Делай скрин — он многое значит.",
    "📡 Сигнал получен. Скрин зафиксируй.",
    "📝 Успей зафиксировать свой вклад. Скринь.",
    "📈 Скрины важны. Они говорят за тебя.",
    "💬 Ксения Анатольевна будет злиться. Скринь актив быстрее!",
    "🔐 Скрин — твой доступ к доверию.",
    "🎯 Меткий скрин — вовремя сделанный.",
    "🔁 Привычка скринить — это дисциплина.",
    "📸 Сейчас — единственный момент для скрина.",
    "📋 Не забудь. Скрин нужен именно сейчас.",
    "📎 Скрин не откладывают. Его делают.",
    "🧠 Скрин — часть ответственности.",
    "👁 Актив — это видно. Скрин покажет.",
    "🧭 Скрин — твой ориентир. Не сбейся.",
    "💬 Скрин — это не просьба. Это необходимость.",
    "🚧 Без скрина — как без фундамента.",
    "🧩 Скрин — важная часть целого.",
    "🏁 Финальный момент — заскринь и всё.",
    "🚦 Сигнал на старт. Скрин актив.",
    "🛎 Твой сигнал: сделай скрин.",
    "📡 Скрин — фиксатор действия.",
    "📬 Сейчас или никогда. Сделай скрин.",
    "💡 Скрин показывает, что ты не забыл.",
    "🧮 Актив считается. Скрин — подтверждение.",
    "🎬 Вышел в онлайн? Скрин сделал?",
    "⛳ Не дотяни до провала. Скринь вовремя.",
    "📆 В календаре есть точка — 20:50. Скрин.",
    "🧷 Скрин — твоя отметка 'я был'.",
    "🏗 Скрин укрепляет доверие.",
    "🕵️‍♂️ Скрин доказывает твоё участие.",
    "🧭 Ответственный — значит скринил.",
    "📢 Не забывай. Скрин — как отчёт.",
    "💥 Скрин — простой шаг. Но важный.",
    "💼 Сделай дело. Скринь.",
    "📱 ЛС открыт. Сделай скрин.",
    "🎓 Быть активным — значит скринить.",
]

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in subscribers:
        subscribers.append(user.id)
        save_users(subscribers)
        await context.bot.send_message(user.id, "✅ *Ты подписался на напоминания!*", parse_mode="MarkdownV2")
    else:
        await context.bot.send_message(user.id, "😎 *Ты уже подписан*", parse_mode="MarkdownV2")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отписаться", callback_data="stop")],
        [InlineKeyboardButton("📋 Список подписчиков", switch_inline_query_current_chat="/list")],
        [InlineKeyboardButton("📢 Рассылка (только для админа)", callback_data="broadcast")] if user.id == ADMIN_ID else []
    ])
    await context.bot.send_message(user.id, "📌 Команды доступны:", reply_markup=keyboard)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in subscribers:
        subscribers.remove(user.id)
        save_users(subscribers)
        await context.bot.send_message(user.id, "❌ *Ты отписался от напоминаний*", parse_mode="MarkdownV2")
    else:
        await context.bot.send_message(user.id, "ℹ️ Ты и так не подписан", parse_mode="MarkdownV2")

async def list_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in ("group", "supergroup"):
        if getattr(update.message, "message_thread_id", None) != THREAD_ID:
            return
    lines = ["📄 *Подписчики:*"]
    if not subscribers:
        lines.append("_Список пуст_")
    else:
        for uid in subscribers:
            try:
                user = await context.bot.get_chat(uid)
                if user.username:
                    lines.append(f"• @{escape(user.username)}")
                elif user.first_name:
                    lines.append(f"• [{escape(user.first_name)}](tg://user?id={uid})")
                else:
                    lines.append(f"• [профиль](tg://user?id={uid})")
            except:
                lines.append(f"• [профиль](tg://user?id={uid})")
    await context.bot.send_message(update.effective_chat.id, escape("\n".join(lines)), parse_mode="MarkdownV2")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "stop":
        await stop(update, context)
    elif query.data == "broadcast" and query.from_user.id == ADMIN_ID:
        await query.message.reply_text("✍️ Введите сообщение для рассылки:")
        context.user_data["awaiting_broadcast"] = True

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("awaiting_broadcast") and user_id == ADMIN_ID:
        text = update.message.text
        context.user_data["awaiting_broadcast"] = False
        success = 0
        fail = 0
        for uid in subscribers:
            try:
                await context.bot.send_message(uid, text)
                success += 1
            except:
                fail += 1
        await update.message.reply_text(f"✅ Успешно: {success}\n❌ Ошибок: {fail}")

async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(MSK)
    if now.hour == REMINDER_HOUR and now.minute == REMINDER_MINUTE:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=THREAD_ID,
            text="20:50 МСК 🔔 Время делать скрин! Все получили напоминание в лс."
        )
        for uid in subscribers:
            try:
                await context.bot.send_message(uid, random.choice(JOKES))
            except:
                continue

async def send_group_intro(bot):
    bot_info = await bot.get_me()
    bot_link = f"https://t.me/{bot_info.username}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Подписаться в ЛС", url=bot_link)]
    ])
    await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            "👋 Привет! Я бот, который будет напоминать тебе делать скрины актива.\n"
            "📅 Напоминание придёт тебе в ЛС и сюда — в эту тему.\n"
            "🔔 Не забудь включить уведомления в Telegram!\n\n"
            "👉 Нажми кнопку ниже, чтобы подписаться:"
        ),
        reply_markup=keyboard
    )

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("list", list_subs))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.job_queue.run_repeating(reminder_job, interval=60, first=10)

    await app.bot.delete_webhook(drop_pending_updates=True)
    await send_group_intro(app.bot)

    logging.info("✅ Бот запущен и готов к работе.")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())



