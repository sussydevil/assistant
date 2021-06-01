#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# extended version
import sqlite3
import logging

# файл базы данных
db_path = "data.db"


class Sqlite:
    """класс для работы с базой данных"""
    @staticmethod
    def create_database():
        """создание базы данных, если её не существует"""
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        sql_create_script = "CREATE TABLE IF NOT EXISTS Day(Timestamp Integer, Temperature REAL, " \
                            "Humidity REAL, Pressure REAL, CO2 REAL);"
        cursor.execute(sql_create_script)
        connection.commit()
        connection.close()
        logging.info('Database -> ok')
        return 0

    @staticmethod
    def write_data(timestamp, temperature, humidity, pressure, co2):
        """запись данных с датчиков в базу данных"""
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Day Values (?,?,?,?,?);",
                       (timestamp, temperature, humidity, pressure, co2))
        connection.commit()
        connection.close()
        logging.info('Database row writing -> ok')
        return 0

    @staticmethod
    def read_last():
        """чтение последней строчки из базы данных"""
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Day WHERE rowid = (SELECT MAX(rowid) FROM Day);")
        logging.info('Database row reading -> ok')
        return cursor.fetchone()

    @staticmethod
    def read_last_n_rows(n_rows):
        """чтение последних N строчек из базы данных"""
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM (SELECT * FROM Day ORDER BY rowid ASC LIMIT {0}) ORDER BY rowid DESC;"
                       .format(n_rows))
        logging.info('Database row array reading -> ok')
        return cursor.fetchall()
