#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 17:36:23 2018

@author: XIA XUE & FANFEI LI & RUI YAN
"""

from Tkinter import *
import random
from PIL import Image, ImageTk


class Bomb:
    def __init__(self):

        powell = PhotoImage(file="background.png")
        w = powell.width()  # 700
        h = powell.height()  # 700

        self.xpos = random.choice([random.randint(20, 200),
                                   random.randint(400, w - 20)])
        self.ypos = random.choice([random.randint(20, 200),
                                   random.randint(400, h - 20)])
        self.set_speed(0)

    def set_speed(self, speed=2):
        self.xspeed = speed
        self.yspeed = speed


class CattGUI():
    def __init__(self):
        # initiate some values
        self.set_difficulty = False
        self.side = 20
        self.isPaused = True

        # initiate the window, the canvas and the buttons
        self.window = Tk()
        self.window.geometry('700x800')
        self.window.title('Powell Cat')
        self.powell = PhotoImage(file="background.png")
        self.w = self.powell.width()  # 700
        self.h = self.powell.height()  # 700
        self.canvas = Canvas(self.window, width=self.w, height=self.h)
        self.canvas.pack(side='top', fill='both', expand=True, padx=1)
        self.canvas.create_image(0, 0, image=self.powell, anchor=NW)

        self.scoree = StringVar()
        self.text = Label(self.window, textvariable=self.scoree, bg='light blue').pack(anchor=S)
        self.scoree.set('Score = 0')

        # frame set up
        self.frame = Frame(self.window)
        self.frame.pack()
        self.frame.focus_set()

        # buttons set up
        self.button = Button(self.frame, text='Start', fg="black",
                             width=20, command=self.start, padx=2)
        self.button.pack()

        self.button2 = Button(self.frame, text='Set Difficulty', fg="black",
                              width=20, command=self.popup, padx=2)
        self.button2.pack()

        self.difficulty_level = 'Easy'
        self.set_difficulty_parameters(self.difficulty_level)

        # running the game
        self.newgame()

        self.window.mainloop()

    def start(self):
        ''' start a new game '''
        self.button.unbind('<Button-1>')
        # if game start, change button to pause
        self.button.config(text='Pause', command=self.pause)
        self.isPaused = False
        self.animate()  # running the game

    def pause(self):
        ''' pause the current game '''
        # if game pause, change button to resume
        self.button.config(text='Resume', command=self.start)
        self.isPaused = True  # indicating game pause

    def popup(self):
        ''' popup windows for difficulty-level setup '''
        self.toplevel = Toplevel()
        self.label1 = Button(self.toplevel, text='Easy', bg="light blue",
                             fg="red", width=20, command=self.closeandeasy)
        self.label1.pack()
        self.label2 = Button(self.toplevel, text='Medium', bg="light blue",
                             fg="red", width=20, command=self.closeandmedium)
        self.label2.pack()
        self.label3 = Button(self.toplevel, text='Hard', bg="light blue",
                             fg="red", width=20, command=self.closeandhard)
        self.label3.pack()
        pass

    def newgame(self):
        ''' '''
        # initiate some parameters
        self.score = 0
        self.scoree.set('Score = 0')

        # size of each 'step' when the cat moves
        self.stepx = 0
        self.stepy = 0
        # initiate list of positions in the board
        self.a = range(0, self.w + 1)
        self.square = [x for x in self.a if x % (self.side / 2) == 0]
        self.b = [x for x in self.square if (x // (self.side / 2)) % 2 != 0]
        # initial coordinates of the first cat segment
        self.x = int(self.w / 2)
        self.y = int(self.h / 2)
        # a list of cat object
        self.segment = []
        # load images of cat, book, and bomb
        self.load_images()

        # coordinates of each cat segment
        self.coor = [[self.x - 40, self.y], [self.x - 20, self.y], [self.x, self.y]]

        # initiate the first cat segment
        mytail = self.coor[0]
        mybody = self.coor[1]

        self.segment.append(self.canvas.create_image(mytail[0] - self.side / 2,
                                                     mytail[1] - self.side / 2,
                                                     image=self.tail, anchor=NW, tags='tail'))
        self.segment.append(self.canvas.create_image(mybody[0] - self.side / 2,
                                                     mybody[1] - self.side / 2,
                                                     image=self.body, anchor=NW, tags='segment'))
        self.segment.append(self.canvas.create_image(self.x - self.side / 2,
                                                     self.y - self.side / 2,
                                                     image=self.head, anchor=NW, tags='head'))

        # initiate the start button again when renew the game
        self.button.config(text='Start', command=self.start)

        # bind key to move the cat
        self.button.bind('<Button-1>', self.right)
        self.window.bind('<Up>', self.up)
        self.window.bind('<w>', self.up)
        self.window.bind('<Down>', self.down)
        self.window.bind('<s>', self.down)
        self.window.bind('<Right>', self.right)
        self.window.bind('<d>', self.right)
        self.window.bind('<Left>', self.left)
        self.window.bind('<a>', self.left)

        self.set_difficulty_parameters(self.difficulty_level)

        self.food()
        self.create_bomb()

        # animate the game after waiting self.time
        # higher self.time implies slower speed
        self.window.after(self.time, self.animate)

    def animate(self):
        ''' implement the details for each step of game running '''
        if not self.isPaused:
            # change the coordinate of the cat's head to make it move
            old_head = self.coor[len(self.coor) - 1]
            old_head_x = old_head[0]
            old_head_y = old_head[1]

            self.x = self.x + self.stepx
            self.y = self.y + self.stepy
            self.coor.append([self.x, self.y])

            self.bomb_run()

            # set up conditions to check game over
            self.game_over = False

            # check if the cat collides the bombs
            for b, bomb in zip(self.bs, self.bombs):
                pos = self.canvas.coords(b)
                tagged_seg = self.canvas.find_withtag('segment')
                tagged_head = self.canvas.find_withtag('head')
                tagged_tail = self.canvas.find_withtag('tail')
                overlap = self.canvas.find_overlapping(pos[0] - 10, pos[1] - 10, pos[0] + 10, pos[1] + 10)
                for item in overlap:
                    if (item in tagged_seg) or (item in tagged_head) or (item in tagged_tail):
                        self.game_over = True
                        break

            # check if the cat collides itself or the boundaries of window
            if (self.y > self.h - 10) or (self.y < 10) or (self.x < 10) or (self.x > self.w - 10) \
                    or (len(self.coor) > 2 and [self.x, self.y] in self.coor[:-1]):
                self.game_over = True

            # if game over, notify "game over" and start another game
            if self.game_over:
                self.isPaused = True
                self.toplevel = Toplevel()
                self.label = Label(self.toplevel, text='Game Over. Score: ' + str(self.score), width=20)
                self.label.pack()
                self.button.config(text='New Game', command=self.recall)

            # if not game over, check if the cat collides the food
            elif [self.x, self.y] == [self.b[self.xfood], self.b[self.yfood]]:
                self.score += 1             # update scores
                self.canvas.delete('food')  # delete food
                self.food()

                lenC = len(self.segment)    # length of cat

                self.canvas.delete(self.segment[lenC - 1])
                del self.segment[lenC - 1]

                self.segment.append(self.canvas.create_image(old_head_x - self.side / 2,
                                                             old_head_y - self.side / 2,
                                                             image=self.body, anchor=NW, tags='segment'))

                self.segment.append(self.canvas.create_image(self.x - self.side / 2,
                                                             self.y - self.side / 2,
                                                             image=self.head, anchor=NW, tags='head'))

                # update score
                self.scoree.set("Score = " + str(self.score))

                # iteratively run the game until the game is over
                self.window.after(self.time, self.animate)

            # if not game over, cat should move
            else:
                lenC = len(self.segment)

                self.canvas.delete(self.segment[lenC - 1])
                del self.segment[lenC - 1]

                self.segment.append(self.canvas.create_image(old_head_x - self.side / 2,
                                                             old_head_y - self.side / 2,
                                                             image=self.body, anchor=NW, tags='segment'))

                self.segment.append(self.canvas.create_image(self.x - self.side / 2,
                                                             self.y - self.side / 2,
                                                             image=self.head, anchor=NW, tags='head'))

                self.canvas.delete(self.segment[0])
                del self.segment[0]
                del self.coor[0]

                self.canvas.delete(self.segment[0])
                del self.segment[0]

                self.segment.insert(0, self.canvas.create_image(self.coor[0][0] - self.side / 2,
                                                                self.coor[0][1] - self.side / 2,
                                                                image=self.tail, anchor=NW, tags='tail'))
                self.window.after(self.time, self.animate)

    def create_bomb(self):
        ''' create bombs '''
        self.bombs = []   # keeps track of bomb objects
        self.bs = []      # keeps track of bomb objects representation on the Canvas
        while len(self.bombs) < self.Nbomb:
            bomb = Bomb()
            if [bomb.xpos, bomb.ypos] not in self.coor:
                bomb.set_speed(self.speed)
                self.bombs.append(bomb)
                self.bs.append(self.canvas.create_image(bomb.xpos - 10, bomb.ypos - 10,
                                                        image=self.bomb, tags='bomb'))

    def bomb_run(self):
        '''moves bombs '''
        for b, bomb in zip(self.bs, self.bombs):
            self.canvas.move(b, bomb.xspeed, bomb.yspeed)
            pos = self.canvas.coords(b)
            if pos[1] + 20 >= self.h or pos[1] <= 0:
                bomb.yspeed = - bomb.yspeed
            if pos[0] + 20 >= self.w or pos[0] <= 0:
                bomb.xspeed = - bomb.xspeed

    def recall(self):
        ''' start another new game after the first try '''
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, image=self.powell, anchor=NW)
        self.label.pack_forget()
        self.newgame()

    def food(self):
        ''' create food '''
        # coordinates of the food
        self.xfood = random.randint(10, len(self.b) - 10)
        self.yfood = random.randint(10, len(self.b) - 10)
        # check if the food collides the cat
        if[self.b[self.xfood], self.b[self.yfood]] not in self.coor:
            self.canvas.create_image(self.b[self.xfood] - self.side / 2,
                                     self.b[self.yfood] - self.side / 2,
                                     image=self.book, anchor=NW, tags='food')
        else:
            self.food()

    def up(self, event):
        ''' moving up '''
        self.stepy = -self.side
        self.stepx = 0

    def down(self, event):
        ''' moving down '''
        self.stepy = self.side
        self.stepx = 0

    def right(self, event):
        ''' moving right '''
        self.stepx = self.side
        self.stepy = 0

    def left(self, event):
        ''' moving left '''
        self.stepx = -self.side
        self.stepy = 0

    def closeandeasy(self):
        ''' setting up difficulty to easy '''
        self.set_difficulty_parameters(level='Easy')
        self.toplevel.destroy()  # close windows

    def closeandmedium(self):
        ''' setting up difficulty to medium '''
        self.set_difficulty_parameters(level='Median')
        self.toplevel.destroy()  # close windows

    def closeandhard(self):
        ''' setting up difficulty to hard '''
        self.set_difficulty_parameters(level='Hard')
        self.toplevel.destroy()  # close windows

    def set_difficulty_parameters(self, level=None):
        ''' setting up parameters used in games for each difficuly level '''
        self.Nbomb = 4  # number of bomb each time
        if level == 'Easy' or None:
            self.time = 180  # speed control of cat
            self.speed = 2  # speed control of bomb
            self.difficulty_level = 'Easy'

        elif level == 'Median':
            self.time = 140
            self.speed = 4
            self.difficulty_level = 'Median'

        elif level == 'Hard':
            self.time = 100
            self.speed = 6
            self.difficulty_level = 'Hard'

        self.set_difficulty = True  # indicating if we have set up difficulty manually

    def load_images(self):
        ''' load images from the disk '''
        self.ibody = Image.open("body.png")
        self.body = ImageTk.PhotoImage(self.ibody)
        self.ishead = Image.open("head.png")
        self.head = ImageTk.PhotoImage(self.ishead)
        self.itail = Image.open("tail.png")
        self.tail = ImageTk.PhotoImage(self.itail)
        self.ibook = Image.open("book.png")
        self.book = ImageTk.PhotoImage(self.ibook)
        self.ibomb = Image.open("bomb.png")
        self.bomb = ImageTk.PhotoImage(self.ibomb)

    def canvas_size(self):
        return (self.w, self.h)


CattGUI()
