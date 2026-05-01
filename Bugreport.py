import discord
from discord import app_commands

def setup(tree: app_commands.CommandTree, guild_id: int):

    @tree.command(
        name="bugreport",
        description="Report a bug",
        guild=discord.Object(id=guild_id)
    )
    async def bugreport(interaction: discord.Interaction, info: str):

        BUG_CHANNEL_ID = 1499576814643707994

        channel = interaction.guild.get_channel(BUG_CHANNEL_ID)

        if channel is None:
            await interaction.response.send_message("❌ Bug report channel not found.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🐞 New Bug Report",
            description=info,
            color=discord.Color.red()
        )

        embed.add_field(
            name="👤 Reported by",
            value=f"{interaction.user} (`{interaction.user.id}`)",
            inline=False
        )

        embed.set_footer(text="Bug Report System")

        await channel.send(embed=embed)

        await interaction.response.send_message("✅ Your bug report has been sent!", ephemeral=True)
