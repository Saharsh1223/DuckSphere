import csv
import random
import chess

def generate_random_puzzle(csv_file, min_rating, max_rating):
    with open(csv_file, 'r') as file:
        puzzles = list(csv.reader(file))

    # Skip the header row
    header = puzzles[0]
    puzzles = puzzles[1:]

    # Filter puzzles based on the specified rating range
    filtered_puzzles = [puzzle for puzzle in puzzles if min_rating <= int(puzzle[3]) <= max_rating]

    if not filtered_puzzles:
        return None

    random_puzzle = random.choice(filtered_puzzles)

    puzzle_id, fen, moves, rating, rating_deviation, popularity, nb_plays, themes, game_url, opening_tags = random_puzzle

    # Ensure that important values are not empty
    if not (puzzle_id and fen and moves and rating and rating_deviation and popularity and nb_plays and themes):
        return None

    board = chess.Board(fen)
    puzzle_moves = moves.split(' ')

    for move in puzzle_moves:
        board.push_uci(move)

    # Extract opening tags from the last column
    opening_tags_list = opening_tags.split()

    return {
        "Puzzle ID": puzzle_id,
        "Start_FEN": fen,
        "End_FEN": board.fen(),
        "Moves": puzzle_moves,
        "Rating": int(rating),
        "Rating Deviation": int(rating_deviation),
        "Popularity": int(popularity),
        "Number of Plays": int(nb_plays),
        "Themes": themes,
        "Game URL": game_url,
        "Opening Tags": opening_tags_list,
    }


if __name__ == "__main__":
    csv_file_path = "lichess_db_puzzle.csv"
    min_rating = 800
    max_rating = 1000
    if puzzle_data := generate_random_puzzle(
        csv_file_path, min_rating, max_rating
    ):
        print("Generated Puzzle Details:")
        for key, value in puzzle_data.items():
            print(f"{key}: {value}")
    else:
        print("No puzzles found within the specified rating range.")
