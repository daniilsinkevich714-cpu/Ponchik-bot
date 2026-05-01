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

# 🔧 FIX: you forgot to import Ping (this would crash your bot)
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
VOUCH_FILE = "vouches.json"
# =========================================

# ================= SAFETY =================
if TOKEN is None:
    print("❌ TOKEN not set in environment variables")
    exit()
# =========================================

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

# ================= VOUCH SYSTEM =================
def load_vouches():
    try:
        with open(VOUCH_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_vouches(data):
    with open(VOUCH_FILE, "w") as f:
        json.dump(data, f)

vouches = load_vouches()

# ================= VOUCH =================
@tree.command(
    name="vouch",
    description="Add a vouch or scam vouch",
    guild=discord.Object(id=GUILD_ID)
)
async def vouch(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason", scam: bool = False):
    uid = str(user.id)

    if uid not in vouches:
        vouches[uid] = []

    vid = len(vouches[uid]) + 1

    vouches[uid].append({
        "id": vid,
        "author": str(interaction.user),
        "reason": reason,
        "scam": scam,
        "time": time.time()
    })

    save_vouches(vouches)

    embed = discord.Embed(
        title="🌌 Vouch Added",
        description=user.mention,
        color=discord.Color.purple()
    )

    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Scam", value=str(scam), inline=True)
    embed.set_footer(text=f"Vouch ID #{vid}")

    await interaction.response.send_message(embed=embed)

# ================= CHECK VOUCH =================
class VouchView(discord.ui.View):
    def __init__(self, entries, user):
        super().__init__(timeout=120)
        self.entries = entries
        self.user = user
        self.page = 0

    def build(self):
        embed = discord.Embed(
            title=f"🌌 Vouches - {self.user}",
            color=discord.Color.purple()
        )

        good = len([v for v in self.entries if not v["scam"]])
        scams = len([v for v in self.entries if v["scam"]])

        embed.add_field(name="Vouches", value=good, inline=True)
        embed.add_field(name="Scam vouches", value=scams, inline=True)

        start = self.page * 5
        end = start + 5

        for v in self.entries[::-1][start:end]:
            tag = "🚨 SCAM" if v["scam"] else "✅"
            embed.add_field(
                name=f"{tag} Vouch #{v['id']}",
                value=f"{v['author']} → {v['reason']}",
                inline=False
            )

        embed.set_footer(text=f"Page {self.page + 1}")
        return embed

    @discord.ui.button(label="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        await interaction.response.edit_message(embed=self.build(), view=self)

    @discord.ui.button(label="➡️")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.page + 1) * 5 < len(self.entries):
            self.page += 1
        await interaction.response.edit_message(embed=self.build(), view=self)

# ================= READY =================
@client.event
async def on_ready():
    print(f"Bot running as {client.user}")

    guild = discord.Object(id=GUILD_ID)

    try:
        Staff_strikes.setup(tree, discord, GUILD_ID, STAFF_ROLE_ID, STRIKE_FILE)

        # 🔧 FIX: prevent crash if setup missing
        if hasattr(Bugreport, "setup"):
            Bugreport.setup(tree, GUILD_ID)
        else:
            print("⚠️ Bugreport.setup missing")

        if Ping and hasattr(Ping, "setup"):
            Ping.setup(tree, GUILD_ID)
        else:
            print("⚠️ Ping.setup missing")

    except Exception as e:
        print("❌ Setup error:", e)

    try:
        await tree.sync(guild=guild)
    except Exception as e:
        print("❌ Sync error:", e)

    if not rotate.is_running():
        rotate.start()

    print("Bot fully loaded 🚀")

# ================= RUN =================
client.run(TOKEN)
