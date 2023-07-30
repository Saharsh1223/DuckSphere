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

class Accept(commands.Cog):
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

    @bot.tree.command(name='accept', description='Accept an invite from a player in this server for a Game!') # type: ignore
    @app_commands.describe(opponent = 'The opponent\'s name you want to accept an invite from!')
    async def accept(self, interaction, opponent: str):
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

            opponent_doc.update({'is_inviting': False, 'inviting_player': ''})

            thisuser_doc = users_ref.document(str(this_username))

            n = random.randint(1, 2)

            white = None
            black = None

            if n == 1:
                white = this_username
                black = opponent
            else:
                white = opponent
                black = this_username

            white_doc = users_ref.document(str(white))
            black_doc = users_ref.document(str(black))

            white_username = white_doc.get().to_dict()['username']
            black_username = black_doc.get().to_dict()['username']

            white_discord_id = white_doc.get().to_dict()['id']
            black_discord_id = black_doc.get().to_dict()['id']

            white_elo = white_doc.get().to_dict()['elo']
            black_elo = black_doc.get().to_dict()['elo']

            white_discord_member = await self.bot.fetch_user(white_discord_id)
            black_discord_member = await self.bot.fetch_user(black_discord_id)

            b = board.createboard()
            b_arr = board.image_to_byte_array(b)
            cb = chess.Board()
            gameid = board.generateGameID()

            gamedoc_ref = db.collection(u'games').document(f'game {str(gameid)}')
            gamedoc_ref.set({'id': gameid, 'fen': cb.fen(), 'board_arr': b_arr, 'movesdone': 0, 'ischeckmate': cb.is_checkmate(), 'isstalemate': cb.is_stalemate()})

            players_ref = (
                db.collection(u'games')
                .document(f'game {str(gameid)}')
                .collection(u'players')
            )

            source_collection = db.collection(u'users')
            #destination_collection = db.collection(u'games').document('game ' + str(gameid)).collection(u'players')
            source_collection_name = source_collection.id
            self.addusersdoctogame(source_collection, players_ref, [str(white), str(black)], white_username, black_username)

            with io.BytesIO() as image_binary:
                b.save(image_binary, 'PNG')
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='board.png')
                embed = discord.Embed(title=f'**{white_username}**: **{white_elo}** elo vs **{black_username}**: **{black_elo}** elo', description=f'Game ID: `{gameid}`, {white_discord_member.mention} plays as White and {black_discord_member.mention} plays as Black!', color=0x00ff00)
                embed.set_image(url='attachment://board.png')

                thisuser_doc.set({'is_playing': True, 'playing_game_id': f'{gameid}'}, merge=True)
                opponent_doc.set({'is_playing': True, 'playing_game_id': f'{gameid}'}, merge=True)

                opponent_doc.set({'is_inviting': False}, merge=True)

                embed2 = discord.Embed(title=f'', description=f'', color=0x00ff00)
                embed2.add_field(name='White', value=f'**{white_username}** (**{white_elo}** elo)', inline=False)
                embed2.add_field(name='Black', value=f'**{black_username}** (**{black_elo}** elo)', inline=False)

                white_wins_rating, black_losses_rating = elo.update_elo_rating(int(white_elo), int(black_elo), 'win')
                white_win_rating_diff = white_wins_rating - int(white_elo)
                black_loss_rating_diff = int(black_elo) - black_losses_rating

                white_losses_rating, black_wins_rating = elo.update_elo_rating(int(black_elo), int(white_elo), 'win')
                white_loss_rating_diff = white_losses_rating - int(white_elo)
                black_win_rating_diff = int(black_elo) - black_wins_rating

                embed2.add_field(name=f'If {white_username} wins', value=f'**{white_username}** will gain **{white_win_rating_diff}** elo and **{black_username}** will lose **{black_loss_rating_diff}** elo', inline=False)
                embed2.add_field(name=f'If {black_username} wins', value=f'**{black_username}** will gain **{black_win_rating_diff}** elo and **{white_username}** will lose **{white_loss_rating_diff}** elo', inline=False)

                embed2.set_footer(text=f'Game ID: {gameid}')

                await interaction.followup.send(f'{white_discord_member.mention} vs {black_discord_member.mention}', embed=embed2, ephemeral=True)
                await interaction.followup.send(embed=embed, file=file)
        except Exception as e:
            await interaction.followup.send(f'Error: {e}')

async def setup(bot):
    await bot.add_cog(Accept(bot))