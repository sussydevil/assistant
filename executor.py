#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from multiprocessing import Queue
from phrases import Phrases
from sys import platform
import multiprocessing
from player import VLC
from mqtt import Mqtt
import ui_controller
import logging
import urllib
import voice
import os

player = VLC()


class Queues:
    """class: queues from main"""
    mqtt_notifications = Queue()
    voice_play = Queue()
    voice_status = Queue()


class Executor:
    """class: execute commands"""
    @staticmethod
    def play_voice(phrase, voice_play: Queue = None, voice_status: Queue = None):
        """public function: play voice with accent on voice (when music plays)"""
        if voice_status is not None and voice_play is not None:
            Queues.voice_play = voice_play
            Queues.voice_status = voice_status
        is_playing = player.is_playing()
        if is_playing == 1:
            volume = player.get_volume()
            player.smooth_volume_drop(volume)
            Queues.voice_play.put(phrase)
            while Queues.voice_status.get()[1] != phrase:
                pass
            player.smooth_volume_growth(volume)
        else:
            Queues.voice_play.put(phrase)
        return 0

    @staticmethod
    def execute(index, notifications: Queue, status: Queue, play: Queue, recognized_text=None):
        """public function: execute command with index"""
        # MUSIC
        Queues.voice_status = status
        Queues.voice_play = play
        Queues.mqtt_notifications = notifications
        is_playing = player.is_playing()

        # music on
        if 0 <= index <= 199:
            if is_playing == 1:
                Executor.play_voice(Phrases.Music.stop)
                player.stop()
                logging.info('Playing process -> stopped')
                return
            else:
                Executor.play_voice(Phrases.Music.on_load)
                ans = player.add_playlist(True, "/main_playlist")
                if ans == -1:
                    logging.error('Music not found. Skipping task...')
                    Executor.play_voice(Phrases.Music.not_found)
                    return
                player.play()
                logging.info('Playing process -> started')
                return

        # music off
        if 200 <= index <= 219:
            if is_playing == 1 or is_playing == 0:
                Executor.play_voice(Phrases.Music.stop)
                player.stop()
                logging.info('Playing process -> stopped')
                return

        # music pause
        if 220 <= index <= 479:
            if is_playing == 1:
                Executor.play_voice(Phrases.Music.pause)
                player.pause()
                logging.info('Playing process -> paused')
                return

        # music resume
        if 480 <= index <= 599:
            if is_playing == 0:
                Executor.play_voice(Phrases.Music.play)
                player.play()
                logging.info('Playing process -> resumed')
                return

        # music volume lower
        if 600 <= index <= 639:
            if is_playing == 1:
                Executor.play_voice(Phrases.Music.volume_lower)
                player.quieter()
                logging.info('Volume of playing -> decreased')
                return

        # music volume higher
        if 640 <= index <= 799:
            if is_playing == 1:
                Executor.play_voice(Phrases.Music.volume_higher)
                player.louder()
                logging.info('Volume of playing -> increased')
                return

        # next song
        if 800 <= index <= 819:
            if is_playing == 1:
                Executor.play_voice(Phrases.Music.next)
                player.next()
                logging.info('Playing song changed -> next')
                return

        # previous song
        if 820 <= index <= 839:
            if is_playing == 1:
                Executor.play_voice(Phrases.Music.previous)
                player.previous()
                logging.info('Playing song changed -> previous')
                return

        # EXTERNAL PROGRAMMES
        # browser on
        if 900 <= index <= 909:
            Executor.play_voice(Phrases.AppOpening.browser)
            os.system('python -m webbrowser "http://google.com/"')
            logging.info('Browser -> opened')

        # vk on
        if 910 <= index <= 919:
            Executor.play_voice(Phrases.BrowserSiteOpening.vk)
            os.system('python -m webbrowser "http://vk.com/"')
            logging.info('VK -> opened')

        # yandex on
        if 920 <= index <= 929:
            Executor.play_voice(Phrases.BrowserSiteOpening.yandex)
            os.system('python -m webbrowser "http://yandex.ru/"')
            logging.info('Yandex -> opened')

        # youtube on
        if 930 <= index <= 939:
            Executor.play_voice(Phrases.BrowserSiteOpening.youtube)
            os.system('python -m webbrowser "http://youtube.com/"')
            logging.info('Youtube -> opened')

        # yandex search
        if 940 <= index <= 949:
            Executor.play_voice(Phrases.BrowserSiteOpening.user_search)
            remove_name = voice.assistant_name
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

        # terminal on
        if 1000 <= index <= 1009:
            if platform == "win32" or platform == "linux" or platform == "linux2":
                logging.warning("This function is not supported on {0}.".format(platform))
                Executor.play_voice(Phrases.AppOpening.not_supported)
                return
            Executor.play_voice(Phrases.AppOpening.terminal)
            os.system('open -a terminal')
            logging.info('Terminal -> opened')
            return

        # telegram on
        if 1010 <= index <= 1019:
            if platform == "win32" or platform == "linux" or platform == "linux2":
                logging.warning("This function is not supported on {0}.".format(platform))
                Executor.play_voice(Phrases.AppOpening.not_supported)
                return
            Executor.play_voice(Phrases.AppOpening.telegram)
            os.system('open -a telegram')
            logging.info('Telegram -> opened')
            return

        # discord on
        if 1020 <= index <= 1029:
            if platform == "win32" or platform == "linux" or platform == "linux2":
                logging.warning("This function is not supported on {0}.".format(platform))
                Executor.play_voice(Phrases.AppOpening.not_supported)
                return
            Executor.play_voice(Phrases.AppOpening.discord)
            os.system('open -a discord')
            logging.info('Discord -> opened')
            return

        # RELAY
        # relay_1 on
        if 1200 <= index <= 1209:
            ans = Mqtt.change_relay_state(1, 1)
            if ans == -1 or ans == -2:
                Executor.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            Executor.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('First relay state changed -> ON')

        # relay_1 off
        if 1210 <= index <= 1219:
            ans = Mqtt.change_relay_state(1, 0)
            if ans == -1 or ans == -2:
                Executor.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            Executor.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('First relay state changed -> OFF')

        # relay_2 on
        if 1220 <= index <= 1229:
            ans = Mqtt.change_relay_state(2, 1)
            if ans == -1 or ans == -2:
                Executor.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            Executor.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('Second relay state changed -> ON')

        # relay_2 off
        if 1230 <= index <= 1239:
            ans = Mqtt.change_relay_state(2, 0)
            if ans == -1 or ans == -2:
                Executor.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            Executor.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('Second relay state changed -> OFF')

        # relay_3 on
        if 1240 <= index <= 1249:
            ans = Mqtt.change_relay_state(3, 1)
            if ans == -1 or ans == -2:
                Executor.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            Executor.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('Third relay state changed -> ON')

        # relay_3 off
        if 1250 <= index <= 1259:
            ans = Mqtt.change_relay_state(3, 0)
            if ans == -1 or ans == -2:
                Executor.play_voice(Phrases.Mqtt.relay_connection_error)
                logging.error('Relay unreachable. Internet connection lost.')
                return
            Executor.play_voice(Phrases.Mqtt.relay_ok)
            logging.info('Third relay state changed -> OFF')

        # GUI on
        if 1300 <= index <= 1309:
            Executor.play_voice(Phrases.GUI.gui_open)
            T = multiprocessing.Process(target=ui_controller.start_ui, args=(notifications,))
            logging.info('GUI -> opened')
            T.start()

    @staticmethod
    def player_is_playing():
        """public function: return state of player (0, 1 or -1)"""
        return player.is_playing()
