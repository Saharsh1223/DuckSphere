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

class GetGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def getusernamefromid(self, id):
        users_ref = db.collection(u'users')
        users = users_ref.stream()

        for user in users:
            #print(user.to_dict()['username'])
            if user.to_dict()['id'] == str(id):
                return user.to_dict()['username']

    @bot.tree.command(name='getgame', description='Get a Game from the database!') #type: ignore
    @app_commands.describe(gameid = 'The ID of the Game you want to get!')
    async def getgame(self, interaction, gameid: str):
        await interaction.response.defer()
        try:
            gamedoc_ref = db.collection(u'completed_games').document(f'game {gameid}')
            if gamedoc_ref.get().exists:

                fen = gamedoc_ref.get().to_dict()['fen']
                movesdone = gamedoc_ref.get().to_dict()['movesdone']

                player_white = gamedoc_ref.collection(u'players').document(u'white')
                player_black = gamedoc_ref.collection(u'players').document(u'black')

                player_white_name = player_white.get().to_dict()['username']
                player_black_name = player_black.get().to_dict()['username']

                is_checkmate = gamedoc_ref.get().to_dict()['ischeckmate']
                is_stalemate = gamedoc_ref.get().to_dict()['isstalemate']

                player_won_id = gamedoc_ref.get().to_dict()['player_won_id']
                player_won_name = self.getusernamefromid(player_won_id)
                player_won_discord = await self.bot.fetch_user(player_won_id)

                won_by_what = ''

                if is_checkmate == True:
                    won_by_what = 'Checkmate'
                elif is_stalemate == True:
                    won_by_what = 'Stalemate'
                elif is_checkmate == False and is_stalemate == False:
                    won_by_what = 'Resignation'

                with io.BytesIO() as image_binary:
                    b = Image.open(io.BytesIO(gamedoc_ref.get().to_dict()['board_arr']))

                    b.save(image_binary, 'PNG')
                    image_binary.seek(0)

                    file = discord.File(fp=image_binary, filename='board.png')

                    embed = discord.Embed(title=f'{player_white_name} vs {player_black_name}', description=f'**{player_won_name}** won by **{won_by_what}**!', color=0x00ff00)
                    embed.add_field(name='Info', value=f'Moves Done: `{movesdone}`\nFEN: ```{fen}```', inline=False)
                    embed.add_field(name='Players', value=f'White: `{player_white_name}`\nBlack: `{player_black_name}`', inline=False)
                    embed.set_author(name=f'Game | {player_won_name} won!', icon_url=f'{player_won_discord.avatar}')
                    embed.set_footer(text=f'Game ID: {gameid}')
                    embed.set_image(url='attachment://board.png')

                    await interaction.followup.send(embed=embed, file=file)
            else:
                await interaction.followup.send(f'Error: A game with ID `{gameid}` does not exist in the database!')
                return
        except Exception as e:
            await interaction.followup.send(f'Error fetching game: {e}')

async def setup(bot):
    await bot.add_cog(GetGame(bot))