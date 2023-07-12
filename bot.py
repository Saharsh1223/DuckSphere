import discord
from discord import app_commands
from discord.ext import commands
#from discord import ButtonStyle, Button
from PIL import Image
import random
import board
import chess
import io
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from py_dotenv import read_dotenv
import os

bot = commands.Bot(command_prefix='c.', intents=discord.Intents.all())

cred = credentials.Certificate('secret-key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(e)

@bot.tree.command(name='synccommands')
async def synccommands(interaction):
    await interaction.response.defer()

    try:
        synced = await bot.tree.sync()
        await interaction.followup.send(f'Synced {len(synced)} commands')
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        await interaction.followup.send(f'Error: {e}')

# @bot.tree.command(name='startgame', description='Starts a Game of Chess!')
# async def startgame(interaction):
#     await interaction.response.defer()

#     try:
#         b = board.createboard()
#         b_arr = board.image_to_byte_array(b)
#         cb = chess.Board()
#         gameid = board.generateGameID()

#         gamedoc_ref = db.collection(u'games').document('game ' + str(gameid))
#         gamedoc_ref.set({'id': gameid, 'fen': cb.fen(), 'board_arr': b_arr, 'movesdone': 0, 'ischeckmate': cb.is_checkmate(), 'isstalemate': cb.is_stalemate()})

#         with io.BytesIO() as image_binary:
#             b.save(image_binary, 'PNG')
#             image_binary.seek(0)

#             file = discord.File(fp=image_binary, filename='board.png')

#             embed = discord.Embed(title='**xxx** vs **yyy**', description=f'Game ID: `{gameid}`, **xxx** plays as White and **yyy** plays as Black!', color=769656)
#             embed.set_image(url='attachment://board.png')

#             await interaction.followup.send(embed=embed, file=file)
#     except Exception as e:
#         await interaction.followup.send(f'Error: {e}')

@bot.tree.command(name='addprofile', description='Add your profile to the database!')
@app_commands.describe(username = 'THe username you want for your profile!')
async def addprofile(interaction, username: str):
    await interaction.response.defer()
    try:
        userdoc_ref = db.collection(u'users').document(username)
        if userdoc_ref.get().exists:
            await interaction.followup.send('Error: You already have a profile!')
            return
        userdoc_ref.set({'id': str(interaction.user.id), 'username': username, 'discord_username': interaction.user.name, 'wins': 0, 'losses': 0, 'draws': 0, 'is_inviting': False, 'is_playing': False, 'playing_game_id': '', 'inviting_player': ''})
        await interaction.followup.send(f'Added profile with username as `{username}`!')
    except Exception as e:
        await interaction.followup.send(f'Error: {e}')

@bot.tree.command(name='getprofile', description='Get a profile from the database!')
@app_commands.describe(username = 'The username of the profile you want to get!')
async def getprofile(interaction, username: str):
    await interaction.response.defer()
    try:
        userdoc_ref = db.collection(u'users').document(username)
        if userdoc_ref.get().exists:
            userid = userdoc_ref.get().to_dict()['id']
            user = await bot.fetch_user(userid)

            embed = discord.Embed(
                title=' ',
                description=f'ID: `{userdoc_ref.get().to_dict()["id"]}`',
                color=769656,
            )
            embed.set_author(name=f'{username} | User Profile', icon_url=f'{user.avatar}')
            embed.add_field(name='Info', value=f'Username: `{userdoc_ref.get().to_dict()["username"]}`\nDiscord Username: `{userdoc_ref.get().to_dict()["discord_username"]}`\nWins: `{userdoc_ref.get().to_dict()["wins"]}`\nLosses: `{userdoc_ref.get().to_dict()["losses"]}`\nDraws: `{userdoc_ref.get().to_dict()["draws"]}`\nIs Inviting: `{userdoc_ref.get().to_dict()["is_inviting"]}`\nIs Playing: `{userdoc_ref.get().to_dict()["is_playing"]}`', inline=False)

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f'Error: Profile with username `{username}` does not exist!')
    except Exception as e:
        await interaction.followup.send(f'Error: {e}')


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

