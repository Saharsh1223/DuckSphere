import discord
from discord.ext import commands
from discord import app_commands

bot = commands.Bot(command_prefix='c.', intents=discord.Intents.all())

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.tree.command(name='help', description='Get help with the bot!') # type: ignore
    async def help(self, interaction):
        await interaction.response.defer()

        embed = discord.Embed(title='Help', description='Help with the bot!', color=0x00ff00)
        embed.add_field(name='About me', value='A Discord Chess Bot available for free on the platform!')
        embed.add_field(name='Commands', value='`/invite <username>` to invite a player to a Game of Chess!\n`/accept <username>` to accept an invite from a player!\n`/decline <username>` to decline an invite from a player!\n`/move <movefrom> <moveto>` to move a piece from <movefrom> to <moveto> in an existing Chess Game!\n`/resign` to resign from an existing Chess Game!\n`/addprofile <username>` to create your profile with the given username!\n`/getprofile <username>` to get a profile with the given username!\n`/getgame <gameid>` to get a existing Game in the Database using the Game ID!\n`/help` to view this command!', inline=False)

        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.set_footer(text='Solo made by @saharshdev, credits to Chess.com for the Board and Piece images!')

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))