import random
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import PhotoImage
from tkinter import messagebox
from datetime import datetime
import os

currentDirectory = os.path.dirname(__file__)

solved_array = list(range(1, 16))


def isSolvable(arr):
    inversions = 0  # Number of inversions in the array
    width = 4  # width of the puzzle
    row = 0
    blankrow = 0  # row on which empty cell exists

    for i in range(0, len(arr)):
        if i % width == 0:
            row += 1  # move to the next row
        if arr[i] == 0:
            blankrow = row  # empty cell exists on this row
            continue

        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j] & arr[j] != 0:
                inversions += 1

    if width % 2 == 0:
        if blankrow % 2 == 0:
            return inversions % 2 == 0
        else:
            return inversions % 2 != 0
    else:
        return inversions % 2 == 0


def isSolved(arr):
    return solved_array == arr[:15]


class GameWon(tk.Toplevel):
    def __init__(self, master, numMoves, func):
        super(GameWon, self).__init__()
        self.title("3 Great Mosques")
        self.geometry("300x200+500+330")
        self.resizable(0, 0)

        self.master = master
        self.numMoves = numMoves
        self.new_game = func

        self.draw_widgets()
        self.protocol("WM_DELETE_WINDOW", self.destroy_top)

    def draw_widgets(self):
        self.photolist = [
            PhotoImage(
                file=os.path.join(currentDirectory, f"images/claps/frame_{i}.png")
            )
            for i in range(4)
        ]
        self.animate_index = 0

        self.animateLabel = tk.Label(self, image=self.photolist[self.animate_index])
        self.animateLabel.grid(row=0, column=2, pady=3)
        tk.Label(
            self,
            text=f"You solved it in {self.numMoves} moves",
            font="verdana 12 bold",
            fg="green",
        ).grid(row=1, column=0, columnspan=4, padx=30, pady=5)
        self.after_id = self.after(100, self.animate_clap)

        tk.Button(
            self,
            text="New Game",
            bg="green",
            fg="white",
            width=10,
            command=self.destroy_top,
            relief=tk.FLAT,
        ).grid(row=2, column=0, columnspan=2, pady=25, padx=(10, 5))

        tk.Button(
            self,
            text="Quit Game",
            bg="green",
            fg="white",
            width=10,
            command=self.quit_game,
            relief=tk.FLAT,
        ).grid(row=2, column=3, columnspan=2, pady=25, padx=5)

    def animate_clap(self):
        self.animate_index = (self.animate_index + 1) % 4
        self.animateLabel.config(image=self.photolist[self.animate_index])
        self.after_id = self.after(100, self.animate_clap)

    def destroy_top(self):
        self.after_cancel(self.after_id)
        self.destroy()
        self.new_game()

    def quit_game(self):
        self.after_cancel(self.after_id)
        self.destroy()
        self.master.destroy()


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.master = master
        self.grid()

        self.gridCells = []
        self.imgType = tk.StringVar()
        self.imgType.set("al-Haram")
        self.numMoves = 0
        self.firstMove = True
        self.timer_id = None

        self.imgDict = {
            "al-Haram": alharam_list,
            "an-Nabawi": annabawi_list,
            "al-Aqsa": alaqsa_list,
        }
        self.solDict = {
            "al-Haram": alharam_sol,
            "an-Nabawi": annabawi_sol,
            "al-Aqsa": alaqsa_sol,
        }

        self.draw_header()
        self.draw_body()

        self.master.bind("<Up>", self.up)
        self.master.bind("<Down>", self.down)
        self.master.bind("<Left>", self.left)
        self.master.bind("<Right>", self.right)

        self.imgType.trace_add("write", self.new_game)

    def draw_header(self):
        self.header = tk.LabelFrame(
            self, width=400, height=100, bg="white", relief=tk.SUNKEN
        )
        self.header.grid()
        self.header.grid_propagate(False)

        self.reset_btn = tk.Button(
            self.header,
            image=refresh_icon,
            relief=tk.FLAT,
            command=self.new_game,
            bg="white",
        )
        self.reset_btn.grid(row=0, column=0, padx=(30, 10), pady=0)

        self.options = ttk.OptionMenu(
            self.header, self.imgType, "al-Haram", *self.imgDict.keys()
        )
        self.options.config(width=10)
        self.options.grid(row=0, column=1, padx=(30, 10), pady=10)

        self.hint_btn = tk.Button(
            self.header,
            image=hint_icon,
            relief=tk.FLAT,
            command=self.show_solution,
            bg="white",
        )
        self.hint_btn.grid(row=0, column=2, padx=(30, 10), pady=0)

        self.timer_label = tk.Label(
            self.header,
            font=("verdana", 14),
            fg="black",
            text="00:00:00",
            width=10,
            bg="white",
        )
        self.timer_label.grid(row=1, column=0, columnspan=3)

        self.movesFrame = tk.LabelFrame(self.header, width=100, height=100, bg="gray")
        self.movesFrame.grid(row=0, column=3, rowspan=2)
        self.movesFrame.grid_propagate(False)

        self.movesLabel = tk.Label(
            self.movesFrame,
            bg="gray",
            fg="white",
            text=self.numMoves,
            font="verdana 24",
            width=3,
            height=2,
        )
        self.movesLabel.grid(row=0, column=0)

        self.sbody = tk.Frame(self, width=400, height=400)
        self.slabel = tk.Label(self.sbody, image=self.solDict[self.imgType.get()])
        self.slabel.grid(row=0, column=0)

    def draw_body(self):
        self.body = tk.Frame(self, width=400, height=400)
        self.body.grid()
        self.body.grid_propagate(False)

        self.create_board(self.imgType.get())

    def create_board(self, im_type):
        self.array = [i for i in range(1, 16)] + [0]
        random.shuffle(self.array)
        while not isSolvable(self.array):
            random.shuffle(self.array)

        self.emptyCell = self.array.index(0)
        img_list = self.imgDict[im_type]
        self.imgMatrix = [
            img_list[index - 1] if index else None for index in self.array
        ]

        for index, img in enumerate(self.imgMatrix):
            frame = tk.Frame(self.body, width=100, height=100)
            frame.grid(row=index // 4, column=index % 4)
            frame.grid_propagate(False)

            if img:
                lbl = tk.Label(frame, image=img)
            else:
                img = white_bg
                lbl = tk.Label(frame, image=img)

            lbl.grid()
            lbl.bind("<Button-1>", lambda event, pos=index: self.move(pos))
            self.gridCells.append(lbl)

    def new_game(self, *args):
        self.body.destroy()

        self.numMoves = 0
        self.movesLabel["text"] = self.numMoves
        self.firstMove = True
        self.gridCells = []

        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_label["text"] = "00:00:00"

        self.draw_body()

    def move(self, pos):
        if self.imgMatrix[pos]:
            for num in (-1, 1, -4, 4):
                index = num + pos
                if index == self.emptyCell and (pos % 4 - (index % 4) in (-1, 0, 1)):
                    self.swap_cell(pos, index)
                    self.emptyCell = pos
                    self.update_state()

    def up(self, event=None):
        if self.emptyCell - 4 >= 0:
            self.swap_cell(self.emptyCell, self.emptyCell - 4)
            self.emptyCell -= 4
            self.update_state()

    def down(self, event=None):
        if self.emptyCell + 4 <= 15:
            self.swap_cell(self.emptyCell, self.emptyCell + 4)
            self.emptyCell += 4
            self.update_state()

    def left(self, event=None):
        row_changed = self.emptyCell // 4 == (self.emptyCell - 1) // 4
        if 0 <= (self.emptyCell - 1) % 4 < 4 and row_changed:
            self.swap_cell(self.emptyCell, self.emptyCell - 1)
            self.emptyCell -= 1
            self.update_state()

    def right(self, event=None):
        row_changed = self.emptyCell // 4 == (self.emptyCell + 1) // 4
        if 0 <= (self.emptyCell + 1) % 4 < 4 and row_changed:
            self.swap_cell(self.emptyCell, self.emptyCell + 1)
            self.emptyCell += 1
            self.update_state()

    def swap_cell(self, p1, p2):
        if self.firstMove:
            self.start_time = datetime.now()
            self.firstMove = False
            self.timer_id = self.after(1000, self.update_timer)

        self.imgMatrix[p1], self.imgMatrix[p2] = self.imgMatrix[p2], self.imgMatrix[p1]
        self.array[p1], self.array[p2] = self.array[p2], self.array[p1]
        self.update_moves()

        if isSolved(self.array):
            GameWon(self.master, self.numMoves, self.new_game)

    def update_state(self):
        for index, img in enumerate(self.imgMatrix):
            if img:
                self.gridCells[index]["image"] = img
            else:
                self.gridCells[index]["image"] = white_bg
        self.update_idletasks()

    def update_moves(self):
        self.numMoves += 1
        self.movesLabel["text"] = self.numMoves

    def update_timer(self):
        now = datetime.now()
        minutes, seconds = divmod((now - self.start_time).total_seconds(), 60)
        string = f"00:{int(minutes):02}:{round(seconds):02}"
        self.timer_label["text"] = string
        self.timer_id = self.after(1000, self.update_timer)

    def show_solution(self):
        self.body.grid_forget()
        self.sbody.grid()
        self.slabel["image"] = self.solDict[self.imgType.get()]
        self.reset_btn.config(state=tk.DISABLED)
        self.hint_btn.config(state=tk.DISABLED)
        self.after(1000, self.hide_solution)

    def hide_solution(self):
        self.sbody.grid_forget()
        self.body.grid()
        self.reset_btn.config(state=tk.NORMAL)
        self.hint_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("3 Great Mosques")
    root.geometry("400x500+450+130")

    white_bg = PhotoImage(file=os.path.join(currentDirectory, "icons/white_bg.png"))
    refresh_icon = PhotoImage(file=os.path.join(currentDirectory, "icons/refresh.png"))
    hint_icon = PhotoImage(file=os.path.join(currentDirectory, "icons/hint.png"))
    solved_icon = PhotoImage(file=os.path.join(currentDirectory, "icons/solved.png"))

    alharam_list = [
        PhotoImage(
            file=os.path.join(currentDirectory, f"images/alharam/img{index}.png")
        )
        for index in range(1, 17)
    ]
    annabawi_list = [
        PhotoImage(
            file=os.path.join(currentDirectory, f"images/annabawi/img{index}.png")
        )
        for index in range(1, 17)
    ]
    alaqsa_list = [
        PhotoImage(file=os.path.join(currentDirectory, f"images/alaqsa/img{index}.png"))
        for index in range(1, 17)
    ]

    alharam_sol = PhotoImage(
        file=os.path.join(currentDirectory, "images/alharam_resized.png")
    )
    annabawi_sol = PhotoImage(
        file=os.path.join(currentDirectory, "images/annabawi_resized.png")
    )
    alaqsa_sol = PhotoImage(
        file=os.path.join(currentDirectory, "images/alaqsa_resized.png")
    )

    app = Application(master=root)
    app.mainloop()
