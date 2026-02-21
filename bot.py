import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue

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
    chat_id = update.effective_chat.id
    scores[chat_id] = 0
    context.chat_data['round'] = 1
    await next_round(context, chat_id)

async def next_round(context: ContextTypes.DEFAULT_TYPE, chat_id):
    round_num = context.chat_data['round']
    if round_num > 5:
        final = scores[chat_id]
        best = records.get(chat_id, 0)
        if final > best:
            records[chat_id] = final
            best = final
        await context.bot.send_message(chat_id=chat_id, text=f"🏁 Partita finita!\n\nPunteggio: {final}\nRecord: {best}")
        return

    target = random.choice(["RED", "BLUE", "GREEN"])
    context.chat_data['target'] = target

    text_map = {
        "RED": "🔴 TAPPA IL ROSSO!",
        "BLUE": "🔵 TAPPA IL BLU!",
        "GREEN": "🟢 TAPPA IL VERDE!"
    }

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Round {round_num}/5\n\n{text_map[target]}",
        reply_markup=keyboard()
    )

    # programma il round successivo dopo 4 secondi
    context.job_queue.run_once(next_round_job, 4, chat_id=chat_id)

async def next_round_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    context.chat_data['round'] += 1
    await next_round(context, chat_id)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    choice = query.data
    await query.answer()

    target = context.chat_data.get('target')
    if target is None:
        return  # se non c'è round attivo, ignora

    if choice == target:
        scores[chat_id] += 10
        await context.bot.send_message(chat_id=chat_id, text="✅ Corretto! +10")
    else:
        scores[chat_id] -= 5
        await context.bot.send_message(chat_id=chat_id, text="❌ Sbagliato! -5")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not records:
        await update.message.reply_text("Nessun punteggio ancora!")
        return
    ranking = sorted(records.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "🏆 Classifica Globale:\n\n"
    for i, (_, score) in enumerate(ranking, 1):
        text += f"{i}. {score} punti\n"
    await update.message.reply_text(text)

# -----------------------------------------
# Sezione Render: mantiene il bot sempre attivo
# -----------------------------------------
if __name__ == "__main__":
    import nest_asyncio
    import asyncio
    nest_asyncio.apply()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot avviato e in ascolto su Render...")
    asyncio.get_event_loop().run_forever()
