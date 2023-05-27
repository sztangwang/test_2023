from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QFrame, QLabel


class TopAllCaseFrame(QFrame):
    def __init__(self, parent=None):
        super(TopAllCaseFrame, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setObjectName("测试用例管理")
        self.topAllCaseLayout = QHBoxLayout()
        self.setFrameStyle(QFrame.Box)
        self.setLayout(self.topAllCaseLayout)
        self.topAllCaseLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.label_all_cases = QLabel()
        self.label_all_cases.setStyleSheet("font: 15pt \"微软雅黑\";")
        self.label_all_cases.setText("全部用例")

        self.label_all_cases_num = QLabel()
        self.label_all_cases_num.setStyleSheet("font: 15pt \"微软雅黑\";\n""color:#aaaa7f;")
        self.label_all_cases_num.setText("10")

        self.topAllCaseLayout.addWidget(self.label_all_cases)
        self.topAllCaseLayout.addWidget(self.label_all_cases_num)