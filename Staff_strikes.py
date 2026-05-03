import discord
import time
import os
from pymongo import MongoClient

def setup(tree, discord, GUILD_ID, STAFF_ROLE_ID, MONGO_URI):

    client = MongoClient(MONGO_URL)
    db = client["staff_system"]
    strikes = db["strikes"]

    @tree.command(
        name="staffstrike",
        description="Add or remove staff strikes",
        guild=discord.Object(id=GUILD_ID)
    )
    async def staffstrike(
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str = None,
        remove: bool = False
    ):

        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message("No permission ❌", ephemeral=True)
            return

        uid = str(user.id)
        data = strikes.find_one({"user_id": uid})

        if not data:
            data = {"user_id": uid, "count": 0, "records": []}

        # ================= REMOVE =================
        if remove:
            if data["count"] == 0:
                await interaction.response.send_message("No strikes ❌", ephemeral=True)
                return

            removed = data["records"][-1]

            strikes.update_one(
                {"user_id": uid},
                {
                    "$pop": {"records": 1},
                    "$inc": {"count": -1}
                }
            )

            embed = discord.Embed(
                title="🟡 Strike Removed",
                description=f"Removed 1 strike from {user.mention}",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Strike ID: {removed['id']}")

            await interaction.response.send_message(embed=embed)
            return

        # ================= ADD =================
        if not reason:
            await interaction.response.send_message("You must provide a reason ❌", ephemeral=True)
            return

        strike_id = data["count"] + 1

        strikes.update_one(
            {"user_id": uid},
            {
                "$push": {
                    "records": {
                        "id": strike_id,
                        "reason": reason,
                        "time": time.time()
                    }
                },
                "$inc": {"count": 1}
            },
            upsert=True
        )

        new_count = data["count"] + 1

        # ================= 3/3 RESET =================
        if new_count >= 3:

            strikes.update_one(
                {"user_id": uid},
                {"$set": {"count": 0, "records": []}}
            )

            embed = discord.Embed(
                title="🚨 DEMOTION TRIGGERED",
                description=f"{user.mention} has reached **3/3 strikes**",
                color=discord.Color.red()
            )

            embed.add_field(name="Status", value="⚠️ Demotion / Action Required", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)

            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(
            title="🟣 Staff Strike",
            description=f"Strike to {user.mention}",
            color=discord.Color.purple()
        )

        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Strikes", value=f"{new_count}/3", inline=False)
        embed.set_footer(text=f"Strike ID: {strike_id}")

        await interaction.response.send_message(embed=embed)
