#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from multiprocessing import Queue
from phrases import Phrases
from speech import Speech
from sys import platform
import multiprocessing
from player import VLC
from mqtt import Mqtt
import ui_controller
import logging
import urllib
import speech
import os

player = VLC()


class CommandBlock:
    """класс команд"""
    @staticmethod
    def play_voice(phrase):
        """проигрывание голоса с понижением и повышением громкости"""
        is_playing = player.is_playing()
        if is_playing == 1:
            volume = player.get_volume()
            player.smooth_volume_drop(volume)
            Speech.play_voice(phrase)
            player.smooth_volume_growth(volume)
        else:
            Speech.play_voice(phrase)
        return 0

    @staticmethod
    def command_block(index, q: Queue = None, recognized_text=None):
        """командный блок с командами по индексу команд"""
        # МУЗЫКА
        is_playing = player.is_playing()
        # включение проигрывания музыки
        if 0 <= index <= 199:
            if is_playing == 1:
                CommandBlock.play_voice(Phrases.Music.stop)
                player.stop()
                logging.info('Playing process -> stopped')
                return
            else:
                CommandBlock.play_voice(Phrases.Music.on_load)
                ans = player.add_playlist(True, "/main_playlist")
                if ans == -1:
                    logging.error('Music not found. Skipping task...')
                    CommandBlock.play_voice(Phrases.Music.not_found)
                    return
                player.play()
                logging.info('Playing process -> started')
                return

        # выключение музыки
        if 200 <= index <= 219:
            if is_playing == 1 or is_playing == 0:
                CommandBlock.play_voice(Phrases.Music.stop)
                player.stop()
                logging.info('Playing process -> stopped')
                return

        # пауза воспроизведения музыки
        if 220 <= index <= 479:
            if is_playing == 1:
                CommandBlock.play_voice(Phrases.Music.pause)
                player.pause()
                logging.info('Playing process -> paused')
                return

        # продолжение воспроизведения музыки
        if 480 <= index <= 599:
            if is_playing == 0:
                CommandBlock.play_voice(Phrases.Music.play)
                player.play()
                logging.info('Playing process -> resumed')
                return

        # сделать потише
        if 600 <= index <= 639:
            if is_playing == 1:
                CommandBlock.play_voice(Phrases.Music.volume_lower)
                player.quieter()
                logging.info('Volume of playing -> decreased')
                return

        # сделать погромче
        if 640 <= index <= 799:
            if is_playing == 1:
                CommandBlock.play_voice(Phrases.Music.volume_higher)
                player.louder()
                logging.info('Volume of playing -> increased')
                return

        # следующая песня
        if 800 <= index <= 819:
            if is_playing == 1:
                CommandBlock.play_voice(Phrases.Music.next)
                player.next()
                logging.info('Playing song changed -> next')
                return

        # предыдущая песня
        if 820 <= index <= 839:
            if is_playing == 1:
                CommandBlock.play_voice(Phrases.Music.previous)
                player.previous()
                logging.info('Playing song changed -> previous')
                return

        # ВНЕШНИЕ ПРОГРАММЫ
        # запуск браузера
        if 900 <= index <= 909:
            CommandBlock.play_voice(Phrases.AppOpening.browser)
            os.system('python -m webbrowser "http://google.com/"')
            logging.info('Browser -> opened')

        # запуск вконтакте
        if 910 <= index <= 919:
            CommandBlock.play_voice(Phrases.BrowserSiteOpening.vk)
            os.system('python -m webbrowser "http://vk.com/"')
            logging.info('VK -> opened')

        # запуск yandex
        if 920 <= index <= 929:
            CommandBlock.play_voice(Phrases.BrowserSiteOpening.yandex)
            os.system('python -m webbrowser "http://yandex.ru/"')
            logging.info('Yandex -> opened')

        # запуск youtube
        if 930 <= index <= 939:
            CommandBlock.play_voice(Phrases.BrowserSiteOpening.youtube)
            os.system('python -m webbrowser "http://youtube.com/"')
            logging.info('Youtube -> opened')

        # поиск яндекс
        if 940 <= index <= 949:
            CommandBlock.play_voice(Phrases.BrowserSiteOpening.user_search)
            remove_name = speech.assistant_name
            remove_command = ['найди', 'найти']
            list_of_words = recognized_text.split()
            output_list = []
            is_name_found = False
            is_command_found = False
            # удаление команды и имени помощника из запроса
            for word in list_of_words:
                if is_name_found and is_command_found:
                    output_list.append(word)
                    continue
                if word in remove_name:
                    is_name_found = True
                    continue
                elif word in remove_command:
                    is_command_found = True
                    continue
                else:
                    output_list.append(word)
            output_string = ' '.join(output_list)
            os.system('python -m webbrowser "https://yandex.ru/search/?text={0}"'.
                      format(urllib.parse.quote(output_string)))
            logging.info("Searching -> {0}".format(output_string))
            return

        # запуск терминала
        if 1000 <= index <= 1009:
            if platform == "win32" or platform == "linux" or platform == "linux2":
                logging.warning("This function is not supported on {0}.".format(platform))
                CommandBlock.play_voice(Phrases.AppOpening.not_supported)
                return
            CommandBlock.play_voice(Phrases.AppOpening.terminal)
            os.system('open -a terminal')
            logging.info('Terminal -> opened')
            return

        # запуск телеграм
        if 1010 <= index <= 1019:
            if platform == "win32" or platform == "linux" or platform == "linux2":
                logging.warning("This function is not supported on {0}.".format(platform))
                CommandBlock.play_voice(Phrases.AppOpening.not_supported)
                return
            CommandBlock.play_voice(Phrases.AppOpening.telegram)
            os.system('open -a telegram')
            logging.info('Telegram -> opened')
            return

        # запуск дискорда
        if 1020 <= index <= 1029:
            if platform == "win32" or platform == "linux" or platform == "linux2":
                logging.warning("This function is not supported on {0}.".format(platform))
                CommandBlock.play_voice(Phrases.AppOpening.not_supported)
                return
            CommandBlock.play_voice(Phrases.AppOpening.discord)
            os.system('open -a discord')
            logging.info('Discord -> opened')
            return

        # РЕЛЕ
        # включение реле_1
        if 1200 <= index <= 1209:
            ans = Mqtt.change_relay_state(1, 1)
            if ans == -1 or ans == -2:
                CommandBlock.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            CommandBlock.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('First relay state changed -> ON')

        # выключение реле_1
        if 1210 <= index <= 1219:
            ans = Mqtt.change_relay_state(1, 0)
            if ans == -1 or ans == -2:
                CommandBlock.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            CommandBlock.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('First relay state changed -> OFF')

        # включение реле_2
        if 1220 <= index <= 1229:
            ans = Mqtt.change_relay_state(2, 1)
            if ans == -1 or ans == -2:
                CommandBlock.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            CommandBlock.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('Second relay state changed -> ON')

        # выключение реле_2
        if 1230 <= index <= 1239:
            ans = Mqtt.change_relay_state(2, 0)
            if ans == -1 or ans == -2:
                CommandBlock.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            CommandBlock.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('Second relay state changed -> OFF')

        # включение реле_3
        if 1240 <= index <= 1249:
            ans = Mqtt.change_relay_state(3, 1)
            if ans == -1 or ans == -2:
                CommandBlock.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            CommandBlock.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('Third relay state changed -> ON')

        # выключение реле_3
        if 1250 <= index <= 1259:
            ans = Mqtt.change_relay_state(3, 0)
            if ans == -1 or ans == -2:
                CommandBlock.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            CommandBlock.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('Third relay state changed -> OFF')

        # открытие графического интерфейса
        if 1300 <= index <= 1309:
            CommandBlock.play_voice(Phrases.GUI.gui_open)
            T = multiprocessing.Process(target=ui_controller.start_ui, args=(q,))
            logging.info('GUI -> opened')
            T.start()

    @staticmethod
    def player_is_playing():
        """определение играет ли плеер или нет (0, 1 или -1)"""
        return player.is_playing()
