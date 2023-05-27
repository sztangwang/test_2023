from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QListWidget, QAbstractItemView, QListWidgetItem

from moduel.device import Device


class DeviceManagerView(QWidget):
    def __init__(self,adbConnectionDeviceList=None, parent=None):
        super(DeviceManagerView, self).__init__(parent)
        self.device_list_widget = None
        self.select_opts = []  # ==> 记录 用户勾选的 选项
        self.all_opts = []  # ==> 窗口中所有的可选选项
        self.select_device_list=[]
        self.device =None
        self.adbConnectionDeviceList= adbConnectionDeviceList
        self.init_ui()

    def init_ui(self):
        self.device_layout = QVBoxLayout()
        self.device_label = QLabel('设备列表')
        self.check_box = QCheckBox("全选")
        self.check_box.stateChanged.connect(self.check_all_device)
        self.device_list_widget = QListWidget()
        self.device_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.device_layout.addWidget(self.device_label)
        self.device_layout.addWidget(self.device_list_widget)
        self.device_layout.addWidget(self.check_box)
        self.setLayout(self.device_layout)
        self.add_device_to_list_widget()



    def add_device_to_list_widget(self):
        if self.adbConnectionDeviceList is None:
            return
        for device in self.adbConnectionDeviceList:
            self.device_list_widget.addItem(device.serialsName)


    def _add_devices(self, serial):
        self.device = Device(serial, "", Device.ONLINE, "", Qt.CheckState.Unchecked, None)
        if self.device not in self.select_device_list:
            self.select_device_list.append(self.device)
        return self.select_device_list

    def _remove_devices(self, serial):
        if self.device in self.select_device_list:
            if self.device.serialsName == serial:
                self.select_device_list.remove(self.device)

    def update_device_list(self, devices):
        self.device_list_widget.clear()
        for device in devices:
            item = QListWidgetItem()
            checkbox = QCheckBox(device.serialsName)
            self.device_list_widget.addItem(item)
            self.device_list_widget.setItemWidget(item, checkbox)

    def get_selected_devices(self):
        selected_devices = []
        for index in range(self.device_list_widget.count()):
            if self.device_list_widget.item(index).checkState() == Qt.Checked:
                item = self.device_list_widget.item(index)
                selected_devices= self._add_devices(item.text())
            else:
                continue
        return selected_devices

    # 全选或者取消全选
    def check_all_device(self):
        if self.check_box.isChecked():
            for i in range(self.device_list_widget.count()):
                self.device_list_widget.item(i).setCheckState(Qt.Checked)
                self._add_devices(self.device_list_widget.item(i).text())
        else:
            for i in range(self.device_list_widget.count()):
                self.device_list_widget.item(i).setCheckState(Qt.Unchecked)
                self._remove_devices(self.device_list_widget.item(i).text())


    def check_device(self):
        if self.device_list_widget.count() == self.device_list_widget.selectedItems():
            self.check_box.setChecked(True)
        else:
            self.check_box.setChecked(False)


class DeviceManagerController:
    def __init__(self, device_manager_view):
        self.device_manager_view = device_manager_view

    def update_device_list(self, devices):
        self.device_manager_view.update_device_list(devices)

    def get_selected_devices(self):
        return self.device_manager_view.get_selected_devices()