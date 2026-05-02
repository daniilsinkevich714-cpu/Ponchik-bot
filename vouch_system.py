import discord
from discord import app_commands
import time
import os
from pymongo import MongoClient

# ================= MONGO CONFIG =================
client = MongoClient(os.getenv("MONGO_URI"))
db = client["discord_bot"]
vouch_db = db["vouches"]


# ================= HELPERS =================
def get_user_data(uid):
    data = vouch_db.find_one({"_id": uid})
    if not data:
        data = {"_id": uid, "vouches": []}
        vouch_db.insert_one(data)
    return data


def save_user(data):
    vouch_db.update_one(
        {"_id": data["_id"]},
        {"$set": data},
        upsert=True
    )


def is_admin(interaction, role_id):
    return any(role.id == role_id for role in interaction.user.roles)


# ================= SETUP =================
def setup(tree, GUILD_ID, VOUCH_CONFIG_ROLE_ID):

    # ================= /vouch =================
    @tree.command(
        name="vouch",
        description="Give a vouch or scam vouch",
        guild=discord.Object(id=GUILD_ID)
    )
    async def vouch(
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
        scam: bool = False
    ):

        uid = str(user.id)
        data = get_user_data(uid)

        vid = len(data["vouches"]) + 1

        data["vouches"].append({
            "id": vid,
            "giver": str(interaction.user),
            "reason": reason,
            "scam": scam,
            "time": time.time()
        })

        save_user(data)

        embed = discord.Embed(
            title="💠 Vouch Added",
            color=discord.Color.green() if not scam else discord.Color.red()
        )

        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Type", value="🚨 SCAM" if scam else "✅ Normal", inline=True)
        embed.set_footer(text=f"Vouch ID #{vid}")

        await interaction.response.send_message(embed=embed)


    # ================= /checkvouches =================
    @tree.command(
        name="checkvouches",
        description="Check user vouches",
        guild=discord.Object(id=GUILD_ID)
    )
    async def checkvouches(
        interaction: discord.Interaction,
        user: discord.Member
    ):

        uid = str(user.id)
        data = get_user_data(uid)
        entries = data["vouches"]

        good = len([v for v in entries if not v.get("scam", False)])
        scams = len([v for v in entries if v.get("scam", False)])

        embed = discord.Embed(
            title=f"📊 Vouch Profile - {user}",
            color=discord.Color.purple()
        )

        embed.add_field(name="✅ Vouches", value=good, inline=True)
        embed.add_field(name="🚨 Scam Vouches", value=scams, inline=True)
        embed.add_field(name="📦 Total", value=len(entries), inline=True)

        last = entries[-3:][::-1]

        if last:
            text = ""
            for v in last:
                tag = "🚨 SCAM" if v.get("scam", False) else "✅"
                text += f"{tag} **#{v['id']}** - {v['giver']}\n> {v['reason']}\n\n"

            embed.add_field(name="🕒 Last 3 Vouches", value=text, inline=False)
        else:
            embed.add_field(name="🕒 Last 3 Vouches", value="No vouches yet", inline=False)

        await interaction.response.send_message(embed=embed)


    # ================= /vouchconfig =================
    @tree.command(
        name="vouchconfig",
        description="Admin vouch management",
        guild=discord.Object(id=GUILD_ID)
    )
    async def vouchconfig(
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int,
        remove: bool,
        scam: bool = False
    ):

        await interaction.response.defer(ephemeral=False)

        if not is_admin(interaction, VOUCH_CONFIG_ROLE_ID):
            return await interaction.followup.send("❌ You don't have permission.")

        uid = str(user.id)
        data = get_user_data(uid)

        if remove:
            filtered = [v for v in data["vouches"] if v.get("scam", False) == scam]

            if not filtered:
                return await interaction.followup.send("❌ No matching vouches found.")

            removed = 0

            for v in filtered[::-1]:
                if removed >= amount:
                    break
                data["vouches"].remove(v)
                removed += 1

            save_user(data)

            return await interaction.followup.send(
                f"🗑️ Removed {removed} {'scam' if scam else 'normal'} vouches from {user.mention}"
            )

        else:
            for i in range(amount):
                vid = len(data["vouches"]) + 1

                data["vouches"].append({
                    "id": vid,
                    "giver": str(interaction.user),
                    "reason": "Admin adjustment",
                    "scam": scam,
                    "time": time.time()
                })

            save_user(data)

            return await interaction.followup.send(
                f"➕ Added {amount} {'scam' if scam else 'normal'} vouches to {user.mention}"
            )
