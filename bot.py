# packages
import asyncio
import discord
import os
import re
import random
import atexit

from dotenv import load_dotenv
from discord.ext import commands

from utils.memory import user_memory, save_memory_to_file
from utils.localization import detect_system_language, load_language, t
from utils.logger import bot_logger, error_logger

# === Init section ===
load_dotenv()
load_language(detect_system_language())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
atexit.register(save_memory_to_file)


# on_message events
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

    if content == "chatty debug admininfo":
        ADMIN_ROLES = ["Admin", "Boss", "CoffyMaster"]
        FALLBACK_ID = 400409909184954373

        is_admin = False
        try:
            if any(role.name in ADMIN_ROLES for role in message.author.roles):
                is_admin = True
        except AttributeError:
            if message.author.id == FALLBACK_ID:
                is_admin = True

        status = t("admin_status_yes") if is_admin else t("admin_status_no")
        message_text = t(
            "admin_debug_message",
            roles=", ".join(ADMIN_ROLES),
            fallback=FALLBACK_ID,
            status=status,
        )
        await message.channel.send(message_text)

        bot_logger.info(
            "Admin debug info requested by %s (ID: %s)",
            message.author.display_name,
            message.author.id,
        )
        return

    if bot.user in message.mentions:
        bot_logger.info(
            "Bot mentioned by %s (ID: %s) in [%s]",
            message.author.display_name,
            message.author.id,
            message.channel.name,
        )
        await message.channel.send(t("mention_help", user=message.author.mention))

    if re.search(r"(coffy|chatty)\s+sei\s+vivo", content):
        responses_list = [
            t("alive_response_1"),
            t("alive_response_2"),
            t("alive_response_3"),
            t("alive_response_4"),
            t("alive_response_5"),
        ]
        response = random.choice(responses_list)
        bot_logger.info(
            "Alive check by %s: response='%s'", message.author.display_name, response
        )
        await message.channel.send(f"{message.author.mention} {response}")

    await bot.process_commands(message)


@bot.event
async def on_ready():
    from services.gemini_service import MODEL

    bot_logger.info(t("bot_online_log", bot=bot.user, model=MODEL))
    try:
        synced = await bot.tree.sync()
        bot_logger.info(t("commands_synced_log", count=len(synced)))
    except Exception as e:
        error_logger.error(t("sync_error_log", error=e))


async def load_all_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    await load_all_cogs()
    await bot.start(os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
