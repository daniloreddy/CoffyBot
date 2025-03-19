# packages
import discord
import logging
import os
import time
import re
import random
import functools
# namespaces
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from typing import Optional
from datetime import datetime, timedelta
# funzioni custom
from gemini_utils import get_gemini_response, cambia_modello
from db_utils import log_to_sqlite
from memory import memoria_utente, aggiorna_memoria, salva_memoria_file
from dashboard import start_dashboard
from services_utils import cerca_wikipedia, ottieni_meteo, genera_audio_tts, genera_immagine, leggi_contenuto_file, check_admin


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
intents.message_content = True

start_dashboard()

import functools
import discord

def gestisci_errori(comando_nome: str):
    def decoratore(func):
        @functools.wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            try:
                await func(interaction, *args, **kwargs)
            except Exception as e:
                logging.error(f"❌ Errore nel comando {comando_nome}: {e}")
                try:
                    if interaction.response.is_done():
                        await interaction.followup.send("❗ Errore durante l'elaborazione. Riprova più tardi.")
                    else:
                        await interaction.response.send_message("❗ Errore durante l'elaborazione. Riprova più tardi.", ephemeral=True)
                except Exception as inner_err:
                    logging.error(f"⚠️ Errore anche nel gestire la risposta d'errore: {inner_err}")
        return wrapper
    return decoratore

@bot.event
async def on_ready():
    from gemini_utils import MODEL
    logging.info(f"🤖 Bot {bot.user} online! Modello: {MODEL}")
    try:
        synced = await bot.tree.sync()
        logging.info(f"✅ Comandi slash sincronizzati: {len(synced)}")
    except Exception as e:
        logging.error(f"❌ Errore durante la sincronizzazione dei comandi: {e}")

# Comando slash /wiki
@bot.tree.command(name="chatty-wiki", description="Cerca un termine su Wikipedia")
@app_commands.describe(termine="Termine da cercare su Wikipedia")
@gestisci_errori("chatty-wiki")
async def wiki(interaction: discord.Interaction, termine: str):
    await interaction.response.defer()  # Mostra "pensaci tu..." se la ricerca dura un po'

    # Riutilizziamo la tua funzione di ricerca
    titolo, descrizione, link, immagine = cerca_wikipedia(termine)

    embed = discord.Embed(
        title=f"📚 Wikipedia: {titolo}",
        description=descrizione,
        color=discord.Color.gold()
    )
    if link:
        embed.add_field(name="🔗 Link", value=link, inline=False)
    if immagine:
        embed.set_thumbnail(url=immagine)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="chatty-meteo", description="Mostra il meteo per una città e una data")
@app_commands.describe(citta="Nome della città", giorno="Oggi, domani, dopodomani o data (YYYY-MM-DD o DD-MM-YYYY)")
@gestisci_errori("chatty-meteo")
async def chatty_meteo(interaction: discord.Interaction, citta: str, giorno: Optional[str] = "oggi"):
    await interaction.response.defer()

    giorno = giorno.lower().strip()
    oggi = datetime.now()

    if giorno == "oggi":
        data_richiesta = oggi
    elif giorno == "domani":
        data_richiesta = oggi + timedelta(days=1)
    elif giorno == "dopodomani":
        data_richiesta = oggi + timedelta(days=2)
    else:
        # Proviamo a interpretare la data
        try:
            if "-" in giorno:
                parts = giorno.split("-")
                if len(parts[0]) == 4:
                    # YYYY-MM-DD
                    data_richiesta = datetime.strptime(giorno, "%Y-%m-%d")
                elif len(parts[2]) == 4:
                    # DD-MM-YYYY
                    data_richiesta = datetime.strptime(giorno, "%d-%m-%Y")
                else:
                    raise ValueError("Formato data non riconosciuto.")
            else:
                raise ValueError("Formato data non riconosciuto.")
        except Exception:
            await interaction.followup.send("❗ Data non valida. Usa 'oggi', 'domani', 'dopodomani' oppure data tipo '2025-03-22' o '22-03-2025'.")
            return

    # Chiama la funzione meteo con la data (passa stringa o oggetto a tua scelta)
    meteo_risposta = ottieni_meteo(citta, data_richiesta.date())
    await interaction.followup.send(meteo_risposta)

