#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from multiprocessing import Process, Queue
from vosk import Model, KaldiRecognizer
from voice import voice_loop, Analyse
from executor import Executor
from phrases import Phrases
from sqlite import Sqlite
from time import sleep
from mqtt import Mqtt
import logging
import pyaudio
import queue
import json
import sys
import os

logging.basicConfig(level=logging.DEBUG, format='%(process)d (%(name)s) - %(levelname)s: %(message)s')
mqtt_config_path = "mqtt_connection.conf"
mqtt_sensor_scope_path = "sensor.conf"
model_path = "model"


class Queues:
    """класс для связи процессов друг с другом"""
    mqtt_notifications = Queue()
    mqtt_voice = Queue()
    voice_play = Queue()
    voice_status = Queue()


def main():
    """распознавание голоса, вызов других функций и процессов по необходимости"""
    # отдельный процесс для воспроизведения голоса с реализацией очереди
    voice_process = Process(target=voice_loop,
                            args=(Queues.voice_play, Queues.voice_status), daemon=True)
    voice_process.start()

    Queues.voice_play.put(Phrases.Load.on_load)
    sleep(2)
    # проверка на наличие модели
    if not os.path.exists(model_path):
        Queues.voice_play.put(Phrases.Load.model_error)
        sys.exit(1)
    Queues.voice_play.put(Phrases.Load.model_ok)
    sleep(2)

    # создание объектов для распознавания
    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    # создание БД, если её нет
    Sqlite.create_database()
    Queues.voice_play.put(Phrases.Load.database_ok)
    sleep(2)

    # создание настроек границ датчиков
    if not os.path.exists(mqtt_sensor_scope_path):
        Queues.voice_play.put(Phrases.Load.sensor_configuring)
        Mqtt.sensor_scope(mqtt_sensor_scope_path)

    # создание настроек подключения к MQTT
    if not os.path.exists(mqtt_config_path):
        Queues.voice_play.put(Phrases.Load.mqtt_configuring)
        Mqtt.connection_configuring(mqtt_config_path)

    # отдельный процесс для получения данных с датчиков по MQTT
    mqtt_process = Process(target=Mqtt.start, args=(Queues.mqtt_notifications, Queues.mqtt_voice))
    mqtt_process.start()
    Queues.voice_play.put(Phrases.Load.ibm_ok)
    sleep(2)

    Queues.voice_play.put(Phrases.Load.recognition_on)
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
            index, percentage = Analyse.recognized_text(recognized_text, name_needed=True)
            if index == -1:
                continue
            print("Recognized: " + recognized_text + " Command index: " + str(index))
            # отправка команды в командный блок
            Executor.execute(index, Queues.mqtt_notifications,
                             Queues.voice_status, Queues.voice_play, recognized_text)
        try:
            answer = Queues.mqtt_voice.get_nowait()
            Executor.play_voice(answer)
        except queue.Empty:
            pass


# точка входа в программу
if __name__ == '__main__':
    main()
