import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

bot = commands.Bot(command_prefix='c.', intents=discord.Intents.all())

cred = credentials.Certificate('secret-key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

@bot.event
async def on_ready():
    print('Bot is ready.')

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded cog: {filename}")

    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(e)

@bot.event
async def on_guild_join(guild):
    if guild.text_channels:
        channel = guild.text_channels[0]
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('Hey there! this is the message I send when I join a server')

token = config['token']
bot.run(token)