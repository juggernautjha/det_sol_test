import pandas as pd
train_df = pd.read_csv("hangman/train.txt", delimiter = "\t", header = None)
test_df = pd.read_csv("hangman/test.txt", delimiter = "\t", header = None)

from server import Hangman
# from agent import Player
from final import Agent

limit = 6
# int(input("Enter the max number of attempts"))

game = Hangman(limit, test_df)
agent = Agent(train_df[0].astype(str).values.tolist())

mask, status, strikes = game.play("")
agent.start_game()
while(status == 0 ):
    guess = agent.guess(mask)
    mask, status, strikes = game.play(guess)
