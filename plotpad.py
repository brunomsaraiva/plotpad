import Tkinter as tk
import tkFileDialog
import random
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from itertools import cycle
import numpy as np
import tkMessageBox
import sys
import FileDialog


class MainWindow:

    def __init__(self):

        self.conditions = []
        self.ratios = []
        self.data = {}

        self.root = tk.Tk()
        self.root.wm_title("PlotPad")

        self.fig = plt.figure(figsize=(10, 6), frameon=True)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig.subplots_adjust(bottom=0.30)
        plt.xticks([])
        plt.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master= self.root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack()

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.root )
        self.toolbar.update()

        self.canvas._tkcanvas.pack()

        self.open_button = tk.Button(self.root, text="Open CSV File", command=self.openfile)
        self.open_button.pack()

        self.plot_button = tk.Button(self.root, text="Plot Data", command=lambda: self.plotdata(self.data))
        self.plot_button.pack()

        self.clear_button = tk.Button(self.root, text="Clear Plot", command=self.clearplot)
        self.clear_button.pack()

    def formatdata(self, cond, rat):
        conditions = sorted(set(cond))
        data = {c: [] for c in conditions}

        for i in range(len(cond)):
            data[cond[i]].append(rat[i])

        return data

    def openfile(self):
        filename = tkFileDialog.askopenfilename(parent=self.root, title='Open CSV file')
        f = open(filename, "rb")
        lines = f.readlines()
        linedata = []

        for line in lines:
            linedata.append(line.strip().split(";"))

        self.conditions = []
        self.ratios = []
        self.data = {}

        for item in linedata:
            self.conditions.append(str(item[0]))
            self.ratios.append(float(item[1]))

        self.data = self.formatdata( self.conditions, self.ratios)

    def plotMedianLine(self, values, count):
        medianvalue = np.median(np.array(values))
        line_x = np.arange(0.2+count, 0.8+count, 0.1)
        self.ax.plot(line_x, [medianvalue]*len(line_x), c="k")
        self.ax.annotate(str(medianvalue)[0:5], (0.4+count, medianvalue+0.3),
                         backgroundcolor="w", bbox=dict(facecolor="red"))

    def plotdata(self, data):
        count = 0
        col_gen = cycle('bgrcm')

        for cond in sorted(self.data.keys()):

            colors = col_gen.next()

            for num in self.data[cond]:
                x = random.randrange(40, 60, 1)
                self.ax.scatter(x*0.01+count, num, s=50, c=colors, alpha=0.5)

            self.plotMedianLine(self.data[cond], count)

            count += 1

        labels = sorted(self.data.keys())
        plt.xticks(np.arange(0.5, 1.5+count, 1), labels, rotation=60)
        plt.ylabel("Fluorescence Ratio")
        self.canvas.show()

    def clearplot(self):
        self.ax.cla()
        plt.xticks([])
        self.canvas.show()

    def on_closing(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

def main():
    App = MainWindow()
    App.root.protocol("WM_DELETE_WINDOW", App.on_closing)
    App.root.mainloop()


if __name__ == '__main__':
    main()
    sys.exit()
