#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from multiprocessing import Queue
from datetime import datetime
import wiotp.sdk.application
from phrases import Phrases
from sqlite import Sqlite
from speech import Speech
import configparser
import logging
import json
import yaml
import time

# файл конфигурации границ значений датчиков
mqtt_sensor_scope_path = "sensor.conf"
queue = Queue()


def mqtt_sensor_scope(path):
    """создание конфигурации границ датчиков"""
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


def mqtt_connection_configuring(path):
    """создание конфигурации настроек MQTT"""
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


class SensorWarningTime:
    """класс, содержащий время последнего уведомления о недопустимых значениях"""
    tem_high = 0
    tem_low = 0
    hum_high = 0
    hum_low = 0
    pre_high = 0
    pre_low = 0
    CO2_high = 0
    CO2_low = 0
    # интервал уведомления 30 минут или 1800 секунд
    interval = 1800
    # интервал уведомления о высоком атмосферном давлении (никак не регулируется) 4 часа или 14400 секунд
    pressure_interval = 14400


class Mqtt:
    """класс для работы с mqtt"""

    # запуск получения данных с MQTT
    @staticmethod
    def start(q: Queue = None):
        """открытие MQTT соединения"""
        options = wiotp.sdk.application.parseConfigFile("mqtt_connection.conf")
        client = wiotp.sdk.application.ApplicationClient(options)
        client.logger.setLevel(logging.INFO)
        global queue
        queue = q
        SensorScope.mqtt_sensor_scope_read()
        client.logger.setLevel(logging.INFO)
        client.connect()
        client.deviceEventCallback = Mqtt.get_data
        client.subscribeToDeviceEvents()
        while True:
            time.sleep(1)

    @staticmethod
    def change_relay_state(relay_number, relay_state):
        """изменение состояния реле"""
        options = wiotp.sdk.application.parseConfigFile("mqtt_connection.conf")
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
        """получение данных с датчиков через MQTT"""
        ans = json.loads(json.dumps(event.data))
        temperature = float(ans["data"]["tem"])
        humidity = float(ans["data"]["hum"])
        pressure = float(ans["data"]["pre"])
        co2 = float(ans["data"]["co2"])
        timestamp = int(ans["data"]["time"])
        logging.info("T: {0}C H: {1}% P: {2}Pa C: {3}PPM".format(temperature, humidity, pressure, co2))
        Sqlite.write_data(timestamp, temperature, humidity, pressure, co2)
        Mqtt.indication_controller(temperature, humidity, pressure, co2)

    @staticmethod
    def indication_controller(temperature, humidity, pressure, co2):
        """проверка данных датчиков, вывод уведомлений о критических показаниях"""
        # низкая температура
        if temperature < SensorScope.temperature[0]:
            if SensorWarningTime.tem_low == 0 or \
                    datetime.now().timestamp() - SensorWarningTime.tem_low > SensorWarningTime.interval:
                SensorWarningTime.tem_low = datetime.now().timestamp()
                Speech.play_voice(Phrases.Mqtt.low_temperature)
                warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                           + "Нижняя граница t: Включение обогревателя."
                queue.put([warning_])
                ans = Mqtt.change_relay_state(4, 1)
                if ans == -1 or ans == -2:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Нижняя граница t: Невозможно включить обогреватель."
                    queue.put([warning_])
                else:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Нижняя граница t: Обогреватель включен."
                    queue.put([warning_])

        # высокая температура
        if temperature > SensorScope.temperature[1]:
            if SensorWarningTime.tem_high == 0 or \
                    datetime.now().timestamp() - SensorWarningTime.tem_high > SensorWarningTime.interval:
                SensorWarningTime.tem_high = datetime.now().timestamp()
                Speech.play_voice(Phrases.Mqtt.high_temperature)
                warning_ = str(datetime.now().strftime("%H:%M:%S - ")) + "Верхняя граница t: Выключение обогревателя."
                queue.put([warning_])
                ans = Mqtt.change_relay_state(4, 0)
                if ans == -1 or ans == -2:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Верхняя граница t: Невозможно выключить обогреватель."
                    queue.put([warning_])
                else:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Верхняя граница t: Обогреватель выключен."
                    queue.put([warning_])

        # повышенное содержание CO2
        if co2 > SensorScope.CO2[1]:
            if SensorWarningTime.CO2_high == 0 or \
                    datetime.now().timestamp() - SensorWarningTime.CO2_high > SensorWarningTime.interval:
                SensorWarningTime.CO2_high = datetime.now().timestamp()
                Speech.play_voice(Phrases.Mqtt.high_CO2)
                warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                           + "Верхняя граница CO2: Включение вентиляции."
                queue.put([warning_])
                ans = Mqtt.change_relay_state(5, 1)
                if ans == -1 or ans == -2:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Верхняя граница CO2: Невозможно включить вентиляцию."
                    queue.put([warning_])
                else:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Верхняя граница CO2: Вентиляция включена."
                    queue.put([warning_])

        # нормальное содержание CO2
        if co2 < SensorScope.CO2[0]:
            if SensorWarningTime.CO2_low == 0 or \
                    datetime.now().timestamp() - SensorWarningTime.CO2_low > SensorWarningTime.interval:
                SensorWarningTime.CO2_low = datetime.now().timestamp()
                Speech.play_voice(Phrases.Mqtt.low_CO2)
                warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                           + "Нижняя граница CO2: Выключение вентиляции."
                queue.put([warning_])
                ans = Mqtt.change_relay_state(5, 0)
                if ans == -1 or ans == -2:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Нижняя граница CO2: Невозможно выключить вентиляцию."
                    queue.put([warning_])
                else:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Нижняя граница CO2: Вентиляция выключена."
                    queue.put([warning_])

        # пониженная влажность
        if humidity < SensorScope.humidity[0]:
            if SensorWarningTime.hum_low == 0 or \
                    datetime.now().timestamp() - SensorWarningTime.hum_low > SensorWarningTime.interval:
                SensorWarningTime.hum_low = datetime.now().timestamp()
                Speech.play_voice(Phrases.Mqtt.low_humidity)
                warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                           + "Нижняя граница %: Включение увлажнителя"
                queue.put([warning_])
                ans = Mqtt.change_relay_state(6, 1)
                if ans == -1 or ans == -2:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Нижняя граница %: Невозможно включить увлажнитель."
                    queue.put([warning_])
                else:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Нижняя граница %: Увлажнитель включен."
                    queue.put([warning_])

        # высокая влажность
        if humidity > SensorScope.humidity[1]:
            if SensorWarningTime.hum_high == 0 or \
                    datetime.now().timestamp() - SensorWarningTime.hum_high > SensorWarningTime.interval:
                SensorWarningTime.hum_high = datetime.now().timestamp()
                Speech.play_voice(Phrases.Mqtt.high_humidity)
                warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                           + "Верхняя граница %: Выключение увлажнителя."
                queue.put([warning_])
                ans = Mqtt.change_relay_state(6, 0)
                if ans == -1 or ans == -2:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Верхняя граница %: Невозможно выключить увлажнитель."
                    queue.put([warning_])
                else:
                    warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                               + "Верхняя граница %: Увлажнитель выключен."
                    queue.put([warning_])

        # высокое атмосферное давление
        if pressure > SensorScope.pressure[1]:
            if SensorWarningTime.pre_high == 0 or \
                    datetime.now().timestamp() - SensorWarningTime.pre_high > SensorWarningTime.pressure_interval:
                SensorWarningTime.pre_high = datetime.now().timestamp()
                Speech.play_voice(Phrases.Mqtt.high_pressure)
                warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                                      + "Верхняя граница Pa: Может быть плохое самочувствие у метеозависимых людей."
                queue.put([warning_])

        # низкое атмосферное давление
        if pressure < SensorScope.pressure[0]:
            if SensorWarningTime.pre_low == 0 or \
                    datetime.now().timestamp() - SensorWarningTime.pre_low > SensorWarningTime.pressure_interval:
                SensorWarningTime.pre_low = datetime.now().timestamp()
                Speech.play_voice(Phrases.Mqtt.low_pressure)
                warning_ = str(datetime.now().strftime("%H:%M:%S - ")) \
                           + "Нижняя граница Pa:Может быть плохое самочувствие у метеозависимых людей."
                queue.put([warning_])
        return 0
