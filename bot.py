from io import BytesIO
import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import chess
import json
import board

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

bot = commands.Bot(command_prefix='c.', intents=discord.Intents.all())

cred = credentials.Certificate('secret-key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# @bot.event
# async def on_message(ctx: commands.Context):

#     puzzles = db.collection('puzzles').stream()

#     for puzzle in puzzles:
#         puzzle_data = puzzle.to_dict()

#         msg = ctx.content
#         puzzle_doc = db.collection('puzzles').document(puzzle_data['puzzle_id'])
#         index = 0
#         index = puzzle_doc.collection('members').document(str(ctx.author.id)).get().to_dict()['stage']

#         print(msg)
#         print(index)

#         print(puzzle_data['moves'][index])

#         b = chess.Board(puzzle_data['start_fen'])

#         # if (puzzle_data['moves'][index] == puzzle_data['opponent_moves'][index]):
#         #     b.push_uci()
#         #     puzzle_doc.collection('members').document(str(ctx.author.id)).set(
#         #         {
#         #             'stage': index + 1
#         #         }
#         #     )

#         if (puzzle_data['moves'][index] == msg):
#             b.push_uci(puzzle_data['moves'][index])

#             t = puzzle_doc.collection('members').document(str(ctx.author.id)).get().to_dict()['turn']
#             b_img = board.create_board_from_fen(fen=f"{b.board_fen()} {t}")
#             board_image_bytes = board.image_to_byte_array(b_img)

#             if (index < len(puzzle_data['moves'])-1):
#                 puzzle_doc.collection('members').document(str(ctx.author.id)).set(
#                     {
#                         'stage': index + 1
#                     }
#                 )
#                 b.push_uci(puzzle_data['moves'][index + 1]) # play opponent move



#             if (len(puzzle_data['moves'])-1 == puzzle_doc.collection('members').document(str(ctx.author.id)).get().to_dict()['stage']):
#                 embed = discord.Embed(title='Awesome!', description=f"{puzzle_data['moves'][index]} is the right move and the puzzle is solved!")
#                 file = discord.File(BytesIO(board_image_bytes), filename="puzzle.png")
#                 embed.set_image(url="attachment://puzzle.png")
#                 puzzle_doc.collection('members').document(str(ctx.author.id)).delete()
#                 await ctx.channel.send(embed=embed, file=file)
#                 continue
                

#             puzzle_doc.collection('members').document(str(ctx.author.id)).update(
#                 {
#                     'fen': f"{b.board_fen()} {t}",
#                 }
#             )

#             embed = discord.Embed(title='Awesome!', description=f"{puzzle_data['moves'][index]} is the right move!")
#             file = discord.File(BytesIO(board_image_bytes), filename="puzzle.png")
#             embed.set_image(url="attachment://puzzle.png")

#             puzzle_doc.collection('members').document(str(ctx.author.id)).update(
#                 {
#                     'stage': index + 1
#                 }
#             )

#             await ctx.channel.send(embed=embed, file=file)

@bot.event
async def on_message(message):
        if message.author.bot:
            return  # Ignore messages from bots

        # Check if the message author is the one who started the puzzle
        username = getusernamefromid(message.author.id)
        userdoc_ref = db.collection(u'users').document(username)
        user_data = userdoc_ref.get().to_dict()
        if not user_data or 'puzzle_id' not in user_data:
            return  # The user is not in a puzzle

        puzzle_id = user_data['puzzle_id']
        puzzle_ref = db.collection('puzzles').document(puzzle_id)
        puzzle_data = puzzle_ref.get().to_dict()

        if not puzzle_data or 'moves' not in puzzle_data:
            return  # Invalid puzzle data

        moves = puzzle_data['moves']
        stage = user_data.get('stage', 0)

        if stage >= len(moves):
            return  # Puzzle already solved

        expected_move = moves[stage]
        user_move = message.content.strip()

        if user_move == expected_move:
            # Correct move, update the stage
            stage += 1
            userdoc_ref.update({'stage': stage})

            if stage == len(moves):
                # Puzzle solved, you can add additional logic here
                await message.channel.send("Congratulations! You solved the puzzle.")
        else:
            # Incorrect move, you can handle this as needed
            await message.channel.send("Incorrect move. Try again.")

def getusernamefromid(id):
        users_ref = db.collection(u'users')
        users = users_ref.stream()

        for user in users:
            #print(user.to_dict()['username'])
            if user.to_dict()['id'] == str(id):
                return user.to_dict()['username']
                            
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

bot.run(config['token'])