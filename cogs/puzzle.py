from io import BytesIO
import traceback
import discord
from discord.ext import commands
from discord import ChannelType, app_commands
import generate_puzzle
from firebase_admin import firestore
import board
import chess

bot = commands.Bot(command_prefix='c.', intents=discord.Intents.all())
db = firestore.client()

class Puzzle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.tree.command(name='puzzle', description='Get a random puzzle!')
    @app_commands.checks.cooldown(1, 15)
    @app_commands.describe(rating_deviation='The deviation of rating from your rating to find the optimal range of rating for you!')
    async def puzzle(self, interaction: discord.Interaction, rating_deviation: int = 100):
        await interaction.response.defer()
        username = self.getusernamefromid(interaction.user.id)
        userdoc_ref = db.collection(u'users').document(username)
        elo = userdoc_ref.get().to_dict()["elo"]

        # Retrieve puzzle_id from user data if it exists
        user_data = userdoc_ref.get().to_dict()
        puzzle_id = user_data.get('puzzle_id')

        puzzle_data = generate_puzzle.generate_random_puzzle('lichess_db_puzzle.csv', elo-rating_deviation, elo+rating_deviation)
        fen = puzzle_data['Start_FEN']
        b = chess.Board(fen=fen)
        b.push_uci(puzzle_data['Moves'][0])
        turn = 'white' if b.turn == chess.WHITE else 'black'
        t = 'w' if turn == 'white' else 'b'
        b_img = board.create_board_from_fen(fen=f"{b.board_fen()} {t}")

        # Convert the board image to bytes
        board_image_bytes = board.image_to_byte_array(b_img)

        moves = puzzle_data['Moves']
        moves.pop(0)

        if len(moves) > 1:
            opponent_moves = [element for index, element in enumerate(moves) if index % 2 != 0]  # filter out opponent moves
        else:
            opponent_moves = []

        puzzle_stage = 0

        if not db.collection('puzzles').document(puzzle_data['Puzzle ID']).get().exists:
            db.collection('puzzles').document(puzzle_data['Puzzle ID']).set(
                {
                    'puzzle_id': puzzle_data['Puzzle ID'],
                    'moves': moves,
                    'opponent_moves': opponent_moves,
                    'start_fen': f"{b.board_fen()} {t}",
                    'end_fen': puzzle_data['End_FEN']
                }
            )
        
        # Save the puzzle_id and stage in user's data
        userdoc_ref.update({'puzzle_id': puzzle_data['Puzzle ID'], 'stage': 0})

        db.collection('puzzles').document(puzzle_data['Puzzle ID']).collection('members').document(str(interaction.user.id)).set(
            {
                'stage': 0,
                'member_id': interaction.user.id,
                'fen': f"{b.board_fen()} {t}",
                'turn': t
            }
        )

        # Create an embed
        embed = discord.Embed(title="Chess Puzzle", description=f"Solve the puzzle, {turn} to move!\n\nRating: {puzzle_data['Rating']}\nPopularity (on a scale of -100 to 100): {puzzle_data['Popularity']}\nNumber of Plays: {puzzle_data['Number of Plays']}\nTheme: {puzzle_data['Themes']}", color=0x00ff00)

        # Add an image to the embed
        file = discord.File(BytesIO(board_image_bytes), filename="puzzle.png")
        embed.set_image(url="attachment://puzzle.png")

        # Send the embed with the image
        await interaction.followup.send(embed=embed, file=file)

        await interaction.followup.send(f"Solution: {puzzle_data['Moves']}")


    @puzzle.error  # Tell the user when they've got a cooldown
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error),
                                                    ephemeral=True)
            
    def getusernamefromid(self, id):
        users_ref = db.collection(u'users')
        users = users_ref.stream()

        for user in users:
            #print(user.to_dict()['username'])
            if user.to_dict()['id'] == str(id):
                return user.to_dict()['username']

async def setup(bot):
    await bot.add_cog(Puzzle(bot))
