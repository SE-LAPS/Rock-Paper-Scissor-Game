import random
import requests

GESTURES = ['rock', 'paper', 'scissors', 'lizard', 'spock']

RPSLS_RULES = {
    ('scissors', 'paper'): 'Scissors cuts Paper',
    ('paper', 'rock'): 'Paper covers Rock',
    ('rock', 'lizard'): 'Rock crushes Lizard',
    ('lizard', 'spock'): 'Lizard poisons Spock',
    ('spock', 'scissors'): 'Spock smashes Scissors',
    ('scissors', 'lizard'): 'Scissors decapitates Lizard',
    ('lizard', 'paper'): 'Lizard eats Paper',
    ('paper', 'spock'): 'Paper disproves Spock',
    ('spock', 'rock'): 'Spock vaporizes Rock',
    ('rock', 'scissors'): 'Rock crushes Scissors'
}

class GameEngine:
    def __init__(self, mode='local', api_url=None):
        self.mode = mode
        self.api_url = api_url

    def get_opponent_move(self):
        if self.mode == 'local':
            return random.choice(GESTURES)
        elif self.mode == 'api' and self.api_url:
            try:
                response = requests.get(self.api_url)
                response.raise_for_status()
                return response.json().get('gesture', random.choice(GESTURES))
            except Exception as e:
                print(f"[WARN] API fallback: {e}")
                return random.choice(GESTURES)
        else:
            return random.choice(GESTURES)

    def decide_winner(self, user_gesture, opponent_gesture):
        if user_gesture == opponent_gesture:
            return "Draw", "Both chose the same gesture."
        elif (user_gesture, opponent_gesture) in RPSLS_RULES:
            return "User Wins", RPSLS_RULES[(user_gesture, opponent_gesture)]
        elif (opponent_gesture, user_gesture) in RPSLS_RULES:
            return "Opponent Wins", RPSLS_RULES[(opponent_gesture, user_gesture)]
        else:
            return "Unknown", "No rule found."
