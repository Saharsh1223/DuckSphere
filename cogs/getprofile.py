import discord
from discord import app_commands # type: ignore
from discord.ext import commands
#from discord import ButtonStyle, Button
from PIL import Image
import random
import board
import elo
import chess # type: ignore
import io
import firebase_admin # type: ignore
from firebase_admin import credentials # type: ignore
from firebase_admin import firestore # type: ignore
#from py_dotenv import read_dotenv # type: ignore
import os

bot = commands.Bot(command_prefix='c.', intents=discord.Intents.all())

#cred = credentials.Certificate('secret-key.json')
#app = firebase_admin.initialize_app(cred)
db = firestore.client()

class GetProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.tree.command(name='getprofile', description='Get a profile from the database!') #type: ignore
    @app_commands.describe(username = 'The username of the profile you want to get!')
    async def getprofile(self, interaction, username: str):
        await interaction.response.defer()
        try:
            userdoc_ref = db.collection(u'users').document(username)
            if userdoc_ref.get().exists:
                userid = userdoc_ref.get().to_dict()['id']
                user = await self.bot.fetch_user(userid)

                embed = discord.Embed(
                    title=' ',
                    description=f'ID: `{userdoc_ref.get().to_dict()["id"]}`',
                    color=0x00ff00,
                )
                embed.set_author(name=f'{username} | User Profile', icon_url=f'{user.avatar}')
                embed.add_field(name='Info', value=f'Username: `{userdoc_ref.get().to_dict()["username"]}`\nDiscord Username: `{userdoc_ref.get().to_dict()["discord_username"]}`\nElo: `{userdoc_ref.get().to_dict()["elo"]}`\nWins: `{userdoc_ref.get().to_dict()["wins"]}`\nLosses: `{userdoc_ref.get().to_dict()["losses"]}`\nDraws: `{userdoc_ref.get().to_dict()["draws"]}`\nIs Inviting: `{userdoc_ref.get().to_dict()["is_inviting"]}`\nIs Playing: `{userdoc_ref.get().to_dict()["is_playing"]}`', inline=False)

                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f'Error: Profile with username `{username}` does not exist!')
        except Exception as e:
            await interaction.followup.send(f'Error: {e}')
    
async def setup(bot):
    await bot.add_cog(GetProfile(bot))