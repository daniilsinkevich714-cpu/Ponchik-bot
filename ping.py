import discord
from discord import app_commands

def setup(tree: app_commands.CommandTree, guild_id: int):

    @tree.command(
        name="ping",
        description="Check bot latency",
        guild=discord.Object(id=guild_id)
    )
    async def ping(interaction: discord.Interaction):
        latency = round(interaction.client.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! {latency}ms")