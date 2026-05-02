import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import time
import os
import random
import string

import Staff_strikes
import Bugreport
import vouch_system
import help

try:
    import Ping
except:
    Ping = None
    print("⚠️ Ping module not found")

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")

GUILD_ID = 1471293085706223703
ROLE_ID = 1471295644969734184
STAFF_ROLE_ID = 1488979323065995365
VOUCH_CONFIG_ROLE_ID = 1490795334291554426

STATE_FILE = "state.json"
STRIKE_FILE = "strikes.json"

if TOKEN is None:
    print("❌ TOKEN not set")
    exit()

# ================= BOT (FIXED) =================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

tree = client.tree  # ✅ THIS NOW WORKS

# ================= STATE =================
def generate_token():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=64))

state = {"token": "", "expiry": 0}

@tasks.loop(minutes=1)
async def rotate():
    state["token"] = generate_token()
    state["expiry"] = time.time() + 60

# ================= READY =================
@client.event
async def on_ready():
    print(f"Bot running as {client.user}")

    guild = discord.Object(id=GUILD_ID)

    print("🔧 Loading modules...")

    Staff_strikes.setup(tree, discord, GUILD_ID, STAFF_ROLE_ID, STRIKE_FILE)

    if hasattr(Bugreport, "setup"):
        Bugreport.setup(tree, GUILD_ID)

    if Ping and hasattr(Ping, "setup"):
        Ping.setup(tree, GUILD_ID)

    vouch_system.setup(tree, GUILD_ID, VOUCH_CONFIG_ROLE_ID)

    help.setup(tree)

    # ================= SYNC =================
    print("🔁 Syncing commands...")

    synced = await tree.sync(guild=guild)
    print(f"✅ Guild synced: {len(synced)} commands")

    print("🚀 Bot fully loaded")

    if not rotate.is_running():
        rotate.start()

# ================= RUN =================
client.run(TOKEN)
