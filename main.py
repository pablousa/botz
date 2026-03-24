import os
import logging
import random
import string
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set.")

# Countries mapped to (min_value, max_value) based on economic tier
COUNTRIES = {
    # Tier 1 — High value
    "USA":            (800, 9999),
    "Canada":         (700, 8500),
    "Australia":      (700, 8000),
    "United Kingdom": (700, 8500),
    "Germany":        (650, 8000),
    "Switzerland":    (800, 9999),
    "Norway":         (700, 8500),
    "Denmark":        (700, 8000),
    "Sweden":         (700, 8000),
    "Netherlands":    (650, 7500),
    "Belgium":        (650, 7500),
    "Austria":        (650, 7500),
    "Finland":        (650, 7500),
    "France":         (650, 7500),
    "Japan":          (600, 7000),
    "New Zealand":    (600, 7000),
    "Singapore":      (700, 8500),
    "UAE":            (750, 9000),
    "Saudi Arabia":   (700, 8500),
    # Tier 2 — Mid-high value
    "South Korea":    (400, 5000),
    "Italy":          (400, 4500),
    "Spain":          (350, 4000),
    "Portugal":       (300, 3500),
    "Greece":         (300, 3000),
    "Hungary":        (250, 3000),
    "Czech Republic": (300, 3500),
    "Poland":         (300, 3500),
    # Tier 3 — Mid value
    "Brazil":         (150, 2000),
    "Mexico":         (150, 1800),
    "Argentina":      (120, 1500),
    "Chile":          (150, 1800),
    "Colombia":       (100, 1400),
    "Turkey":         (100, 1400),
    "Romania":        (150, 1600),
    "Ukraine":        (100, 1200),
    "China":          (200, 2500),
    "Russia":         (150, 2000),
    # Tier 4 — Lower value
    "India":          (50,  900),
    "Indonesia":      (50,  800),
    "Philippines":    (50,  700),
    "Vietnam":        (50,  700),
    "Thailand":       (80,  900),
    "Malaysia":       (80,  1000),
    "Pakistan":       (50,  600),
    "Egypt":          (50,  600),
    "Nigeria":        (50,  600),
    "Kenya":          (50,  500),
    "South Africa":   (80,  900),
    "Peru":           (80,  800),
    "Venezuela":      (50,  700),
}

CONNECTION_TYPES = ["VPN", "Proxy", "Normal"]

USERNAME_PREFIXES = [
    "Dark", "Pro", "Shadow", "Ultra", "Night", "Ghost", "Hyper", "Storm",
    "Neon", "Alpha", "Omega", "Cyber", "Stealth", "Blaze", "Frost", "Void",
    "Rogue", "Sniper", "Viper", "Eagle", "Phantom", "Swift", "Iron", "Toxic",
    "Turbo", "Razor", "Savage", "Silent", "Rapid", "Deadly", "Elite", "Chaos",
    "Crimson", "Arctic", "Lunar", "Solar", "Cosmic", "Atomic", "Digital", "Nexus"
]

USERNAME_SUFFIXES = [
    "X", "Pro", "King", "Master", "Hunter", "Wolf", "Fox", "Dragon", "Hawk",
    "Blade", "Force", "Strike", "Shot", "Fire", "Ice", "Star", "Ninja",
    "Warrior", "Legend", "Titan", "Venom", "Storm", "Fury", "Rage", "Ace",
    "Byte", "Pixel", "Node", "Core", "Zero", "One", "Bot", "Dev", "Hacker"
]

SIGNATURE = "━━━━━━━━━━━━━━━\nZeus Holding • Monitoring System"

# Tracks which users have ever activated /logs (one-time lock)
activated_users: set[int] = set()

# Holds the running asyncio task per chat_id
active_tasks: dict[int, asyncio.Task] = {}


def generate_username() -> str:
    prefix = random.choice(USERNAME_PREFIXES)
    suffix = random.choice(USERNAME_SUFFIXES)
    number = random.choice(["", str(random.randint(1, 999)), str(random.randint(1, 99))])
    separator = random.choice(["", "_", ""])
    return f"{prefix}{separator}{suffix}{number}"


def generate_key() -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=30))


def generate_log_message() -> str:
    username = generate_username()
    country = random.choice(list(COUNTRIES.keys()))
    min_val, max_val = COUNTRIES[country]
    value = random.randint(min_val, max_val)
    connection = random.choice(CONNECTION_TYPES)
    key = generate_key()

    connection_emoji = {"VPN": "🔒", "Proxy": "🔁", "Normal": "🌐"}[connection]

    return (
        f"👤 User: {username}\n"
        f"🌍 Country: {country}\n"
        f"{connection_emoji} Connection: {connection}\n"
        f"🔑 Key: {key}\n"
        f"💸 Value: ${value}\n\n"
        f"{SIGNATURE}"
    )


async def send_logs_loop(chat_id: int, bot) -> None:
    while True:
        delay = random.uniform(20 * 60, 30 * 60)
        await asyncio.sleep(delay)
        try:
            msg = generate_log_message()
            await bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logger.warning(f"Failed to send log to {chat_id}: {e}")
            await asyncio.sleep(60)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    first_name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Olá, {first_name}!\n\n"
        "Seja bem-vindo à Zeus Holding.\n\n"
        "📊 Nosso sistema envia logs automaticamente sempre que houver novas solicitações de usuários.\n\n"
        "⏳ Fique atento — as atualizações serão entregues em tempo real.\n\n"
        "🚀 Zeus Holding | Monitoramento Inteligente"
    )


async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    if chat_id in activated_users:
        await update.message.reply_text("⚠️ Os Logs já estão ativos.")
        return

    activated_users.add(chat_id)

    first_msg = generate_log_message()
    await update.message.reply_text(
        "✅ Log stream activated. You will receive new logs every 30–60 minutes.\n\n"
        f"📡 Initial log:\n\n{first_msg}"
    )

    task = asyncio.create_task(send_logs_loop(chat_id, context.bot))
    active_tasks[chat_id] = task
    logger.info(f"Log stream permanently started for chat_id={chat_id}")


async def test1_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    count = random.randint(1, 3)
    await update.message.reply_text(f"🧪 Sending {count} test log(s)...")
    for _ in range(count):
        msg = generate_log_message()
        await update.message.reply_text(msg)


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("logs", logs_command))
    app.add_handler(CommandHandler("test1", test1_command))

    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
