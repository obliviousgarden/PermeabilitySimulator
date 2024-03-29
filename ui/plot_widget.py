import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

plt.rcParams.update({'font.size': 24})

class PlotWidget(QWidget):
    def __init__(self):
        super(PlotWidget, self).__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax1 = self.figure.add_subplot(111)
        self.ax1.set_xlabel('Frequency, f (log scale)')
        self.ax1.set_ylabel('Real Permeability, μ\'', color='blue')
        self.ax1.tick_params('y', colors='blue')

        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel('Imaginary Permeability, μ"', color='red')
        self.ax2.tick_params('y', colors='red')

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.colors = list(plt.rcParams['axes.prop_cycle'].by_key()['color'])

    def update_plot(self, x_data_list,y1_data_list,y2_data_list):
        # 更新数据

        # 清空绘图区域
        self.ax1.clear()
        self.ax2.clear()
        for index,x_data in enumerate(x_data_list):
            # self.ax1.semilogx(x_data, y1_data_list[index], label=f'μ\'-#{index}', color=self.colors[index])
            # self.ax2.semilogx(x_data, y2_data_list[index], label=f'μ"-#{index}', color=self.colors[index],linestyle='--')
            self.ax1.loglog(x_data, y1_data_list[index], label=f'μ\'-#{index}', color=self.colors[index])
            self.ax2.loglog(x_data, y2_data_list[index], label=f'μ"-#{index}', color=self.colors[index],
                              linestyle='--')

        self.ax1.set_title('Permeability LLG Simulation on Frequency')
        lines, labels = self.ax1.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        self.ax2.legend(lines + lines2, labels + labels2, loc='upper right')
        # self.ax1.grid(True)

        # 刷新画布
        self.canvas.draw()

