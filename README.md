# 🤖 Smart Study Hub — Telegram Bot

Auto-posts study tips and quizzes to your Telegram channel using AI.

---

## Features

- 📅 **Daily study tips** at 9:00 AM UTC (AI-generated)
- 🧠 **Weekly quizzes** every Monday at 10:00 AM UTC (native Telegram quiz polls)
- 💬 **Manual commands** — trigger posts anytime from your phone
- 🎯 **Topic-specific** — ask for a tip or quiz on any subject

---

## Setup (Step by Step)

### Step 1 — Create your Telegram Bot

1. Open Telegram → search **@BotFather**
2. Send `/newbot`
3. Give it a name: `Smart Study Hub Bot`
4. Give it a username: `smart_study_hub_bot` (must end in `bot`)
5. Copy the **token** BotFather gives you — save it

### Step 2 — Make the bot an admin of your channel

1. Open your channel → Settings → Administrators
2. Add your bot as admin
3. Give it permission to **Post Messages**

### Step 3 — Get your Anthropic API key

1. Go to https://console.anthropic.com
2. Create an account (free)
3. Go to API Keys → Create Key
4. Copy the key — save it
> You get $5 free credits on signup. Each tip/quiz costs ~$0.001. That's ~5,000 posts free.

### Step 4 — Deploy for free on Railway

1. Push this folder to a GitHub repo (public or private)
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Select your repo
4. Go to **Variables** tab and add:
   ```
   TELEGRAM_BOT_TOKEN = your_token_from_step_1
   TELEGRAM_CHANNEL_ID = @YourChannelUsername
   ANTHROPIC_API_KEY = your_key_from_step_3
   ```
5. Railway will build and deploy automatically
6. Bot is now running 24/7 for free ✅

---

## Manual Commands

Send these to your bot in a private chat (not the channel):

| Command | What it does |
|---|---|
| `/start` | Show help |
| `/tip` | Post a random study tip now |
| `/tip memory techniques` | Post a tip about memory techniques |
| `/quiz` | Post a random quiz now |
| `/quiz biology` | Post a biology quiz |
| `/status` | Check if bot is running |

---

## Changing the Schedule

In `bot.py`, find these lines and adjust the time (UTC):

```python
# Daily tip — change hour/minute
app.job_queue.run_daily(job_daily_tip, time=time(hour=9, minute=0))

# Weekly quiz — days=(0,) means Monday. 1=Tue, 2=Wed... 6=Sun
app.job_queue.run_daily(job_weekly_quiz, time=time(hour=10, minute=0), days=(0,))
```

---

## Running Locally (for testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in your values
cp .env.example .env
nano .env

# Load env and run
export $(cat .env | xargs) && python bot.py
```

---

## Free Tier Limits

| Service | Free Limit |
|---|---|
| Telegram Bot API | Unlimited |
| Railway | 500 hours/month (~21 days) |
| Render | Always-on free tier (may sleep) |
| Anthropic | $5 credits (~5,000 posts) |

> **Tip**: Railway's free tier resets monthly. For truly always-on free hosting, use **Fly.io** with their free machines tier.
