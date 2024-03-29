import os, sys
from copy import deepcopy

import matplotlib
from decimal import Decimal
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QStringListModel, QEvent, pyqtSlot, QObject, Qt, QModelIndex, QItemSelectionModel, \
    QItemSelection, QTimer
from PyQt5.QtGui import QDoubleValidator, QStandardItem, QIntValidator, QPalette, QColor, QStandardItemModel
from PyQt5.QtWidgets import QStyledItemDelegate, QApplication, QLineEdit, QDialog, qApp, QMessageBox, QListWidgetItem, \
    QCheckBox, QAbstractItemView, QVBoxLayout, QWidget, QListView
from matplotlib.figure import Figure

from ui.main_window import Ui_MainWindow
import matplotlib.pyplot as plt

from ui.parameter_info import ParameterInfoDict
from utils.science_plot import SciencePlot, SciencePlotData

matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ui.parameter_adjust_widget import ParameterAdjustWidget
from ui.test_widget import TestWidget
from ui.plot_widget import PlotWidget
from ui.parameter_info import ParameterInfoDict
from physical_model.landau_lifshitz_gilbert import LandauLifshitzGilbertCalculator,CGSSampleInfo,CalculatorType,UnitType


def on_Action_quit():
    sys.exit(0)
    pass


class Simulator(Ui_MainWindow):
    def __init__(self):
        super(Simulator, self).__init__()
        self.intro_text = {
            "en": "Info",
            "cn": "Info",
            "jp": "Info",
        }
        self.alpha_range = [0.0, 1.0]
        self.he_range = [0.0, 200000.0] # A/m
        self.phi_0_range = [0.0, 6.28318530718]
        self.delta_range = [0.0, 6.28318530718]
        self.beta_range = [0.0, 6.28318530718]

        self.alpha = 0.001
        self.he = 0.0
        self.phi_0 = 0.0
        self.delta = 0.0
        self.beta = np.pi / 2

        self.ms = 15.0
        self.hk = 1.0
        self.rho = 1500.
        self.t = 20000

        self.freq_from = 1.
        self.freq_to = 1.e9
        self.num_points = 200

        self.scientific_validator = QDoubleValidator()
        self.scientific_validator.setNotation(QDoubleValidator.ScientificNotation)

        self.sample_info_list = []
        self.list_view_sampleinfo_model = QStandardItemModel()

        self.timer = QTimer()
        self.timer.timeout.connect(self.plot_curves)
        self.timer.start(5000)  # 启动定时器，每5秒触发一次

        self.new_plot_widget = PlotWidget()

    def setupUi(self, MainWindow):
        Ui_MainWindow.setupUi(self, MainWindow)
        # EN-CN-JP
        self.textEdit_intro.setText(self.intro_text.get("en"))
        self.radioButton_intro_en.clicked.connect(self.update_textEdit_intro)
        self.radioButton_intro_cn.clicked.connect(self.update_textEdit_intro)
        self.radioButton_intro_jp.clicked.connect(self.update_textEdit_intro)
        self.radioButton_intro_en.click()

        self.init_fieldinfo_all()

        self.pushButton_shimada_alpha.clicked.connect(self.on_pushButton_shimada_alpha_clicked)
        self.pushButton_shimada_he.clicked.connect(self.on_pushButton_shimada_he_clicked)
        self.pushButton_shimada_phi_0.clicked.connect(self.on_pushButton_shimada_phi_0_clicked)
        self.pushButton_shimada_delta.clicked.connect(self.on_pushButton_shimada_delta_clicked)
        self.pushButton_shimada_beta.clicked.connect(self.on_pushButton_shimada_beta_clicked)

        self.horizontalSlider_shimada_alpha.valueChanged.connect(self.on_horizontalSlider_shimada_alpha_valueChanged)
        self.horizontalSlider_shimada_he.valueChanged.connect(self.on_horizontalSlider_shimada_he_valueChanged)
        self.horizontalSlider_shimada_phi_0.valueChanged.connect(self.on_horizontalSlider_shimada_phi_0_valueChanged)
        self.horizontalSlider_shimada_delta.valueChanged.connect(self.on_horizontalSlider_shimada_delta_valueChanged)
        self.horizontalSlider_shimada_beta.valueChanged.connect(self.on_horizontalSlider_shimada_beta_valueChanged)

        self.init_sampleinfo_all()

        self.lineEdit_info_ohnuma_ms.textEdited.connect(self.on_lineEdit_info_ohnuma_ms_textEdited)
        self.lineEdit_info_ohnuma_hk.textEdited.connect(self.on_lineEdit_info_ohnuma_hk_textEdited)
        self.lineEdit_info_ohnuma_rho.textEdited.connect(self.on_lineEdit_info_ohnuma_rho_textEdited)
        self.lineEdit_info_ohnuma_t.textEdited.connect(self.on_lineEdit_info_ohnuma_t_textEdited)
        self.lineEdit_sampleinfo_freq_from.textEdited.connect(self.on_lineEdit_sampleinfo_freq_from_textEdited)
        self.lineEdit_sampleinfo_freq_to.textEdited.connect(self.on_lineEdit_sampleinfo_freq_to_textEdited)
        self.listView_sampleinfo.setModel(self.list_view_sampleinfo_model)
        self.listView_sampleinfo.setSelectionMode(QListView.SingleSelection)
        self.listView_sampleinfo.setEditTriggers(QListView.NoEditTriggers)
        self.pushButton_sampleinfo_add.clicked.connect(self.on_pushButton_sampleinfo_add_clicked)
        self.pushButton_sampleinfo_update.clicked.connect(self.on_pushButton_sampleinfo_update_clicked)
        self.pushButton_sampleinfo_delete.clicked.connect(self.on_pushButton_sampleinfo_delete_clicked)

        self.spinBox_sampleinfo_freq_nums.setValue(self.num_points)
        self.spinBox_sampleinfo_freq_nums.valueChanged.connect(self.on_spinBox_sampleinfo_freq_nums_valueChanged)

        self.horizontalLayout_2.replaceWidget(self.widget_plot, self.new_plot_widget)
        self.widget_plot.deleteLater()



    def init_fieldinfo_all(self):
        self.lineEdit_shimada_alpha_from.setValidator(self.scientific_validator)
        self.lineEdit_shimada_alpha_to.setValidator(self.scientific_validator)
        self.lineEdit_shimada_alpha_value.setValidator(self.scientific_validator)
        self.lineEdit_shimada_he_from.setValidator(self.scientific_validator)
        self.lineEdit_shimada_he_to.setValidator(self.scientific_validator)
        self.lineEdit_shimada_he_value.setValidator(self.scientific_validator)
        self.lineEdit_shimada_phi_0_from.setValidator(self.scientific_validator)
        self.lineEdit_shimada_phi_0_to.setValidator(self.scientific_validator)
        self.lineEdit_shimada_phi_0_value.setValidator(self.scientific_validator)
        self.lineEdit_shimada_delta_from.setValidator(self.scientific_validator)
        self.lineEdit_shimada_delta_to.setValidator(self.scientific_validator)
        self.lineEdit_shimada_delta_value.setValidator(self.scientific_validator)
        self.lineEdit_shimada_beta_from.setValidator(self.scientific_validator)
        self.lineEdit_shimada_beta_to.setValidator(self.scientific_validator)
        self.lineEdit_shimada_beta_value.setValidator(self.scientific_validator)

        self.lineEdit_shimada_alpha_from.setText(str(self.alpha_range[0]))
        self.lineEdit_shimada_alpha_to.setText(str(self.alpha_range[1]))
        self.lineEdit_shimada_alpha_value.setText(f"{self.alpha:.5g}")
        self.horizontalSlider_shimada_alpha.setValue(get_scale(self.alpha_range[0], self.alpha_range[1],self.alpha))
        self.lineEdit_shimada_he_from.setText(str(self.he_range[0]))
        self.lineEdit_shimada_he_to.setText(str(self.he_range[1]))
        self.lineEdit_shimada_he_value.setText(f"{self.he:.5g}")
        self.horizontalSlider_shimada_he.setValue(get_scale(self.he_range[0], self.he_range[1], self.he))
        self.lineEdit_shimada_phi_0_from.setText(str(self.phi_0_range[0]))
        self.lineEdit_shimada_phi_0_to.setText(str(self.phi_0_range[1]))
        self.lineEdit_shimada_phi_0_value.setText(f"{self.phi_0:.5g}")
        self.horizontalSlider_shimada_phi_0.setValue(get_scale(self.phi_0_range[0], self.phi_0_range[1], self.phi_0))
        self.lineEdit_shimada_delta_from.setText(str(self.delta_range[0]))
        self.lineEdit_shimada_delta_to.setText(str(self.delta_range[1]))
        self.lineEdit_shimada_delta_value.setText(f"{self.delta:.5g}")
        self.horizontalSlider_shimada_delta.setValue(get_scale(self.delta_range[0], self.delta_range[1], self.delta))
        self.lineEdit_shimada_beta_from.setText(str(self.beta_range[0]))
        self.lineEdit_shimada_beta_to.setText(str(self.beta_range[1]))
        self.lineEdit_shimada_beta_value.setText(f"{self.beta:.5g}")
        self.horizontalSlider_shimada_beta.setValue(get_scale(self.beta_range[0], self.beta_range[1], self.beta))

    def init_sampleinfo_all(self):
        self.lineEdit_info_ohnuma_ms.setValidator(self.scientific_validator)
        self.lineEdit_info_ohnuma_hk.setValidator(self.scientific_validator)
        self.lineEdit_info_ohnuma_rho.setValidator(self.scientific_validator)
        self.lineEdit_info_ohnuma_t.setValidator(self.scientific_validator)
        self.lineEdit_info_ohnuma_ms.setText(str(self.ms))
        self.lineEdit_info_ohnuma_hk.setText(str(self.hk))
        self.lineEdit_info_ohnuma_rho.setText(str(self.rho))
        self.lineEdit_info_ohnuma_t.setText(str(self.t))

        self.lineEdit_sampleinfo_freq_from.setValidator(self.scientific_validator)
        self.lineEdit_sampleinfo_freq_to.setValidator(self.scientific_validator)
        self.lineEdit_sampleinfo_freq_from.setText(str(self.freq_from))
        self.lineEdit_sampleinfo_freq_to.setText(str(self.freq_to))
        self.spinBox_sampleinfo_freq_nums.setValue(self.num_points)

    def on_pushButton_shimada_alpha_clicked(self):
        self.alpha_range = [float(self.lineEdit_shimada_alpha_from.text()),float(self.lineEdit_shimada_alpha_to.text())]
        self.alpha = self.alpha_range[0]
        self.lineEdit_shimada_alpha_value.setText(str(self.alpha))
        self.horizontalSlider_shimada_alpha.setValue(get_scale(self.alpha_range[0], self.alpha_range[1], self.alpha))
    def on_pushButton_shimada_he_clicked(self):
        self.he_range = [float(self.lineEdit_shimada_he_from.text()),float(self.lineEdit_shimada_he_to.text())]
        self.he = self.he_range[0]
        self.lineEdit_shimada_he_value.setText(str(self.he))
        self.horizontalSlider_shimada_he.setValue(get_scale(self.he_range[0], self.he_range[1], self.he))
    def on_pushButton_shimada_phi_0_clicked(self):
        self.phi_0_range = [float(self.lineEdit_shimada_phi_0_from.text()),float(self.lineEdit_shimada_phi_0_to.text())]
        self.phi_0 = self.phi_0_range[0]
        self.lineEdit_shimada_phi_0_value.setText(str(self.phi_0))
        self.horizontalSlider_shimada_phi_0.setValue(get_scale(self.phi_0_range[0], self.phi_0_range[1], self.phi_0))
    def on_pushButton_shimada_delta_clicked(self):
        self.delta_range = [float(self.lineEdit_shimada_delta_from.text()),float(self.lineEdit_shimada_delta_to.text())]
        self.delta = self.delta_range[0]
        self.lineEdit_shimada_delta_value.setText(str(self.delta))
        self.horizontalSlider_shimada_delta.setValue(get_scale(self.delta_range[0], self.delta_range[1], self.delta))
    def on_pushButton_shimada_beta_clicked(self):
        self.beta_range = [float(self.lineEdit_shimada_beta_from.text()),float(self.lineEdit_shimada_beta_to.text())]
        self.beta = self.beta_range[0]
        self.lineEdit_shimada_beta_value.setText(str(self.beta))
        self.horizontalSlider_shimada_beta.setValue(get_scale(self.beta_range[0], self.beta_range[1], self.beta))
    def on_horizontalSlider_shimada_alpha_valueChanged(self,new_scale):
        self.alpha = get_value(self.alpha_range[0],self.alpha_range[1],new_scale)
        self.lineEdit_shimada_alpha_value.setText(f"{self.alpha:.5g}")
    def on_horizontalSlider_shimada_he_valueChanged(self,new_scale):
        self.he = get_value(self.he_range[0],self.he_range[1],new_scale)
        self.lineEdit_shimada_he_value.setText(f"{self.he:.5g}")
    def on_horizontalSlider_shimada_phi_0_valueChanged(self,new_scale):
        self.phi_0 = get_value(self.phi_0_range[0],self.phi_0_range[1],new_scale)
        self.lineEdit_shimada_phi_0_value.setText(f"{self.phi_0:.5g}")
    def on_horizontalSlider_shimada_delta_valueChanged(self,new_scale):
        self.delta = get_value(self.delta_range[0],self.delta_range[1],new_scale)
        self.lineEdit_shimada_delta_value.setText(f"{self.delta:.5g}")
    def on_horizontalSlider_shimada_beta_valueChanged(self,new_scale):
        self.beta = get_value(self.beta_range[0],self.beta_range[1],new_scale)
        self.lineEdit_shimada_beta_value.setText(f"{self.beta:.5g}")
    def update_textEdit_intro(self):
        if self.radioButton_intro_en.isChecked():
            self.textEdit_intro.setText(self.intro_text.get("en"))
        elif self.radioButton_intro_cn.isChecked():
            self.textEdit_intro.setText(self.intro_text.get("cn"))
        elif self.radioButton_intro_jp.isChecked():
            self.textEdit_intro.setText(self.intro_text.get("jp"))
        else:
            pass
    def on_lineEdit_info_ohnuma_ms_textEdited(self):
        if self.lineEdit_info_ohnuma_ms.text():
            self.ms = float(self.lineEdit_info_ohnuma_ms.text())
    def on_lineEdit_info_ohnuma_hk_textEdited(self):
        if self.lineEdit_info_ohnuma_hk.text():
            self.hk = float(self.lineEdit_info_ohnuma_hk.text())
    def on_lineEdit_info_ohnuma_rho_textEdited(self):
        if self.lineEdit_info_ohnuma_rho.text():
            self.rho = float(self.lineEdit_info_ohnuma_rho.text())
    def on_lineEdit_info_ohnuma_t_textEdited(self):
        if self.lineEdit_info_ohnuma_t.text():
            self.t = float(self.lineEdit_info_ohnuma_t.text())
    def on_lineEdit_sampleinfo_freq_from_textEdited(self):
        if self.lineEdit_sampleinfo_freq_from.text():
            self.freq_from = float(self.lineEdit_sampleinfo_freq_from.text())
    def on_lineEdit_sampleinfo_freq_to_textEdited(self):
        if self.lineEdit_sampleinfo_freq_to.text():
            self.freq_to = float(self.lineEdit_sampleinfo_freq_to.text())

    def on_pushButton_sampleinfo_add_clicked(self):
        new_sampleinfo = [self.ms,self.hk,self.rho,self.t]
        self.sample_info_list.append(new_sampleinfo)
        self.list_view_sampleinfo_model.appendRow(QStandardItem(f"Ms={self.ms:.2f}kG, Hk={self.hk:3f}Oe\nRho={self.rho:3f}μΩ*cm, t={self.t:.3f}mm"))
    def on_pushButton_sampleinfo_update_clicked(self):
        if self.listView_sampleinfo.selectedIndexes():
            new_sampleinfo = [self.ms,self.hk,self.rho,self.t]
            new_data = QStandardItem(f"Ms={self.ms:.2f}kG, Hk={self.hk:3f}Oe\nRho={self.rho:3f}μΩ*cm, t={self.t:.3f}mm")
            index = self.listView_sampleinfo.selectedIndexes()[0]
            self.sample_info_list[index.row()]=new_sampleinfo
            self.list_view_sampleinfo_model.setItem(index.row(),index.column(),new_data)
            # print(self.sample_info_list)
    def on_pushButton_sampleinfo_delete_clicked(self):
        if self.listView_sampleinfo.selectedIndexes():
            index = self.listView_sampleinfo.selectedIndexes()[0]
            self.sample_info_list.pop(index.row())
            self.list_view_sampleinfo_model.removeRow(index.row())
            print(self.sample_info_list)
            # print(self.listView_sampleinfo.selectedIndexes())
    def on_spinBox_sampleinfo_freq_nums_valueChanged(self,new_value):
        self.num_points = new_value

    def plot_curves(self):
        if self.sample_info_list:
            print("Plot")
            calculator = LandauLifshitzGilbertCalculator(calculator_type=CalculatorType.SHIMADA,
                                                 unit_type=UnitType.SI,
                                                 alpha=self.alpha,
                                                 He=self.he,
                                                 phi_0=self.phi_0,
                                                 delta=self.delta,
                                                 beta=self.beta)
            ohnuma_sample_info_list = []
            for sample_info in self.sample_info_list:
                ohnuma_sample_info_list.append(CGSSampleInfo(sample_info[0], sample_info[1], sample_info[2], sample_info[3]))
            x_list = []

            y1_list = []
            y2_list = []
            for ohnuma_sample_info in ohnuma_sample_info_list:
                freq, (miu_real, miu_imag) = calculator.calculate(f_info=(self.freq_from,self.freq_to), num_points=self.num_points,
                                                                  sample_info=ohnuma_sample_info)
                x_list.append(freq)
                print(f"f from {freq[0]}Hz to {freq[-1]}Hz")
                y1_list.append(miu_real)
                y2_list.append(miu_imag)
            self.new_plot_widget.update_plot(x_list,y1_list,y2_list)
            # for index,x_data in enumerate(x_list):
            #     self.plot_canvas.

        else:
            print("sample_info_list is None")
def get_scale(from_value,to_value,value):
    return int((value - from_value) / (to_value - from_value) * 100.)

def get_value(from_value,to_value,scale):
    return from_value + (to_value-from_value) * scale / 100.



if __name__ == "__main__":
    # 必须添加应用程序，同时不要忘了sys.argv参数
    app = QtWidgets.QApplication(sys.argv)
    # user_data_dir = app.applicationDirPath()  # 获取应用程序的路径
    # user_data_dir = os.path.join(user_data_dir, "userdata/permeability")  # 拼接子目录
    # os.makedirs(user_data_dir, exist_ok=True)  # 确保目录存在
    # 分别对窗体进行实例化
    mainWindow = QtWidgets.QMainWindow()
    # 包装
    # param_info_dict_obj = ParameterInfoDict(user_data_dir)
    simulator = Simulator()
    # 分别初始化UI
    simulator.setupUi(mainWindow)
    # 连接窗体
    # simulator.actionParameter_Setting.triggered.connect(parameterSettingDialog.show)
    # parameterSettingDialogWindow.pushButton_psd_info_greek.clicked.connect(greekAlphabetDialog.show)

    mainWindow.show()  # show（）显示主窗口

    # 软件正常退出
    sys.exit(app.exec_())
