import tkinter as tk
from tkinter import messagebox
import os
import pathlib
from copy import deepcopy
import tkinter.font as tkFont
import time
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from sudoku import *

MARGIN = 10
SIDE = 50
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9
WINDOW_WIDTH, WINDOW_HEIGHT = 1080, 763
POS_X, POS_Y = -1, -1

e = pathlib.Path(__file__).parent.absolute().joinpath("continueeasy.sudoku")
h = pathlib.Path(__file__).parent.absolute().joinpath("continuehard.sudoku")

class FirstWindow():
    
    def __init__(self, *args, **kwargs):
        root = tk.Tk()
        root.title("Sudoku")
        root.iconbitmap("pictures/sudoku.ico")
        WINDOW_WIDTH, WINDOW_HEIGHT = image.size
        root.geometry('{}x{}'.format(WINDOW_WIDTH, WINDOW_HEIGHT))

        self.parent = root
        self.parent.resizable(False, False)
        
        self.__init_welcome(self.parent)

        if POS_X != -1:
            self.parent.update_idletasks()
            self.parent.geometry("+{}+{}".format(int(POS_X-self.parent.winfo_reqwidth()/2),int(POS_Y-self.parent.winfo_reqheight()/2)))
        self.parent.mainloop()


    def __init_welcome(self, parent):
        self.canvas = tk.Canvas(self.parent, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.canvas.pack()
        photo_image = ImageTk.PhotoImage(image)
        self.canvas.background = photo_image
        bg = self.canvas.create_image(0, 0, anchor=tk.NW, image=photo_image)

        self.frame = tk.Frame(self.canvas, width=400, height=400, borderwidth=10,
            highlightbackground="blue", highlightthickness=3)

        self.welcome_label = tk.Label(self.frame, text="SUDOKU", font=('Arial',18,'bold'))
        self.welcome_label.pack(pady=(0,5))

        easy_text = "NEW EASY" if e.exists() else "EASY"
        hard_text = "NEW HARD" if h.exists() else "HARD"

        self.easy_button = tk.Button(self.frame, text=easy_text, width=25, command=lambda *args: self.second_window(easy_text))
        self.easy_button.pack(pady=1)

        if e.exists():
            self.cont_easy_button = tk.Button(self.frame, text="CONTINUE EASY", width=25, command=lambda *args: self.second_window("CONTINUE EASY"))
            self.cont_easy_button.pack(pady=1)

        self.hard_button = tk.Button(self.frame, text=hard_text, width=25, command=lambda *args: self.second_window(hard_text))
        self.hard_button.pack(pady=1)

        if h.exists():
            self.cont_hard_button = tk.Button(self.frame, text="CONTINUE HARD", width=25, command=lambda *args: self.second_window("CONTINUE HARD"))
            self.cont_hard_button.pack(pady=1)

        self.frame_window = self.canvas.create_window(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, anchor=tk.CENTER, window=self.frame)
    
    def second_window(self, difficulty):
        self.difficulty = difficulty
        if "EASY" in difficulty:
            if "CONTINUE" in difficulty:
                self.game = Sudoku(e, difficulty)
                self.update_center()
                self.parent.destroy()
                SecondWindow(self.difficulty, self.game)
            else:
                self.game = Sudoku(None, difficulty)
                if e.exists():
                    self.show_popup()
                else:
                    self.update_center()
                    self.parent.destroy()
                    SecondWindow(self.difficulty, self.game) 

        if "HARD" in difficulty:
            if "CONTINUE" in difficulty:
                self.game = Sudoku(h, difficulty)
                self.update_center()
                self.parent.destroy()
                SecondWindow(self.difficulty, self.game)
            else:
                self.game = Sudoku(None, difficulty)
                if h.exists():
                    self.show_popup()
                else:
                    self.update_center()
                    self.parent.destroy()
                    SecondWindow(self.difficulty, self.game) 
   
    def show_popup(self):
        self.popup = tk.Tk()
        self.popup.iconbitmap("pictures/sudoku.ico")
        self.popup.grab_set()
        self.popup.title("Are you sure?")
        self.popup.resizable(False, False)
        label = tk.Label(self.popup, text="Do you want to start {} game?\nThis will erase saved {} game!".format(self.difficulty, self.difficulty.split()[-1]))
        label.grid(row=0, columnspan=2, padx=20, pady=20)
        ok_button = tk.Button(self.popup, text="OK", command=self.ok)
        ok_button.grid(row=1, column=0, pady=(0,10))
        cancel_button = tk.Button(self.popup, text="Cancel", command=self.cancel)
        cancel_button.grid(row=1, column=1, pady=(0,10))
        self.popup.update_idletasks()
        pos_x, pos_y = self.parent.winfo_x(), self.parent.winfo_y()
        x = int(pos_x + self.parent.winfo_width()/2 - self.popup.winfo_reqwidth()/2)
        y = int(pos_y + self.parent.winfo_height()/2 - self.popup.winfo_reqheight()/2)
        self.popup.geometry("+{}+{}".format(x,y))
        self.popup.mainloop()

    def ok(self):
        if self.difficulty == "NEW EASY":
            e.unlink()
        if self.difficulty == "NEW HARD":
            h.unlink()
        self.popup.destroy()
        self.update_center()
        self.parent.destroy()
        SecondWindow(self.difficulty, self.game)

    def cancel(self):
        self.popup.destroy()

    def update_center(self):
        global POS_X, POS_Y
        self.parent.update_idletasks()
        POS_X = int(self.parent.winfo_x() + self.parent.winfo_width()/2)
        POS_Y = int(self.parent.winfo_y() + self.parent.winfo_height()/2)

class SecondWindow():
    def __init__(self, difficulty, game):
        self.parent = tk.Tk()
        self.parent.resizable(False, False)
        self.parent.iconbitmap("pictures/sudoku.ico")
        self.parent.title("Sudoku")
        self.difficulty = difficulty
        self.game = game
        self.game.is_solved = False
        self.row, self.col = -1, -1

        self.parent.protocol("WM_DELETE_WINDOW", self.__on_close)

        self.__initUI()

        self.parent.update_idletasks()
        self.parent.geometry("+{}+{}".format(int(POS_X-self.parent.winfo_reqwidth()/2),int(POS_Y-self.parent.winfo_reqheight()/2)))

    def __initUI(self):
        self.back_photo = ImageTk.PhotoImage(back_image)
        self.back_button = tk.Button(self.parent,image=self.back_photo, text="Back", bd=0, command=self.first_window)
        self.back_button.grid(row=0, column=0, pady=(10,0))
        self.diff_label = tk.Label(self.parent, text=self.difficulty.split()[-1], font=('Arial',18,'bold'))
        self.diff_label.grid(row=0, column=1, pady=(10,0))
        self.second = timedelta(seconds=1)
        self.clock = tk.Label(self.parent, text=self.game.time, font=('Arial',18,'bold'))
        self.update_clock()
        self.clock.grid(row=0, column=2, pady=(10,0))
        self.undo_photo = ImageTk.PhotoImage(undo_image)
        self.undo_button = tk.Button(self.parent, image=self.undo_photo, text="Undo", bd=0, state=tk.DISABLED if self.game.undo_stack.is_empty() else tk.NORMAL, command=self.undo)
        self.undo_button.grid(row=0, column=3, pady=(10,0))
        self.redo_photo = ImageTk.PhotoImage(redo_image)
        self.redo_button = tk.Button(self.parent, text="Redo", bd=0, image=self.redo_photo, state=tk.DISABLED if self.game.redo_stack.is_empty() else tk.NORMAL, command=self.redo)
        self.redo_button.grid(row=0, column=4, pady=(10,0))

        self.menu_photo = ImageTk.PhotoImage(menu_image)
        self.mb = tk.Menubutton(self.parent, text="Menu", bd=0, image=self.menu_photo, relief=tk.RAISED)
        self.mb.grid(row=0, column=5, pady=(10,0))
        self.mb.menu = tk.Menu(self.mb, tearoff=0)
        self.mb["menu"] = self.mb.menu

        self.mb.menu.add_command(label="Validate", command=self.validate)
        self.mb.menu.add_command(label="Restart", command=self.restart)
        self.mb.menu.add_command(label="Solve", command=self.solve)

        self.canvas = tk.Canvas(self.parent, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.grid(row=1, columnspan=6, sticky=tk.N)

        self.button_frame = tk.Frame(self.parent)
        self.button_frame.grid(row=2, columnspan=6, pady=(0,10))

        self.one_photo = ImageTk.PhotoImage(one_image)
        self.two_photo = ImageTk.PhotoImage(two_image)
        self.three_photo = ImageTk.PhotoImage(three_image)
        self.four_photo = ImageTk.PhotoImage(four_image)
        self.five_photo = ImageTk.PhotoImage(five_image)
        self.six_photo = ImageTk.PhotoImage(six_image)
        self.seven_photo = ImageTk.PhotoImage(seven_image)
        self.eight_photo = ImageTk.PhotoImage(eight_image)
        self.nine_photo = ImageTk.PhotoImage(nine_image)
        self.ten_photo = ImageTk.PhotoImage(ten_image)
        col = 0
        row = 0
        photos = [self.one_photo, self.two_photo, self.three_photo, self.four_photo, self.five_photo, self.six_photo,
            self.seven_photo, self.eight_photo, self.nine_photo, self.ten_photo]
        for num, photo in zip(map(str,range(1,10)),photos):
            command = lambda x=num: self.__key_pressed(Mock(x))
          
            tk.Button(self.button_frame, image=photo, text=num, bd=0,
                padx=1, pady=1, command=command).grid(row=row, column=col)
            col+=1
            if col > 4:
                col = 0
                row = 1

        tk.Button(self.button_frame, text="E", image=self.ten_photo, bd=0,
            padx=1, pady=1, command=lambda x=None: self.__backspace(x)).grid(row=1, column=4)

        self.__draw_grid()
        self.__draw_board()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)
        self.canvas.bind("<BackSpace>", self.__backspace)

    def validate(self):
        self.canvas.delete("cursor")
        self.canvas.delete("highlight")
        if not self.game.is_solved:
            self.game.solved = deepcopy(self.game.start_puzzle)
            self.game.solve(self.game.solved)
            self.game.is_solved = True

        for i in range(9):
            for j in range(9):
                if self.game.board[i][j] != 0 and self.game.board[i][j] != self.game.solved[i][j]:
                    self.__draw_cursor(i, j)

    def restart(self):
        self.game.board = deepcopy(self.game.start_puzzle)
        self.game.time = datetime.fromtimestamp(0)
        self.game.game_over = False

        if not self._clock:
            self.update_clock()

        self.row, self.col = -1, -1
        self.game.undo_stack = Stack()
        self.game.redo_stack = Stack()
        self.undo_button.config(state="disabled")
        self.redo_button.config(state="disabled")
        self.__draw_board()
        self.canvas.delete("highlight")
        self.canvas.delete("cursor")


    def solve(self):
        if not self.game.is_solved:
            self.game.board = deepcopy(self.game.start_puzzle)
            self.game.solve(self.game.board)
            self.game.solved = deepcopy(self.game.board)
            self.game.is_solved = True
        else:
            self.game.board = deepcopy(self.game.solved)
        self.game.game_over = True
        if self._clock:
            self.parent.after_cancel(self._clock)
            self._clock = None
        self.undo_button.config(state="disabled")
        self.redo_button.config(state="disabled")
        self.__draw_board()
        self.canvas.delete("highlight")
        self.canvas.delete("cursor")

    def __on_close(self):
        if  not self.game.game_over:
            self.game.save_game(e if "EASY" in self.difficulty else h, self.clock)
        self.parent.destroy()

    def update_clock(self):
        self.clock.configure(text=self.game.time.strftime("%M:%S"))
        self.game.time += self.second
        self._clock = self.parent.after(1000, self.update_clock)

    def undo(self):
        last = self.game.undo_stack.pop()
        self.game.redo_stack.push([last[0], last[1], self.game.board[last[0]][last[1]]])
        self.redo_button.config(state="normal")
        self.game.board[last[0]][last[1]] = last[2]
        self.row = last[0]
        self.col = last[1]
        self.refresh_display()
        if self.game.undo_stack.is_empty():
            self.undo_button.config(state="disabled")

    def redo(self):
        last = self.game.redo_stack.pop()
        self.game.undo_stack.push([last[0], last[1], self.game.board[last[0]][last[1]]])
        self.undo_button.config(state="normal")
        self.game.board[last[0]][last[1]] = last[2]
        self.row = last[0]
        self.col = last[1]
        self.refresh_display()
        if self.game.redo_stack.is_empty():
            self.redo_button.config(state="disabled")

    def refresh_display(self):
        self.__draw_board()
        self.canvas.delete("highlight")
        self.__highlight_all()
        self.__highlight_numbers()
        self.canvas.lift("numbers")
        self.canvas.delete("cursor")
        self.__draw_cursor()
        self.canvas.lift("cursor")

    def first_window(self):
        global POS_X, POS_Y
        if not self.game.game_over:
            self.game.save_game(e if "EASY" in self.difficulty else h, self.clock)
        if self._clock:
            self.parent.after_cancel(self._clock)
            self._clock = None
        self.parent.update_idletasks()
        POS_X = int(self.parent.winfo_x() + self.parent.winfo_width()/2)
        POS_Y = int(self.parent.winfo_y() + self.parent.winfo_height()/2)
        self.parent.destroy()
        FirstWindow()

    def __draw_grid(self):
        for i in range(10):
            self.color_of_squares = "blue"
            self.color_of_other = "gray"
            color = self.color_of_squares if i % 3 == 0 else self.color_of_other
            width = 3 if i % 3 == 0 else 1

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=width, tags=color)

            x0 = MARGIN-1
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN+2
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=width, tags=color)
    
    def __draw_board(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.board[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.start_puzzle[i][j]
                    color = "black"

                    if answer == original:
                        x0 = MARGIN + j * SIDE + 1
                        y0 = MARGIN + i * SIDE + 1
                        x1 = MARGIN + (j + 1) * SIDE - 1
                        y1 = MARGIN + (i + 1) * SIDE - 1
                        self.canvas.create_rectangle(
                            x0, y0, x1, y1,
                            fill="snow3", tags="background", outline="snow3"
                        )
                    
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color, font=('Arial',20,'bold')
                    )
                    self.canvas.lift(self.color_of_other)
                    self.canvas.lift(self.color_of_squares)

    def __backspace(self, event):
        if self.game.start_puzzle[self.row][self.col] == 0 and self.row != -1:
            self.game.undo_stack.push([self.row, self.col, self.game.board[self.row][self.col]])
            self.undo_button.config(state="normal")
            self.game.board[self.row][self.col] = 0
            self.__draw_board()
            self.__highlight_all()

    def __cell_clicked(self, event):
        self.canvas.delete("highlight")
        self.canvas.delete("cursor")
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
            self.canvas.focus_set()

            row, col = int((y - MARGIN) / SIDE), int((x - MARGIN) / SIDE)

            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()
        self.__paint_background()

    def __paint_background(self):
        if self.row >= 0 and self.col >= 0:
            self.__highlight_all()
            self.__highlight_numbers()
            self.canvas.lift("numbers")
            self.canvas.lift("cursor")

    def __highlight_all(self):
        for i in range(9):
            #ROW
            fill = "lemon chiffon" if self.game.start_puzzle[self.row][i] == 0 else "LemonChiffon3"
            x0 = MARGIN + i * SIDE + 2
            y0 = MARGIN + self.row * SIDE + 2
            x1 = MARGIN + (i + 1) * SIDE - 2
            y1 = MARGIN + (self.row + 1) * SIDE - 2
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=fill, tags="highlight", outline=fill
            )

            #COLUMN
            fill = "lemon chiffon" if self.game.start_puzzle[i][self.col] == 0 else "LemonChiffon3"
            x0 = MARGIN + self.col * SIDE + 2
            y0 = MARGIN + i * SIDE + 2
            x1 = MARGIN + (self.col + 1) * SIDE - 2
            y1 = MARGIN + (i + 1) * SIDE - 2
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=fill, tags="highlight", outline=fill
            )
        
        self.__highlight_square()
        self.canvas.lift("numbers")
        self.canvas.lift("cursor")
    
    def __highlight_square(self):
        i = int(self.row/3)
        j = int(self.col/3)
        for k in range(3):
            for l in range(3):
                self.__highlight_column(i,j,k,l)
            
    def __highlight_column(self, i, j, k, l):
        fill = "lemon chiffon" if self.game.start_puzzle[i*3+l][j*3+k] == 0 else "LemonChiffon3"
        x0 = MARGIN + (j*3+k) * SIDE + 2
        y0 = MARGIN + (i*3+l) * SIDE + 2
        x1 = MARGIN + (j*3+k + 1) * SIDE - 2
        y1 = MARGIN + (i*3+l + 1) * SIDE - 2
        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=fill, tags="highlight", outline=fill
        )
    
    def __highlight_numbers(self):
        if self.game.board[self.row][self.col] in range(1,10):
            for i in range(9):
                for j in range(9):
                    if self.game.board[i][j] == self.game.board[self.row][self.col]:
                        x0 = MARGIN + j * SIDE + 2
                        y0 = MARGIN + i * SIDE + 2
                        x1 = MARGIN + (j + 1) * SIDE - 2
                        y1 = MARGIN + (i + 1) * SIDE - 2
                        self.canvas.create_rectangle(
                            x0, y0, x1, y1,
                            fill="light sky blue", tags="highlight", outline="light sky blue"
                        )

    def __key_pressed(self, event):
        if not self.game.redo_stack.is_empty():
            self.game.redo_stack.stack = np.array(list(), dtype=int)
            self.redo_button.config(state="disabled")
        if self.game.game_over:
            return

        if self.row >= 0 and self.col >= 0 and event.char in "1234567890" and self.game.start_puzzle[self.row][self.col] == 0 and event.char != "":
            new_value = int(event.char)
            self.game.undo_stack.push([self.row, self.col, self.game.board[self.row][self.col]])
            self.undo_button.config(state="normal")
            self.game.board[self.row][self.col] = new_value
            self.canvas.delete("highlight")
            self.__draw_board()
            self.__draw_cursor()
            self.__highlight_all()
            self.__highlight_numbers()
            self.canvas.lift("numbers")
            self.canvas.lift("cursor")

            if self.game.check_win():
                self.game.game_over = True

                self.__victory()

    def __draw_cursor(self, i=-1, j=-1):
        if i == -1:
            i = self.row
            j = self.col
        if i >= 0 and j >= 0:
            x0 = MARGIN + j * SIDE + 1
            y0 = MARGIN + i * SIDE + 1
            x1 = MARGIN + (j + 1) * SIDE - 1
            y1 = MARGIN + (i + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor", width=3
            )

    def __victory(self):
        if self.difficulty == "CONTINUE EASY":
            e.unlink()
        if self.difficulty == "CONTINUE HARD":
            h.unlink()
        if self._clock:
            self.parent.after_cancel(self._clock)
            self._clock = None
        self.canvas.delete("highlight")
        self.canvas.delete("cursor")
        root = tk.Tk()
        root.title("Sudoku")
        root.resizable(False, False)
        label = tk.Label(root, text="CONGRATULATIONS!\n\nYou solved {} puzzle in {}".format(
            "EASY" if "EASY" in self.game.difficulty else "HARD", self.game.time.strftime("%M:%S")))
        label.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        button = tk.Button(root, text="OK", command=lambda: root.destroy())
        button.pack(side="bottom", fill="none", expand=True, padx=5, pady=5)
        root.mainloop()