@bot.tree.command(name="chatty-tts", description="Genera un audio dal testo inserito (text-to-speech)")
@app_commands.describe(testo="Testo da convertire in audio")
@gestisci_errori("chatty-tts")
async def tts(interaction: discord.Interaction, testo: str):
    if not testo.strip():
        await interaction.response.send_message("❗ Devi scrivere qualcosa.", ephemeral=True)
        return

    await interaction.response.defer()  # Mostra "in elaborazione..."

    audio_file = genera_audio_tts(testo)
    if audio_file:
        await interaction.followup.send(file=discord.File(audio_file))
        os.remove(audio_file)
    else:
        await interaction.followup.send("❌ Errore nella generazione dell'audio.")

@bot.tree.command(name="chatty-image", description="Genera un'immagine dal prompt inserito")
@app_commands.describe(prompt="Descrizione dell'immagine da generare")
@gestisci_errori("chatty-image")
async def image(interaction: discord.Interaction, prompt: str):
    if not prompt.strip():
        await interaction.response.send_message("❗ Devi scrivere qualcosa.", ephemeral=True)
        return

    await interaction.response.defer()  # Mostra "elaborazione..."

    immagine_file = genera_immagine(prompt)

    if immagine_file == "loading":
        await interaction.followup.send("⏳ Il modello sta caricando. Riprova tra qualche secondo.")
    elif immagine_file == "limit":
        await interaction.followup.send("⚠️ Hai raggiunto il limite giornaliero di generazione immagini. Riprova domani!")
    elif immagine_file:
        await interaction.followup.send(file=discord.File(immagine_file))
        os.remove(immagine_file)
    else:
        await interaction.followup.send("❌ Errore nella generazione dell'immagine.")

@bot.tree.command(name="chatty-reset", description="Azzera la memoria della chat con il bot")
@gestisci_errori("chatty-reset")
async def reset(interaction: discord.Interaction):

    if not await check_admin(interaction):
        return
    
    user_id = interaction.user.id
    memoria_utente.pop(user_id, None)

    await interaction.response.send_message("🧠 Memoria azzerata!", ephemeral=False)

    try:
        # Aggiunge la reazione 🧹 al messaggio originale (se possibile)
        await interaction.channel.last_message.add_reaction("🧹")
    except Exception:
        pass  # Ignora errori se non può aggiungere reazione

@bot.tree.command(name="chatty-info", description="Mostra informazioni sul bot e la memoria attiva")
@gestisci_errori("chatty-info")
async def info(interaction: discord.Interaction):
    from gemini_utils import MODEL  # Import come nella tua on_ready
    utenti_memorizzati = len(memoria_utente)

    messaggio = f"🤖 Modello attivo: `{MODEL}`\n🧠 Utenti in memoria: `{utenti_memorizzati}`"
    await interaction.response.send_message(messaggio)

@bot.tree.command(name="chatty-model", description="Cambia il modello Gemini utilizzato dal bot")
@app_commands.describe(modello="Nome del nuovo modello (es: gemini-1.5-flash)")
@gestisci_errori("chatty-model")
async def model(interaction: discord.Interaction, modello: str):

    if not await check_admin(interaction):
        return
    
    ok = cambia_modello(modello)

    if ok:
        await interaction.response.send_message(f"✅ ⚙️ Modello cambiato in: `{modello}`")
    else:
        await interaction.response.send_message("❌ Modello non valido.")

MODELLI_DISPONIBILI = ['gemini-1.5-flash', 'gemini-1.5-pro']
@model.autocomplete('modello')
async def autocomplete_modelli(interaction: discord.Interaction, current: str):
    suggerimenti = [
        app_commands.Choice(name=mod, value=mod)
        for mod in MODELLI_DISPONIBILI if current.lower() in mod.lower()
    ]
    return suggerimenti[:5]

