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

cred = credentials.Certificate('secret-key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

@bot.event
async def on_ready():
    print('change this part')
    
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded cog: {filename}")
    
    print(f'Logged in as {bot.user} (ID: {bot.user.id})') #type: ignore
    try:
        synced = await bot.tree.sync() #type: ignore
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(e)
        
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('Hey there! this is the message i send when i join a server')
        break

# class Buttons(discord.ui.View):
#     def __init__(self):
#         super().__init__()
#         self.value = None

#     @discord.ui.button(label='Beginning', style=discord.ButtonStyle.green)
#     async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.edit_message(content='Start')

#     @discord.ui.button(label='Left', style=discord.ButtonStyle.green)
#     async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.edit_message(content='Left')

#     @discord.ui.button(label='Right', style=discord.ButtonStyle.green)
#     async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.edit_message(content='Right')

#     @discord.ui.button(label='End', style=discord.ButtonStyle.green)
#     async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.edit_message(content='End')

token = 'MTEyMzYwMDkxMTcwOTc4MjE0Ng.GHcqcb.uYgnb8gHxpOjZBglppcI0xou9k4E7uOUyLC3gU'
bot.run(token)