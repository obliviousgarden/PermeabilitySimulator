import numpy as np
from PyQt5.QtGui import QDoubleValidator, QCursor
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt, pyqtSlot

from ui.parameter_info import ParameterInfo


# label             from_value to_value update_range
# label_value_now               slider
class ParameterAdjustWidget(QWidget):
    suffix:str = "parm_adj"
    counter:int = 1
    scientific_validator = QDoubleValidator()
    scientific_validator.setNotation(QDoubleValidator.ScientificNotation)

    def __init__(self, parameter_info:ParameterInfo):
        super(ParameterAdjustWidget, self).__init__()
        self.name:str = parameter_info.name
        self.description:str = parameter_info.description
        self.symbol:str = parameter_info.symbol
        self.unit:str = parameter_info.unit
        self.from_value:float = parameter_info.from_value
        self.to_value:float = parameter_info.to_value
        self.value:float = parameter_info.default_value
        self.is_log:bool = parameter_info.is_log

        self.scale = (np.log10(self.value) - np.log10(self.from_value)) / (np.log10(self.to_value / self.from_value)) * 100. \
            if self.is_log else (self.value - self.from_value) / (self.to_value - self.from_value) * 100.

        self.layout = QGridLayout()
        self.layout.setObjectName(f"gridLayout_{ParameterAdjustWidget.suffix}_{ParameterAdjustWidget.counter}")

        label_name_str: str = f"{self.name} ({self.symbol})" if self.unit == "1" else f"{self.name} ({self.symbol}) [{self.unit}]"
        self.name_label = QLabel(label_name_str)
        self.name_label.setObjectName(f"label_{ParameterAdjustWidget.suffix}_name_{ParameterAdjustWidget.counter}")
        self.name_label.setToolTip(f"<html><body>"
                              f"<p><b>{self.name.upper()}</b></p>"
                              f"<p>-----------------------------------------------</p>"
                              f"<p><i><u>Name</u></i>&nbsp;:&nbsp;{self.name}</p>"
                              f"<p><i><u>Description</u></i>&nbsp;:&nbsp;{self.description}</p>"
                              f"<p><i><u>Symbol</u></i>&nbsp;:&nbsp;{self.symbol}</p>"
                              f"<p><i><u>Min.</u></i>&nbsp;:&nbsp;{self.from_value}</p>"
                              f"<p><i><u>Max.</u></i>&nbsp;:&nbsp;{self.to_value}</p>"
                              f"<p><i><u>Unit</u></i>&nbsp;:&nbsp;{self.unit}</p>"
                              f"<p><i><u>Is LOG?</u></i>&nbsp;:&nbsp;{self.is_log}</p>"
                              f"</body></html>")
        self.layout.addWidget(self.name_label, 0, 0)

        line_edit_from_value_str = f"{self.from_value:.{5}e}" if self.is_log else f"{self.from_value:.{5}g}"
        self.line_edit_from_value = QLineEdit()
        self.line_edit_from_value.setObjectName(f"lineEdit_{ParameterAdjustWidget.suffix}_from_{ParameterAdjustWidget.counter}")
        self.line_edit_from_value.setText(line_edit_from_value_str)
        self.line_edit_from_value.setValidator(ParameterAdjustWidget.scientific_validator)
        self.layout.addWidget(self.line_edit_from_value,0,1)

        line_edit_to_value_str = f"{self.to_value:.{5}e}" if self.is_log else f"{self.to_value:.{5}g}"
        self.line_edit_to_value = QLineEdit()
        self.line_edit_to_value.setObjectName(
            f"lineEdit_{ParameterAdjustWidget.suffix}_to_{ParameterAdjustWidget.counter}")
        self.line_edit_to_value.setText(line_edit_to_value_str)
        self.line_edit_to_value.setValidator(ParameterAdjustWidget.scientific_validator)
        self.layout.addWidget(self.line_edit_to_value, 0, 2)

        self.push_button_update = QPushButton("UPDATE")
        self.setObjectName(f"pushButton_{ParameterAdjustWidget.suffix}_update_{ParameterAdjustWidget.counter}")
        self.push_button_update.clicked.connect(self.on_push_button_update_clicked)
        self.layout.addWidget(self.push_button_update, 0, 3)

        label_value_str = f"{self.value:.{5}e}" if self.is_log else f"{self.value:.{5}g}"
        self.value_label = QLabel(label_value_str)
        self.value_label.setObjectName(f"label_{ParameterAdjustWidget.suffix}_value_{ParameterAdjustWidget.counter}")
        self.layout.addWidget(self.value_label, 1, 0)

        self.horizontalSlider = QSlider()
        self.horizontalSlider.setObjectName(f"horizontalSlider_{ParameterAdjustWidget.suffix}_slider_{ParameterAdjustWidget.counter}")
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider.setCursor(QCursor(Qt.ArrowCursor))
        self.horizontalSlider.setInvertedControls(False)
        self.horizontalSlider.setTickPosition(QSlider.TicksAbove)
        if self.is_log:
            self.horizontalSlider.setMinimum(1)
        else:
            self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setPageStep(5)
        self.horizontalSlider.setValue(int(self.scale))
        self.horizontalSlider.valueChanged.connect(self.on_horizontalSlider_valueChanged)
        self.horizontalSlider.sliderReleased.connect(self.on_horizontalSlider_valueChanged)
        self.layout.addWidget(self.horizontalSlider, 1, 1, 1, 3)
        # print(self.push_button_update.isVisible(),self.push_button_update.isEnabled())
        ParameterAdjustWidget.counter += 1

    def on_push_button_update_clicked(self):
        print("on_push_button_update_clickedA")
        self.from_value = float(self.line_edit_from_value.text())
        self.to_value = float(self.line_edit_to_value.text())
        # TODO: 更新slider


    def on_horizontalSlider_valueChanged(self,scale):
        print("on_horizontalSlider_valueChangedA")
        self.scale = scale
        if self.is_log:
            self.value = np.power(10, np.log10(self.from_value) + (
                    np.log10(self.to_value) - np.log10(self.from_value)) * self.scale / 100.0)
        else:
            self.value = self.from_value + (self.to_value - self.from_value) * self.scale / 100.0
        label_value_str = f"{self.value:.{5}e}" if self.is_log else f"{self.value:.{5}g}"
        self.value_label.setText(label_value_str)







