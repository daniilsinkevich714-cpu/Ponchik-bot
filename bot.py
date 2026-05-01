import discord
from discord import app_commands
import json
import time
import os

import Staff_strikes
import Bugreport

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")  # Render/Railway environment variable

GUILD_ID = 1471293085706223703

ROLE_ID = 1471295644969734184

STAFF_ROLE_ID = 1488979323065995365
VOUCH_CONFIG_ROLE_ID = 1490795334291554426

STATE_FILE = "state.json"
STRIKE_FILE = "strikes.json"
VOUCH_FILE = "vouches.json"
# =========================================

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ================= STATE =================
def generate_token():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_-+=[]{}|;:,.<>?/`~\"'"
    return ''.join(random.choices(chars, k=64))

def load_state():
    try:
        return json.load(open(STATE_FILE))
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


# ================= STRIKES =================
import Staff_strikes

# ================= VOUCH SYSTEM =================
def load_vouches():
    try:
        return json.load(open(VOUCH_FILE))
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
        description=f"{user.mention}",
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

        # 🔥 FIXED HERE (NO "GOOD VOUCHES" TEXT)
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

@tree.command(
    name="checkvouch",
    description="Check user vouches",
    guild=discord.Object(id=GUILD_ID)
)
async def checkvouch(interaction: discord.Interaction, user: discord.Member):

    uid = str(user.id)

    if uid not in vouches or len(vouches[uid]) == 0:
        await interaction.response.send_message("No vouches ❌", ephemeral=True)
        return

    view = VouchView(vouches[uid], user)
    await interaction.response.send_message(embed=view.build(), view=view)

# ================= VOUCH CONFIG =================
@tree.command(
    name="vouchconfig",
    description="Config vouches (add/remove normal or scam)",
    guild=discord.Object(id=GUILD_ID)
)
async def vouchconfig(
    interaction: discord.Interaction,
    user: discord.Member,
    amount: int,
    remove: bool = False,
    scam_only: bool = False
):

    if VOUCH_CONFIG_ROLE_ID not in [r.id for r in interaction.user.roles]:
        await interaction.response.send_message("No permission ❌", ephemeral=True)
        return

    uid = str(user.id)

    if uid not in vouches:
        vouches[uid] = []

    if remove:
        removed = 0

        for v in vouches[uid][:]:
            if removed >= amount:
                break

            if scam_only and v["scam"]:
                vouches[uid].remove(v)
                removed += 1
            elif not scam_only and not v["scam"]:
                vouches[uid].remove(v)
                removed += 1

        save_vouches(vouches)

        await interaction.response.send_message(
            f"Removed {removed} vouches",
            ephemeral=True
        )
        return

    for _ in range(amount):
        vouches[uid].append({
            "id": len(vouches[uid]) + 1,
            "author": "ADMIN",
            "reason": "Manual add",
            "scam": scam_only,
            "time": time.time()
        })

    save_vouches(vouches)

    await interaction.response.send_message(
        f"Added {amount} vouches",
        ephemeral=True
    )

# ================= READY =================
@client.event
async def on_ready():
    print(f"Bot running as {client.user}")

    guild = discord.Object(id=GUILD_ID)

    Staff_strikes.setup(tree, discord, GUILD_ID, STAFF_ROLE_ID, STRIKE_FILE)
Bugreport.setup(tree, GUILD_ID)

    await tree.sync(guild=guild)

    rotate.start()
    print("Bot fully loaded")

client.run(TOKEN)
