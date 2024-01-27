import discord
from discord.ext import commands
from discord import app_commands

bot = commands.Bot(command_prefix='c.', intents=discord.Intents.all())

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.tree.command(name='ping', description='Get my current Latency!')
    async def ping(self, interaction: discord.Interaction):
        ping1 = f"{str(round(self.bot.latency * 1000))} ms"
        embed = discord.Embed(
            title="**Pong!**", description=f"**{ping1}**", color=0xAFDAFC
        )
        await interaction.response.send_message(embed = embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))