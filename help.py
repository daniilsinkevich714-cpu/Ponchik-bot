import discord
from discord import app_commands
print("✅ HELP MODULE LOADED")

GUILD_ID = 1471293085706223703

def setup(tree: app_commands.CommandTree):

    @tree.command(
        name="help",
        description="Shows all bot commands",
        guild=discord.Object(id=GUILD_ID)
    )
    async def help_command(interaction: discord.Interaction):

        embed = discord.Embed(
            title="📖 Ponchik Galaxy Help Menu",
            description="All available commands in this bot:",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="👤 Member Commands",
            value=(
                "/vouch user reason scam:true/false\n"
                "/checkvouches @user\n"
                "/ping\n"
                "/bugreport info"
            ),
            inline=False
        )

        embed.add_field(
            name="🛡️ Staff Commands",
            value=(
                "/staffstrike @user reason remove:true/false\n"
                "/vouchconfig @user amount remove:true/false scam:true/false"
            ),
            inline=False
        )

        embed.add_field(
            name="📊 Info",
            value="A bot made to help ponchik galaxy.",
            inline=False
        )

        embed.set_footer(text="Donut SMP Bot • Help System")

        await interaction.response.send_message(embed=embed)
