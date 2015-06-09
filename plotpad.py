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
import FileDialog  # only usefull, when creating a windows executable file, using pyinstaller
                   # without it, a few dependencies won't be imported


class MainWindow:

    def __init__(self):

        self.conditions = []
        self.ratios = []
        self.data = {}

        self.state_file = False
        self.state_plot = False
        self.state_mean = False
        self.state_median = False
        self.state_percentile = False

        self.root = tk.Tk()
        self.root.wm_title("PlotPad")

        self.fig = plt.figure(figsize=(10, 6), frameon=True)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig.subplots_adjust(bottom=0.30)
        plt.xticks([])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=0)

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
        self.toolbar.update()

        self.canvas._tkcanvas.pack()

        self.buttons_topframe = tk.Frame(self.root)
        self.buttons_topframe.pack()

        self.buttons_midframe = tk.Frame(self.root)
        self.buttons_midframe.pack()

        self.buttons_botframe = tk.Frame(self.root)
        self.buttons_botframe.pack()

        self.open_button = tk.Button(self.buttons_topframe, text="Open CSV File", command=self.openfile)
        self.open_button.pack(side="left")

        self.plot_button = tk.Button(self.buttons_topframe, text="Plot Data", command=self.plotdata)
        self.plot_button.pack(side="left")

        self.clear_button = tk.Button(self.buttons_topframe, text="Clear Plot", command=self.clearplot)
        self.clear_button.pack(side="left")

        self.plotmean_button = tk.Button(self.buttons_midframe, text="Plot Mean", command=self.plotmeanline)
        self.plotmean_button.pack(side="left")

        self.clearmean_button = tk.Button(self.buttons_midframe, text="Clear Mean Plot", command=self.clearmean)
        self.clearmean_button.pack(side="left")

        self.plotmedian_button = tk.Button(self.buttons_midframe, text="Plot Median", command=self.plotmedianline)
        self.plotmedian_button.pack(side="left")

        self.clearmedian_button = tk.Button(self.buttons_midframe, text="Clear Median Plot", command=self.clearmedian)
        self.clearmedian_button.pack(side="left")

        self.plotpercentile_button = tk.Button(self.buttons_botframe, text="Plot Percentile",
                                               command=self.plotpercentile)
        self.plotpercentile_button.pack(side="left")

        self.percentile1_entry = tk.Entry(self.buttons_botframe, justify="center")
        self.percentile1_entry.pack(side="left")
        self.percentile1_entry.insert(10, "25")

        self.percentile2_entry = tk.Entry(self.buttons_botframe, justify="center")
        self.percentile2_entry.pack(side="left")
        self.percentile2_entry.insert(10, "75")

        self.clearpercentile_button = tk.Button(self.buttons_botframe, text="Clear Percentile",
                                                command=self.clearpercentile)
        self.clearpercentile_button.pack(side="left")

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

        self.data = self.formatdata(self.conditions, self.ratios)
        self.state_file = True

    def plotmeanline(self):
        count = 0

        for cond in sorted(self.data.keys()):
            meanvalue = np.mean(np.array(self.data[cond]))
            line_x = np.arange(0.1+count, 1.0+count, 0.1)[0:10]

            self.ax.plot(line_x, [meanvalue]*len(line_x), c="k", linewidth=1.5, linestyle="--")
            """self.ax.annotate(str(meanvalue)[0:5], (0.4+count, meanvalue+0.3),
                             backgroundcolor="w", bbox=dict(facecolor="red"))"""

            count += 1

        self.canvas.show()
        self.state_mean = True

    def plotmedianline(self):
        count = 0

        for cond in sorted(self.data.keys()):
            medianvalue = np.median(np.array(self.data[cond]))
            line_x = np.arange(0.1+count, 1.0+count, 0.1)[0:10]

            self.ax.plot(line_x, [medianvalue]*len(line_x), c="k", linewidth=1.5)
            """self.ax.annotate(str(medianvalue)[0:5], (0.4+count, medianvalue+0.3),
                             backgroundcolor="w", bbox=dict(facecolor="red"))"""

            count += 1

        self.canvas.show()
        self.state_median = True

    def plotpercentile(self):
        if self.state_percentile:
            self.clearpercentile()

            count = 0

            for cond in sorted(self.data.keys()):
                percentilevalue1 = np.percentile(np.array(self.data[cond]), int(self.percentile1_entry.get()))
                percentilevalue2 = np.percentile(np.array(self.data[cond]), int(self.percentile2_entry.get()))
                line_x = np.arange(0.1+count, 1.0+count, 0.1)[0:10]

                self.ax.plot(line_x, [percentilevalue1]*len(line_x), c="k", linewidth=1.5, linestyle="-")
                self.ax.plot(line_x, [percentilevalue2]*len(line_x), c="k", linewidth=1.5, linestyle="-")
                self.ax.plot([0.5+count, 0.5+count], [percentilevalue1, percentilevalue2], c="k", linewidth=1.5,
                             linestyle="-")

                count += 1

            self.canvas.show()
            self.state_percentile = True

        else:
            count = 0

            for cond in sorted(self.data.keys()):
                percentilevalue1 = np.percentile(np.array(self.data[cond]), int(self.percentile1_entry.get()))
                percentilevalue2 = np.percentile(np.array(self.data[cond]), int(self.percentile2_entry.get()))
                line_x = np.arange(0.1+count, 1.0+count, 0.1)[0:10]

                self.ax.plot(line_x, [percentilevalue1]*len(line_x), c="k", linewidth=1.5, linestyle="-")
                self.ax.plot(line_x, [percentilevalue2]*len(line_x), c="k", linewidth=1.5, linestyle="-")
                self.ax.plot([0.5+count, 0.5+count], [percentilevalue1, percentilevalue2], c="k", linewidth=1.5,
                             linestyle="-")

                count += 1

            self.canvas.show()
            self.state_percentile = True

    def plotdata(self):
        if self.state_file:
            plt.grid(True)

            if self.state_plot:
                self.clearplot()

                count = 0
                col_gen = cycle('bgrcm')

                for cond in sorted(self.data.keys()):

                    colors = col_gen.next()

                    for num in self.data[cond]:
                        x = random.randrange(40, 60, 1)
                        self.ax.scatter(x*0.01+count, num, s=50, c=colors, alpha=0.5)

                    count += 1

                labels = sorted(self.data.keys())
                plt.xticks(np.arange(0.5, 1.5+count, 1), labels, rotation=60)
                plt.ylabel("Fluorescence Ratio")
            else:
                count = 0
                col_gen = cycle('bgrcm')

                for cond in sorted(self.data.keys()):

                    colors = col_gen.next()

                    for num in self.data[cond]:
                        x = random.randrange(40, 60, 1)
                        self.ax.scatter(x*0.01+count, num, s=50, c=colors, alpha=0.5)

                    count += 1

                labels = sorted(self.data.keys())
                plt.xticks(np.arange(0.5, 1.5+count, 1), labels, rotation=60)
                plt.ylabel("Fluorescence Ratio")

            self.state_plot = True
            self.canvas.show()

    def clearplot(self):
        if self.state_plot:
            self.ax.cla()
            plt.xticks([])

            self.state_plot = False
            self.state_percentile = False
            self.state_median = False
            self.state_mean = False

            self.canvas.show()

    def clearmean(self):
        if self.state_mean:
            self.state_mean = False

            if self.state_median:
                if self.state_percentile:
                    self.clearplot()
                    self.plotdata()
                    self.plotmedianline()
                    self.plotpercentile()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotmedianline()

            elif self.state_percentile:
                self.clearplot()
                self.plotdata()
                self.plotpercentile()

            else:
                self.clearplot()
                self.plotdata()

    def clearmedian(self):
        if self.state_median:
            self.state_median = False

            if self.state_mean:
                if self.state_percentile:
                    self.clearplot()
                    self.plotdata()
                    self.plotmeanline()
                    self.plotpercentile()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotmeanline()

            elif self.state_percentile:
                self.clearplot()
                self.plotdata()
                self.plotpercentile()

            else:
                self.clearplot()
                self.plotdata()

    def clearpercentile(self):
        if self.state_percentile:
            self.state_percentile = False

            if self.state_mean:
                if self.state_median:
                    self.clearplot()
                    self.plotdata()
                    self.plotmeanline()
                    self.plotmedianline()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotmeanline()

            elif self.state_median:
                self.clearplot()
                self.plotdata()
                self.plotmedianline()

            else:
                self.clearplot()
                self.plotdata()

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