class Mock():

    def __init__(self, char):
        self.char = char


if __name__ == "__main__":
    image = Image.open("pictures/background.pgm")
    back_image = Image.open("pictures/left-arrow.png")
    back_image = back_image.resize((25, 25), Image.ANTIALIAS)
    undo_image = Image.open("pictures/undo.png")
    undo_image = undo_image.resize((25, 25), Image.ANTIALIAS)
    redo_image = Image.open("pictures/redo.png")
    redo_image = redo_image.resize((25, 25), Image.ANTIALIAS)
    menu_image = Image.open("pictures/more.png")
    menu_image = menu_image.resize((25, 25), Image.ANTIALIAS)

    size = 50
    one_image = Image.open("pictures/one.png")
    one_image = one_image.resize((size, size), Image.ANTIALIAS)
    two_image = Image.open("pictures/two.png")
    two_image = two_image.resize((size, size), Image.ANTIALIAS)
    three_image = Image.open("pictures/three.png")
    three_image = three_image.resize((size, size), Image.ANTIALIAS)
    four_image = Image.open("pictures/four.png")
    four_image = four_image.resize((size, size), Image.ANTIALIAS)
    five_image = Image.open("pictures/five.png")
    five_image = five_image.resize((size, size), Image.ANTIALIAS)
    six_image = Image.open("pictures/six.png")
    six_image = six_image.resize((size, size), Image.ANTIALIAS)
    seven_image = Image.open("pictures/seven.png")
    seven_image = seven_image.resize((size, size), Image.ANTIALIAS)
    eight_image = Image.open("pictures/eight.png")
    eight_image = eight_image.resize((size, size), Image.ANTIALIAS)
    nine_image = Image.open("pictures/nine.png")
    nine_image = nine_image.resize((size, size), Image.ANTIALIAS)
    ten_image = Image.open("pictures/ten.png")
    ten_image = ten_image.resize((size, size), Image.ANTIALIAS)
    FirstWindow()
