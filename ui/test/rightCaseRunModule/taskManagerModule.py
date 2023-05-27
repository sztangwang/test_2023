from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox
from ui.test.model.model import TaskStatus, TaskType
from utils.fileutils import list_class_to_json


class TaskManagerView(QTableWidget):
    def __init__(self,taskManagerView=None, parent=None):
        super(TaskManagerView, self).__init__(parent)
        self.taskManagerView = taskManagerView
        # 处理清空任务列表的信号
        self.taskManagerView.importCaseFrame.signal.clear_task_list_signal.connect(self.on_clear_task_list)
        self.all_header_checkbox = []
        self.task_list = []
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(['选择','任务ID', '任务名称', '执行用例', '执行设备', '执行状态', '执行结果'])
        self.horizontalHeader().setStretchLastSection(True)


    def add_task(self, task):
        task_id = len(self.task_list)
        if task not in self.task_list:
            self.task_list.append(task)
        row_position = self.rowCount()
        self.insertRow(row_position)
        checkbox = QCheckBox()
        self.setCellWidget(row_position, 0, checkbox)
        # 当选中了一个，整行都选中
        checkbox.stateChanged.connect(lambda: self.select_all_row(checkbox, row_position))
        self.setItem(row_position, 1, QTableWidgetItem(str(task_id)))
        self.setItem(row_position, 2, QTableWidgetItem(task.task_name))
        if task.task_type == TaskType.KW_UI_TEST:
            case_json = list_class_to_json(task.test_cases)
            self.setItem(row_position, 3, QTableWidgetItem(",".join(case_json)))
        elif task.task_type == TaskType.PO_UI_TEST:
            self.setItem(row_position, 3, QTableWidgetItem(",".join(task.test_cases)))
        self.setItem(row_position, 4, QTableWidgetItem(task.device.serialsName))
        self.setItem(row_position, 5, QTableWidgetItem(task.status))
        self.setItem(row_position, 6, QTableWidgetItem(task.result))
       # print("self.task_list", self.task_list)

    def on_clear_task_list(self):
        self.task_list = []
        self.all_header_checkbox = []
        self.clearContents()

    def select_all_row(self, checkbox, row_position):
        """
        选中一行
        @param checkbox:
        @param row_position:
        @return:
        """
        if checkbox.isChecked():
            self.task_list[row_position-1].checkState = Qt.CheckState.Checked
            self.selectRow(row_position)
           # print("选中了", self.task_list[row_position-1].checkState)
            # 将选中的checkbox 的任务添加到列表中
            if self.task_list[row_position-1] not in self.all_header_checkbox:
                self.all_header_checkbox.append(self.task_list[row_position])

        else:
           # print("取消选中了", self.task_list[row_position-1].checkState)
            # 将取消选中的checkbox 的任务从列表中移除
            if self.task_list[row_position-1] in self.all_header_checkbox:
                self.all_header_checkbox.remove(self.task_list[row_position])
            self.clearSelection()

       # print("all_header_checkbox",self.all_header_checkbox)

    def update_task_status(self, task_id, status):
        row_position = task_id
        self.setItem(row_position, 5, QTableWidgetItem(status))

    def update_task_result(self, task_id, result):
        row_position = task_id
        self.setItem(row_position, 6, QTableWidgetItem(result))


    def get_selected_task(self):
        if len(self.all_header_checkbox) == 0:
            QMessageBox.information(self, '提示', '请选择一个任务', QMessageBox.Yes)
            return
        return self.all_header_checkbox

    def no_selected_task_messagebox(self):
        if len(self.all_header_checkbox) == 0:
            QMessageBox.information(self, '提示', '请选择一个任务', QMessageBox.Yes)
            return False
        return True


    #取消已经完成的任务弹框
    def cancel_task_messagebox(self,task):
        if task.status == TaskStatus.CANCELLING:
            # 提示 任务正在取消中，不能取消
            QMessageBox.information(self, '提示', '任务正在取消中，不能取消', QMessageBox.Yes)
        elif task.status == TaskStatus.FINISHED:
            # 提示 任务已经执行完成，不能取消
            QMessageBox.information(self, '提示', '任务已经执行完成，不能取消', QMessageBox.Yes)
        else:
            # 提示 任务已经执行完成，不能取消
            QMessageBox.information(self, '提示', '没有可以取消的任务', QMessageBox.Yes)

    def get_task_list(self):
        return self.task_list


class TaskManagerController:
    def __init__(self, view):
        self.view = view
        self.threads = []  # 存储所有任务线程
        self.task_list = []

    def add_task(self, task):
        self.view.add_task(task)

    def get_task_list(self):
        self.task_list = self.view.get_task_list()
        return self.task_list

    def update_task_status(self, task_id, status):
        self.view.update_task_status(task_id, status)

    def update_task_result(self, task_id, result):
        self.view.update_task_result(task_id, result)

    def cancel_task(self,task):
        if task.status == TaskStatus.RUNNING:
           # task.status = TaskStatus.CANCELLED
            # 发送任务取消的信号，任务正在取消中
            self.update_task_status(task.task_id, TaskStatus.CANCELLING)
            # task.status = 'Cancelling'
            thread = self.get_thread(task)
            print("cancel_task_thread_id---------------->", id(thread))
            if thread is not None:
                thread.task_cancelled()
                thread.update_status_signal.connect(self.update_task_status)
                thread.update_result_signal.connect(self.update_task_result)
                thread.quit()  # 结束线程循环
        self.view.cancel_task_messagebox(task) # 取消任务的弹框

    def get_all_header_checkbox(self):
        return self.view.all_header_checkbox

    def no_selected_task_messagebox(self):
        return self.view.no_selected_task_messagebox()

    def set_thread(self, thread):
        # 每次只保存最新的线程
        self.threads.clear()
        self.threads.append(thread)

    def get_thread(self,task):
        for t in self.threads:
            if t.task == task:
                return t
        return None

    def is_device_occupied(self, devices):
        """
        判断设备是否被占用
        @param devices:
        @return:
        """
        for device in devices:
            if self._is_device_occupied_by_task(device):
                return True
        return False

    def _is_device_occupied_by_task(self, device):
        """
        判断设备是否被占用
        @param device:
        @return:
        """
        for task in self.task_list:
            # TODO 如果设备的状态是正在执行，那么就不允许再次执行，需要等待执行完成
            if task.device == device:
                return True
        return False


    def get_selected_task(self):
        return self.view.get_selected_task()


