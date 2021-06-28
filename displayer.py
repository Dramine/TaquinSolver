from tkinter import *
from PIL import Image, ImageTk
import tkinter as tk
from environment import Environment
from utils import PositionManager


class Application(tk.Tk):
    def __init__(self, env: Environment):
        super().__init__()
        self.env = env
        self.width = 500
        self.height = 500
        self.create_window()
        self.canvas_grid = []
        self.images = []
        self.init_image()
        self.load_image()

    def init_image(self):
        for i in range(self.env.n*self.env.n-1):
            img = ImageTk.PhotoImage(
                Image.open("images/" + str(self.env.n) + "x" + str(self.env.n) + "/" + str(i) + ".png"))
            self.images.append(img)
            self.canvas_grid.append(Canvas(self, width=self.width / self.env.n, height=self.height / self.env.n))
            self.canvas_grid[i].create_image(0, 0, anchor=NW, image=self.images[i])
        print("fin_init")

    def create_window(self):
        self.title("The taquin")
        self.geometry(str(self.width + self.env.n*4)+"x"+str(self.height + self.env.n*4)+"+0+0")

    def load_image(self):
        for i in range(self.env.n * self.env.n-1):
            self.canvas_grid[i].grid_forget()
        for i, agent in list(self.env.agents.items()):
            pos = PositionManager.pos_2D(i, self.env.n)
            self.canvas_grid[agent.id].grid(row=pos[1], column=pos[0])
        self.update()
        self.env.screen_updated = True
        if not self.env.is_finish():
            self.after(0, self.load_image)
