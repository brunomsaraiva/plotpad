import Tkinter as tk
import tkFileDialog
import random
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from itertools import cycle
import numpy as np
import scipy.stats
import tkMessageBox
import sys


class PlotPadApp:

    def __init__(self):

        # variables used to control the state of the program
        self.state_file = False
        self.state_plot = False
        self.state_mean = False
        self.state_median = False
        self.state_percentile = False
        self.state_threshold = False

        # variables used to store the relevant data
        self.conditions = []
        self.ratios = []
        self.data = {}
        self.means = []
        self.medians = []
        self.stds = []
        self.ttest_matrix = []

        # GUI components
        self.root = tk.Tk()
        self.root.wm_title("PlotPad v2.0")

        self.fig = plt.figure(figsize=(14, 6), frameon=True)

        self.ax = None
        self.table1 = None
        self.table2 = None

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack()

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
        self.toolbar.update()

        self.canvas._tkcanvas.pack()

        self.buttons_topframe = tk.Frame(self.root)
        self.buttons_topframe.pack(fill="x")

        self.buttons_midframe = tk.Frame(self.root)
        self.buttons_midframe.pack(fill="x")

        self.buttons_botframe = tk.Frame(self.root)
        self.buttons_botframe.pack(fill="x")

        b_width = 14
        b_side = "left"

        self.open_button = tk.Button(self.buttons_topframe, text="Open CSV File", command=self.openfile, width=b_width)
        self.open_button.pack(side=b_side)

        self.plot_button = tk.Button(self.buttons_topframe, text="Plot Data", command=self.plotdata, width=b_width)
        self.plot_button.pack(side=b_side)

        self.plotpercentile_button = tk.Button(self.buttons_topframe, text="Plot Percentile",
                                               command=self.plotpercentile, width=b_width)
        self.plotpercentile_button.pack(side=b_side)

        self.plotthreshold_button = tk.Button(self.buttons_topframe, text="Plot Threshold",
                                              command=self.plotthreshold, width=b_width)
        self.plotthreshold_button.pack(side=b_side)

        self.plotmean_button = tk.Button(self.buttons_midframe, text="Plot Mean", command=self.plotmeanline,
                                         width=b_width)
        self.plotmean_button.pack(side=b_side)

        self.plotmedian_button = tk.Button(self.buttons_midframe, text="Plot Median", command=self.plotmedianline,
                                           width=b_width)
        self.plotmedian_button.pack(side=b_side)

        self.percentile1_entry = tk.Entry(self.buttons_midframe, justify="center", width=8)
        self.percentile1_entry.pack(side=b_side)
        self.percentile1_entry.insert(10, "25")

        self.percentile2_entry = tk.Entry(self.buttons_midframe, justify="center", width=8)
        self.percentile2_entry.pack(side=b_side)
        self.percentile2_entry.insert(10, "75")

        self.threshold_entry = tk.Entry(self.buttons_midframe, justify="center", width=16)
        self.threshold_entry.pack(side=b_side)
        self.threshold_entry.insert(10, "2")

        self.clearmean_button = tk.Button(self.buttons_botframe, text="Clear Mean Plot", command=self.clearmean,
                                          width=b_width)
        self.clearmean_button.pack(side=b_side)

        self.clearmedian_button = tk.Button(self.buttons_botframe, text="Clear Median Plot", command=self.clearmedian,
                                            width=b_width)
        self.clearmedian_button.pack(side=b_side)

        self.clearpercentile_button = tk.Button(self.buttons_botframe, text="Clear Percentile",
                                                command=self.clearpercentile, width=b_width)
        self.clearpercentile_button.pack(side=b_side)

        self.clearthreshold_button = tk.Button(self.buttons_botframe, text="Clear Threshold",
                                               command=self.clearthreshold, width=b_width)
        self.clearthreshold_button.pack(side=b_side)

        self.clear_button = tk.Button(self.buttons_botframe, text="Clear Plot", command=self.clearplot, width=b_width)
        self.clear_button.pack(side=b_side)

    def formatdata(self):
        conditions = sorted(set(self.conditions))
        self.data = {c: [] for c in conditions}
        count = 1

        for i in range(len(self.conditions)):
            self.data[self.conditions[i]].append(self.ratios[i])

        for cond in sorted(self.data.keys()):
            self.means.append(np.mean(np.array(self.data[cond])))
            self.medians.append(np.median(np.array(self.data[cond])))
            self.stds.append(np.std(np.array(self.data[cond])))

            ttest_row = ["C"+str(count)]
            count+=1

            for cond2 in sorted(self.data.keys()):
                if cond == cond2:
                    ttest_row.append("X")
                else:
                    pval = scipy.stats.ttest_ind(self.data[cond], self.data[cond2])[1]
                    if pval < 0.05:
                        ttest_row.append("Yes")
                    else:
                        ttest_row.append("No")

            self.ttest_matrix.append(ttest_row)

    def openfile(self):
        filename = tkFileDialog.askopenfilename(parent=self.root, title='Open CSV file')

        # in case no file is selected keeps the previous plot (if any)
        # otherwise clears the plot before loading the new csv
        if self.state_plot and filename != "":
            self.clearplot()
            self.conditions = []
            self.ratios = []
            self.data = {}
            self.means = []
            self.medians = []
            self.stds = []
            self.ttest_matrix = []

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

        self.formatdata()
        self.state_file = True

    def plotdata(self):
        if self.state_file:
            plt.grid(True)

            if self.state_plot:
                self.ax = plt.subplot2grid((2, 2), (0, 0), rowspan=2)

                self.table1 = plt.subplot2grid((2, 2), (0, 1))
                self.table1.axis("off")

                self.table2 = plt.subplot2grid((2, 2), (1, 1))
                self.table2.axis("off")

                self.fig.subplots_adjust(bottom=0.25)
                self.fig.subplots_adjust(right=0.98)
                self.fig.subplots_adjust(left=0.05)
                self.fig.subplots_adjust(hspace=0.15)
                self.fig.subplots_adjust(wspace=0.36)

                count = 0
                col_gen = cycle('bgrcm')

                for cond in sorted(self.data.keys()):

                    colors = col_gen.next()

                    for num in self.data[cond]:
                        x = random.randrange(40, 60, 1)
                        self.ax.scatter(x*0.01+count, num, s=50, c=colors, alpha=0.5)

                    count += 1

                labels = sorted(self.data.keys())
                self.ax.set_xticks(np.arange(0.5, 1.5+count, 1))
                self.ax.set_xticklabels(labels, rotation=65)

            else:
                self.ax = plt.subplot2grid((2, 2), (0, 0), rowspan=2)

                self.table1 = plt.subplot2grid((2, 2), (0, 1))
                self.table1.axis("off")

                self.table2 = plt.subplot2grid((2, 2), (1, 1))
                self.table2.axis("off")

                self.fig.subplots_adjust(bottom=0.25)
                self.fig.subplots_adjust(bottom=0.34)
                self.fig.subplots_adjust(right=0.98)
                self.fig.subplots_adjust(left=0.05)
                self.fig.subplots_adjust(hspace=0.15)
                self.fig.subplots_adjust(wspace=0.36)

                count = 0
                col_gen = cycle('bgrcm')

                for cond in sorted(self.data.keys()):

                    colors = col_gen.next()

                    for num in self.data[cond]:
                        x = random.randrange(40, 60, 1)
                        self.ax.scatter(x*0.01+count, num, s=50, c=colors, alpha=0.5)

                    count += 1

                labels = sorted(self.data.keys())
                self.ax.set_xticks(np.arange(0.5, 1.5+count, 1))
                self.ax.set_xticklabels(labels, rotation=65)

            self.createtables()
            self.state_plot = True
            self.canvas.show()

    def plotmeanline(self):
        count = 0

        for meanvalue in self.means:
            line_x = np.arange(0.1+count, 1.0+count, 0.1)[0:10]
            self.ax.plot(line_x, [meanvalue]*len(line_x), c="k", linewidth=1.5, linestyle="--")

            count += 1

        self.state_mean = True
        self.canvas.show()

    def plotmedianline(self):
        count = 0

        for medianvalue in self.medians:
            line_x = np.arange(0.1+count, 1.0+count, 0.1)[0:10]
            self.ax.plot(line_x, [medianvalue]*len(line_x), c="k", linewidth=1.5, linestyle="-")

            count += 1

        self.state_median = True
        self.canvas.show()

    def plotpercentile(self):
        if self.state_plot:
            if self.state_percentile:
                self.clearpercentile()

                count = 0

                for cond in sorted(self.data.keys()):
                    percentilevalue1 = np.percentile(np.array(self.data[cond]), int(self.percentile1_entry.get()))
                    percentilevalue2 = np.percentile(np.array(self.data[cond]), int(self.percentile2_entry.get()))
                    line_x = np.arange(0.3+count, 0.8+count, 0.1)[0:6]

                    self.ax.plot(line_x, [percentilevalue1]*len(line_x), c="k", linewidth=1.5, linestyle="-")
                    self.ax.plot(line_x, [percentilevalue2]*len(line_x), c="k", linewidth=1.5, linestyle="-")
                    self.ax.plot([0.5+count, 0.5+count], [percentilevalue1, percentilevalue2], c="k", linewidth=1.5,
                                 linestyle="-")

                    count += 1

                self.state_percentile = True
                self.canvas.show()

            else:
                count = 0

                for cond in sorted(self.data.keys()):
                    percentilevalue1 = np.percentile(np.array(self.data[cond]), int(self.percentile1_entry.get()))
                    percentilevalue2 = np.percentile(np.array(self.data[cond]), int(self.percentile2_entry.get()))
                    line_x = np.arange(0.3+count, 0.8+count, 0.1)[0:6]

                    self.ax.plot(line_x, [percentilevalue1]*len(line_x), c="k", linewidth=1.5, linestyle="-")
                    self.ax.plot(line_x, [percentilevalue2]*len(line_x), c="k", linewidth=1.5, linestyle="-")
                    self.ax.plot([0.5+count, 0.5+count], [percentilevalue1, percentilevalue2], c="k", linewidth=1.5,
                                 linestyle="-")

                    count += 1

                self.state_percentile = True
                self.canvas.show()

    def plotthreshold(self):
        if self.state_plot:
            self.ax.plot([0, len(self.data.keys())], [int(self.threshold_entry.get())]*2, c="b",
                         linewidth=1.5, linestyle="--")

            self.state_threshold = True
            self.canvas.show()

    def clearplot(self):
        if self.state_plot:
            plt.clf()

            self.state_plot = False
            self.state_percentile = False
            self.state_median = False
            self.state_mean = False
            self.state_threshold = False

            self.canvas.show()

    def clearmean(self):

        if self.state_mean:
            self.state_mean = False

            if self.state_median:
                if self.state_percentile:
                    if self.state_threshold:
                        self.clearplot()
                        self.plotdata()
                        self.plotmedianline()
                        self.plotpercentile()
                        self.plotthreshold()

                    else:
                        self.clearplot()
                        self.plotdata()
                        self.plotmedianline()
                        self.plotpercentile()

                elif self.state_threshold:
                    self.clearplot()
                    self.plotdata()
                    self.plotmedianline()
                    self.plotthreshold()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotmedianline()

            elif self.state_percentile:
                if self.state_threshold:
                    self.clearplot()
                    self.plotdata()
                    self.plotpercentile()
                    self.plotthreshold()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotpercentile()

            elif self.state_threshold:
                self.clearplot()
                self.plotdata()
                self.plotthreshold()

            else:
                self.clearplot()
                self.plotdata()

    def clearmedian(self):
        if self.state_median:
            self.state_median = False

            if self.state_mean:
                if self.state_percentile:
                    if self.state_threshold:
                        self.clearplot()
                        self.plotdata()
                        self.plotmeanline()
                        self.plotpercentile()
                        self.plotthreshold()

                    else:
                        self.clearplot()
                        self.plotdata()
                        self.plotmeanline()
                        self.plotpercentile()

                elif self.state_threshold:
                    self.clearplot()
                    self.plotdata()
                    self.plotmeanline()
                    self.plotthreshold()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotmeanline()

            elif self.state_percentile:
                if self.state_threshold:
                    self.clearplot()
                    self.plotdata()
                    self.plotpercentile()
                    self.plotthreshold()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotpercentile()

            elif self.state_threshold:
                self.clearplot()
                self.plotdata()
                self.plotthreshold()

            else:
                self.clearplot()
                self.plotdata()

    def clearthreshold(self):
        if self.state_threshold:
            self.state_threshold = False

            if self.state_median:
                if self.state_percentile:
                    if self.state_mean:
                        self.clearplot()
                        self.plotdata()
                        self.plotmedianline()
                        self.plotpercentile()
                        self.plotmeanline()

                    else:
                        self.clearplot()
                        self.plotdata()
                        self.plotmedianline()
                        self.plotpercentile()

                elif self.state_mean:
                    self.clearplot()
                    self.plotdata()
                    self.plotmedianline()
                    self.plotmeanline()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotmedianline()

            elif self.state_percentile:
                if self.state_mean:
                    self.clearplot()
                    self.plotdata()
                    self.plotpercentile()
                    self.plotmeanline()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotpercentile()

            elif self.state_mean:
                self.clearplot()
                self.plotdata()
                self.plotmeanline()

            else:
                self.clearplot()
                self.plotdata()

    def clearpercentile(self):
        if self.state_percentile:
            self.state_percentile = False

            if self.state_median:
                if self.state_mean:
                    if self.state_threshold:
                        self.clearplot()
                        self.plotdata()
                        self.plotmedianline()
                        self.plotmeanline()
                        self.plotthreshold()

                    else:
                        self.clearplot()
                        self.plotdata()
                        self.plotmedianline()
                        self.plotmeanline()

                elif self.state_threshold:
                    self.clearplot()
                    self.plotdata()
                    self.plotmedianline()
                    self.plotthreshold()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotmedianline()

            elif self.state_mean:
                if self.state_threshold:
                    self.clearplot()
                    self.plotdata()
                    self.plotmeanline()
                    self.plotthreshold()

                else:
                    self.clearplot()
                    self.plotdata()
                    self.plotmeanline()

            elif self.state_threshold:
                self.clearplot()
                self.plotdata()
                self.plotthreshold()

            else:
                self.clearplot()
                self.plotdata()

    def createtables(self):
        celldata = []
        conditions = sorted(self.data.keys())
        table_fs = 10

        for i in range(len(conditions)):
            celldata.append([str(self.means[i])[0:4], str(self.medians[i])[0:4],
                             str(self.stds[i])[0:4]])

        table = self.table1.table(cellText=celldata, rowLabels=sorted(self.data.keys()),
                                  colLabels=["Mean", "Median", "Std"], cellLoc="center",
                                  loc="center", colWidths=[0.20, 0.20, 0.20])

        table.auto_set_font_size(False)
        table.set_fontsize(table_fs)

        table2_colLabels= [""]

        self.table2.set_title("Independent t-test (p-value < 0.05)")

        for line in self.ttest_matrix:
            table2_colLabels.append(line[0])

        table2 = self.table2.table(cellText=self.ttest_matrix, rowLabels=sorted(self.data.keys()),
                                   colLabels=table2_colLabels, cellLoc="center",
                                   loc="center")

        table2.auto_set_font_size(False)
        table2.set_fontsize(table_fs)

    def on_closing(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()


def main():
    App = PlotPadApp()
    App.root.protocol("WM_DELETE_WINDOW", App.on_closing)
    App.root.mainloop()

if __name__ == '__main__':
    main()
    sys.exit()
