from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTreeWidgetItem


class CaseManagerSignal(QObject):
    importCaseSignal = pyqtSignal(str, str)     # 导入用例信号，类型，路径
    case_list_update_signal = pyqtSignal(str,QTreeWidgetItem,int) #用例类型，item,column
    # 清空用例列表数据
    clear_case_list_signal = pyqtSignal()
    # 清空任务列表数据
    clear_task_list_signal = pyqtSignal()