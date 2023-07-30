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

class AddProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def getusernamefromid(self, id):
        users_ref = db.collection(u'users')
        users = users_ref.stream()

        for user in users:
            #print(user.to_dict()['username'])
            if user.to_dict()['id'] == str(id):
                return user.to_dict()['username']

    @bot.tree.command(name='addprofile', description='Add your profile to the database!') #type: ignore
    @app_commands.describe(username = 'THe username you want for your profile!')
    @app_commands.choices(elo=[
        app_commands.Choice(name='New to Chess: 400', value='400'),
        app_commands.Choice(name='Beginner: 800', value='800'),
        app_commands.Choice(name='Intermediate: 1200', value='1200'),
        app_commands.Choice(name='Advanced: 1600', value='1600'),
        app_commands.Choice(name='Expert: 2000', value='2000'),
    ])
    @app_commands.describe(elo = 'What do you want your elo to be? (Choose visely as you cannot change it later)')
    async def addprofile(self, interaction, username: str, elo: str):
        await interaction.response.defer()
        try:
            userdoc_ref = db.collection(u'users').document(username)
            x = self.getusernamefromid(interaction.user.id)
            
            if x != None:
                await interaction.followup.send(f'Error: You already have a profile registered with the name `{x}`')
                return
            
            if userdoc_ref.get().exists:
                await interaction.followup.send('Error: You already have a profile!')
                return
            userdoc_ref.set({'id': str(interaction.user.id), 'username': username, 'discord_username': interaction.user.name, 'wins': 0, 'losses': 0, 'draws': 0, 'is_inviting': False, 'is_playing': False, 'playing_game_id': '', 'inviting_player': '', 'elo': f'{elo}'})
            await interaction.followup.send(f'Added profile with username as `{username}`!')
        except Exception as e:
            await interaction.followup.send(f'Error: {e}')

async def setup(bot):
    await bot.add_cog(AddProfile(bot))