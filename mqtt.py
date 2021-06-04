#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from multiprocessing import Queue
from datetime import datetime
import wiotp.sdk.application
from phrases import Phrases
from sqlite import Sqlite
import configparser
import logging
import json
import yaml
import time

mqtt_sensor_scope_path = "sensor.conf"
mqtt_config_path = "mqtt_connection.conf"


class Queues:
    """class: hold queues from main"""
    notify_queue = Queue()
    voice_queue = Queue()


class Sensor:
    """class: hold sensor data"""
    class Scope:
        """class: hold scope of normal values of sensors"""
        temperature = []
        humidity = []
        pressure = []
        CO2 = []

    class LastWarning:
        """class: hold last timestamp warning about not normal values of sensors"""
        tem_high = 0
        tem_low = 0
        hum_high = 0
        hum_low = 0
        pre_high = 0
        pre_low = 0
        CO2_high = 0
        CO2_low = 0
        # interval of notifications - 30 minutes
        interval = 1800
        # interval of pressure notifications - 4 hours
        pressure_interval = 14400


class Mqtt:
    """class: work with MQTT protocol"""
    @staticmethod
    def start(notify_out: Queue, voice_in: Queue):
        """public function: open MQTT connection"""
        options = wiotp.sdk.application.parseConfigFile(mqtt_config_path)
        client = wiotp.sdk.application.ApplicationClient(options)
        client.logger.setLevel(logging.INFO)
        Queues.notify_queue, Queues.voice_queue = notify_out, voice_in
        client.connect()
        Mqtt.sensor_scope_read()
        client.deviceEventCallback = Mqtt.get_data
        client.subscribeToDeviceEvents()
        while True:
            time.sleep(1)

    @staticmethod
    def change_relay_state(relay_number, relay_state):
        """public function: change of relay state"""
        options = wiotp.sdk.application.parseConfigFile(mqtt_config_path)
        client = wiotp.sdk.application.ApplicationClient(options)
        data = {'r_n': relay_number, 'r_s': relay_state}
        try:
            client.connect()
            client.publishCommand("esp", "esp_32", "change_relay", "json", data)
            client.disconnect()
        except wiotp.sdk.exceptions.ConnectionException:
            return -1
        except wiotp.sdk.exceptions.ApiException:
            return -2
        return 0

    @staticmethod
    def get_data(event):
        """public function: get data from ESP32 via MQTT"""
        ans = json.loads(json.dumps(event.data))
        try:
            temperature = float(ans["data"]["tem"])
            humidity = float(ans["data"]["hum"])
            pressure = float(ans["data"]["pre"])
            co2 = float(ans["data"]["co2"])
            timestamp = int(ans["data"]["time"])
        except TypeError:
            return
        logging.info("T: {0}C H: {1}% P: {2}Pa C: {3}PPM".format(temperature, humidity, pressure, co2))
        Sqlite.write_data(timestamp, temperature, humidity, pressure, co2)
        Mqtt.indication_controller(temperature, humidity, pressure, co2)

    @staticmethod
    def indication_controller(temperature, humidity, pressure, co2):
        """public function: check data and display notifications"""
        # low temperature
        if temperature < Sensor.Scope.temperature[0]:
            if Sensor.LastWarning.tem_low == 0 or \
                    datetime.now().timestamp() - Sensor.LastWarning.tem_low > Sensor.LastWarning.interval:
                Sensor.LastWarning.tem_low = datetime.now().timestamp()
                Queues.voice_queue.put(Phrases.Mqtt.low_temperature)
                message = str(datetime.now().strftime("%H:%M:%S - ")) \
                          + "Нижняя граница t: Включение обогревателя."
                Queues.notify_queue.put([message])
                ans = Mqtt.change_relay_state(4, 1)
                if ans == -1 or ans == -2:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Нижняя граница t: Невозможно включить обогреватель."
                    Queues.notify_queue.put([message])
                else:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Нижняя граница t: Обогреватель включен."
                    Queues.notify_queue.put([message])

        # high temperature
        if temperature > Sensor.Scope.temperature[1]:
            if Sensor.LastWarning.tem_high == 0 or \
                    datetime.now().timestamp() - Sensor.LastWarning.tem_high > Sensor.LastWarning.interval:
                Sensor.LastWarning.tem_high = datetime.now().timestamp()
                Queues.voice_queue.put(Phrases.Mqtt.high_temperature)
                message = str(datetime.now().strftime("%H:%M:%S - ")) + "Верхняя граница t: Выключение обогревателя."
                Queues.notify_queue.put([message])
                ans = Mqtt.change_relay_state(4, 0)
                if ans == -1 or ans == -2:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Верхняя граница t: Невозможно выключить обогреватель."
                    Queues.notify_queue.put([message])
                else:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Верхняя граница t: Обогреватель выключен."
                    Queues.notify_queue.put([message])

        # high CO2
        if co2 > Sensor.Scope.CO2[1]:
            if Sensor.LastWarning.CO2_high == 0 or \
                    datetime.now().timestamp() - Sensor.LastWarning.CO2_high > Sensor.LastWarning.interval:
                Sensor.LastWarning.CO2_high = datetime.now().timestamp()
                Queues.voice_queue.put(Phrases.Mqtt.high_CO2)
                message = str(datetime.now().strftime("%H:%M:%S - ")) \
                          + "Верхняя граница CO2: Включение вентиляции."
                Queues.notify_queue.put([message])
                ans = Mqtt.change_relay_state(5, 1)
                if ans == -1 or ans == -2:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Верхняя граница CO2: Невозможно включить вентиляцию."
                    Queues.notify_queue.put([message])
                else:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Верхняя граница CO2: Вентиляция включена."
                    Queues.notify_queue.put([message])

        # normal CO2
        if co2 < Sensor.Scope.CO2[0]:
            if Sensor.LastWarning.CO2_low == 0 or \
                    datetime.now().timestamp() - Sensor.LastWarning.CO2_low > Sensor.LastWarning.interval:
                Sensor.LastWarning.CO2_low = datetime.now().timestamp()
                Queues.voice_queue.put(Phrases.Mqtt.low_CO2)
                message = str(datetime.now().strftime("%H:%M:%S - ")) \
                          + "Нижняя граница CO2: Выключение вентиляции."
                Queues.notify_queue.put([message])
                ans = Mqtt.change_relay_state(5, 0)
                if ans == -1 or ans == -2:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Нижняя граница CO2: Невозможно выключить вентиляцию."
                    Queues.notify_queue.put([message])
                else:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Нижняя граница CO2: Вентиляция выключена."
                    Queues.notify_queue.put([message])

        # low humidity
        if humidity < Sensor.Scope.humidity[0]:
            if Sensor.LastWarning.hum_low == 0 or \
                    datetime.now().timestamp() - Sensor.LastWarning.hum_low > Sensor.LastWarning.interval:
                Sensor.LastWarning.hum_low = datetime.now().timestamp()
                Queues.voice_queue.put(Phrases.Mqtt.low_humidity)
                message = str(datetime.now().strftime("%H:%M:%S - ")) \
                          + "Нижняя граница %: Включение увлажнителя"
                Queues.notify_queue.put([message])
                ans = Mqtt.change_relay_state(6, 1)
                if ans == -1 or ans == -2:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Нижняя граница %: Невозможно включить увлажнитель."
                    Queues.notify_queue.put([message])
                else:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Нижняя граница %: Увлажнитель включен."
                    Queues.notify_queue.put([message])

        # high humidity
        if humidity > Sensor.Scope.humidity[1]:
            if Sensor.LastWarning.hum_high == 0 or \
                    datetime.now().timestamp() - Sensor.LastWarning.hum_high > Sensor.LastWarning.interval:
                Sensor.LastWarning.hum_high = datetime.now().timestamp()
                Queues.voice_queue.put(Phrases.Mqtt.high_humidity)
                message = str(datetime.now().strftime("%H:%M:%S - ")) \
                          + "Верхняя граница %: Выключение увлажнителя."
                Queues.notify_queue.put([message])
                ans = Mqtt.change_relay_state(6, 0)
                if ans == -1 or ans == -2:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Верхняя граница %: Невозможно выключить увлажнитель."
                    Queues.notify_queue.put([message])
                else:
                    message = str(datetime.now().strftime("%H:%M:%S - ")) \
                              + "Верхняя граница %: Увлажнитель выключен."
                    Queues.notify_queue.put([message])

        # high pressure
        if pressure > Sensor.Scope.pressure[1]:
            if Sensor.LastWarning.pre_high == 0 or \
                    datetime.now().timestamp() - Sensor.LastWarning.pre_high > Sensor.LastWarning.pressure_interval:
                Sensor.LastWarning.pre_high = datetime.now().timestamp()
                Queues.voice_queue.put(Phrases.Mqtt.high_pressure)
                message = str(datetime.now().strftime("%H:%M:%S - ")) \
                          + "Верхняя граница Pa: Может быть плохое самочувствие у метеозависимых людей."
                Queues.notify_queue.put([message])

        # low pressure
        if pressure < Sensor.Scope.pressure[0]:
            if Sensor.LastWarning.pre_low == 0 or \
                    datetime.now().timestamp() - Sensor.LastWarning.pre_low > Sensor.LastWarning.pressure_interval:
                Sensor.LastWarning.pre_low = datetime.now().timestamp()
                Queues.voice_queue.put(Phrases.Mqtt.low_pressure)
                message = str(datetime.now().strftime("%H:%M:%S - ")) \
                          + "Нижняя граница Pa: Может быть плохое самочувствие у метеозависимых людей."
                Queues.notify_queue.put([message])
        return 0

    @staticmethod
    def sensor_scope(path):
        """public function: create configuration of sensor scope"""
        print("\n#############################################")
        print("Настройка границ нормальных значений датчиков")
        temp = input("Введите границы датчика температуры в C (Пример - 15:35):\n>>> ")
        temp = temp.split(':')
        humi = input("Введите границы датчика влажности в % (Пример - 30:60):\n>>> ")
        humi = humi.split(':')
        pres = input("Введите границы датчика давления в Pa (Пример - 99000:103000):\n>>> ")
        pres = pres.split(':')
        CO2 = input("Введите границы датчика CO2 в PPM (Пример - 200:1200):\n>>> ")
        CO2 = CO2.split(':')
        config = configparser.ConfigParser()
        config.add_section("Settings")
        config.set("Settings", "temp_low", temp[0])
        config.set("Settings", "temp_high", temp[1])
        config.set("Settings", "humi_low", humi[0])
        config.set("Settings", "humi_high", humi[1])
        config.set("Settings", "pres_low", pres[0])
        config.set("Settings", "pres_high", pres[1])
        config.set("Settings", "CO2_low", CO2[0])
        config.set("Settings", "CO2_high", CO2[1])
        with open(path, "w") as config_file:
            config.write(config_file)
        print("#############################################\n")
        return 0

    @staticmethod
    def connection_configuring(path):
        """public function: create configuration of MQTT connection"""
        print("\n#############################################")
        print("Настройка подключения MQTT")
        key_ = input("Введите ключ (Пример - a-4icjaj-bosbzreg7k):\n>>> ")
        token_ = input("Введите токен (Пример - LHjqZ9MjHGRL&&)-1o):\n>>> ")
        data = dict(
            identity=dict(appId="MacBookPro"),
            auth=dict(
                key=key_,
                token=token_, ),
            options=dict(
                domain='internetofthings.ibmcloud.com',
                loglevel='debug',
                mqtt=dict(port=1883, transport='tcp', cleanStart=True, sessionExpiry=7200, keepAlive=120,
                          caFile='/home/ubuntu/ibmiot/messaging.pem', )
            )
        )
        with open(path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    @staticmethod
    def sensor_scope_read():
        """public function: read configuration of sensor scope"""
        config = configparser.ConfigParser()
        config.read(mqtt_sensor_scope_path)
        Sensor.Scope.temperature = [float(config.get("Settings", "temp_low")),
                                    float(config.get("Settings", "temp_high"))]
        Sensor.Scope.humidity = [float(config.get("Settings", "humi_low")),
                                 float(config.get("Settings", "humi_high"))]
        Sensor.Scope.pressure = [float(config.get("Settings", "pres_low")),
                                 float(config.get("Settings", "pres_high"))]
        Sensor.Scope.CO2 = [float(config.get("Settings", "CO2_low")),
                            float(config.get("Settings", "CO2_high"))]
        return 0
