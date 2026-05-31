"""
Smart Study Hub Bot — Telegram bot for @SmartStudyHub
Features: Scheduled study tips, AI-generated quizzes, manual triggers
AI: Google Gemini (free tier — no credit card needed)
"""

import os
import json
import logging
import httpx
from datetime import time
from telegram import Update, Poll
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

TELEGRAM_TOKEN  = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID      = os.environ["TELEGRAM_CHANNEL_ID"]
GEMINI_API_KEY  = os.environ["GEMINI_API_KEY"]
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
    if GEMINI_API_KEY else ""
)

# ── AI helper ─────────────────────────────────────────────────────────────────

async def ask_gemini(prompt: str) -> str:
    """Call Gemini 2.0 Flash and return text response."""
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 600, "temperature": 0.8},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=body)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


async def generate_study_tip(topic: str = "") -> str:
    topic_line = f"Topic: {topic}" if topic else "Pick any useful study skill or learning technique."
    prompt = f"""You are a study coach for a Telegram channel called Smart Study Hub.
{topic_line}

Write a SHORT, engaging study tip post (max 200 words).
Format it with:
- A punchy emoji opener
- A bold headline (use * for bold in Telegram)
- 3–5 bullet points using emojis
- A motivating sign-off line
- Relevant hashtags at the end (3–5 max)

Write in a friendly, encouraging tone suitable for students.
"""
    return await ask_gemini(prompt)


async def generate_quiz(topic: str = "") -> dict:
    topic_line = f"Topic: {topic}" if topic else "Pick any interesting study/science/history topic."
    prompt = f"""You are creating a quiz for a student Telegram channel called Smart Study Hub.
{topic_line}

Return ONLY valid JSON (no explanation, no markdown, no backticks) in this exact structure:
{{
  "question": "Your question here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_index": 0,
  "explanation": "Brief 1-sentence explanation of why the answer is correct."
}}

Rules:
- Question should be educational and interesting
- correct_index is 0-based index of the correct option in the options array
- Keep each option under 100 characters
- Explanation is friendly and adds value
"""
    raw = await ask_gemini(prompt)
    raw = raw.strip().strip("```json").strip("```").strip()
    return json.loads(raw)


# ── Scheduled jobs ────────────────────────────────────────────────────────────

async def job_daily_tip(context: ContextTypes.DEFAULT_TYPE):
    log.info("Running scheduled study tip...")
    try:
        tip = await generate_study_tip()
        await context.bot.send_message(chat_id=CHANNEL_ID, text=tip)
        log.info("Study tip posted.")
    except Exception as e:
        log.error(f"Failed to post tip: {e}")


async def job_weekly_quiz(context: ContextTypes.DEFAULT_TYPE):
    log.info("Running scheduled quiz...")
    try:
        quiz = await generate_quiz()
        await context.bot.send_poll(
            chat_id=CHANNEL_ID,
            question=quiz["question"],
            options=quiz["options"],
            type=Poll.QUIZ,
            correct_option_id=quiz["correct_index"],
            explanation=quiz["explanation"],
            is_anonymous=True,
            open_period=86400,
        )
        log.info("Quiz posted.")
    except Exception as e:
        log.error(f"Failed to post quiz: {e}")


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Smart Study Hub Bot is running!\n\n"
        "Commands:\n"
        "/tip — Post a study tip now\n"
        "/tip <topic> — Post a tip on a specific topic\n"
        "/quiz — Post a quiz now\n"
        "/quiz <topic> — Post a quiz on a specific topic\n"
        "/status — Check bot status"
    )


async def cmd_tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else ""
    msg = await update.message.reply_text("✍️ Generating study tip...")
    try:
        tip = await generate_study_tip(topic)
        await context.bot.send_message(chat_id=CHANNEL_ID, text=tip)
        await msg.edit_text("✅ Study tip posted to the channel!")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")


async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else ""
    msg = await update.message.reply_text("🧠 Generating quiz...")
    try:
        quiz = await generate_quiz(topic)
        await context.bot.send_poll(
            chat_id=CHANNEL_ID,
            question=quiz["question"],
            options=quiz["options"],
            type=Poll.QUIZ,
            correct_option_id=quiz["correct_index"],
            explanation=quiz["explanation"],
            is_anonymous=True,
            open_period=86400,
        )
        await msg.edit_text("✅ Quiz posted to the channel!")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢 Bot is online\n"
        f"📢 Channel: {CHANNEL_ID}\n"
        "⏰ Daily tip: 9:00 AM UTC\n"
        "📅 Weekly quiz: Every Monday 10:00 AM UTC\n"
        "🤖 AI: Gemini 2.0 Flash (free)"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("tip",    cmd_tip))
    app.add_handler(CommandHandler("quiz",   cmd_quiz))
    app.add_handler(CommandHandler("status", cmd_status))

    # Daily tip — every day at 09:00 UTC
    app.job_queue.run_daily(
        job_daily_tip,
        time=time(hour=9, minute=0),
        name="daily_tip",
    )

    # Weekly quiz — every Monday at 10:00 UTC
    app.job_queue.run_daily(
        job_weekly_quiz,
        time=time(hour=10, minute=0),
        days=(0,),  # 0 = Monday
        name="weekly_quiz",
    )

    log.info("Smart Study Hub Bot started. Polling...")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
