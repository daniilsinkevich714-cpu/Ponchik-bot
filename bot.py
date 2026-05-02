import discord
from discord.ext import commands, tasks
import os
import time
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

STRIKE_FILE = "strikes.json"

if not TOKEN:
    print("❌ TOKEN not set")
    exit()

# ================= BOT SETUP =================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

# ================= ROTATION (your system kept) =================
state = {"token": "", "expiry": 0}

def generate_token():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=64))

@tasks.loop(minutes=1)
async def rotate():
    state["token"] = generate_token()
    state["expiry"] = time.time() + 60

# ================= READY =================
@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

    guild = discord.Object(id=GUILD_ID)

    print("🔧 Loading modules...")

    # Register all command systems FIRST
    Staff_strikes.setup(tree, discord, GUILD_ID, STAFF_ROLE_ID, STRIKE_FILE)
    Bugreport.setup(tree, GUILD_ID)
    vouch_system.setup(tree, GUILD_ID, VOUCH_CONFIG_ROLE_ID)

    if Ping:
        Ping.setup(tree, GUILD_ID)

    # IMPORTANT: help MUST be registered before sync
    help.setup(tree)
    print("✅ Help loaded")

    print("🔁 Syncing slash commands...")

    # FORCE SAFE SYNC
    try:
        synced = await tree.sync(guild=guild)
        print(f"✅ Guild synced: {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

    print("🚀 Bot fully loaded")

    if not rotate.is_running():
        rotate.start()

# ================= RUN =================
client.run(TOKEN)
