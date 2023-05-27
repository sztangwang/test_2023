
from PyQt5.QtCore import *
from config.menuDataConfig import *
from utils.adbsocket import *
from PyQt5.QtGui import QIcon
from qtpy import QtWidgets
from compoment.agentSocketChannel import ChannelSingle
from compoment.agentSocketServer import SocketServer
from moduel.agentConnection import Connection
from moduel.agentItem import *
from moduel.device import Device
from moduel.nettyMessage import NettyMessage
from ui.base.baseLayout import BaseLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from ui.test.featureMenuWindow import FeatureMenuWindow
from ui.test.suitConfigMenuLayout import SuitMenuLayout
from ui.test.record.record_main import record_main
from ui.test.uvc_test.uvc_client_ui_main import uvc_client_ui_main
from ui.test.Repeat_Frame.repeat_frame_ui_main import repeat_frame_ui_main
from ui.test.Exception_Frame.exceptio_frame_ui_main import exceptio_frame_ui_main
from ui.widget.notification import NotificationWindow
from utils.fileutils import getResPath, read_yaml_data, write_yaml_data, device_file_path

logger = Logger(level="info").logger

file_lock = threading.Lock()


def delete_yaml_data_by_serial(file_path, device):
    """
    根据device.serial 删除对应的设备号信息
    @param file_path:
    @param device:
    @return:
    """
    data = read_yaml_data(file_path)
    if device.serialsName in data["devices"]:
        del data["devices"][device.serialsName]
        write_yaml_data(file_path, data)


def write_device_list(file_path, device):
    file_lock.acquire()
    try:
        add_device_list_yaml(file_path, device)
    finally:
        file_lock.release()


def add_device_list_yaml(file_path, device):
    """
    添加设备信息到 device_list.yaml 中
    @param file_path:
    @param device:
    @return:
    """
    devices = read_yaml_data(file_path)
    if not devices:
        devices = {"devices": {}}
    if device.serialsName in devices:
        devices["devices"][device.serialsName]['status'] = Device.ONLINE
        devices["devices"][device.serialsName]['device_id'] = device.serialsName
        devices["devices"][device.serialsName]['device_type'] = device.projectName
        devices["devices"][device.serialsName]["info"] = device.info
    else:
        devices["devices"][device.serialsName] = {"device_id": device.serialsName,
                                                  "device_type": device.projectName,
                                                  "status": Device.ONLINE,
                                                  "info": device.info}
    write_yaml_data(file_path, devices)


