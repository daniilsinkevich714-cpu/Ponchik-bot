@tree.command(
    name="help",
    description="Shows all bot commands",
    guild=discord.Object(id=GUILD_ID)
)
async def help_command(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📖 Donut SMP Help Menu",
        description="All available commands in this bot:",
        color=discord.Color.purple()
    )

    # ================= MEMBER COMMANDS =================
    embed.add_field(
        name="👤 Member Commands",
        value=(
            "/vouch user reason scam:true/false - Give a vouch or scam report\n"
            "/checkvouches @user - View user vouches\n"
            "/ping - Check bot latency\n"
            "/bugreport info - Report a bug"
        ),
        inline=False
    )

    # ================= STAFF COMMANDS =================
    embed.add_field(
        name="🛡️ Staff Commands",
        value=(
            "/staffstrike @user reason remove:true/false - Manage staff strikes\n"
            "/vouchconfig @user amount remove:true/false scam:true/false - Manage vouches (Admin only)"
        ),
        inline=False
    )

    # ================= INFO =================
    embed.add_field(
        name="📊 Info",
        value=(
            "This bot is used for Donut SMP trading reputation.\n"
            "Use commands responsibly."
        ),
        inline=False
    )

    embed.set_footer(text="Donut SMP Bot • Help System")

    await interaction.response.send_message(embed=embed, ephemeral=True)
