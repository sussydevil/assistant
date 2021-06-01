#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
class Phrases:
    """класс фраз голосового помощника"""
    class Load:
        """фразы: загрузка"""
        on_load = \
            {
                'on_load_1.wav': 'Загружаюсь, пожалуйста подождите',
                'on_load_2.wav': 'Голосовой помощник загружается',
                'on_load_3.wav': 'Запуск систем, пожалуйста подождите'
            }
        model_error = \
            {
                'model_err_1.wav': 'Ошибка, модель для распознавания не найдена',
                'model_err_2.wav': 'Ошибка, модель для распознавания отсутствует'
            }
        model_ok = \
            {
                'model_ok_1.wav': 'Модель для распознавания найдена',
                'model_ok_2.wav': 'Модель для распознавания голоса найдена'
            }
        database_ok = \
            {
                'database_ok_1.wav': 'База данных в норме',
                'database_ok_2.wav': 'База данных проверена'
            }
        ibm_ok = \
            {
                'ibm_ok_1.wav': 'Соединение с айбиэм установлено',
                'ibm_ok_2.wav': 'Соединение с сервером для работы с датчиками установлено'
            }
        recognition_on = \
            {
                'recognition_on_1.wav': 'Включаю распознавание речи',
                'recognition_on_2.wav': 'Распознавание речи включается'
            }
        sensor_configuring = \
            {
                'sensor_configuring_1.wav': 'Верхние и нижние границы значений датчиков не настроены. Пожалуйста,'
                                            'введите их в командной строке'
            }
        mqtt_configuring = \
            {
                'mqtt_configuring_1.wav': 'Соединение с айбиэм не настроено. Пожалуйста, введите данные подключения '
                                          'в командной строке'
            }

    class Music:
        """фразы: музыка"""
        on_load = \
            {
                'msc_on_load_1.wav': 'Включаю вашу музыку',
                'msc_on_load_2.wav': 'Включаю',
                'msc_on_load_3.wav': 'Сейчас включу'
            }
        on_load_playlist = \
            {
                'on_load_playlist_1.wav': 'Включаю выбранный плейлист',
                'on_load_playlist_2.wav': 'Хорошо, включаю',
                'on_load_playlist_3.wav': 'Сейчас включу'
            }
        next = \
            {
                'next_song_1.wav': 'Переключаю',
                'next_song_2.wav': 'Хорошо, переключаю вперёд',
                'next_song_3.wav': 'Переключаю вперёд',
                'next_song_4.wav': 'Сейчас',
            }
        previous = \
            {
                'prev_song_1.wav': 'Переключаю',
                'prev_song_2.wav': 'Хорошо, переключаю назад',
                'prev_song_3.wav': 'Переключаю назад',
                'prev_song_4.wav': 'Сейчас',
            }
        volume_lower = \
            {
                'vol_lower_1.wav': 'Хорошо',
                'vol_lower_2.wav': 'Принято',
                'vol_lower_3.wav': 'Поняла, сейчас',
                'vol_lower_4.wav': 'Сейчас убавлю'
            }
        volume_higher = \
            {
                'vol_higher_1.wav': 'Хорошо',
                'vol_higher_2.wav': 'Принято',
                'vol_higher_3.wav': 'Поняла, сейчас',
                'vol_higher_4.wav': 'Сейчас прибавлю'
            }
        pause = \
            {
                'pause_1.wav': 'Хорошо',
                'pause_2.wav': 'Ставлю на паузу',
                'pause_3.wav': 'Ага, поняла'

            }
        stop = \
            {
                'stop_1.wav': 'Выключаю музыку',
                'stop_2.wav': 'Процесс завершается',
                'stop_3.wav': 'Хорошо'
            }
        play = \
            {
                'play_1.wav': 'Хорошо, продолжаю',
                'play_2.wav': 'Продолжаю воспроизведение',
                'play_3.wav': 'Сейчас включу'
            }
        not_found = \
            {
                'music_not_found_1.wav': 'Музыка не найдена',
                'music_not_found_2.wav': 'Музыки не обнаружено, проигрывать нечего. Загрузите её в мою папку'
            }

    class Mqtt:
        """фразы: MQTT"""
        relay_connection_error = \
            {
                'mqtt_relay_connection_error_1.wav': 'Реле недоступно, интернет отсутствует',
                'mqtt_relay_connection_error_2.wav': 'Не могу переключить реле, интернета нет'
            }
        relay_ok = \
            {
                'relay_1.wav': 'Хорошо, статус реле изменён',
                'relay_2.wav': 'Я поменяла статус реле',
                'relay_3.wav': 'Ага, поняла'
            }
        low_temperature = \
            {
                'low_temperature_1.wav': 'Внимание, обнаружена низкая температура, включаю обогреватель',
                'low_temperature_2.wav': 'Очень холодно, включаю обогреватель'
            }
        high_temperature = \
            {
                'high_temperature_1.wav': 'Внимание, обнаружена высокая температура, выключаю обогреватель',
                'high_temperature_2.wav': 'Слишком жарко, выключаю обогреватель',
            }
        low_humidity = \
            {
                'low_humidity_1.wav': 'Внимание, обнаружена низкая влажность, включаю увлажнитель',
                'low_humidity_2.wav': 'Слишком сухо, включаю увлажнитель'
            }
        high_humidity = \
            {
                'high_humidity_1.wav': 'Внимание, обнаружена высокая влажность, выключаю увлажнитель',
                'high_humidity_2.wav': 'Похоже, я перестаралась с увлажнителем, выключаю'
            }
        high_CO2 = \
            {
                'high_CO2_1.wav': 'Внимание, обнаружено высокое содержание углекислого газа, включаю вентиляцию',
                'high_CO2_2.wav': 'Воздух очень грязный, пора бы и вентиляцию включить'
            }
        low_CO2 = \
            {
                'low_CO2_1.wav': 'Углекислый газ в пределах нормы, выключаю вентиляцию',
                'low_CO2_2.wav': 'Воздух хороший, в вентиляции не нуждается, выключаю'
            }
        high_pressure = \
            {
                'high_pressure_1.wav': 'Внимание, обнаружено высокое атмосферное давление, '
                                       'с которым я ничего сделать не могу',
                'high_pressure_2.wav': 'Вижу высокое атмосферное давление, метеозависимым людям может быть нехорошо'
            }
        low_pressure = \
            {
                'high_pressure_1.wav': 'Внимание, обнаружено низкое атмосферное давление, '
                                       'с которым я ничего сделать не могу',
                'high_pressure_2.wav': 'Вижу низкое атмосферное давление, метеозависимым людям может быть нехорошо'
            }

    class AppOpening:
        """фразы: приложения"""
        browser = \
            {
                'browser_1.wav': 'Открываю браузер',
                'browser_2.wav': 'Одну минутку'
            }
        terminal = \
            {
                'terminal_1.wav': 'Открываю терминал',
                'terminal_2.wav': 'Сейчас открою'
            }
        telegram = \
            {
                'telegram_1.wav': 'Открываю телеграм',
                'telegram_2.wav': 'Поняла, сейчас'
            }
        discord = \
            {
                'discord_1.wav': 'Открываю дискорд',
                'discord_2.wav': 'Дискорд открывается'
            }

    class BrowserSiteOpening:
        """фразы: браузер"""
        vk = \
            {
                'vk_1.wav': 'Открываю вконтакте',
                'vk_2.wav': 'Вконтакте открывается'
            }
        yandex = \
            {
                'yandex_1.wav': 'Открываю яндекс',
                'yandex_2.wav': 'Сейчас открою'
            }
        youtube = \
            {
                'youtube_1.wav': 'Открываю ютуб',
                'youtube_2.wav': 'Ютуб сейчас откроется'
            }
        user_search = \
            {
                'user_search_1.wav': 'Давайте поищем',
                'user_search_2.wav': 'Хорошо, сейчас найду'
            }

    class GUI:
        """фразы: графический интерфейс"""
        gui_open = \
            {
                'gui_open_1.wav': 'Открываю интерфейс',
                'gui_open_2.wav': 'Сейчас открою',
                'gui_open_3.wav': 'Графический интерфейс открывается'
            }
