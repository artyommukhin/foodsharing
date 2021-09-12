# foodsharing telegram bot

v 0.1.0 (MVP)

## Установка

Для работы с данными нужно установить sqlite3, создать файл БД в папке *data*:

    sqlite3 database.db '.read db_export.sql'

Для работы карты нужно установить сервер nginx в map/nginx.  
Для запуска и остановки сервера используй скрипты в папке *map*

## Структура

- bot - вся логика бота
  - bot.py
  - db_worker.py
  - storage
- data - БД sqlite3, изначально там лежит скрипт для создания базы данных
- map - карта, для запуска нужен веб-сервер с PHP

## Использованные технологии

- python (telebot)
- sqlite3
- nginx
- php
- 2GIS API
