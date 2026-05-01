import discord
from discord.ext import commands

@commands.command()
async def bugreport(ctx, *, info: str = None):
    if info is None:
        await ctx.send("❌ Please write your bug report. Example: `!bugreport vouch command not working`")
        return

    # 👇 CHANGE THIS to your bug report channel ID
    BUG_CHANNEL_ID = 1499576814643707994

    channel = ctx.guild.get_channel(BUG_CHANNEL_ID)

    if channel is None:
        await ctx.send("❌ Bug report channel not found.")
        return

    embed = discord.Embed(
        title="🐞 New Bug Report",
        description=info,
        color=discord.Color.red()
    )

    embed.add_field(
        name="👤 Reported by",
        value=f"{ctx.author} (`{ctx.author.id}`)",
        inline=False
    )

    embed.set_footer(text="Bug Report System")

    await channel.send(embed=embed)

    await ctx.send("✅ Your bug report has been sent!")
