import asyncio
import discord
import re
import random
import time

from dotenv import load_dotenv
from discord.ext import commands

from utils.config import ADMIN_ROLES, FALLBACK_ID, BOT_TOKEN
from utils.localization import detect_system_language, load_language, translate
from utils.logger import bot_logger, error_logger
from services.gemini import get_gemini_response, get_current_model
from utils.context import get_context_prompt
from utils.generic import check_admin


# === Init section ===
BOT_START_TIME = time.time()
load_dotenv()
load_language(detect_system_language())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def chatty_debug_admininfo(message):
    """
    Send admin role and fallback ID information for debugging purposes.
    """
    is_admin = await check_admin(message)

    status = translate("admin_status_yes") if is_admin else translate("admin_status_no")
    message_text = translate(
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


async def handle_chatty_interaction(message: discord.Message, user_message: str):
    """
    Handle user messages directed to the bot and get a Gemini response.
    """
    server_name = message.guild.name if message.guild else f"DM-{message.author.name}"
    context_prompt = get_context_prompt(server_name)

    # Compose the final prompt
    if context_prompt:
        full_prompt = context_prompt.strip() + "\n\n" + user_message
        bot_logger.info("Context applied for server '%s'", server_name)
    else:
        full_prompt = user_message

    response = get_gemini_response(full_prompt)

    if response:
        await message.channel.send(response)
        preview = response[:100] + "..." if len(response) > 100 else response
        bot_logger.info(
            "Gemini response sent to %s: %s",
            message.author.display_name,
            preview,
        )
    else:
        await message.channel.send(translate("gemini_error"))


@bot.event
async def on_message(message):
    """
    Event handler for all incoming messages.
    """
    if message.author == bot.user:
        return

    content = message.content.lower()

    if content == "chatty debug admininfo":
        await chatty_debug_admininfo(message)
        return

    if bot.user in message.mentions:
        bot_logger.info(
            "Bot mentioned by %s (ID: %s) in [%s]",
            message.author.display_name,
            message.author.id,
            message.channel.name,
        )

        cleaned_message = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not cleaned_message:
            await message.channel.send(
                "❓ Please include a message after mentioning me."
            )
            return

        await handle_chatty_interaction(message, cleaned_message)
        return

    if content.startswith(("chatty", "coffy")):
        bot_logger.info(
            "Text trigger by %s (ID: %s) in [%s]",
            message.author.display_name,
            message.author.id,
            message.channel.name,
        )

        cleaned_message = re.sub(
            r"^(chatty|coffy)[\s,:]*", "", content, count=1
        ).strip()
        if not cleaned_message:
            await message.channel.send("❓ Say something after calling me.")
            return

        await handle_chatty_interaction(message, cleaned_message)
        return

    if re.search(r"(coffy|chatty)\s+sei\s+vivo", content):
        responses_list = [
            translate("alive_response_1"),
            translate("alive_response_2"),
            translate("alive_response_3"),
            translate("alive_response_4"),
            translate("alive_response_5"),
        ]
        response = random.choice(responses_list)
        bot_logger.info(
            "Alive check by %s: response='%s'",
            message.author.display_name,
            response,
        )
        await message.channel.send(f"{message.author.mention} {response}")
        return

    await bot.process_commands(message)


@bot.event
async def on_ready():
    """
    Event handler triggered when the bot is ready.
    """
    bot_logger.info("Bot %s is online! Model: %s", bot.user, get_current_model())

    try:
        synced = await bot.tree.sync()
        bot_logger.info("Slash commands synced: %s", len(synced))
    except Exception as e:
        error_logger.error("Error syncing commands: %s", str(e))


async def load_all_cogs():
    """
    Load all cog extensions from the ./cogs directory.
    """
    import os

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    """
    Entry point: Load all cogs and start the bot using the token from environment.
    """
    await load_all_cogs()
    await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
