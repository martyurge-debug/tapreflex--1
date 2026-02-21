import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8554013325:AAHV8N6sXezW2YKhNtD4Z5jQDQn5outH-zw"

scores = {}
records = {}

def keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔴", callback_data="RED"),
            InlineKeyboardButton("🔵", callback_data="BLUE"),
            InlineKeyboardButton("🟢", callback_data="GREEN"),
        ]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Benvenuto in Tap Reflex ⚡\n\nPremi /play per iniziare!")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    scores[user] = 0
    await next_round(context, user, 1)

async def next_round(context, user, round_num):
    target = random.choice(["RED", "BLUE", "GREEN"])
    context.user_data["target"] = target
    context.user_data["round"] = round_num

    text_map = {
        "RED": "🔴 TAPPA IL ROSSO!",
        "BLUE": "🔵 TAPPA IL BLU!",
        "GREEN": "🟢 TAPPA IL VERDE!"
    }

    await context.bot.send_message(
        chat_id=user,
        text=f"Round {round_num}/5\n\n{text_map[target]}",
        reply_markup=keyboard()
    )

    import asyncio
    await asyncio.sleep(4)

    if context.user_data.get("round") == round_num:
        await context.bot.send_message(chat_id=user, text="⏱ Tempo scaduto!")
        await process_round(context, user, None)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user.id
    choice = query.data

    await query.answer()
    await process_round(context, user, choice)

async def process_round(context, user, choice):
    round_num = context.user_data.get("round")

    if choice == context.user_data.get("target"):
        scores[user] += 10
        await context.bot.send_message(chat_id=user, text="✅ Corretto! +10")
    elif choice is not None:
        scores[user] -= 5
        await context.bot.send_message(chat_id=user, text="❌ Sbagliato! -5")

    if round_num < 5:
        await next_round(context, user, round_num + 1)
    else:
        final = scores[user]
        best = records.get(user, 0)
        if final > best:
            records[user] = final
            best = final
        await context.bot.send_message(chat_id=user, text=f"🏁 Partita finita!\n\nPunteggio: {final}\nRecord: {best}")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not records:
        await update.message.reply_text("Nessun punteggio ancora!")
        return

    ranking = sorted(records.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "🏆 Classifica Globale:\n\n"
    for i, (_, score) in enumerate(ranking, 1):
        text += f"{i}. {score} punti\n"
    await update.message.reply_text(text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()