@bot.tree.command(name='getgame', description='Get a Game from the database!')
@app_commands.describe(gameid = 'The ID of the Game you want to get!')
async def getgame(interaction, gameid: str):
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
            player_won_name = getusernamefromid(player_won_id)
            player_won_discord = await bot.fetch_user(player_won_id)

            won_by_what = ''

            if is_checkmate == True:
                won_by_what = 'Checkmate'
            elif is_stalemate == True:
                won_by_what = 'Stalemate'

            with io.BytesIO() as image_binary:
                b = Image.open(io.BytesIO(gamedoc_ref.get().to_dict()['board_arr']))

                b.save(image_binary, 'PNG')
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='board.png')

                embed = discord.Embed(title=f'{player_white_name} vs {player_black_name}', description=f'**{player_won_name}** won by **{won_by_what}**!', color=769656)
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

# @bot.tree.command(name='resign', description='Resign from the Game you\'re playing!')
# @app_commands.describe(gameid = 'The ID of the Game you want to resign from!')
# async def resign(interaction, gameid: str):
#     await interaction.response.defer()
#     try:
#         users_ref = db.collection(u'users')
#         games_ref = db.collection(u'games')
        
#         #gameid = users_ref.document(getusernamefromid(interaction.user.id)).get().to_dict()['playing_game_id']

#         gamedoc_ref = games_ref.document('game ' + str(gameid))

#         if gamedoc_ref.get().exists:
#             player_white = gamedoc_ref.collection(u'players').document(u'white')
#             player_black = gamedoc_ref.collection(u'players').document(u'black')

#             player_white_id = player_white.get().to_dict()['id']
#             player_black_id = player_black.get().to_dict()['id']

#             if player_white_id == interaction.user.id:
#                 player_won_id = player_black_id
#             elif player_black_id == interaction.user.id:
#                 player_won_id = player_white_id
#             else:
#                 await interaction.followup.send(f'Error: You are not in this game!')
#                 return

#             player_won_name = getusernamefromid(player_won_id)
#             player_won_discord = await bot.fetch_user(player_won_id)

#             gamedoc_ref.update({
#                 u'ischeckmate': True,
#                 u'isstalemate': False,
#                 u'player_won_id': player_won_id
#             })

#             fen = gamedoc_ref.get().to_dict()['fen']
#             movesdone = gamedoc_ref.get().to_dict()['movesdone']
#             player_white_name = player_white.get().to_dict()['username']
#             player_black_name = player_black.get().to_dict()['username']

#             with io.BytesIO() as image_binary:
#                 b = Image.open(io.BytesIO(gamedoc_ref.get().to_dict()['board_arr']))

#                 b.save(image_binary, 'PNG')
#                 image_binary.seek(0)
                
#                 file = discord.File(fp=image_binary, filename='board.png')

#                 embed = discord.Embed(title=f'{player_white_name} vs {player_black_name}', description=f'**{player_won_name}** won by **Resignation**!', color=769656)
#                 embed.add_field(name='Info', value=f'Moves Done: `{movesdone}`\nFEN: ```{fen}```', inline=False)
#                 embed.add_field(name='Players', value=f'White: `{player_white_name}`\nBlack: `{player_black_name}`', inline=False)
#                 embed.set_author(name=f'Game | {player_won_name} won!', icon_url=f'{player_won_discord.avatar}')
#                 embed.set_footer(text=f'Game ID: {gameid}')
#                 embed.set_image(url='attachment://board.png')

#                 movemovestocompletedgames(gameid)
#                 moveplayerstocompletedgames(gameid)

#                 await interaction.followup.send(embed=embed, file=file)
#         else:
#             await interaction.followup.send(f'Error: A game with ID `{gameid}` does not exist in the database!')
#             return
#     except Exception as e:
#         await interaction.followup.send(f'Error fetching game: {e}')

