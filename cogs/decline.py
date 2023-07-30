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

class Decline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def getusernamefromid(self, id):
        users_ref = db.collection(u'users')
        users = users_ref.stream()

        for user in users:
            #print(user.to_dict()['username'])
            if user.to_dict()['id'] == str(id):
                return user.to_dict()['username']

    @bot.tree.command(name='decline', description='Decline an invite from a player in this server for a Game!') # type: ignore
    @app_commands.describe(opponent = 'The opponent\'s name you want to decline an invite from!')
    async def decline(self, interaction: discord.Interaction, opponent: str):
        await interaction.response.defer()

        try:
            users_ref = db.collection(u'users')
            users = users_ref.stream()

            for user in users:
                if user.to_dict()['id'] == interaction.user.id and user.to_dict()['is_inviting'] == True:
                    await interaction.followup.send('Error: You are already inviting someone!')
                    return

            opponent_doc = users_ref.document(opponent)
            opponent_name = opponent_doc.get().to_dict()['username']

            isopponentinviting = users_ref.document(str(opponent_name)).get().to_dict()['is_inviting']
            inviting_player = users_ref.document(str(opponent_name)).get().to_dict()['inviting_player']

            this_username = self.getusernamefromid(interaction.user.id)

            if inviting_player != this_username:
                if isopponentinviting == False:
                    await interaction.followup.send(f'Error: {opponent_name} is not inviting you!')
                    return

                await interaction.followup.send(f'Error: {opponent_name} is not inviting you!')
                return

            thisuser_doc = users_ref.document(str(this_username))

            thisuser_doc.set({'is_inviting': False}, merge=True)
            opponent_doc.set({'is_inviting': False}, merge=True)

            thisuser_doc.set({'inviting_player': ''}, merge=True)
            opponent_doc.set({'inviting_player': ''}, merge=True)

            await interaction.followup.send(f'You have declined {opponent_name}\'s invite!')
        except Exception as e:
            await interaction.followup.send(f'Error: {e}')

async def setup(bot):
    await bot.add_cog(Decline(bot))