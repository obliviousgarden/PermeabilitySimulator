from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout


class TestWidget(QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()
        self.layout = QHBoxLayout()
        self.label = QLabel("Hello")
        self.layout.addWidget(self.label)