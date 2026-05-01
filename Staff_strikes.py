import discord
import json, time

def setup(tree, discord, GUILD_ID, STAFF_ROLE_ID, STRIKE_FILE):

    def load_strikes():
        try:
            return json.load(open(STRIKE_FILE))
        except:
            return {}

    def save_strikes(data):
        with open(STRIKE_FILE, "w") as f:
            json.dump(data, f)

    strikes = load_strikes()

    @tree.command(
        name="staffstrike",
        description="Add or remove staff strikes",
        guild=discord.Object(id=GUILD_ID)
    )
    async def staffstrike(interaction: discord.Interaction, user: discord.Member, reason: str = None, remove: bool = False):

        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message("No permission ❌", ephemeral=True)
            return

        uid = str(user.id)

        if uid not in strikes:
            strikes[uid] = []

        # ================= REMOVE =================
        if remove:
            if len(strikes[uid]) == 0:
                await interaction.response.send_message("No strikes ❌", ephemeral=True)
                return

            removed = strikes[uid].pop()
            save_strikes(strikes)

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

        # 🔥 NEW: simple increment ID
        strike_id = len(strikes[uid]) + 1

        strikes[uid].append({
            "id": strike_id,
            "reason": reason,
            "time": time.time()
        })

        save_strikes(strikes)

        count = len(strikes[uid])

        embed = discord.Embed(
            title="🟣 Staff Strike",
            description=f"Strike to {user.mention}",
            color=discord.Color.purple()
        )

        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Strikes", value=f"{count}/3", inline=False)
        embed.set_footer(text=f"Strike ID: {strike_id}")

        await interaction.response.send_message(embed=embed)
