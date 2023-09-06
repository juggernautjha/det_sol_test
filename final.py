import random
import pickle
import numpy as np
from collections import Counter
from copy import deepcopy
from tqdm import tqdm
import re

class Agent:
    def __init__(self, vocab_list, verbose = True, n_min = 2, n_max = 9, ngrams = None, words = None, totals = None):
        self.verbose = verbose
        self.guessed_letters = [] # key: letter, value: player ID
        self.candidates = []

        self.n = n_max

        self.n_min = n_min
        self.n_max = n_max

        self.full_dictionary = vocab_list
        
        if ngrams is not None and totals is not None and words is not None:
            self.perm_ngrams = ngrams
            self.perm_totals = totals
            self.word_ngrams = words
        else:
            self.perm_ngrams, self.perm_totals = self.generate_ngrams(self.full_dictionary, n_min, n_max)
            self.word_ngrams = {n:set() for n in range(self.n_min, self.n_max + 1)}
            self.generate_word_ngrams()

        # if ngrams is not None and totals is not None:
        #     self.current_ngrams = ngrams
        #     self.current_totals = totals
        # else:
        #     self.current_ngrams, self.current_totals = self.generate_ngrams(vocab_list, n_min, n_max)

    def start_game(self):
        self.guessed_letters = []
        self.current_ngrams = deepcopy(self.perm_ngrams)
        self.current_dictionary = self.full_dictionary
        self.candidates = []

    def extract_character_ngrams(self, word, n):
        return [word[i:i+n] for i in range(len(word) - n + 1)]

    def generate_ngrams(self, words_list, n_min, n_max):

        ngrams_dict = {n: Counter() for n in range(n_min, n_max + 1)}
        ngrams_total = {n: 0 for n in range(n_min, n_max + 1)}

        if self.verbose: 
            print("Extracting ngrams")

        for word in tqdm(words_list):
            for n in range(n_min, n_max + 1):
                ngrams = self.extract_character_ngrams(word, n)
                ngrams_dict[n].update(ngrams)
                ngrams_total[n] += len(ngrams)
        
        # statistics
        
        if self.verbose:
            for i in ngrams_dict.keys():
                print(f"Total number of unique {i} grams")
                print(len(ngrams_dict[i]))

                print(f"Top 5 {i} grams")
                top_n_items = sorted(ngrams_dict[i].items(), key=lambda item: (-item[1], item[0]))[:5]
                print(top_n_items)

        return ngrams_dict, ngrams_total

    def current_wrong_guesses(self, mask): # wrong guesses by current player
        ans = []
        for guess in self.guessed_letters:
            if guess not in mask and self.guessed_letters[guess] == self.n:
                ans.append(guess)

        return ans

    def all_wrong_guesses(self, mask): # wrong guesses by all players
        ans = []
        for guess in self.guessed_letters:
            if guess not in mask:
                ans.append(guess)
        return ans


    def guess(self, mask):
        mask = mask.replace(" ","" )
        if len(self.guessed_letters) == 0:
            self.guessed_letters.append('e')
            return 'e'
        if len(self.guessed_letters) == 1:
            self.guessed_letters.append('a')
            return 'a'
        if len(self.guessed_letters) == 2:
            self.guessed_letters.append('i')
            return 'i'
        
        if(len(mask) < self.n_max) and len(mask) > 2:
            self.n = len(mask)

        return self.vote(mask)
    
    ### Shannongram player

    
    def vote(self, mask):
        
        self.update_ngrams(mask)
        # assert len(self.current_ngrams[self.n]) > 0
        self.update_candidates(mask)
        # assert len(self.candidates) > 0

        while len(self.current_ngrams[self.n]) < 1 and self.n > self.n_min :
                self.n -=1
                self.update_ngrams(mask)
                self.update_candidates(mask)
        
        votes  = {}

        for ngram in (self.current_ngrams[self.n]):
            k = 1
            if ngram in self.word_ngrams[self.n] and self.n == 5:
                k = self.n

            elif ngram in self.word_ngrams[self.n] and self.n >= 6:
                k = self.n^2
            
            for char in ngram:
                if char in self.candidates:
                    if char in votes:
                        votes[char] += k*(self.current_ngrams[self.n][ngram])
                    else:
                        votes[char] = k*(self.current_ngrams[self.n][ngram])
        
        ans = max(votes, key=votes.get)
#         ans = random.choices(list(votes.keys()), weights=list(votes.values()), k=1)[0]

        if self.verbose:
            print(ans)

        self.guessed_letters.append(ans)
        return str(ans)
    
    def new_masks(self, mask, ngram, guess):
        if not guess in ngram:
            return [mask]
        
        coords = self.match(mask, ngram)[1]
        # print(mask, ngram, guess)
        if len(coords) ==0:
            return [mask]
        
        permut = self.generate_subsets(coords)
        masks = [self.new_mask(mask, ngram, guess, i) for i in permut]
        
        if(len(masks) == 0):
            return [mask]
        # print(masks)
        # weights = np.array([self.prob(new_mask, guess) for new_mask in masks])

        # probs =  self.current_ngrams[self.n][ngram]/self.current_totals[self.n] * weights/sum(weights)

        return masks #, probs

    
    def repl(self, string, index, new_character):
        if index < 0 or index >= len(string):
            raise ValueError("Index out of range")
        new_string = string[:index] + new_character + string[index+1:]
        return new_string
    
    def generate_subsets(self, lst):
        n = len(lst)
        subsets = [[]]
        total_subsets = 2**n - 1
        for i in range(1, total_subsets + 1):
            subset = []
            for j in range(n):
                # Check if jth bit is set in binary representation of i
                if i & (1 << j):
                    subset.append(lst[j])
            subsets.append(subset)
        return subsets

    def generate_word_ngrams(self):
        print("Logging words")
        for word in tqdm(self.full_dictionary):
            if len(word) >= self.n_min and len(word) <= self.n_max:
                self.word_ngrams[len(word)].add(word)

    def update_ngrams(self, mask, n = None):
        if n == None:
            n = self.n
        to_delete = []
        for ngram in self.current_ngrams[n]:
            if not self.match(mask, ngram)[0]:
#                 self.current_totals[n] -= self.current_ngrams[n][ngram]
                to_delete.append(ngram)

        for ngram in to_delete:
            del self.current_ngrams[self.n][ngram]

    def update_candidates(self, mask, n=None):
        if n  == None:
            n = self.n

        unique_letters = set()
        for s in self.current_ngrams[n]:
            unique_letters.update(s)
    
        ans =[]
        for i in unique_letters:
            if i in self.guessed_letters or i in mask:
                continue
            else:
                ans.append(i)
    
        self.candidates = ans

    def match(self, mask, ngram, guessed_list = {}):
        # checks if an ngram can potentially occur in a masked word (False if it already exists in the word)
        if len(guessed_list)==0:
            guessed_list = self.guessed_letters
        
        coords = []

        for i in self.all_wrong_guesses(mask):
            if i in ngram:
                return False, coords

        if(len(ngram) > len(mask)):
            return False, coords

        for i in range(len(mask)- len(ngram) + 1):
            ans = True
            if "_" not in mask[i:i+len(ngram)]:
                ans = False
            else:
                for j in range(len(ngram)):
                    if mask[i+j] == "_":
                        if ngram[j] in guessed_list:
                            ans = False
                            break
                    elif mask[i+j] != ngram[j]:
                        ans = False
                        break
            
            if ans == True:
                coords.append(i)
            
        if len(coords) > 0:
            return True, coords

        return False, coords
    
    