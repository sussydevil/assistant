#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from PyQt5 import QtWidgets, QtCore, QtGui
from multiprocessing import Queue
from datetime import datetime
from sqlite import Sqlite
import pyqtgraph as pg
from mqtt import Mqtt
import configparser
import queue
import sys
import ui

# список значений датчиков
sensor_list = ["Температура", "Влажность", "Давление", "CO2"]
# файл конфигурации границ значений датчиков
mqtt_sensor_scope_path = "sensor.conf"
# интервал между получениями данных от ESP32
mqtt_interval = 60
# таймер между обновлениями в мс
chart_timer = 1000
# количество точек в графике
point_count = 1000
# таймаут, в течение которого queue ждёт информацию от mqtt модуля
queue_timeout = 0.5
queue_: Queue


class SensorScope:
    """класс, содержащий границы допустимых значений датчиков"""
    temperature = []
    humidity = []
    pressure = []
    CO2 = []

    @staticmethod
    def mqtt_sensor_scope_read():
        """считывание границ допустимых значений"""
        config = configparser.ConfigParser()
        config.read(mqtt_sensor_scope_path)
        SensorScope.temperature = [float(config.get("Settings", "temp_low")),
                                   float(config.get("Settings", "temp_high"))]
        SensorScope.humidity = [float(config.get("Settings", "humi_low")),
                                float(config.get("Settings", "humi_high"))]
        SensorScope.pressure = [float(config.get("Settings", "pres_low")),
                                float(config.get("Settings", "pres_high"))]
        SensorScope.CO2 = [float(config.get("Settings", "CO2_low")),
                           float(config.get("Settings", "CO2_high"))]
        return 0


class ChartWidget(QtWidgets.QWidget):
    """класс виджета - график"""
    def __init__(self, parent=None):
        """инициализация"""
        super().__init__(parent)
        # объекты и переменные для графика
        layout = QtWidgets.QHBoxLayout()
        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)
        self.setLayout(layout)
        self.plot.setBackground(None)


