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

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def getusernamefromid(self, id):
        users_ref = db.collection(u'users')
        users = users_ref.stream()

        for user in users:
            #print(user.to_dict()['username'])
            if user.to_dict()['id'] == str(id):
                return user.to_dict()['username']

    @bot.tree.command(name='invite', description='Invite a player in this server to play a Game!') # type: ignore
    @app_commands.describe(opponent = 'The opponent name want to invite')
    async def invite(self, interaction: discord.Interaction, opponent: str):
        await interaction.response.defer()

        try:
            users_ref = db.collection(u'users')
            username_doc = users_ref.document(opponent)

            username = username_doc.get().to_dict()['username']
            discord_id = username_doc.get().to_dict()['id']
            discord_member = await self.bot.fetch_user(discord_id)

            if username != opponent:
                await interaction.followup.send(f'Error: {discord_member.mention} is not registered!')
                return

            if discord_member == interaction.user:
                await interaction.followup.send('Error: You cannot invite yourself!')
                return

            thisusername = self.getusernamefromid(interaction.user.id)
            thisuser_doc = users_ref.document(str(thisusername))

            thisdiscord_member = await self.bot.fetch_user(interaction.user.id)

            thisuser_doc.update({'is_inviting': True, 'inviting_player': f'{username}'})

            channel = await discord_member.create_dm()
            em = discord.Embed(title=f'Game invitation from {thisusername}', description=f'{thisdiscord_member.mention} has invited you to a Game of Chess! To accept the invite, use `/accept {thisusername}`!', color=0x00ff00)
            em.set_thumbnail(url=thisdiscord_member.avatar)
            em.set_footer(text=f'User ID: {thisdiscord_member.id}')
            await channel.send(embed=em)

            await interaction.followup.send(f'Invite successfully sent to {discord_member.mention} a.k.a. **{username}**!')
        except Exception as e:
            await interaction.followup.send(f'Error: {e}')

async def setup(bot):
    await bot.add_cog(Invite(bot))