class BaseWindow(BaseLayout):
    def __init__(self, *args, **kwargs):
        super(BaseWindow, self).__init__(*args, **kwargs)
        # 当前ui rowindex ：device
        self.rowDict = None
        # 线程组
        self.runners = None
        # 通知
        self.notification = None
        # 线程池
        self.pool = None
        # 服务线程
        self.socketServerThread = None
        # 监听线程
        self.androidDeviceWatcherThread = None
        # 默认显示栏
        self.currentKey = "ADB device"
        self.initUi()
        self.initMenuActions()
        # 表格栏数据类型标题 serials
        self.adbAgentItems = [
            AgentItem('全选', AGENT_TYPE_CHECKBOX, 0),
            AgentItem('序列号', AGENT_TYPE_DATA, 1),
            AgentItem('机型', AGENT_TYPE_DATA, 2),
            AgentItem('状态', AGENT_TYPE_DATA, 3),
            AgentItem('操作', AGENT_TYPE_DATA, 4),
        ]
        # 表格栏数据类型标题 serials
        self.serialsAgentItems = [
            AgentItem('全选', AGENT_TYPE_CHECKBOX, 0),
            AgentItem('序列号', AGENT_TYPE_DATA, 1),
            AgentItem('机型', AGENT_TYPE_DATA, 2),
            AgentItem('状态', AGENT_TYPE_DATA, 3),
            AgentItem('操作', AGENT_TYPE_DATA, 4),
        ]
        # 表格栏数据类型标题 server
        self.serverAgentItems = [
            AgentItem('全选', AGENT_TYPE_CHECKBOX, 0),
            AgentItem('名称', AGENT_TYPE_DATA, 1),
            AgentItem('机型', AGENT_TYPE_DATA, 2),
            AgentItem('状态', AGENT_TYPE_DATA, 3),
            AgentItem('操作', AGENT_TYPE_DATA, 4),
        ]
        # 左边栏列表类型
        self.agentTypeItems = {
            'ADB device': self.adbAgentItems,
            'Serials': self.serialsAgentItems,
            'Server': self.serverAgentItems
        }
        # Android类设备初始化列表
        self.adbConnectionDeviceList = [
        ]
        self.serialsConnectionDeviceList = [
            # Device("a", "haha", 1, runnable=None),
            # Device("b", "haha2", 2, runnable=None),
            # Device("c", "haha", 1, runnable=None),
            # Device("d", "haha2", 2, runnable=None)
        ]
        self.remoteServerConnectionList = [
            # Device("a", "123123", 1, runnable=None)
        ]

        self.agentTableWidgetDataItems = {
            'ADB device': self.adbConnectionDeviceList,
            'Serials': self.serialsConnectionDeviceList,
            'Server': self.remoteServerConnectionList
        }

        self.buildHorizontalHeader(self.adbAgentItems)
        self.initThreadData()
        self.initData()

        self.tuple_main_thread = (self.pool, self.adbConnectionDeviceList, self.runners)
        self.SUitMenuLayout = SuitMenuLayout(self.tuple_main_thread)  # 定义子窗口
        self.record_main = record_main(self.tuple_main_thread)  # 定义子窗口
        self.uvc_client = uvc_client_ui_main(self.tuple_main_thread)



    def initData(self):
        """
        初始化数据
        """
        # 当前的页面的列表key
        for item in self.agentTypeItems.keys():
            widget = QtWidgets.QListWidgetItem()
            widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            widget.setText(item)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.onAllCheckBoxClicked)

    def initThreadData(self):
        """
       初始化线程数据
        """
        self.pool = QThreadPool()
        self.runners = []
        self.rowDict = {}
        self.pool.setMaxThreadCount(100)
        self.notification = NotificationWindow()
        self.androidDeviceWatcherThread = DeviceNotificationThread()
        self.androidDeviceWatcherThread.pyqtSignal.device.connect(self.resultProcessor)
        # 服务端线程
        self.socketServerThread = SocketServer()
        self.socketServerThread.serverSignal.dataTupleSignal.connect(self.dataReceiver)
        self.androidDeviceWatcherThread.start()
        self.socketServerThread.start()

    def initMenuActions(self):
        self.mainMenu.triggered.connect(self.menuActionController)

    def menuActionController(self, action: QAction):
        controllerData = action.data()
        if controllerData == FeatureData:
            self.window = FeatureMenuWindow(self.tuple_main_thread)
            self.window.show()

        if controllerData == recordData:
            self.window = record_main(self.tuple_main_thread)
            self.window.show()

        if controllerData == uvc_clientData:
            self.window = uvc_client_ui_main(self.tuple_main_thread)
            self.window.show()

        if controllerData == Repeat_FrameData:
            self.window = repeat_frame_ui_main(self.tuple_main_thread)
            self.window.show()

        if controllerData == Exception_FrameData:
            self.window = exceptio_frame_ui_main(self.tuple_main_thread)
            self.window.show()


        elif controllerData == SuitConfigData:
            self.window = SuitMenuLayout(self.tuple_main_thread)
            self.window.show()
        # logger.info(f"action.data(): {action.data()} {type(action)}")

    def dataReceiver(self, response: tuple):
        """
        Server 数据接收
        """
        # logger.info(f" dataReceiver :{response}")
        nettyMsg, channel = response
        SYNC_MSG = 0
        HEARTBEAT_MSG = 1
        DATA_MSG = 2

        typeDict = {
            SYNC_MSG: lambda: self.syncStateController(nettyMsg, channel),
            HEARTBEAT_MSG: lambda: self.onlineStateController(nettyMsg, channel),
            DATA_MSG: lambda: self.reportStateController(nettyMsg, channel)
        }

        typeDict[nettyMsg.type]()
        self.refreshUi(self.currentKey)

    def onlineStateController(self, nettyMsg: NettyMessage, channel: Connection):
        """
        在线状态控制
        """
        deviceName = channel.deviceId
        #
        for ads in self.adbConnectionDeviceList:
            if ads.serialsName == deviceName:
                ads.connectionState = Device.ONLINE

    # 信息同步状态控制
    def syncStateController(self, nettyMsg: NettyMessage, channel: Connection):
        """
        信息同步状态控制
        """
        deviceName = channel.deviceId
        for index, ads in enumerate(self.adbConnectionDeviceList):
            if ads.serialsName == deviceName:
                #logger.info(F"sync .. Device : {deviceName}")
                self.adbConnectionDeviceList[index].connectionState = Device.ONLINE
                self.adbConnectionDeviceList[index].projectName = nettyMsg.nettyData.deviceData.projectName
                self.adbConnectionDeviceList[index].info = nettyMsg.nettyData.deviceData.to_json()
                # TODO  将设备信息写到yaml文件中.
                write_device_list(device_file_path, self.adbConnectionDeviceList[index])

    def reportStateController(self, nettyMsg: NettyMessage, channel: Connection):
        """
        结果回收状态控制
        """
        pass

    def getRowIdxByDeviceId(self, deviceName: str):
        """
        通过设备获取 UI 行级
        """
        for rowIdx, name in self.rowDict.items():
            if name == deviceName:
                return name

        return None

    #
    def generateRows(self, device: Device, rowIdx: int):
        """
        生成每一行数据
        """
        row = []
        checkBoxCell = self.buildCheckBoxCell(rowIdx=rowIdx, device=device)
        row.append(checkBoxCell)

        self.buildDataCell(row, device, rowIdx)
        operateCell = self.buildOperateCell(rowIdx=rowIdx)
        row.append(operateCell)
        return row

    # 刷新ui
    def refreshUi(self, agentType: str):
        """
        刷新UI
        """
        self.tableWidget.clear()
        self.buildHorizontalHeader(self.agentTypeItems.get(agentType))
        data = self.agentTableWidgetDataItems.get(agentType)
        self.tableWidget.setRowCount(len(data))
        for rowIdx, newDevice in enumerate(data):
            itemList = self.generateRows(newDevice, rowIdx)
            for columnIdx, itemWidget in enumerate(itemList):
                if isinstance(itemWidget, QTableWidgetItem):
                    self.tableWidget.setItem(rowIdx, columnIdx, itemWidget)
                else:
                    self.tableWidget.setCellWidget(rowIdx, columnIdx,
                                                   itemWidget)

    # 生成表头
    def buildHorizontalHeader(self, agentItems: list[AgentItem]):
        """
        表头生成
        """
        self.tableWidget.setColumnCount(len(agentItems))
        self.tableWidget.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for index, header in enumerate(agentItems):
            if header.type == AGENT_TYPE_CHECKBOX:
                item = QTableWidgetItem(header.name)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
                              | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
                self.tableWidget.setHorizontalHeaderItem(index, item)
            elif header.type == AGENT_TYPE_DATA:
                item = QTableWidgetItem(header.name)
                self.tableWidget.setHorizontalHeaderItem(index, item)

    #
    def buildDataCell(self, row: list, device: Device, rowIdx: int):
        """
        构建中间数据
        """
        self.stateDict = {Device.ONLINE:
                              QIcon(getResPath("images", "online.svg")),
                          Device.OFFLINE:
                              QIcon(getResPath("images", "offline.svg"))
                          }

        nameItem = QTableWidgetItem(device.serialsName)
        nameItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        nameItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        row.append(nameItem)

        infoItem = QTableWidgetItem(device.projectName)
        infoItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        infoItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        row.append(infoItem)

        stateLayout = QHBoxLayout()
        stateButton = QPushButton()
        stateButton.setIcon(self.stateDict[device.connectionState])
        stateButton.setStyleSheet("border:none;")
        cellFrame = QFrame()
        stateLayout.addWidget(stateButton)
        cellFrame.setLayout(stateLayout)

        row.append(cellFrame)
        # 存储关系
        self.rowDict.update({rowIdx: device})

    # 构建选择列
    def buildCheckBoxCell(self, rowIdx, device):
        """
        构建选择列
        """
        cellLayout = QHBoxLayout()
        checkBox = QCheckBox()
        cellFrame = QFrame()
        cellLayout.addWidget(checkBox)
        cellFrame.setLayout(cellLayout)
        checkBox.setCheckState(device.checkState)
        checkBox.clicked.connect(lambda: self.onCheckBoxSelected(checkBox, rowIdx))
        return cellFrame

    # 构建当前行最后一列
    def buildOperateCell(self, rowIdx: int):
        """
        构建当前行最后一列
        """
        cellLayout = QHBoxLayout()
        debugButton = QPushButton(text="调试")
        forceButton = QPushButton(text="上线")
        infoButton = QPushButton(text="信息")
        cellFrame = QFrame()
        cellLayout.addWidget(debugButton)
        cellLayout.addWidget(forceButton)
        cellLayout.addWidget(infoButton)
        cellFrame.setLayout(cellLayout)
        forceButton.clicked.connect(lambda: self.onForceClicked(rowIdx))
        debugButton.clicked.connect(lambda: self.onTestClicked(rowIdx))
        infoButton.clicked.connect(lambda: self.onDeviceInfoClicked(rowIdx))
        return cellFrame

    # 行选项选择
    def onCheckBoxSelected(self, checkbox, rowIdx: int):
        """
        单个Checkbox选择
        """
        row = str(rowIdx)

        if checkbox.isChecked():
            self.rowDict[rowIdx].checkState = Qt.CheckState.Checked
            logger.info(f"isChecked : {row}")
            return
        self.rowDict[rowIdx].checkState = Qt.CheckState.Unchecked
        logger.info(f"unChecked : {row}")
        return

    def onTestClicked(self, rowIdx: int):
        """
        测试按钮选择
        """
        deviceName = self.rowDict[rowIdx].serialsName
        logger.info(f"debug : {rowIdx} :{deviceName}")
        if len(self.socketServerThread.connections) == 0:
            logger.info("Connection not Init")
            return
        for conn in self.socketServerThread.connections:
            if conn.deviceId == deviceName:
                logger.info("Found Connection ！！！ ...")
                timestamp = int(round(time.time() * 1000))
                nettyMessage = NettyMessage(type=1, timestamp=timestamp, nettyData=None)
                single = ChannelSingle(conn, nettyMessage.to_json())
                single.signal.dataSignal.connect(self.singleResponse)
                self.pool.start(single)
                return
        logger.info("Not Found Connection !!! ....")

    def singleResponse(self, resp: str):
        logger.info(f" response {resp}")

    def onAgentItemClicked(self, item: QListWidgetItem):
        self.refreshUi(item.text())
        self.currentKey = item.text()

    def onAllCheckBoxClicked(self, column):
        # 点击后，全选当前页面的数据
        isCheckedList = []
        unCheckedList = []
        if column != 0:
            return
        for row, device in enumerate(
                self.agentTableWidgetDataItems.get(self.currentKey)):
            frame = self.tableWidget.cellWidget(row, column)
            if isinstance(frame, QFrame):
                checkbox = (frame.children()[1])
                # 设置选择
                state = Qt.CheckState.Checked
                if checkbox.isChecked() == True:
                    # state = Qt.CheckState.Unchecked
                    isCheckedList.append(checkbox)
                else:
                    unCheckedList.append(checkbox)
        checkedSize = len(isCheckedList)
        unCheckedSize = len(unCheckedList)
        allCheckState = Qt.CheckState.Checked

        if (checkedSize != 0 and unCheckedSize != 0
            and checkedSize > unCheckedSize) or (checkedSize == 0) or (
                checkedSize == unCheckedSize):
            for unCheckbox in unCheckedList:
                unCheckbox.setCheckState(Qt.CheckState.Checked)
                allCheckState = Qt.CheckState.Checked
        elif (checkedSize != 0 and unCheckedSize != 0
              and checkedSize < unCheckedSize) or unCheckedSize == 0:
            for isCheckbox in isCheckedList:
                isCheckbox.setCheckState(Qt.CheckState.Unchecked)
                allCheckState = Qt.CheckState.Unchecked
        for row, device in self.rowDict.items():
            device.checkState = allCheckState

    def resultProcessor(self, data: ADBConnectionData):

        #logger.info("in resultProcessor ... ")
        connectProcessDict = {
            ADBConnectionData.TYPE_IN: lambda: self.connectProcessor(data),
            ADBConnectionData.TYPE_OUT: lambda: self.disconnectProcessor(data)
        }
        connectProcessDict[data.connectionType]()

    def handle_device_changed(self):
        # 将设备列表的数据返回到子窗口的设备列表中
        if self.adbConnectionDeviceList:
            return self.adbConnectionDeviceList

    # 设备连接处理器
    def connectProcessor(self, data: ADBConnectionData):
        for currentDevice in self.adbConnectionDeviceList:
            if data.connected == currentDevice.serialsName:
                logger.error("exist Same SerialsNo :{}".format(data.connected))
                return
        self.adbConnectionDeviceList.append(
            Device(data.connected, "", Device.OFFLINE, "", Qt.CheckState.Unchecked, None))
        self.notification.success("通知", data.connected)
        if len(data.currentDevices) == 0:
            self.refreshUi(self.currentKey)
            return
        for newDevice in data.currentDevices:
            logger.info("connectionProcessor : {}".format(newDevice))
        self.refreshUi(self.currentKey)

    # 设备断开处理器
    def disconnectProcessor(self, data: ADBConnectionData):
        self.notification.error("提示", data.disConnect)
        for index, connected in enumerate(self.adbConnectionDeviceList):
            if connected.serialsName == data.disConnect:
                removeDevice = self.adbConnectionDeviceList.pop(index)
                logger.info(f"removeDevice : {removeDevice}")
                # TODO  移除相应的设备并且也从yaml中移除
             #   delete_yaml_data_by_serial(device_file_path, removeDevice)
        for runnable in self.runners:
            if runnable.device.serial == ADBConnectionData.disConnect:
                self.pool.globalInstance().cancel(runnable=runnable)
        self.refreshUi(self.currentKey)

    # 单个adb线程实例化

    def closeEvent(self, event):
        for runnable in self.runners:
            if not runnable.isStop():
                runnable.stop()
                self.pool.cancel(runnable)
        self.pool.clear()
        self.pool.deleteLater()
        self.socketServerThread.stop()
        self.androidDeviceWatcherThread.stop()
        return super().closeEvent(event)

    def onForceClicked(self, rowIdx):
        logger.info(f"force Online : {rowIdx}")
        device = self.rowDict[rowIdx]
        utils = DUtils(adbutils.device(device.serialsName))
        if not utils.isServiceInstalled():
            self.notification.error("错误", "未安装[硬件测试App]!")
            return
        if not utils.isSocketServiceStart():
            utils.startADBSocketService()
        adbutils.adb.reverse(device.serialsName, "tcp:9100", "tcp:9100", True)
        utils.sendBroadcast("com.hollyland.action.ADB_CONNECTED")
        pass

    def onDeviceInfoClicked(self, rowIdx):
        pass
