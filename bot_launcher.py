# bot_launcher.py

"""
Launcher script to run Coffy Discord and/or Telegram bots based on command-line arguments.
Example usage:
    python bot_launcher.py discord telegram
"""

import sys
import asyncio

from bot_discord import start_discord
from bot_telegram import start_telegram
from utils.localization import detect_system_language, load_language


def parse_args():
    args = [arg.lower() for arg in sys.argv[1:]]
    return {"discord": "discord" in args, "telegram": "telegram" in args}


async def main():
    """
    Launch one or both bots depending on command-line arguments.
    """

    selected = parse_args()

    tasks = []
    if selected["discord"]:
        tasks.append(start_discord())
    if selected["telegram"]:
        tasks.append(start_telegram())

    if not tasks:
        print("Usage: python bot_launcher.py [discord] [telegram]")
        return

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    load_language(detect_system_language())
    asyncio.run(main())
