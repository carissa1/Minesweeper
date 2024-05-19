from tkinter import *
from tkinter import messagebox
import random

class MinesweeperCell(Label):
    '''Represents a Minesweeper cell'''
    
    def __init__(self, master, coord):
        '''MinesweeperCell(master,coord) -> SudokuCell
        creates a new blank MinesweeperCell with (row,column) coord'''
        Label.__init__(self,master,height=1,width=2,text='',\
                       bg='white',font=('Arial',16),relief=RAISED)
        self.coord = coord # (row,column) coord
        self.neighbors = [] # all neighbors
        self.colors = ['','blue','darkgreen','red','purple','maroon', \
                       'dodgerblue','black','dim gray']
        self.number = 0  # the number of the cell, 0 = empty
        self.clicked = False # is the cell clicked
        self.flagged = False # is the cell flagged as a bomb
        self.bomb = False # is the cell a bomb
        
        # set up listeners
        self.bind('<Button-1>',self.click)
        self.bind('<Button-2>',self.toggleFlag)
        self.bind('<Button-3>',self.toggleFlag)

    def getNumber(self):
        '''MinesweeperCell.getNumber() -> int
        returns the number in the cell (0 if empty)'''
        return self.number

    def getCoord(self):
        '''MinesweeperCell.getCoord() -> tuple
        returns the coordinate of the square'''
        return self.coord

    def getIndex(self):
        '''MinesweeperCell.getIndex() -> int
        returns the number of the square out of all the squares in the board'''
        return self.coord[0]*self.master.width + self.coord[1]

    def isClicked(self):
        '''MinesweeperCell.isClicked() -> boolean
        returns True if the cell has been clicked, False if not'''
        return self.clicked

    def isFlagged(self):
        '''MinesweeperCell.isFlagged() -> boolean
        returns True if the cell is flagged, False if not'''
        return self.flagged

    def isBomb(self):
        '''MinesweeperCell.isBomb() -> boolean
        returns True if the cell is a bomb, False if not'''
        return self.bomb

    def setBomb(self):
        '''MinesweeperCell.setBomb()
        makes the square a bomb'''
        self.bomb = True

    def click(self,coord):
        '''MinesweeperCell.click(coord)
        handler function for mouse click
        changes the cell so it shows the number of neighbors'''
        if not self.bomb: # if the square is not a bomb
            self.reveal() # reveal the square
            # if the square has 0 bomb neighbors, reveal all the neighbors
            if self.number == 0:
                self.master.revealNeighbors(self,[self.getIndex()])
        self.master.updateGame(self,False) # update the game

    def reveal(self):
        '''MinesweeperCell.reveal()
        reveals the square'''
        self.clicked = True # the square is clicked
        self['bg'] = 'lightgrey'
        self['relief'] = SUNKEN
        if self.flagged: # if the square is flagged, unflag it
            self.toggleFlag(self.coord)
        if self.number != 0: # if the number isn't 0 it should have the number of bombs around it
            self['text'] = str(self.number)
            self['fg'] = self.colors[self.number]

    def toggleFlag(self,coord):
        '''MinesweeperCell.toggleFlag(coord)
        flags or unflags a square and updates the game'''
        flaggable = self.master.canFlagSq(self)
        if flaggable[0]: # if the square is flaggable, change the flag state
            self.flagged = not self.flagged
            if self.flagged:
                self['text'] = '*'
            else:
                self['text'] = ''
            if flaggable[1] == 0: # if the game is still going
                self.master.updateGame(self,True)

    def getNeighbors(self):
        '''MinesweeperCell.getNeighbors()
        returns the neighbors of the cell'''
        return self.neighbors
    
    def setNeighbors(self,neighborList):
        '''MinesweeperCell.setNeighbors(neighborList)
        sets the neighbors and the number of bombs around the cell'''
        self.neighbors = neighborList[0]
        self.number = neighborList[1]
        
