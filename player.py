#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
from random import shuffle
from vlc import Instance
import logging
import time
import os


class VLC:
    """класс для работы с плеером"""
    __music_formats = ['.mp3', '.wma', '.wav', '.flac', '.aac', '.ogg', '.m4a']
    __volume = 60

    def __init__(self):
        """инициализация"""
        self.Player = Instance('--loop')
        self.listPlayer = None
        self.mediaList = None

    def add_playlist(self, random=False, path='/main_playlist/'):
        """добавление плейлиста:
        рандом (True, False);
        путь к папке (например: /main_playlist/)"""
        self.mediaList = self.Player.media_list_new()
        directory = os.getcwd() + '/music' + path
        songs = os.listdir(directory)
        if random:
            shuffle(songs)
        for song in songs:
            filename, file_extension = os.path.splitext(song)
            # пропуск ненужных форматов в папке
            if file_extension not in VLC.__music_formats:
                logging.warning('{0} - bad format. Skipping...'.format(song))
                continue
            self.mediaList.add_media(self.Player.media_new(os.path.join(directory, song)))
        if len(songs) == 0:
            return -1
        self.listPlayer = self.Player.media_list_player_new()
        self.listPlayer.set_media_list(self.mediaList)
        logging.info('Playlist -> added')

    def play(self):
        """проигрывание"""
        self.listPlayer.get_media_player().audio_set_volume(VLC.__volume)
        self.listPlayer.play()

    def pause(self):
        """пауза"""
        self.listPlayer.pause()

    def stop(self):
        """стоп"""
        self.listPlayer.stop()

    def next(self):
        """следующая песня"""
        self.listPlayer.next()

    def previous(self):
        """предыдущая песня"""
        self.listPlayer.previous()

    def quieter(self):
        """убавление громкости на 10 пунктов"""
        VLC.__volume = self.listPlayer.get_media_player().audio_get_volume() - 10
        if VLC.__volume < 0:
            VLC.__volume = 0
        self.listPlayer.get_media_player().audio_set_volume(VLC.__volume)

    def louder(self):
        """прибавление громкости на 10 пунктов"""
        VLC.__volume = self.listPlayer.get_media_player().audio_get_volume() + 10
        if VLC.__volume > 100:
            VLC.__volume = 100
        self.listPlayer.get_media_player().audio_set_volume(VLC.__volume)

    def get_volume(self):
        """получение громкости"""
        return self.listPlayer.get_media_player().audio_get_volume()

    def smooth_volume_drop(self, volume):
        """плавное понижение громкости"""
        step = volume * 0.1
        for i in range(3):
            volume = round(volume - step)
            self.listPlayer.get_media_player().audio_set_volume(volume)
            time.sleep(0.4)

    def smooth_volume_growth(self, volume):
        """плавное повышение громкости"""
        step = volume * 0.1
        temp_volume = self.get_volume()
        for i in range(3):
            temp_volume = round(temp_volume + step)
            self.listPlayer.get_media_player().audio_set_volume(temp_volume)
            time.sleep(0.4)
        self.listPlayer.get_media_player().audio_set_volume(volume)

    def is_playing(self):
        """возвращение результата - играет плеер или нет (0, 1 или -1)"""
        try:
            return self.listPlayer.get_media_player().is_playing()
        except AttributeError:
            return -1
