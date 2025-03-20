# packages
import discord
import logging
import os
import time
import re
import random
import functools
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from typing import Optional
from datetime import datetime, timedelta

# custom functions
from gemini_utils import get_gemini_response, change_model
from db_utils import log_to_sqlite
from memory import user_memory, update_memory, save_memory_to_file
from dashboard import start_dashboard
from services_utils import search_wikipedia, get_weather, generate_tts_audio, generate_image, read_file_content, check_admin

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

start_dashboard()

def handle_errors(command_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            try:
                await func(interaction, *args, **kwargs)
            except Exception as e:
                logging.error(f"❌ Error in command {command_name}: {e}")
                try:
                    if interaction.response.is_done():
                        await interaction.followup.send("❗ An error occurred. Please try again later.")
                    else:
                        await interaction.response.send_message("❗ An error occurred. Please try again later.", ephemeral=True)
                except Exception as inner_err:
                    logging.error(f"⚠️ Error handling the error response: {inner_err}")
        return wrapper
    return decorator

@bot.event
async def on_ready():
    from gemini_utils import MODEL
    logging.info(f"🤖 Bot {bot.user} is online! Model: {MODEL}")
    try:
        synced = await bot.tree.sync()
        logging.info(f"✅ Slash commands synced: {len(synced)}")
    except Exception as e:
        logging.error(f"❌ Error syncing commands: {e}")

# /chatty-wiki
@bot.tree.command(name="chatty-wiki", description="Search for a term on Wikipedia")
@app_commands.describe(termine="Term to search on Wikipedia")
@handle_errors("chatty-wiki")
async def wiki_command(interaction: discord.Interaction, termine: str):
    await interaction.response.defer()
    title, description, link, image = search_wikipedia(termine)

    embed = discord.Embed(
        title=f"📚 Wikipedia: {title}",
        description=description,
        color=discord.Color.gold()
    )
    if link:
        embed.add_field(name="🔗 Link", value=link, inline=False)
    if image:
        embed.set_thumbnail(url=image)

    await interaction.followup.send(embed=embed)

# /chatty-meteo
@bot.tree.command(name="chatty-meteo", description="Show the weather for a city and date")
@app_commands.describe(citta="City name", giorno="oggi, domani, dopodomani or date (YYYY-MM-DD or DD-MM-YYYY)")
@handle_errors("chatty-meteo")
async def weather_command(interaction: discord.Interaction, citta: str, giorno: Optional[str] = "oggi"):
    await interaction.response.defer()
    giorno = giorno.lower().strip()
    today = datetime.now()

    if giorno == "oggi":
        requested_date = today
    elif giorno == "domani":
        requested_date = today + timedelta(days=1)
    elif giorno == "dopodomani":
        requested_date = today + timedelta(days=2)
    else:
        try:
            parts = giorno.split("-")
            if len(parts[0]) == 4:
                requested_date = datetime.strptime(giorno, "%Y-%m-%d")
            elif len(parts[2]) == 4:
                requested_date = datetime.strptime(giorno, "%d-%m-%Y")
            else:
                raise ValueError
        except Exception:
            await interaction.followup.send("❗ Invalid date. Use 'oggi', 'domani', 'dopodomani' or formats '2025-03-22' or '22-03-2025'.")
            return

    weather_response = get_weather(citta, requested_date.date())
    await interaction.followup.send(weather_response)

# /chatty-tts
@bot.tree.command(name="chatty-tts", description="Generate audio from text (text-to-speech)")
@app_commands.describe(testo="Text to convert to audio")
@handle_errors("chatty-tts")
async def tts_command(interaction: discord.Interaction, testo: str):
    if not testo.strip():
        await interaction.response.send_message("❗ Please enter some text.", ephemeral=True)
        return

    await interaction.response.defer()
    audio_file = generate_tts_audio(testo)
    if audio_file:
        await interaction.followup.send(file=discord.File(audio_file))
        os.remove(audio_file)
    else:
        await interaction.followup.send("❌ Error generating audio.")

# /chatty-image
@bot.tree.command(name="chatty-image", description="Generate an image from a prompt")
@app_commands.describe(prompt="Description of the image to generate")
@handle_errors("chatty-image")
async def image_command(interaction: discord.Interaction, prompt: str):
    if not prompt.strip():
        await interaction.response.send_message("❗ Please enter a prompt.", ephemeral=True)
        return

    await interaction.response.defer()
    image_file = generate_image(prompt)

    if image_file == "loading":
        await interaction.followup.send("⏳ The model is loading. Try again in a few seconds.")
    elif image_file == "limit":
        await interaction.followup.send("⚠️ Daily image generation limit reached. Try again tomorrow!")
    elif image_file:
        await interaction.followup.send(file=discord.File(image_file))
        os.remove(image_file)
    else:
        await interaction.followup.send("❌ Error generating image.")

# /chatty-reset
@bot.tree.command(name="chatty-reset", description="Reset the chat memory with the bot")
@handle_errors("chatty-reset")
async def reset_memory(interaction: discord.Interaction):
    if not await check_admin(interaction):
        return
    user_id = interaction.user.id
    user_memory.pop(user_id, None)

    await interaction.response.send_message("🧠 Memory reset!", ephemeral=False)
    try:
        await interaction.channel.last_message.add_reaction("🧹")
    except Exception:
        pass

# /chatty-info
@bot.tree.command(name="chatty-info", description="Show info about the bot and memory")
@handle_errors("chatty-info")
async def info(interaction: discord.Interaction):
    from gemini_utils import MODEL
    users_memorized = len(user_memory)

    message_text = f"🤖 Active model: `{MODEL}`\n🧠 Users in memory: `{users_memorized}`"
    await interaction.response.send_message(message_text)

# /chatty-model
@bot.tree.command(name="chatty-model", description="Change the Gemini model used by the bot")
@app_commands.describe(modello="Name of the new model (e.g., gemini-1.5-flash)")
@handle_errors("chatty-model")
async def model_switch(interaction: discord.Interaction, modello: str):
    if not await check_admin(interaction):
        return
    ok = change_model(modello)

    if ok:
        await interaction.response.send_message(f"✅ ⚙️ Model switched to: `{modello}`")
    else:
        await interaction.response.send_message("❌ Invalid model.")

AVAILABLE_MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro']
@model_switch.autocomplete('modello')
async def autocomplete_models(interaction: discord.Interaction, current: str):
    suggestions = [
        app_commands.Choice(name=mod, value=mod)
        for mod in AVAILABLE_MODELS if current.lower() in mod.lower()
    ]
    return suggestions[:5]

# /chatty-help
@bot.tree.command(name="chatty-help", description="Show the list of available commands")
async def help_command(interaction: discord.Interaction):
    message_text = (
        "📖 **Available commands:**\n"
        "/chatty ➜ Chat with Coffy (supports attachments)\n"
        "/chatty-wiki ➜ Search Wikipedia\n"
        "/chatty-meteo ➜ Show weather for a city\n"
        "/chatty-tts ➜ Generate audio from text\n"
        "/chatty-image ➜ Generate image from prompt\n"
        "/chatty-reset ➜ Reset user memory\n"
        "/chatty-info ➜ Show bot info and memory\n"
        "/chatty-model ➜ Change Gemini model\n"
    )
    await interaction.response.send_message(message_text, ephemeral=True)

# /chatty
@bot.tree.command(name="chatty", description="Ask a question to Coffy (Gemini model)")
@app_commands.describe(prompt="Your question or request for Coffy", allegato="(Optional) Attachment to analyze")
@handle_errors("chatty")
async def chatty(interaction: discord.Interaction, prompt: str, allegato: Optional[discord.Attachment] = None):
    await interaction.response.defer()
    user_id = interaction.user.id
    now = time.time()

    attachment_texts = []
    if allegato:
        result = await read_file_content(allegato)
        if result.startswith("⚠️") or result.startswith("❌"):
            await interaction.followup.send(result)
            return
        attachment_texts.append(result)

    final_prompt = prompt
    if attachment_texts:
        final_prompt += "\n\nAttachment content:\n" + "\n".join(attachment_texts)

    contextual_prompt = update_memory(user_id, final_prompt, now)
    response_text = get_gemini_response(contextual_prompt)

    user_memory[user_id]["exchanges"].append({"question": final_prompt, "answer": response_text})

    log_to_sqlite(interaction.user, interaction.channel, final_prompt, response_text)

    if len(response_text) <= 4096:
        embed = discord.Embed(title="🤖 Coffy's Response", description=response_text, color=discord.Color.green())
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send(response_text)

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

        status = "✅ You ARE admin." if is_admin else "⛔ You are NOT admin."
        message_text = (
            f"👑 **Authorized admin roles:** `{', '.join(ADMIN_ROLES)}`\n"
            f"🆔 **Fallback User ID:** `{FALLBACK_ID}`\n\n"
            f"{status}"
        )
        await message.channel.send(message_text)
        return

    if bot.user in message.mentions:
        await message.channel.send(f"Hi {message.author.mention}! 👋 Use slash commands to get started. Try `/help`!")

    if re.search(r"(coffy|chatty)\s+sei\s+vivo", content):
        responses_list = [
            "I’m alive and full of caffeine ☕⚡",
            "More alive than ever, ready to generate images and answers!",
            "Alive... in server RAM 💾👾",
            "As long as there’s power, I’m operational! 🔋🤖",
            "Calculating life, universe, and everything... 42!"
        ]
        response = random.choice(responses_list)
        await message.channel.send(f"{message.author.mention} {response}")

    await bot.process_commands(message)

import atexit
atexit.register(save_memory_to_file)
bot.run(TOKEN)