class MinesweeperFrame(Frame):
    '''frame to play Minesweeper'''

    def __init__(self,master,width,height,numBombs,name):
        '''MinesweeperFrame(master,width,height,numBombs,name)
        creates a new blank MinesweeperFrame using width, height, the number of bombs, and the player's name'''
        # set up Frame object
        Frame.__init__(self,master)
        self.grid()

        # set up dimensions, the number of bombs, the player's name, and the game state
        self.width = width
        self.height = height
        self.numBombs = numBombs
        self.name = name
        self.gameState = 0 # 0 = playing, 1 = win, -1 = lose
        # set up the variable for the label
        self.flagsLeft = IntVar()
        self.flagsLeft.set(numBombs)

        # labels for the player's name, the state of the game, and the number of flags
        Label(self,text=self.name,font=('Arial',14)).grid(columnspan=3)
        self.gameLabel = Label(self,text='MINESWEEPER',font=('Arial',14))
        self.gameLabel.grid(row=0,column=self.width//2-2,columnspan=5)
        self.flagsLabel = Label(self,textvariable=self.flagsLeft,font=('Arial',14))
        self.flagsLabel.grid(row=0,column=self.width-2,columnspan=2)

        # set up the squares
        self.squares = {}
        for r in range(self.height):
            self.squares[r] = []
            for c in range(self.width):
                self.squares[r].append(MinesweeperCell(self,(r,c)))
                self.squares[r][c].grid(row=r+1,column=c)

        # set up the bombs
        self.bombIndices = random.sample(range(self.width*self.height), self.numBombs)
        self.bombs = []
        for bombIndex in self.bombIndices:
            r = bombIndex//self.width
            c = bombIndex % self.width
            bomb = self.squares[r][c]
            bomb.setBomb()
            self.bombs.append(bomb)

        # get all neighbors
        for r in range(self.height):
            for c in range(self.width):
                allNeighbors = self.getNeighbors(r,c)
                self.squares[r][c].setNeighbors(allNeighbors)

    def getNeighbors(self,r,c):
        '''MinesweeperFrame.getNeighbors(h,w) -> list
        returns the neighbors and the number of bombs around the cell'''
        neighbors = []
        if c != 0: # left
            neighbors.append(self.squares[r][c-1])
        if c < self.width-1: # right
            neighbors.append(self.squares[r][c+1])
        if r != 0: # top
            neighbors.append(self.squares[r-1][c]) # up
            if c != 0: # up left
                neighbors.append(self.squares[r-1][c-1])
            if c < self.width-1: # up right
                neighbors.append(self.squares[r-1][c+1])
        if r < self.height-1: # bottom
            neighbors.append(self.squares[r+1][c]) # down
            if c != 0: # down left
                neighbors.append(self.squares[r+1][c-1])
            if c < self.width-1: # down right
                neighbors.append(self.squares[r+1][c+1])

        numBombs = len([sq for sq in neighbors if sq.isBomb()])
        return [neighbors, numBombs]

    def revealNeighbors(self,cell,visited):
        '''MinesweeperFrame.revealNeighbors(cell,visited)
        if an empty cell is clicked clear all other empty cells until reach bombs'''
        for sq in cell.getNeighbors(): # check all the neighbors
            neighborIndex = sq.getIndex()
            # checks if the square is not a bomb and hasn't already been visited
            if neighborIndex not in visited and not sq.isBomb():
                sq.reveal() # reveals the square
                visited.append(neighborIndex) # the square has been visited
                if sq.getNumber() == 0: # if its a 0, keep revealing squares
                    self.revealNeighbors(sq, visited)

    def canFlagSq(self,sq):
        '''MinesweeperFrame.flagSq(sq)
        returns if a cell can be flagged and the gameState'''
        # the square is flagged
        if sq.isFlagged():
            self.flagsLeft.set(self.flagsLeft.get()+1)
            return [True,self.gameState]
        # the square isn't flagged and there are flags left and the square has not been clicked
        elif not sq.isClicked() and self.flagsLeft.get() != 0:
            self.flagsLeft.set(self.flagsLeft.get()-1)
            return [True,self.gameState]
        return [False,self.gameState] # the square cannot be flagged or unflagged

    def countCorrect(self):
        '''MinesweeperFrame.countCorrect() -> int
        returns the number of clicked and correctly flagged squares'''
        count = 0
        for r in range(self.height):
            for c in range(self.width):
                # the number of clicked squares
                if self.squares[r][c].isClicked():
                    count += 1
                # the number of correctly flagged squares
                if self.squares[r][c].isBomb() and self.squares[r][c].isFlagged():
                    count += 1
        return count

    def revealAll(self):
        '''MinesweeperFrame.revealAll()
        unbinds and reveals all squares and highlights bombs'''
        for r in range(self.height):
            for c in range(self.width):
                # unbind all buttons
                self.squares[r][c].unbind('<Button-1>')
                self.squares[r][c].unbind('<Button-2>')
                self.squares[r][c].unbind('<Button-3>')
                # if the square is a bomb remove the flags and change the background color
                if self.squares[r][c].isBomb():
                    if self.gameState == 1: # won
                        self.squares[r][c]['bg'] = 'green'
                    else: # lost
                        self.squares[r][c]['bg'] = 'red'
                    if self.squares[r][c].isFlagged():
                        self.squares[r][c].toggleFlag((r,c))
                # if the game is lost there are still unclicked squares
                elif self.gameState == -1:
                    self.squares[r][c].reveal()

    def updateGame(self,sq,isFlag):
        '''MinesweeperFrame.updateGame(sq,isFlag)
        checks for flagged squares and the end of the game'''
        if sq.isBomb() and not isFlag: # lose
            messagebox.showerror('Minesweeper','KABOOM! Sorry ' + str(self.name) + ', you lose.', parent=self)
            self.gameLabel['text'] = 'YOU LOSE'
            self.gameState = -1
            self.revealAll()
        if self.countCorrect() == self.height*self.width: # win
            messagebox.showinfo('Minesweeper','Congratulations ' + str(self.name) + ' -- you win!',parent=self)
            self.gameLabel['text'] = 'YOU WIN!'
            self.gameState = 1
            self.revealAll()

def Minesweeper():
    '''Minesweeper()
    plays Minesweeper'''
    name = input("Enter your name: ")
    # get the width and height
    # makes sure the width and height are integers and aren't too large
    while True:
        w = input("Enter the width of the board (10-40): ")
        h = input("Enter the height of the board (1-20): ")
        if w.isnumeric() and h.isnumeric():
            w = int(w)
            h = int(h)
            if 10 <= w <= 40 and 1 <= h <= 20:
                break
            else:
                print("Please make sure the width is between 10 and 40 and the height is between 1 and 20")
        else:
           print("Please make sure the width is an integer between 10 and 40 and the height is an integer between 1 and 20") 

    # get the number of bombs based on difficulty
    while True:
        difficulty = input("Please enter a difficulty (easy, medium, hard): ").lower()
        if difficulty in ['easy','medium','hard']:
            break
        else:
            print("Please choose easy, medium, or hard")
    # average of 1 bombs per n squares
    if difficulty == 'easy': # n = 8.1
        numBombs = int(w*h/8.1)
    if difficulty == 'medium': # n = 6.4
        numBombs = int(w*h/6.4)
    if difficulty == 'hard': # n = 4.85
        numBombs = int(w*h/4.85)

    root = Tk()
    root.title('Minesweeper')
    game = MinesweeperFrame(root,w,h,numBombs,name)
    game.mainloop()

Minesweeper()
