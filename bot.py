import discord
from discord import app_commands
import json
import time
import os
import random
import string
from discord.ext import tasks

import Staff_strikes
import Bugreport
import vouch_system  # ✅ VOUCH SYSTEM

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
# =========================================

if TOKEN is None:
    print("❌ TOKEN not set in environment variables")
    exit()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ================= STATE =================
def generate_token():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_-+=[]{}|;:,.<>?/`~\"'"
    return ''.join(random.choices(chars, k=64))

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"token": "", "expiry": 0}

def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f)

state = load_state()

@tasks.loop(minutes=1)
async def rotate():
    global state
    state["token"] = generate_token()
    state["expiry"] = time.time() + 60
    save_state(state)

# ================= READY =================
@client.event
async def on_ready():
    print(f"Bot running as {client.user}")

    guild = discord.Object(id=GUILD_ID)

    try:
        print("🔧 Loading modules...")

        Staff_strikes.setup(tree, discord, GUILD_ID, STAFF_ROLE_ID, STRIKE_FILE)

        if hasattr(Bugreport, "setup"):
            Bugreport.setup(tree, GUILD_ID)
        else:
            print("⚠️ Bugreport.setup missing")

        if Ping and hasattr(Ping, "setup"):
            Ping.setup(tree, GUILD_ID)
        else:
            print("⚠️ Ping.setup missing")

        # ✅ FIXED: correct vouch setup call
        vouch_system.setup(tree, GUILD_ID, VOUCH_CONFIG_ROLE_ID)

    except Exception as e:
        print("❌ Setup error:", e)

    # ================= SYNC =================
    try:
        print("🔁 Syncing commands...")

        # ALWAYS sync guild first (fast + instant update)
        synced = await tree.sync(guild=guild)
        print(f"✅ Guild synced: {len(synced)} commands")

        # backup global sync
        synced_global = await tree.sync()
        print(f"🌍 Global synced: {len(synced_global)} commands")

    except Exception as e:
        print("❌ Sync error:", e)

    if not rotate.is_running():
        rotate.start()

    print("🚀 Bot fully loaded")

# ================= RUN =================
client.run(TOKEN)
