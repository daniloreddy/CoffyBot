# telegram_commands/chatty_admin.py

import os
import sqlite3

from telegram.ext import CommandHandler

from utils.localization import translate
from utils.context import set_context_file, reset_context, get_server_context
from services.gemini import get_supported_models, get_current_model, change_model
from utils.config import PROMPT_DIR, DB_FILE
from utils.logger import bot_logger, error_logger
from utils.generic import (
    require_telegram_dm,
    require_telegram_admin,
    resolve_server_name,
)


# --- CONTEXT: Set ---
@require_telegram_admin()
async def chatty_admin_context(update, context):
    """
    Reset the context prompt associated with the current Telegram group or user.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    if not context.args:
        await update.message.reply_text(translate("invalid_context_file"))
        return

    filename = context.args[0].strip()
    if not filename.endswith(".txt"):
        filename += ".txt"

    user = update.effective_user
    chat = update.effective_chat
    server_name = resolve_server_name(user, chat)

    if set_context_file(server_name, filename):
        bot_logger.info("Context set to '%s' for %s", filename, server_name)
        await update.message.reply_text(translate("context_set"))
    else:
        error_logger.warning("Invalid context file: %s", filename)
        await update.message.reply_text(translate("invalid_context_file"))


# --- CONTEXT: Reset ---
@require_telegram_admin()
async def chatty_admin_context_reset(update, context):
    """
    Reset the context prompt for the current Telegram group or user.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    user = update.effective_user
    chat = update.effective_chat
    server_name = resolve_server_name(user, chat)
    reset_context(server_name)
    bot_logger.info("Context reset for %s", server_name)
    await update.message.reply_text(translate("context_reset"))


# --- CONTEXT: List files ---
@require_telegram_admin()
async def chatty_admin_contexts(update, context):
    """
    List all available context files from the prompts/ directory.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    try:
        files = [f for f in os.listdir(PROMPT_DIR) if f.endswith(".txt")]
        if files:
            await update.message.reply_text(
                translate("available_context_files", files="\n".join(files))
            )
        else:
            await update.message.reply_text(translate("no_context_files"))
    except Exception as e:
        error_logger.error("Context listing error: %s", str(e))
        await update.message.reply_text(translate("context_files_error"))


# --- MODELS: List ---
@require_telegram_dm
@require_telegram_admin()
async def chatty_admin_models(update, context):
    """
    List all available Gemini models and highlight the currently selected one.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    current = get_current_model()
    supported = get_supported_models()
    model_list = "\n".join(
        [f"🔹 {m} {'(active)' if m == current else ''}".strip() for m in supported]
    )
    await update.message.reply_text(translate("available_models", models=model_list))
    bot_logger.info("Model list sent to %s", update.effective_user.full_name)


# --- MODELS: Switch ---
@require_telegram_dm
@require_telegram_admin()
async def chatty_admin_model(update, context):
    """
    Change the active Gemini model used by the bot.

    Args:
        update (Update): Telegram update object containing the model name.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    if not context.args:
        await update.message.reply_text(translate("invalid_model"))
        return

    requested = context.args[0].strip()
    success = change_model(requested)

    if success:
        bot_logger.info(
            "Model switched to '%s' by %s", requested, update.effective_user.full_name
        )
        await update.message.reply_text(translate("model_switched", model=requested))
    else:
        error_logger.warning(
            "Invalid model '%s' requested by %s",
            requested,
            update.effective_user.full_name,
        )
        await update.message.reply_text(translate("invalid_model"))


# --- STATS ---
@require_telegram_dm
@require_telegram_admin()
async def chatty_admin_stats(update, context):
    """
    Show basic statistics including total prompts and unique users.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    ctx = get_server_context()
    model = get_current_model()

    info = translate("embed_stats_desc", model=model)
    context_info = "\n".join([f"{k}: {v}" for k, v in ctx.items()]) or "None"

    msg = f"{info}\n\n{translate('embed_context_title')}\n{context_info}"
    await update.message.reply_text(msg)


# --- ACTIVITY (last 7 days) ---
@require_telegram_dm
@require_telegram_admin()
async def chatty_admin_activity(update, context):
    """
    Display daily prompt activity for the last 7 days.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    if not os.path.isfile(DB_FILE):
        await update.message.reply_text(translate("db_missing_dm"))
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DATE(timestamp), COUNT(*) 
            FROM conversations 
            GROUP BY DATE(timestamp) 
            ORDER BY DATE(timestamp) DESC 
            LIMIT 7
        """
        )
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        error_logger.error("DB error in activity: %s", str(e))
        await update.message.reply_text(translate("db_error"))
        return

    if not rows:
        await update.message.reply_text(translate("no_activity_dm"))
        return

    log = "\n".join([f"{day}: {count} messages" for day, count in rows])
    await update.message.reply_text(log)


# --- LASTLOGS ---
@require_telegram_dm
@require_telegram_admin()
async def chatty_admin_lastlogs(update, context):
    """
    Show the last 10 recorded conversations from the SQLite database.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    if not os.path.isfile(DB_FILE):
        await update.message.reply_text(translate("db_missing_dm"))
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, user, user_id, channel, message, response 
            FROM conversations 
            ORDER BY id DESC 
            LIMIT 10
        """
        )
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        error_logger.error("DB error in lastlogs: %s", str(e))
        await update.message.reply_text(translate("db_error"))
        return

    if not rows:
        await update.message.reply_text(translate("no_conversations_dm"))
        return

    logs = ""
    for row in rows:
        logs += f"🕒 {row[0]} - 👤 {row[1]} ({row[2]}) - 📢 #{row[3]}\n💬 {row[4]}\n🤖 {row[5]}\n{'-'*40}\n"

    await update.message.reply_text(logs[:4096])  # Telegram max message size


@require_telegram_dm
@require_telegram_admin()
async def chatty_admin_help(update, context):
    """
    Display a list of all available administrative commands with descriptions.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Context from the handler.
    """
    bot_logger.info("Admin help invoked by %s", update.effective_user.full_name)
    await update.message.reply_text(translate("admin_help_message_telegram"))


# --- REGISTER ---
def register(app):
    app.add_handler(CommandHandler("chatty_admin_context", chatty_admin_context))
    app.add_handler(
        CommandHandler("chatty_admin_context_reset", chatty_admin_context_reset)
    )
    app.add_handler(CommandHandler("chatty_admin_contexts", chatty_admin_contexts))
    app.add_handler(CommandHandler("chatty_admin_models", chatty_admin_models))
    app.add_handler(CommandHandler("chatty_admin_model", chatty_admin_model))
    app.add_handler(CommandHandler("chatty_admin_stats", chatty_admin_stats))
    app.add_handler(CommandHandler("chatty_admin_activity", chatty_admin_activity))
    app.add_handler(CommandHandler("chatty_admin_lastlogs", chatty_admin_lastlogs))
    app.add_handler(CommandHandler("chatty_admin_help", chatty_admin_help))
