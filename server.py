import random

class Hangman():
    def __init__(self, limit, df, verbose= True, seed = None):
        if seed is None:
            seed = random.randint(0, len(df)-1)
            
        self.word = df[seed]
        self.verbose = verbose

        self.limit = int(limit)
        self.wrong = 0

        self.guesses = []

    def play(self, guess):
        # initial play
        if self.wrong == 0 and guess == "":
            if self.verbose:
                print(self.mask())
            return self.mask(), 0, self.wrong
        
        # recieve the guess
        self.guesses.append(guess)

        if not guess in self.word:
            self.wrong += 1
        
        # check if game over
        if self.wrong >= self.limit:
            if self.verbose:
                print("Game over")
                print(f"Right word is {self.word}")
            return self.mask(), -1, self.wrong
        
        # check if game won
        elif self.mask() == self.word:
            if self.verbose:
                print(self.word)
                print(f"You won with {self.wrong} strikes!")
            return self.mask(), 1, self.wrong
        
        # normal routine
        if self.verbose:
            print(self.mask())
        return self.mask(), 0, self.wrong

    def mask(self):
        final = ""
        for letter in self.word:
            if(letter in self.guesses):
                final += letter
            else:
                final += "_"
        return final
