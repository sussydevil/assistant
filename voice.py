#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from commands import commands_list
from multiprocessing import Queue
from fuzzywuzzy import fuzz
import requests
import pyaudio
import logging
import random
import queue
import wave
import os


class Analyse:
    """class: analyse recognized text"""
    @staticmethod
    def recognized_text(recognized_text, assistant_name, name_needed=True, name_check=False):
        """public function: analyse of recognised text and return command index"""
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
            for key, value in commands_list.items():
                ratio = fuzz.token_set_ratio(value, recognized_text)
                if (ratio > 70) and (ratio > best_result):
                    best_result = ratio
                    best_result_index = key
        else:
            for key, value in commands_list.items():
                ratio = fuzz.token_set_ratio(value, recognized_text)
                if (ratio > 70) and (ratio > best_result):
                    best_result = ratio
                    best_result_index = key
        return best_result_index, best_result


class SpeechPlayer:
    """class: work with assistant's speech"""
    @staticmethod
    def play_voice(dictionary, folder):
        """public function: play random phrase from dictionary and save to the current folder if file not exists"""
        key, phrase = random.choice(list(dictionary.items()))
        answer = 0
        if not os.path.exists(os.path.join(folder, key)):
            answer = SpeechPlayer.__create_wav(phrase, key, folder)
            logging.info('Successfully created new voice file.')
            logging.info("Phrase is: " + phrase)
        if answer == 1:
            logging.error("No wav voice file found, 'cause Unitools API returned not 200.")
            logging.info("Phrase is: " + phrase)
            return 1
        if answer == 2:
            logging.error("No wav voice file found, 'cause no connection found.")
            logging.info("Phrase is: " + phrase)
            return 2
        SpeechPlayer.__play_wav(key, folder)
        return 0

    @staticmethod
    def __play_wav(name_of_file, folder):
        """private function: play wav with PyAudio from current folder"""
        chunk = 1024
        wf = wave.open(os.path.join(folder, name_of_file), 'rb')
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
    def __create_wav(text, name_of_file, folder):
        """private function: create wav file with Unitools.Tech API Service to current folder"""
        if not os.path.exists(folder):
            os.mkdir(folder)
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
        except requests.exceptions.ConnectionError:
            return 2
        logging.debug('Status:' + str(result.status_code))
        if result.status_code == 200:
            logging.debug('Url: ' + str(result.json()['url']))
            logging.debug('Balance: ' + str(result.json()['balance']))
            audio = requests.get(result.json()['url']).content
            with open(os.path.join(folder, name_of_file), 'wb') as f:
                f.write(audio)
            return 0
        else:
            return 1


def voice_loop(dictionary: Queue, status: Queue, wav_folder):
    """public function: loop and wait for new tasks of playing voice (dictionary: Queue)"""
    while True:
        try:
            phrases = dictionary.get(True, 10)
            answer = SpeechPlayer.play_voice(phrases, wav_folder)
            status.put([answer, phrases])
        except queue.Empty:
            continue
