import discord
from discord import app_commands
import os

import Bugreport
import Ping
import Staff_strikes
import vouch  # if you separated it


TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ================= READY =================
@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

    guild = discord.Object(id=config.GUILD_ID if "config" in globals() else 1471293085706223703)

    # ================= SETUP MODULES =================
    try:
        Staff_strikes.setup(tree, discord, config.GUILD_ID, config.STAFF_ROLE_ID, config.STRIKE_FILE)
        print("✅ Staff_strikes loaded")
    except Exception as e:
        print("❌ Staff_strikes error:", e)

    try:
        Bugreport.setup(tree, config.GUILD_ID)
        print("✅ Bugreport loaded")
    except Exception as e:
        print("❌ Bugreport error:", e)

    try:
        Ping.setup(tree, config.GUILD_ID)
        print("✅ Ping loaded")
    except Exception as e:
        print("❌ Ping error:", e)

    try:
        vouch.setup(tree, config.GUILD_ID)
        print("✅ Vouch loaded")
    except Exception as e:
        print("❌ Vouch error:", e)

    # ================= SYNC =================
    try:
        print("🔁 Syncing commands...")
        synced = await tree.sync(guild=guild)
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print("❌ Sync error:", e)

    print("🚀 Bot fully ready")

# ================= RUN =================
client.run(TOKEN)
