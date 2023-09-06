from copy import deepcopy
import pandas as pd
train_df = pd.read_csv("data/words_250000_train.txt", delimiter = "\t", header = None)
test_df = pd.read_csv("data/250k_test.txt", delimiter = "\t", header = None)

from server import Hangman
from final import Agent
from tqdm import tqdm

# df: mask, info , guess,... result

def evaluate(num, limit):

    # df = pd.DataFrame(index=range(num), columns=range(65))

    log = []
    for i in tqdm(range(num)):
        
        k = 0
        game = Hangman(limit, test_df[0].astype(str).values.tolist(), verbose = True)
        
        if i == 0:
            agent = Agent(train_df[0].astype(str).values.tolist(), verbose = True)
            
            ngrams = deepcopy(agent.perm_ngrams)
            totals = deepcopy(agent.perm_totals)
            words = deepcopy(agent.word_ngrams)
        else:
            agent = Agent(train_df[0].astype(str).values.tolist(), ngrams = deepcopy(ngrams), totals = deepcopy(totals), words =  deepcopy(words), verbose = True)
        
        agent.start_game()
        mask, status, strikes = game.play("")
        # df.iloc[i, k] = game.word
        # k += 1
        while(status == 0 ):    
            guess = agent.guess(mask)
            mask, status, strikes = game.play(guess)
        log.append(status)

        current_rate = sum([1 for i in log if i == 1])/(i+1)
        print(current_rate)


    success_rate = sum([1 for i in log if i == 1])/num
    print(f"Success rate is {success_rate}")
    return success_rate



num = int(input("Enter number of simulations"))
limit = int(input("Enter the max number of attempts"))
suc = evaluate(num, limit)
# print(f"Success rate {suc}")
# df.to_csv('logs/output12.csv', index=False)


