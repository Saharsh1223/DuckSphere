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

class Move(commands.Cog):
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
                self.renamedocumentname(destination_collection, document_name, 'white')
                #print(destination_collection_name)
            elif document_name == black_doc_name:
                self.renamedocumentname(destination_collection, document_name, 'black')
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

    @bot.tree.command(name='move', description='Move a piece in the Game you\'re playing!') #type: ignore
    @app_commands.describe(moveto = 'Where you are moving the piece to?')
    @app_commands.describe(movefrom = 'Where you are moving the piece from?')
    async def move(self, interaction: discord.Interaction, movefrom: str, moveto: str):
        await interaction.response.defer()

        #try:
        users_ref = db.collection(u'users')
        games_ref = db.collection(u'games')

        gameid = users_ref.document(self.getusernamefromid(interaction.user.id)).get().to_dict()['playing_game_id']

        gamedoc_ref = games_ref.document(f'game {str(gameid)}')

        if gamedoc_ref.get().exists:
            cb_ = chess.Board(gamedoc_ref.get().to_dict()['fen'])
            b_ = gamedoc_ref.get().to_dict()['board_arr']

            movesdone = gamedoc_ref.get().to_dict()['movesdone']

            image = Image.open(io.BytesIO(b_))

            cb, b, fen, pgn, isover = board.movepiece(movefrom, moveto, image, cb_) # pyright: ignore

            user_white = gamedoc_ref.collection(u'players').document(u'white')
            user_black = gamedoc_ref.collection(u'players').document(u'black')

            user_white_discord_name = user_white.get().to_dict()['discord_username']
            user_black_discord_name = user_black.get().to_dict()['discord_username']

            user_white_name = user_white.get().to_dict()['username']
            user_black_name = user_black.get().to_dict()['username']

            user_white_elo = user_white.get().to_dict()['elo']
            user_black_elo = user_black.get().to_dict()['elo']

            turn = cb.turn # pyright: ignore

            if turn == chess.WHITE:
                turn = 'black'
            elif turn == chess.BLACK:
                turn = 'white'

            if (
                (turn == 'black' and user_black_discord_name == interaction.user.name)
                or 
                (turn == 'white' and user_white_discord_name == interaction.user.name)
            ):
                await interaction.followup.send('Error: It is not your turn!', ephemeral=True)
                return
            
            if b is None and fen is None and pgn is None and isover is None:
                await interaction.followup.send(f'Error: {moveto} is an invalid move!', ephemeral=True)
                return

            if isover == 'checkmate':
                username_won = ''
                username_lost = ''

                if turn == 'black':
                    username_won = user_black_name
                    username_lost = user_white_name
                elif turn == 'white':
                    username_won = user_white_name
                    username_lost = user_black_name

                user_won_ref = users_ref.document(username_won)
                user_lost_ref = users_ref.document(username_lost)

                user_won_elo = user_won_ref.get().to_dict()['elo']
                user_lost_elo = user_lost_ref.get().to_dict()['elo']

                user_won_new_elo, user_lost_new_elo = elo.update_elo_rating(int(user_won_elo), int(user_lost_elo), 'win')
                #print('User won elo: ' + str(user_won_new_elo) + 'User lost elo:' + str(user_lost_new_elo))

                player_won_id = user_won_ref.get().to_dict()['id']

                b_arr = board.image_to_byte_array(b)
                gamedoc_ref.set({'id': gameid, 'fen': fen, 'board_arr': b_arr, 'movesdone': movesdone + 1, 'ischeckmate': True, 'isstalemate': False, 'player_won_id': player_won_id}, merge=True)

                user_white.update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})
                users_ref.document(user_white_name).update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})

                user_black.update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})
                users_ref.document(user_black_name).update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})

                if username_won == user_white_discord_name :
                    user_white.update({'wins': user_white.get().to_dict()['wins'] + 1, 'elo': str(user_won_new_elo)})
                    user_black.update({'losses': user_black.get().to_dict()['losses'] + 1, 'elo': str(user_lost_new_elo)})

                    users_ref.document(user_white_name).update({'wins': users_ref.document(user_white_name).get().to_dict()['wins'] + 1, 'elo': str(user_won_new_elo)})
                    users_ref.document(user_black_name).update({'losses': users_ref.document(user_black_name).get().to_dict()['losses'] + 1, 'elo': str(user_lost_new_elo)})
                elif username_won == user_black_discord_name :
                    user_white.update({'losses': user_white.get().to_dict()['losses'] + 1, 'elo': str(user_lost_new_elo)})
                    user_black.update({'wins': user_black.get().to_dict()['wins'] + 1, 'elo': str(user_won_new_elo)})

                    users_ref.document(user_white_name).update({'losses': users_ref.document(user_white_name).get().to_dict()['losses'] + 1, 'elo': str(user_lost_new_elo)})
                    users_ref.document(user_black_name).update({'wins': users_ref.document(user_black_name).get().to_dict()['wins'] + 1, 'elo': str(user_won_new_elo)})

                with io.BytesIO() as image_binary:
                    b.save(image_binary, 'PNG') # pyright: ignore
                    image_binary.seek(0)

                    file = discord.File(fp=image_binary, filename='board.png')

                    embed = discord.Embed(title=f'**{user_white_name}** vs **{user_black_name}**', description=f'**{username_won}** won with **Checkmate**, Game ID: `{gameid}`', color=0x00ff00)
                    embed.set_image(url='attachment://board.png')

                self.movemovestocompletedgames(gameid)
                self.moveplayerstocompletedgames(gameid)
                await interaction.followup.send(embed=embed, file=file)
                await interaction.followup.send(f'{moveto} is Checkmate and the Game is over!', ephemeral=True)
                return

            if isover == 'stalemate':
                user_white.update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})
                users_ref.document(user_white_name).update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})

                user_black.update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})
                users_ref.document(user_black_name).update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})

                b_arr = board.image_to_byte_array(b)
                gamedoc_ref.set({'id': gameid, 'fen': fen, 'board_arr': b_arr, 'movesdone': movesdone + 1, 'ischeckmate': False, 'isstalemate': True}, merge=True)

                with io.BytesIO() as image_binary:
                    b.save(image_binary, 'PNG') # pyright: ignore
                    image_binary.seek(0)

                    file = discord.File(fp=image_binary, filename='board.png')

                    embed = discord.Embed(title=f'**{user_white_name}** vs **{user_black_name}**', description=f'**{user_white_discord_name}** drew to **{user_black_discord_name}** with Stalemate, Game ID: `{gameid}`', color=0x00ff00)
                    embed.set_image(url='attachment://board.png')

                self.movemovestocompletedgames(gameid)
                self.moveplayerstocompletedgames(gameid)
                await interaction.followup.send(embed=embed, file=file)
                await interaction.followup.send(f'{moveto} is Stalemate and the Game is over!', ephemeral=True)
                return

            b_arr = board.image_to_byte_array(b)

            gamedoc_ref = db.collection(u'games').document(f'game {str(gameid)}')
            gamedoc_ref.set({'id': gameid, 'fen': fen, 'board_arr': b_arr, 'movesdone': movesdone + 1, 'ischeckmate': False, 'isstalemate': False})

            moves_ref = (
                db.collection(u'games')
                .document(f'game {str(gameid)}')
                .collection(u'moves')
                .document(f'move {str(movesdone + 1)}')
            )
            moves_ref.set({'move': movefrom + moveto})

            with io.BytesIO() as image_binary:
                b.save(image_binary, 'PNG') # pyright: ignore
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='board.png')

                nextturn = ''
                if turn == 'black':
                    nextturn = 'white'

                elif turn == 'white':
                    nextturn = 'black'
                embed = discord.Embed(title=f'**{user_white_name}** vs **{user_black_name}**', description=f'Game ID: `{gameid}`, {nextturn}\'s turn!', color=0x00ff00)
                embed.set_image(url='attachment://board.png')

                await interaction.followup.send(embed=embed, file=file)
        else:
            await interaction.followup.send(f'Error: A Game with ID `{gameid}` does not exist in the database!')
            return
        #except Exception as e:
            #await interaction.followup.send(f'Error: {e}')

async def setup(bot):
    await bot.add_cog(Move(bot))