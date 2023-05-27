from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QFrame

class TopSearchCaseFrame(QFrame):
    def __init__(self, parent=None):
        super(TopSearchCaseFrame, self).__init__(parent)
        self.init_ui()

    def add_case_comboBox_label(self):
        case_level_list = []
        for level in range(3):
            case_level_list.append(f"P{level}")
        self.case_level_comboBox.addItems(case_level_list)


    def init_ui(self):
        self.topSearchLayout = QHBoxLayout()  # 顶部第二行水平布局
        self.topSearchLayout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.topSearchLayout)

        ########## 用例等级 ############
        self.case_level_level = QLabel()  # 用例等级
        self.case_level_level.setText("用例等级：")
        self.case_level_comboBox = QComboBox()  # 用例等级的下拉框
        self.case_level_comboBox.setObjectName("comboBox")
        self.case_level_comboBox.setFixedSize(100, 30)

        ########## 设备 ###########
        self.device_label = QLabel()
        self.device_label.setText("设备：")
        self.device_comboBox = QComboBox()
        self.device_comboBox.setObjectName("comboBox")
        self.device_comboBox.setFixedSize(150, 30)
        # self.device_comboBox.addItems(self.getDeviceList())

        ######### 用例模式 ###########
        self.case_mode = QLabel()
        self.case_mode.setText("用例模式：")
        self.case_mode_comboBox = QComboBox()
        self.case_mode_comboBox.setObjectName("comboBox")
        self.case_mode_comboBox.setFixedSize(100, 30)
        self.case_mode_comboBox.addItem("关键字模式")
        self.case_mode_comboBox.addItem("PO模式")

        ############## 搜索 ##############
        self.serach_line_edit = QLineEdit()
        self.serach_line_edit.setText("输入用例名称搜索")
        self.serach_push_button = QPushButton()
        self.serach_push_button.setText("搜索")


        self.topSearchLayout.addWidget(self.case_level_level)
        self.topSearchLayout.addWidget(self.case_level_comboBox)
        self.topSearchLayout.addWidget(self.device_label)
        self.topSearchLayout.addWidget(self.device_comboBox)
        self.topSearchLayout.addWidget(self.case_mode)
        self.topSearchLayout.addWidget(self.case_mode_comboBox)
        self.topSearchLayout.addWidget(self.serach_line_edit)
        self.topSearchLayout.addWidget(self.serach_push_button)