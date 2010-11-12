from Tkinter import *

class Wall64_Visualizer(object):
    PIXEL_WIDTH = 50

    def __init__(self):
        self.tk_init()
        self.cull_list = []

    def tk_init(self):
        self.root = Tk()
        self.root.title("Wall64")
        self.root.resizable(0, 0)
        self.frame = Frame(self.root, bd=5, relief=SUNKEN)
        self.frame.pack()
        width = self.PIXEL_WIDTH * 8
        self.canvas = Canvas(self.frame, 
                        width=width, 
                        height=width, bd=0, 
                        highlightthickness=0)
        self.canvas.pack()
        self.root.update()

    def draw(self, wall):
        for item in self.cull_list:
            self.canvas.delete(item)
        self.cull_list = []
        for x in range(8):
            for y in range(8):
                x_0 = x * self.PIXEL_WIDTH
                y_0 = y * self.PIXEL_WIDTH
                x_1 = x_0 + self.PIXEL_WIDTH
                y_1 = y_0 + self.PIXEL_WIDTH
                pixel = wall.pixel(x, y)
                color = "#%02x%02x%02x" % pixel.rgb_8bit
                rect = self.canvas.create_rectangle(x_0, y_0, x_1, y_1, fill=color)
                self.cull_list.append(rect)
        self.canvas.update()
        #self.root.update_idletasks()
        #self.root.update()

