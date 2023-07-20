import math

# Function to calculate the expected probability of winning
def expected_probability(rating_a, rating_b):
    return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

# Function to update the Elo ratings
def update_elo_rating(rating_a, rating_b, outcome, k_factor=20):
    expected_a = expected_probability(rating_a, rating_b)
    expected_b = expected_probability(rating_b, rating_a)

    # Update ratings based on the outcome
    if outcome == "win":
        new_rating_a = rating_a + k_factor * (1 - expected_a)
        new_rating_b = rating_b + k_factor * (0 - expected_b)
    elif outcome == "loss":
        new_rating_a = rating_a + k_factor * (0 - expected_a)
        new_rating_b = rating_b + k_factor * (1 - expected_b)
    else:
        new_rating_a = rating_a + k_factor * (0.5 - expected_a)
        new_rating_b = rating_b + k_factor * (0.5 - expected_b)

    return round(new_rating_a), round(new_rating_b)

# # Example usage
# player_a_rating = 200
# player_b_rating = 600

# print("Initial Ratings:")
# print("Player A: ", player_a_rating)
# print("Player B: ", player_b_rating)

# # Player A wins against Player B
# player_a_rating, player_b_rating = update_elo_rating(player_a_rating, player_b_rating, "win")

# print("\nUpdated Ratings (Player A wins):")
# print("Player A: ", player_a_rating)
# print("Player B: ", player_b_rating)

# # Player B wins against Player A
# player_a_rating, player_b_rating = update_elo_rating(player_b_rating, player_a_rating, "win")

# print("\nUpdated Ratings (Player B wins):")
# print("Player A: ", player_a_rating)
# print("Player B: ", player_b_rating)