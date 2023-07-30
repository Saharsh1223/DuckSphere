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

class Resign(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def getusernamefromid(self, id):
        users_ref = db.collection(u'users')
        users = users_ref.stream()

        for user in users:
            #print(user.to_dict()['username'])
            if user.to_dict()['id'] == str(id):
                return user.to_dict()['username']
            
    def movemovestocompletedgames(self, gameid):
        source_collection = db.collection(u'games')
        destination_collection = db.collection(u'completed_games')

        document_id = db.collection(u'games').document(f'game {str(gameid)}').id
        collection_id = (
            db.collection(u'games')
            .document(f'game {str(gameid)}')
            .collection(u'moves')
            .id
        )

        source_doc_ref = source_collection.document(document_id)
        source_doc = source_doc_ref.get().to_dict()

        collection_doc_ref = source_collection.document(document_id).collection(collection_id)
        collection_docs = collection_doc_ref.stream()

        destination_doc_ref = destination_collection.document(document_id)
        destination_doc_ref.set(source_doc)

        for doc in collection_docs:
            destination_doc_ref.collection(collection_id).document(doc.id).set(doc.to_dict())

        source_doc_ref.delete()
        
    def addusersdoctogame(self, source_collection, destination_collection, document_names, white_doc_name, black_doc_name):
        for document_name in document_names:
            source_doc_ref = source_collection.document(document_name)
            source_doc = source_doc_ref.get().to_dict()
            destination_doc_ref = destination_collection.document(document_name)
            destination_doc_ref.set(source_doc)

            if document_name == white_doc_name:
                renamedocumentname(destination_collection, document_name, 'white')
                #print(destination_collection_name)
            elif document_name == black_doc_name:
                renamedocumentname(destination_collection, document_name, 'black')
                #print(destination_collection_name)

            # source_collection.document(document_name).delete()
            
    def renamedocumentname(self, original_collection, original_document_id, new_document_name):
        original_doc_ref = original_collection.document(original_document_id)
        original_doc = original_doc_ref.get().to_dict()

        new_doc_ref = original_collection.document(new_document_name)
        new_doc_ref.set(original_doc)

        original_doc_ref.delete()

    def moveplayerstocompletedgames(self, gameid):
        source_collection = db.collection(u'games')
        destination_collection = db.collection(u'completed_games')

        document_id = db.collection(u'games').document(f'game {str(gameid)}').id
        collection_id = (
            db.collection(u'games')
            .document(f'game {str(gameid)}')
            .collection(u'players')
            .id
        )

        source_doc_ref = source_collection.document(document_id).collection(collection_id)
        source_docs = source_doc_ref.stream()

        destination_doc_ref = destination_collection.document(document_id).collection(collection_id)

        for doc in source_docs:
            destination_doc_ref.document(doc.id).set(doc.to_dict())
            source_doc_ref.document(doc.id).delete()
            
        source_collection.document(document_id).delete()

    @bot.tree.command(name='resign', description='Resign from the Game you\'re playing!')
    async def resign(self, interaction):
        await interaction.response.defer()
        #try:
        users_ref = db.collection(u'users')
        games_ref = db.collection(u'games')

        gameid = users_ref.document(self.getusernamefromid(interaction.user.id)).get().to_dict()['playing_game_id']

        gamedoc_ref = games_ref.document(f'game {str(gameid)}')
        print(gameid)

        if gamedoc_ref.get().exists:
            player_white = gamedoc_ref.collection(u'players').document(u'white')
            player_black = gamedoc_ref.collection(u'players').document(u'black')

            player_white_id = player_white.get().to_dict()['id']
            player_black_id = player_black.get().to_dict()['id']

            print(player_white_id)
            print(player_black_id)
            print(interaction.user.id)

            player_won_id = ''

            if str(interaction.user.id) == player_white_id:
                player_won_id = player_black_id
            elif str(interaction.user.id) == player_black_id:
                player_won_id = player_white_id
            # else:
            #     await interaction.followup.send('Error: You are not in this game!')
            #     return

            player_won_name = self.getusernamefromid(player_won_id)
            player_won_discord = await self.bot.fetch_user(player_won_id)

            user_won_ref = users_ref.document(player_won_name)
            user_lost_ref = users_ref.document(self.getusernamefromid(interaction.user.id))

            user_won_elo = user_won_ref.get().to_dict()['elo']
            user_lost_elo = user_lost_ref.get().to_dict()['elo']

            user_won_new_elo, user_lost_new_elo = elo.update_elo_rating(int(user_won_elo), int(user_lost_elo), 'win')
            print('User won elo: ' + str(user_won_new_elo) + 'User lost elo:' + str(user_lost_new_elo))

            user_won_ref.update({
                u'elo': user_won_new_elo,
                'is_playing': False,
                'is_playing_id': ''
            })

            user_lost_ref.update({
                u'elo': user_lost_new_elo,
                'is_playing': False,
                'is_playing_id': ''
            })

            gamedoc_ref.update({
                u'ischeckmate': False,
                u'isstalemate': False,
                u'player_won_id': player_won_id
            })

            fen = gamedoc_ref.get().to_dict()['fen']
            movesdone = gamedoc_ref.get().to_dict()['movesdone']
            player_white_name = player_white.get().to_dict()['username']
            player_black_name = player_black.get().to_dict()['username']

            with io.BytesIO() as image_binary:
                b = Image.open(io.BytesIO(gamedoc_ref.get().to_dict()['board_arr']))

                b.save(image_binary, 'PNG')
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='board.png')

                embed = discord.Embed(title=f'{player_white_name} vs {player_black_name}', description=f'**{player_won_name}** won by **Resignation**!', color=769656)
                embed.add_field(name='Info', value=f'Moves Done: `{movesdone}`\nFEN: ```{fen}```', inline=False)
                embed.add_field(name='Players', value=f'White: `{player_white_name}`\nBlack: `{player_black_name}`', inline=False)
                embed.set_author(name=f'Game | {player_won_name} won!', icon_url=f'{player_won_discord.avatar}')
                embed.set_footer(text=f'Game ID: {gameid}')
                embed.set_image(url='attachment://board.png')

                self.movemovestocompletedgames(gameid)
                self.moveplayerstocompletedgames(gameid)

                await interaction.followup.send(embed=embed, file=file)
        else:
            await interaction.followup.send(f'Error: A game with ID `{gameid}` does not exist in the database!')
            return
        #except Exception as e:
            #await interaction.followup.send(f'Error fetching game: {e}')

async def setup(bot):
    await bot.add_cog(Resign(bot))