@bot.tree.command(name="chatty-help", description="Mostra la lista dei comandi disponibili")
async def help_command(interaction: discord.Interaction):
    messaggio = (
        "📖 **Comandi disponibili:**\n"
        "/chatty ➜ Chatta con Coffy (supporta allegati)\n"
        "/chatty-wiki ➜ Cerca un termine su Wikipedia\n"
        "/chatty-meteo ➜ Mostra il meteo per una città\n"
        "/chatty-tts ➜ Genera audio da testo\n"
        "/chatty-image ➜ Genera immagine da prompt\n"
        "/chatty-reset ➜ Azzera la memoria utente\n"
        "/chatty-info ➜ Mostra info sul bot e memoria\n"
        "/chatty-model ➜ Cambia modello Gemini\n"
    )
    await interaction.response.send_message(messaggio, ephemeral=True)

@bot.tree.command(name="chatty", description="Fai una domanda a Coffy (modello Gemini)")
@app_commands.describe(prompt="Scrivi la tua domanda o richiesta per Coffy", allegato="(Opzionale) File allegato da analizzare")
@gestisci_errori("chatty")
async def chatty(interaction: discord.Interaction, prompt: str, allegato: Optional[discord.Attachment] = None):

    await interaction.response.defer()

    user_id = interaction.user.id
    now = time.time()

    allegati_testo = []

    if allegato:
        risultato = await leggi_contenuto_file(allegato)
        if risultato.startswith("⚠️") or risultato.startswith("❌"):
            await interaction.followup.send(risultato)
            return
        allegati_testo.append(risultato)

    prompt_finale = prompt
    if allegati_testo:
        prompt_finale += "\n\nContenuto allegato:\n" + "\n".join(allegati_testo)

    prompt_contestuale = aggiorna_memoria(user_id, prompt_finale, now)
    risposta = get_gemini_response(prompt_contestuale)

    memoria_utente[user_id]["scambi"].append({"domanda": prompt_finale, "risposta": risposta})

    log_to_sqlite(interaction.user, interaction.channel, prompt_finale, risposta)

    if len(risposta) <= 4096:
        embed = discord.Embed(title="🤖 Risposta di Coffy", description=risposta, color=discord.Color.green())
        embed.set_footer(text=f"Richiesta da {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send(risposta)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    contenuto = message.content.lower()

    # --- Funzioni debug ---
    if contenuto == "chatty debug admininfo":
        RUOLI_ADMIN = ["Admin", "Boss", "CoffyMaster"]
        FALLBACK_ID = 400409909184954373  # Inserisci il tuo ID

        is_admin = False
        try:
            if any(role.name in RUOLI_ADMIN for role in message.author.roles):
                is_admin = True
        except AttributeError:
            if message.author.id == FALLBACK_ID:
                is_admin = True

        status = "✅ SEI un admin." if is_admin else "⛔ NON sei admin."
        messaggio = (
            f"👑 **Ruoli admin autorizzati:** `{', '.join(RUOLI_ADMIN)}`\n"
            f"🆔 **Fallback User ID:** `{FALLBACK_ID}`\n\n"
            f"{status}"
        )
        await message.channel.send(messaggio)
        return

    # Risposta alla menzione
    if bot.user in message.mentions:
        await message.channel.send(f"Ciao {message.author.mention}! 👋 Posso aiutarti con i comandi slash. Digita `/help` per iniziare!")

    # Easter egg: Coffy o Chatty sei vivo?
    if re.search(r"(coffy|chatty)\s+sei\s+vivo", contenuto):
        risposte = [
            "Sono vivo e frullato di caffeina ☕⚡",
            "Più vivo che mai, pronto a generare immagini e risposte!",
            "Vivo... nella RAM del server 💾👾",
            "Finché non spengono la corrente, sono operativo! 🔋🤖",
            "Sto calcolando la vita, l’universo e tutto quanto... 42!"
        ]
        risposta = random.choice(risposte)
        await message.channel.send(f"{message.author.mention} {risposta}")

    await bot.process_commands(message)



import atexit
atexit.register(salva_memoria_file)
bot.run(TOKEN)
