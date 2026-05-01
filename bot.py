import discord
from discord import app_commands
import json
import time
import os

import ping
import Staff_strikes

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")

GUILD_ID = 1471293085706223703

ROLE_ID = 1471295644969734184

STAFF_ROLE_ID = 1488979323065995365
VOUCH_CONFIG_ROLE_ID = 1490795334291554426

VOUCH_FILE = "vouches.json"
STRIKE_FILE = "strikes.json"
# =========================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# (rest of your code stays EXACTLY the same)

@client.event
async def on_ready():
    print(f"Bot running as {client.user}")

    guild = discord.Object(id=GUILD_ID)

    Staff_strikes.setup(tree, discord, GUILD_ID, STAFF_ROLE_ID, STRIKE_FILE)
    ping.setup(tree, GUILD_ID)

    await tree.sync(guild=guild)

    print("Bot fully loaded 🚀")

client.run(TOKEN)