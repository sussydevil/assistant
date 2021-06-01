#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from mqtt import Mqtt, mqtt_sensor_scope, mqtt_connection_configuring
from multiprocessing import Process, Queue
from vosk import Model, KaldiRecognizer
from command import CommandBlock
from threading import Thread
from phrases import Phrases
from sqlite import Sqlite
from speech import Speech
from time import sleep
import logging
import pyaudio
import json
import sys
import os

logging.basicConfig(level=logging.DEBUG, format='%(process)d (%(name)s) - %(levelname)s: %(message)s')
mqtt_config_path = "mqtt_connection.conf"
mqtt_sensor_scope_path = "sensor.conf"
model_path = "model"


class QueueGetter:
    """класс для связи mqtt модуля с графическим интерфейсом"""
    queue = Queue()


def main():
    """распознавание голоса, вызов других функций и процессов по необходимости"""
    # создание папки для хранения голоса
    if not os.path.exists('wav'):
        os.mkdir('wav')
    Speech.play_voice(Phrases.Load.on_load)
    sleep(2)

    # проверка на наличие модели
    if not os.path.exists(model_path):
        Speech.play_voice(Phrases.Load.model_error)
        sys.exit(1)
    Speech.play_voice(Phrases.Load.model_ok)
    sleep(2)

    # создание объектов для распознавания
    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    # создание БД, если её нет
    Sqlite.create_database()
    Speech.play_voice(Phrases.Load.database_ok)
    sleep(2)

    # создание настроек границ датчиков
    if not os.path.exists(mqtt_sensor_scope_path):
        Speech.play_voice(Phrases.Load.sensor_configuring)
        mqtt_sensor_scope(mqtt_sensor_scope_path)

    # создание настроек подключения к MQTT
    if not os.path.exists(mqtt_config_path):
        Speech.play_voice(Phrases.Load.mqtt_configuring)
        mqtt_connection_configuring(mqtt_config_path)

    # подключение к MQTT для получения данных с датчиков (отдельный процесс), передача queue
    mqtt_reading_process = Process(target=Mqtt.start, args=(QueueGetter.queue,))
    mqtt_reading_process.start()
    Speech.play_voice(Phrases.Load.ibm_ok)
    sleep(2)

    Speech.play_voice(Phrases.Load.recognition_on)
    sleep(2)

    # бесконечное распознавание голоса
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            x = json.loads(rec.Result())
            # результат распознавания
            recognized_text = x["text"]
            # по умолчанию имя помощника нужно для команд
            name_needed = True
            # но если воспроизводятся песни, то имя не нужно для команд, связанных с ними
            if CommandBlock.player_is_playing() == 1:
                name_needed = False
            index, percentage = Speech.text_analyse(recognized_text, name_needed)
            if index == -1:
                continue
            # если музыка играет, то доступны команды без имени помощника, только связанные с музыкой (index = 0..899)
            if not name_needed and index >= 900:
                if not Speech.text_analyse(recognized_text, name_needed=True, name_check=True):
                    continue
            print("Recognized: " + recognized_text + " Command index: " + str(index))
            # отправка команды в командный блок отдельным потоком
            thread = Thread(target=CommandBlock.command_block(index, QueueGetter.queue, recognized_text), daemon=True)
            thread.start()


# точка входа в программу
if __name__ == '__main__':
    main()