@bot.tree.command(name='move', description='Move a piece in the Game you\'re playing!')
@app_commands.describe(moveto = 'Where you are moving the piece to?')
@app_commands.describe(movefrom = 'Where you are moving the piece from?')
async def move(interaction, movefrom: str, moveto: str):
    await interaction.response.defer()

    #try:
    users_ref = db.collection(u'users')
    games_ref = db.collection(u'games')

    gameid = users_ref.document(getusernamefromid(interaction.user.id)).get().to_dict()['playing_game_id']

    gamedoc_ref = games_ref.document(f'game {str(gameid)}')

    if gamedoc_ref.get().exists:
        cb_ = chess.Board(gamedoc_ref.get().to_dict()['fen'])
        b_ = gamedoc_ref.get().to_dict()['board_arr']

        movesdone = gamedoc_ref.get().to_dict()['movesdone']

        image = Image.open(io.BytesIO(b_))

        cb, b, fen, pgn, isover = board.movepiece(movefrom, moveto, image, cb_) # pyright: ignore

        if cb is None and b is None and fen is None and pgn is None:
            await interaction.followup.send(f'Error: {moveto} is an invalid move!', ephemeral=True)
            return

        turn = cb.turn

        if turn == chess.WHITE:
            turn = 'black'
        elif turn == chess.BLACK:
            turn = 'white'

        user_white = gamedoc_ref.collection(u'players').document(u'white')
        user_black = gamedoc_ref.collection(u'players').document(u'black')

        user_white_discord_name = user_white.get().to_dict()['discord_username']
        user_black_discord_name = user_black.get().to_dict()['discord_username']

        user_white_name = user_white.get().to_dict()['username']
        user_black_name = user_black.get().to_dict()['username']

        if (
            turn == 'black'
            and user_black_discord_name != interaction.user.name
            or turn != 'black'
            and turn == 'white'
            and user_white_discord_name != interaction.user.name
        ):
            await interaction.followup.send('Error: It is not your turn!', ephemeral=True)
            return

        if isover == 'checkmate':
            username_won = ''
            if turn == 'black':
                username_won = user_black_name

            elif turn == 'white':
                username_won = user_white_name
            player_won_id = users_ref.document(username_won).get().to_dict()['id']

            b_arr = board.image_to_byte_array(b)
            gamedoc_ref.set({'id': gameid, 'fen': fen, 'board_arr': b_arr, 'movesdone': movesdone + 1, 'ischeckmate': True, 'isstalemate': False, 'player_won_id': player_won_id}, merge=True)

            user_white.update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})
            users_ref.document(user_white_name).update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})

            user_black.update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})
            users_ref.document(user_black_name).update({'is_playing': False, 'is_inviting': False, 'inviting_player': False, 'playing_game_id': ''})

            if username_won == user_white_discord_name :
                user_white.update({'wins': user_white.get().to_dict()['wins'] + 1})
                user_black.update({'losses': user_black.get().to_dict()['losses'] + 1})

                users_ref.document(user_white_name).update({'wins': users_ref.document(user_white_name).get().to_dict()['wins'] + 1})
                users_ref.document(user_black_name).update({'losses': users_ref.document(user_black_name).get().to_dict()['losses'] + 1})
            elif username_won == user_black_discord_name :
                user_white.update({'losses': user_white.get().to_dict()['losses'] + 1})
                user_black.update({'wins': user_black.get().to_dict()['wins'] + 1})

                users_ref.document(user_white_name).update({'losses': users_ref.document(user_white_name).get().to_dict()['losses'] + 1})
                users_ref.document(user_black_name).update({'wins': users_ref.document(user_black_name).get().to_dict()['wins'] + 1})

            with io.BytesIO() as image_binary:
                b.save(image_binary, 'PNG')
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='board.png')

                embed = discord.Embed(title=f'**{user_white_name}** vs **{user_black_name}**', description=f'**{username_won}** won with **Checkmate**, Game ID: `{gameid}`', color=769656)
                embed.set_image(url='attachment://board.png')

            movemovestocompletedgames(gameid)
            moveplayerstocompletedgames(gameid)
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
                b.save(image_binary, 'PNG')
                image_binary.seek(0)

                file = discord.File(fp=image_binary, filename='board.png')

                embed = discord.Embed(title=f'**{user_white_name}** vs **{user_black_name}**', description=f'**{user_white_discord_name}** drew to **{user_black_discord_name}** with Stalemate, Game ID: `{gameid}`', color=769656)
                embed.set_image(url='attachment://board.png')

            movemovestocompletedgames(gameid)
            moveplayerstocompletedgames(gameid)
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
            b.save(image_binary, 'PNG')
            image_binary.seek(0)

            file = discord.File(fp=image_binary, filename='board.png')

            nextturn = ''
            if turn == 'black':
                nextturn = 'white'

            elif turn == 'white':
                nextturn = 'black'
            embed = discord.Embed(title=f'**{user_white_name}** vs **{user_black_name}**', description=f'Game ID: `{gameid}`, {nextturn}\'s turn!', color=769656)
            embed.set_image(url='attachment://board.png')

            await interaction.followup.send(embed=embed, file=file)
    else:
        await interaction.followup.send(f'Error: A Game with ID `{gameid}` does not exist in the database!')
        return

        # await interaction.response.send_message(f'You are moving to {moveto}')

    #except Exception as e:
        #await interaction.followup.send(f'Error: {e}')

