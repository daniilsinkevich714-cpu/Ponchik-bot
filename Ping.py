import discord
from discord import app_commands

def setup(tree: app_commands.CommandTree, guild_id: int):

    GUILD = discord.Object(id=guild_id)

    @tree.command(
        name="ping",
        description="Check bot latency",
        guild=GUILD
    )
    async def ping(interaction: discord.Interaction):
        latency = round(interaction.client.latency * 1000)

        await interaction.response.send_message(
            f"🏓 Pong! `{latency}ms`"
        )