class Window(QtWidgets.QMainWindow, ui.Ui_MainWindow):
    """класс окна"""
    def __init__(self):
        """ инициализация"""
        super().__init__()
        self.setupUi(self)
        self.chart_widget = ChartWidget(self)
        self.ChartLayout.addWidget(self.chart_widget)
        # добавление модели в ListView
        self.action_model = QtGui.QStandardItemModel()
        self.ActionListView.setModel(self.action_model)
        self.ActionListView.setStyleSheet("QListView {background: transparent;}")
        # добавление элементов в ComboBox
        self.SensorSelectionComboBox.addItems(sensor_list)
        # считывание допустимых границ датчиков
        SensorScope.mqtt_sensor_scope_read()
        # добавление Label в StatusBar
        self.StatusLabel = QtWidgets.QLabel()
        self.StatusBar.addWidget(self.StatusLabel)
        # получение данных выбранного в ComboBox датчика
        self.timestamp, self.data = self.GetSensorData(self.SensorSelectionComboBox.currentIndex())
        self.curve = self.chart_widget.plot.getPlotItem().plot()
        # добавление таймера
        self.timer = QtCore.QTimer()
        # обновление Label'ов с данными
        self.UpdateSensorData()
        # добавление функций для обновления и построения графика
        self.updater()
        self.plotter()
        self.curve.setData(self.data)
        # добавление события - изменить состояние реле
        self.RelayCommitButton.clicked.connect(self.SendRelayState)
        # добавление события - значение в ComboBox поменялось
        self.SensorSelectionComboBox.currentIndexChanged.connect(lambda: self.updater(True))

    def plotter(self):
        """таймер графика"""
        self.timer.timeout.connect(self.updater)
        self.timer.start(chart_timer)

    def updater(self, combobox_changed=False):
        """обновление графика"""
        data = Sqlite.read_last()
        # обновление Label'ов с данными
        self.UpdateSensorData()
        # обновление StatusBar
        if datetime.now().timestamp() - data[0] > mqtt_interval:
            self.StatusLabel.setStyleSheet("QLabel {color:#CD5C5C;}")
            self.StatusLabel.setText(" Обновлено: " + str(datetime.fromtimestamp(data[0]).strftime("%H:%M:%S"))
                                     + ",  отключено")
        else:
            self.StatusLabel.setStyleSheet("QLabel {color:#90EE90;}")
            self.StatusLabel.setText(" Обновлено: " + str(datetime.fromtimestamp(data[0]).strftime("%H:%M:%S"))
                                     + ",  подключено")
        # сравнение timestamp последней строчки из БД с имеющимся последним элементом в массиве
        if data[0] == self.timestamp[-1]:
            if not combobox_changed:
                return
        # если появились новые данные, значит нужно обновить
        self.timestamp, self.data = self.GetSensorData(self.SensorSelectionComboBox.currentIndex())
        self.curve.setData(self.data)

    def GetSensorData(self, checkbox_id):
        """получение большого количества данных для построения графика"""
        data = Sqlite.read_last_n_rows(point_count)
        # получение информации от модуля MQTT
        try:
            q = queue_.get(True, queue_timeout)
            item = QtGui.QStandardItem(q[0])
            self.action_model.appendRow(item)
        except queue.Empty:
            pass
        # answer - данные по выбранному элементу из ComboBox, timestamp - время в формате unix
        answer = []
        timestamp = []
        for row in data:
            answer.append(row[checkbox_id + 1])
            timestamp.append(row[0])
        return timestamp, answer

    def SendRelayState(self):
        """изменение состояния реле"""
        # проверка checkbox
        r1_s = self.RelayOneCheckBox.isChecked()
        r2_s = self.RelayTwoCheckBox.isChecked()
        r3_s = self.RelayThreeCheckBox.isChecked()
        # включение реле
        ans1_s = Mqtt.change_relay_state(1, r1_s)
        ans2_s = Mqtt.change_relay_state(2, r2_s)
        ans3_s = Mqtt.change_relay_state(3, r3_s)
        time = str(datetime.now().strftime("%H:%M:%S - "))
        # проверка ответа от mqtt модуля
        if ans1_s == -1 or ans1_s == -2:
            item = QtGui.QStandardItem(time + " Реле 1: Ошибка изменения состояния.")
            self.action_model.appendRow(item)
        else:
            item = QtGui.QStandardItem(time + "Реле 1: Успешное изменение состояния.")
            self.action_model.appendRow(item)
        if ans2_s == -1 or ans2_s == -2:
            item = QtGui.QStandardItem(time + "Реле 2: Ошибка изменения состояния.")
            self.action_model.appendRow(item)
        else:
            item = QtGui.QStandardItem(time + "Реле 2: Успешное изменение состояния.")
            self.action_model.appendRow(item)
        if ans3_s == -1 or ans3_s == -2:
            item = QtGui.QStandardItem(time + "Реле 3: Ошибка изменения состояния.")
            self.action_model.appendRow(item)
        else:
            item = QtGui.QStandardItem(time + "Реле 3: Успешное изменение состояния.")
            self.action_model.appendRow(item)
        return 0

    def UpdateSensorData(self):
        """обновление значений датчиков"""
        data = Sqlite.read_last()
        # в зависимости от показаний, Label принимает зеленый или красный цвет
        # температура
        if data[1] > SensorScope.temperature[1] or data[1] < SensorScope.temperature[0]:
            self.TLabelValue.setStyleSheet("QLabel {color:#CD5C5C;}")
        elif data[1] > SensorScope.temperature[1] * 0.9 or data[1] < SensorScope.temperature[0] * 1.1:
            self.TLabelValue.setStyleSheet("QLabel {color:#FF8C00;}")
        else:
            self.TLabelValue.setStyleSheet("QLabel {color:#90EE90;}")
        # влажность
        if data[2] > SensorScope.humidity[1] or data[2] < SensorScope.humidity[0]:
            self.HLabelValue.setStyleSheet("QLabel {color:#CD5C5C;}")
        elif data[2] > SensorScope.humidity[1] * 0.9 or data[2] < SensorScope.humidity[0] * 1.1:
            self.HLabelValue.setStyleSheet("QLabel {color:#FF8C00;}")
        else:
            self.HLabelValue.setStyleSheet("QLabel {color:#90EE90;}")
        # давление
        if data[3] > SensorScope.pressure[1] or data[3] < SensorScope.pressure[0]:
            self.PLabelValue.setStyleSheet("QLabel {color:#CD5C5C;}")
        elif data[3] > SensorScope.pressure[1] * 0.98 or data[3] < SensorScope.pressure[0] * 1.02:
            self.PLabelValue.setStyleSheet("QLabel {color:#FF8C00;}")
        else:
            self.PLabelValue.setStyleSheet("QLabel {color:#90EE90;}")
        # углекислый газ
        if data[4] > SensorScope.CO2[1]:
            self.CLabelValue.setStyleSheet("QLabel {color:#CD5C5C;}")
        elif data[4] > SensorScope.CO2[1] * 0.9:
            self.CLabelValue.setStyleSheet("QLabel {color:#FF8C00;}")
        else:
            self.CLabelValue.setStyleSheet("QLabel {color:#90EE90;}")

        self.TLabelValue.setText(str(data[1]) + " °C")
        self.HLabelValue.setText(str(data[2]) + " %")
        self.PLabelValue.setText(str(data[3]) + " Pa")
        self.CLabelValue.setText(str(data[4]) + " PPM")
        return 0
    

def start_ui(q: Queue):
    """запуск интерфейса"""
    global queue_
    queue_ = q
    app = QtWidgets.QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    app_icon.addFile('logo.png', QtCore.QSize(64, 64))
    app.setWindowIcon(app_icon)
    window = Window()
    window.show()
    app.exec_()
