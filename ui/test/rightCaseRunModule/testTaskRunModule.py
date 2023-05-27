from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox

from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.task.task_manage import TaskType
from ui.test.execTaskThread import TaskManagerThread
from ui.test.model.model import Task, TaskStatus

logger = Logger().get_logger
class TestTaskRunModule(QFrame):
    def __init__(self, case_manager_controller=None,device_manager_controller=None,task_type_controller=None,task_manager_table_controller=None,parent=None):
        super(TestTaskRunModule, self).__init__(parent)
        self.initUI()
        self.case_manager_controller = case_manager_controller
        self.device_manager_controller =device_manager_controller
        self.task_type_controller = task_type_controller
        self.task_manager_table_controller = task_manager_table_controller

    def initUI(self):
        ################ 执行任务操作 ###############
        self.testTaskRunLayout = QHBoxLayout()
        self.testTaskRunLayout.setAlignment(Qt.AlignBottom)
        self.setLayout(self.testTaskRunLayout)

        self.run_case_label = QLabel("操作")
        self.testTaskRunLayout.addWidget(self.run_case_label)

        self.task_button = QPushButton('添加任务')
        self.testTaskRunLayout.addWidget(self.task_button)
        self.task_button.clicked.connect(self.on_add_task)

        self.run_task_button = QPushButton('执行任务')
        self.testTaskRunLayout.addWidget(self.run_task_button)
        self.run_task_button.clicked.connect(self.on_run_task)

        self.cancel_task_button = QPushButton('取消任务')
        self.testTaskRunLayout.addWidget(self.cancel_task_button)
        self.cancel_task_button.clicked.connect(self.on_cancel_task)

    def on_add_task(self):
        cases=[]
        selected_cases = self.case_manager_controller.get_selected_cases()
        selected_devices = self.device_manager_controller.get_selected_devices()
        selected_task_type =self.task_type_controller.get_task_type()
        if not selected_cases:
            QMessageBox.warning(self, '警告', '请选择测试用例')
            return
        if not selected_devices:
            QMessageBox.warning(self, '警告', '请选择一个设备')
            return
        if selected_task_type==TaskType.NONE:
            QMessageBox.warning(self, '警告', '请选择一种任务类型')
            return
        if self.task_manager_table_controller.is_device_occupied(selected_devices):
            QMessageBox.warning(self, '警告', f'设备[{selected_devices[0].serialsName}]已经被占用了')
            return
        # todo 根据任务类型的不同，需要选择对应的用例, 如果不同则弹出提示框
        try:
            if selected_task_type == TaskType.KW_UI_TEST:
                cases = self.case_manager_controller.get_test_case_list_view()
            elif selected_task_type == TaskType.PO_UI_TEST:
                cases = self.case_manager_controller.get_po_py_case_list()
                cases = sum(cases, [])
            if cases:
                # 根据设备的数量，创建多个任务
                for device in selected_devices:
                    task = Task(task_id=len(self.task_manager_table_controller.task_list), task_name='task1', test_cases=cases, device=device,
                                task_type=selected_task_type, status=TaskStatus.PENDING, result='',task_timeout=300)
                    self.task_manager_table_controller.add_task(task)
            else:
                QMessageBox.warning(self, '警告', '没有可执行的用例')
                return
        except Exception as e:
            logger.error("添加任务失败{}".format(e))
            QMessageBox.warning(self, '警告', '添加任务失败')

    def on_run_task(self):
        tasks =self.task_manager_table_controller.get_task_list()
        if tasks is None:
            QMessageBox.warning(self, '警告', '没有可以执行的任务')
            return
        if tasks:
            for task in tasks:   # 根据任务数量，创建多个线程
                # TODO 这里要判断一下有没有选中的任务
                if not self.task_manager_table_controller.no_selected_task_messagebox():
                    return
                # 如果任务已经在执行了，或者任务取消中，就不再执行
                # TODO 这里要改成通知 另一个专门做自动化用例执行的线程，去执行任务，而不是在这里直接执行，取消任务也是一样
                if task.status == TaskStatus.RUNNING or task.status == TaskStatus.CANCELLING:
                    QMessageBox.warning(self, '警告', '任务已经在执行了')
                    continue
                # 设置任务状态为执行中
                task.status = TaskStatus.RUNNING
                task_thread = TaskManagerThread(task)
                self.task_manager_table_controller.set_thread(task_thread)
                print("task_thread_id------------>:", id(task_thread))
                # task_thread.task_cancelled_signal.connect(self.task_manager.cancel_task)
                task_thread.update_status_signal.connect(self.task_manager_table_controller.update_task_status)
                task_thread.update_result_signal.connect(self.task_manager_table_controller.update_task_result)
                task_thread.start()

    def on_cancel_task(self):
        """
        取消任务
        @return:
        """
        # 获取选中的任务
        tasks = self.task_manager_table_controller.get_selected_task()
        print('取消任务: {}'.format(tasks))
        for task in tasks:
            print("任务类型：", type(task))
            self.task_manager_table_controller.cancel_task(task)


