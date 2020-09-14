from copy import deepcopy
from datetime import datetime, timedelta
import string
import random
import numpy as np


class Sudoku():

    def __init__(self, filename, difficulty):
        self.difficulty = difficulty
        self.game_over = False
        if filename:
            lines = open(filename, "r").readlines()
            self.board = np.array([list(line.strip()) for line in lines[:9]], int)
            self.time = datetime.fromtimestamp(int(lines[9].strip()))
            self.start_puzzle = np.array([list(line.strip()) for line in lines[10:19]], int)
            self.undo_stack = Stack(np.fromstring(lines[19].strip("\n"), dtype=int, sep=" "))
            self.redo_stack = Stack(np.fromstring(lines[20].strip("\n"), dtype=int, sep=" "))

        else:
            self.start_puzzle = np.array(self.generate_puzzle())
            self.board = deepcopy(self.start_puzzle)
            self.time = datetime.fromtimestamp(0)
            self.undo_stack = Stack()
            self.redo_stack = Stack()

    def generate_puzzle(self):
        puzzle = random.choice([easy_template_1, easy_template_2, easy_template_3]) if "EASY" in self.difficulty else \
                 random.choice([hard_template_1, hard_template_2, hard_template_3])
        mapped_puzzle = self.map_puzzle(puzzle)
        for _ in range(np.random.randint(0,4)):
            mapped_puzzle = np.rot90(mapped_puzzle)
        return mapped_puzzle
        
    def map_puzzle(self, puzzle):
        letters = string.ascii_lowercase[:10]
        numbers = np.random.permutation(range(1,10))
        numbers = np.append(numbers, 0)
        mappings = dict(zip(letters, numbers))
        mapped_puzzle = []
        for l in puzzle:
            mapped_puzzle.append(list(map(mappings.get, l)))
        return mapped_puzzle    

    def check_win(self):
        s = set(range(1,10))
        rows = set()
        cols = set()
        for i in range(9):
            for j in range(9):
                rows.add(self.board[i][j])
                cols.add(self.board[j][i])
            if rows != s or cols != s:
                return False
            rows = set()
            cols = set()
        for i in range(3):
            for j in range(3):
                if not self.check_square(i,j):
                    return False
        return True
    
    def check_square(self, i, j):
        s = set(range(1,10))
        square = set()
        for k in range(3):
            square.add(self.board[i*3][j*3+k])
            square.add(self.board[i*3+1][j*3+k])
            square.add(self.board[i*3+2][j*3+k])
        if square != s:
            return False
        return True

    def save_game(self, filename, clock):
        with open(filename, "w") as f:
            for l in self.board:
                f.write("".join(str(x) for x in l) + "\n")
            t = datetime.strptime(clock["text"], "%M:%S")
            f.write(str(t.second + t.minute*60) + "\n")
            for l in self.start_puzzle:
                f.write("".join(str(x) for x in l) + "\n")
            if self.undo_stack.is_empty():
                f.write("\n")
            else:
                np.savetxt(f, self.undo_stack.stack, newline=" ", fmt="%d")
                f.write("\n")
            if self.redo_stack.is_empty():
                f.write("\n")
            else:
                np.savetxt(f, self.redo_stack.stack, newline=" ", fmt="%d")

    def solve(self, puzzle, i=0, j=0):
        i, j = self.get_empty_indices(puzzle)	
        if i == -1:
            return True
        for e in range(1, 10):
             if self.is_valid(puzzle, i, j, e):
                puzzle[i][j] = e
                if self.solve(puzzle, i, j):
                    return True
                puzzle[i][j] = 0
        return False

    def get_empty_indices(self, puzzle):
        for x in range(9):
            for y in range(9):
                if puzzle[x][y] == 0:
                    return x, y
        return -1, -1

    def is_valid(self, puzzle, i, j, e):
        if e not in puzzle[i,:] and e not in puzzle[:,j]:
            sector_x, sector_y = 3*(i//3), 3*(j//3)
            for x in range(sector_x, sector_x+3):
                for y in range(sector_y, sector_y+3):
                    if puzzle[x][y] == e:
                        return False
            return True
        return False


class Stack():

    def __init__(self, s=None):
        self.stack = s if s is not None else np.array(list(), dtype=int)

    def is_empty(self):
        return not self.stack.size

    def pop(self):
        result = self.stack[-3:]
        self.stack = self.stack[:-3]
        return result

    def push(self, elem):
        self.stack = np.hstack([self.stack, elem])

    def save(self, f):
        f.write(str(self.stack))

     
easy_template_1 = [["j","j","j", "e","j","j", "j","g","d"],
                   ["j","c","j", "j","j","j", "a","e","j"],
                   ["j","j","j", "g","b","j", "j","j","j"],
                   
                   ["g","b","j", "c","h","j", "j","j","j"],
                   ["c","i","h", "j","a","j", "d","j","j"],
                   ["j","j","j", "j","j","j", "j","h","j"],
                   
                   ["b","j","e", "j","c","j", "g","j","i"],
                   ["a","j","j", "i","e","j", "j","b","h"],
                   ["j","j","i", "j","g","j", "e","j","j"]] #67

easy_template_2 = [["j","g","j", "j","j","j", "j","j","i"],
                   ["b","j","c", "j","j","g", "j","a","j"],
                   ["h","j","j", "j","c","j", "j","j","g"],
                   
                   ["j","j","h", "j","a","j", "j","i","f"],
                   ["i","a","j", "j","g","j", "j","h","j"],
                   ["d","j","j", "c","j","h", "j","j","j"],
                   
                   ["j","h","j", "j","j","j", "e","b","j"],
                   ["j","j","j", "f","e","j", "j","j","j"],
                   ["j","j","i", "j","j","j", "a","j","j"]] #78

easy_template_3 = [["i","j","a", "c","j","b", "j","j","j"],
                   ["j","j","j", "i","j","f", "j","j","c"],
                   ["j","j","j", "j","j","a", "j","h","j"],
                   
                   ["f","h","j", "j","j","j", "j","c","i"],
                   ["j","j","e", "j","j","j", "a","g","h"],
                   ["j","j","j", "j","j","g", "j","f","e"],
                   
                   ["j","j","c", "j","g","j", "j","j","j"],
                   ["d","j","j", "b","j","i", "j","j","j"],
                   ["j","f","b", "a","j","j", "j","i","j"]] #92

hard_template_1 = [["j","d","j", "j","j","h", "j","c","j"],
                   ["j","j","e", "f","c","j", "j","b","j"],
                   ["j","j","j", "b","j","j", "j","j","d"],
                   
                   ["j","j","j", "j","j","j", "j","a","h"],
                   ["f","j","a", "i","d","j", "j","j","b"],
                   ["e","j","j", "j","j","a", "d","i","j"],
                   
                   ["j","j","d", "j","j","g", "i","j","j"],
                   ["j","g","j", "j","j","j", "j","j","a"],
                   ["j","j","j", "j","b","i", "j","e","j"]] #111

hard_template_2 = [["j","d","j", "j","j","j", "j","g","j"],
                   ["j","b","j", "e","j","h", "j","j","j"],
                   ["i","j","j", "a","j","j", "j","j","j"],
                   
                   ["j","j","j", "j","d","i", "j","j","c"],
                   ["j","j","e", "j","j","g", "b","d","j"],
                   ["j","j","j", "j","j","j", "j","f","j"],
                   
                   ["j","j","b", "j","j","j", "d","j","j"],
                   ["j","j","j", "j","f","j", "j","b","a"],
                   ["j","j","d", "j","j","e", "f","j","g"]] #129

hard_template_3 = [["j","j","j", "j","j","j", "j","j","j"],
                   ["b","g","j", "j","j","j", "d","j","j"],
                   ["j","j","h", "i","j","a", "j","j","b"],
                   
                   ["j","j","g", "j","j","j", "j","a","j"],
                   ["j","i","j", "f","j","j", "j","h","j"],
                   ["c","j","j", "j","e","i", "j","j","g"],
                   
                   ["a","j","j", "h","j","b", "j","j","j"],
                   ["j","j","j", "j","j","j", "f","j","j"],
                   ["j","j","e", "j","d","j", "j","c","j"]] #139
