#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from command_dictionary import commands_list
from fuzzywuzzy import fuzz
import requests
import pyaudio
import logging
import random
import wave
import os

assistant_name = ['катя', 'кать', 'кати', 'кате', 'екатерина', 'екатерины', 'екатерине']
wav_folder = '/wav/'


class Speech:
    """класс для работы с речью - распознавание, синтез"""
    @staticmethod
    def text_analyse(recognized_text, name_needed=True, name_check=False):
        """анализ переданного текста, возврат номера команды и вероятности угадывания"""
        best_result = -1
        best_result_index = -1
        if name_needed:
            NameOK = False
            for name in assistant_name:
                if fuzz.partial_ratio(name, recognized_text) > 80:
                    NameOK = True
                    break
            if name_check:
                return NameOK
            if not NameOK:
                return -1, -1
            # проверка текста на совпадение с командами в словаре
            for key, value in commands_list.items():
                ratio = fuzz.token_set_ratio(value, recognized_text)
                if (ratio > 75) and (ratio > best_result):
                    best_result = ratio
                    best_result_index = key
        else:
            for key, value in commands_list.items():
                ratio = fuzz.token_set_ratio(value, recognized_text)
                if (ratio > 75) and (ratio > best_result):
                    best_result = ratio
                    best_result_index = key
        return best_result_index, best_result

    @staticmethod
    def play_voice(dictionary):
        """выбор рандомного варианта из списка доступных ответов, проигрывание ответа помощника"""
        key, phrase = random.choice(list(dictionary.items()))
        ans = 0
        if not os.path.exists(os.path.abspath(os.curdir) + wav_folder + key):
            ans = Speech.__create_wav(phrase, key)
        if ans == -1:
            logging.error("No wav voice file found, 'cause Unitools API returned not 200.")
            return
        if ans == -2:
            logging.error("No wav voice file found, 'cause no connection found.")
            return
        Speech.__play_wav(key)
        return 0

    @staticmethod
    def __play_wav(name_of_file):
        """проигрывание wav файла"""
        chunk = 1024
        wf = wave.open(os.path.abspath(os.curdir) + wav_folder + name_of_file, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()
        return 0

    @staticmethod
    def __create_wav(text, name_of_file):
        """создание wav файла по API сервиса unitools.tech"""
        data = {
            "email": "ilya.kom123@gmail.com",
            "password": "cNNzmVMdzPe2cQk",
            "token": "RoJeZv",
            "name": "Cate",
            "round": True,
            "text": "{0}".format(text)
        }
        try:
            result = requests.post(f'https://unitools.tech/dev-api/tts', data=data)
            print('Status:', result.status_code)
        except requests.exceptions.ConnectionError:
            return -2
        if result.status_code == 200:
            print('Url:', result.json()['url'])
            print('Balance:', result.json()['balance'])
            audio = requests.get(result.json()['url']).content
            with open(os.path.abspath(os.curdir) + wav_folder + name_of_file, 'wb') as f:
                f.write(audio)
        else:
            return -1
        return 0
