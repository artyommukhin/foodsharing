# -*- coding: utf-8 -*-

from config import token, shelve_name, db_name 
import storage_worker
from db_worker import DBWorker
from classes import * #UserState, OfferInfo, State

import telebot
import requests
import time
import shelve
import json
import random
from datetime import datetime


rules = '''\
Фудшеринг - это хорошо
Правила:
1. Если вы хотите поделиться продуктами, нажмите "Поделиться" 
2. Если вы хотите забрать продукты, нажмите "Забрать"
3. Если вы хотите просмотреть список своих предложений, нажмите "Мои предложения"
'''

# Инициализация объекта бота
bot = telebot.TeleBot(token)

# Обработчик тестовой команды
@bot.message_handler(commands=['test'])
def test_message(message):
    # bot.send_location(message.chat.id, 56.018012, 92.868991)
    bot.send_message(message.chat.id, str(message))
    # uid = message.from_user.id
    # with shelve.open(shelve_name, flag='c') as db:
    #     print(db[str(uid)])
    

# Обработчик стартовой команды
@bot.message_handler(commands=['start'])
def start_message(message):
    
    uid = message.from_user.id

    # Сохранение пользователя в БД
    with DBWorker(db_name) as db:
        db.insert_user(uid)

    # Настройки клавиатуры
    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Правила', 'Мои предложения','Поделиться', 'Забрать')
    keyboard_main.resize_keyboard = True

    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, 'Привет! Добро пожаловать в мир рационального использования ресурсов\nВыбери действие', reply_markup=keyboard_main)


# Обработчик вызова помощи
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, rules)
    


# обработчик нажатия кнопки изменения названия предложения
@bot.callback_query_handler(func=lambda call: call.data == "input_offer_name")
def callback_inline(call):

    user = storage_worker.get_user(call.message.chat.id)
    user.state = State.ENTER_NAME
    user.last_info_msg_id = call.message.message_id
    storage_worker.save_user(user)

    bot.send_message(call.message.chat.id, "Введите название предложения")    

# обработчик ввода названия предложения
@bot.message_handler(func=lambda message: storage_worker.get_user(message.from_user.id).state == State.ENTER_NAME)
def enter_offer_name(message):
    offer_name = message.text
    if offer_name:
        
        uid = message.from_user.id
        user = storage_worker.get_user(uid)
        
        with DBWorker(db_name) as db:
            db.update_offer_name(user.cur_offer_id, offer_name)
        
        user.state = State.START
        storage_worker.save_user(user)

# Обработчик всех сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    cid = message.chat.id
    uid = message.from_user.id

    if message.text == 'Поделиться':

        user = storage_worker.get_user(uid)
 
        db = DBWorker(db_name)
        offer_id = db.insert_offer(uid)
        offer = db.select_offer(offer_id)
        user.cur_offer_id = offer_id 
        db.close()

        storage_worker.save_user(user)

        # with DBWorker(db_name) as db:
        #     db.select_all_offers_of_user(uid)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Добавить название", callback_data="input_offer_name")
        )

        bot.send_message(cid, make_offer_info_string(offer), reply_markup=keyboard)
        
        
    elif message.text == 'Забрать':
        markup_inline = telebot.types.InlineKeyboardMarkup()
        markup_inline.add(
            telebot.types.InlineKeyboardButton('Карта доноров (1)' ,  url = 'http://192.168.0.4/fsmap'), 
                # url='https://2gis.ru/krasnoyarsk/firm/986145966616730?m=92.797081%2C55.994433%2F16')
            telebot.types.InlineKeyboardButton('Карта доноров (2)' ,  url = 'http://192.168.0.3/fsmap') 
        )     
        bot.send_message(cid, 'Карта:', reply_markup=markup_inline)

    elif message.text == 'Правила':
        bot.send_message(message.chat.id, rules)

    elif message.text == 'Мои предложения':
        answer_str = 'Ваши предложения:\n'
        
        with DBWorker(db_name) as db:
            db.select_user_offers(uid)
                
        bot.send_message(cid, answer_str)
 
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю :(')





        
# обработчик ввода описания предложения
# @bot.message_handler(func=lambda message: storage_worker.get_user(message.from_user.id).state == State.ENTER_DESCRIPTION)
# def enter_offer_description(message):

#     uid = message.from_user.id

#     offer_id = storage_worker.get_user(uid).cur_offer_id


############################ Служебные функции ############################ 

def make_offer_info_string(offer: Offer):
    return f"Данные вашего предложения:\n{str(offer)}"






if __name__ == '__main__':
    bot.infinity_polling()