@bot.tree.command(name='invite', description='Invite a player in this server to play a Game!')
@app_commands.describe(opponent = 'The opponent name want to invite')
async def invite(interaction, opponent: str):
    await interaction.response.defer()

    try:
        users_ref = db.collection(u'users')
        username_doc = users_ref.document(opponent)
        #users = users_ref.stream()

        username = username_doc.get().to_dict()['username']
        discord_id = username_doc.get().to_dict()['id']
        discord_member = await bot.fetch_user(discord_id)

        if username != opponent:
            await interaction.followup.send(f'Error: {discord_member.mention} is not registered!')
            return

        if discord_member == interaction.user:
            await interaction.followup.send('Error: You cannot invite yourself!')
            return

        thisusername = getusernamefromid(interaction.user.id)
        thisuser_doc = users_ref.document(str(thisusername))

        thisdiscord_member = await bot.fetch_user(interaction.user.id)

        thisuser_doc.update({'is_inviting': True, 'inviting_player': f'{username}'})

        channel = await discord_member.create_dm()
        em = discord.Embed(title=f'Game invitation from {thisusername}', description=f'{thisdiscord_member.mention} has invited you to a Game of Chess! To accept the invite, use `/accept {thisusername}`!', color=769656)
        em.set_thumbnail(url=thisdiscord_member.avatar)
        em.set_footer(text=f'User ID: {thisdiscord_member.id}')
        await channel.send(embed=em)

        await interaction.followup.send(f'Invite sent to {discord_member.mention}!')
    except Exception as e:
        await interaction.followup.send(f'Error: {e}')

@bot.tree.command(name='accept', description='Accept an invite from a player in this server for a Game!')
@app_commands.describe(opponent = 'The opponent\'s name you want to accept an invite from!')
async def accept(interaction, opponent: str):
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

        this_username = getusernamefromid(interaction.user.id)

        if inviting_player != this_username:
            if isopponentinviting == False:
                await interaction.followup.send(f'Error: {opponent_name} is not inviting you!')
                return

            await interaction.followup.send(f'Error: {opponent_name} is not inviting you!')
            return

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

        white_discord_member = await bot.fetch_user(white_discord_id)
        black_discord_member = await bot.fetch_user(black_discord_id)

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
        addusersdoctogame(source_collection, players_ref, [str(white), str(black)], white_username, black_username)

        with io.BytesIO() as image_binary:
            b.save(image_binary, 'PNG')
            image_binary.seek(0)

            file = discord.File(fp=image_binary, filename='board.png')
            embed = discord.Embed(title=f'**{white_username}** vs **{black_username}**', description=f'Game ID: `{gameid}`, {white_discord_member.mention} plays as White and {black_discord_member.mention} plays as Black!', color=769656)
            embed.set_image(url='attachment://board.png')

            thisuser_doc.set({'is_playing': True, 'playing_game_id': f'{gameid}'}, merge=True)
            opponent_doc.set({'is_playing': True, 'playing_game_id': f'{gameid}'}, merge=True)

            opponent_doc.set({'is_inviting': False}, merge=True)

            await interaction.followup.send(embed=embed, file=file)
    except Exception as e:
        await interaction.followup.send(f'Error: {e}')

@bot.tree.command(name='decline', description='Decline an invite from a player in this server for a Game!')
@app_commands.describe(opponent = 'The opponent\'s name you want to decline an invite from!')
async def decline(interaction, opponent: str):
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

        this_username = getusernamefromid(interaction.user.id)

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



def movemovestocompletedgames(gameid):
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

def addusersdoctogame(source_collection, destination_collection, document_names, white_doc_name, black_doc_name):

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

def renamedocumentname(original_collection, original_document_id, new_document_name):
    original_doc_ref = original_collection.document(original_document_id)
    original_doc = original_doc_ref.get().to_dict()

    new_doc_ref = original_collection.document(new_document_name)
    new_doc_ref.set(original_doc)

    original_doc_ref.delete()

def moveplayerstocompletedgames(gameid):
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

def getusernamefromid(id):
    users_ref = db.collection(u'users')
    users = users_ref.stream()

    for user in users:
        #print(user.to_dict()['username'])
        if user.to_dict()['id'] == str(id):
            return user.to_dict()['username']

dotenv_path = os.path.join(os.path.dirname(''), '.env')
read_dotenv(dotenv_path)

token = os.getenv('token')
assert token is not None, 'token is not set in .env file'
bot.run(token)