# -*- coding: utf-8 -*-

from config import token, shelve_name, db_name 
import storage_worker
from db_worker import DBWorker
from classes import  State, UserState, User, Offer

import telebot


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

    # Сохранение пользователя в хранилище
    storage_worker.save_user_state(UserState(uid))

    # Настройки клавиатуры
    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Правила', 'Мои предложения','Поделиться', 'Забрать')
    keyboard_main.resize_keyboard = True

    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, 'Привет! Добро пожаловать в мир рационального использования ресурсов\nВыберите действие', reply_markup=keyboard_main)


# Обработчик вызова помощи
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, rules)
    

# обработчик нажатия callback-кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # обработчик нажатия кнопки изменения названия предложения
    if call.data == "input_offer_name":

        user = storage_worker.get_user_state(call.message.chat.id)
        user.state = State.ENTER_NAME
        user.last_info_msg_id = call.message.message_id
        storage_worker.save_user_state(user)

        bot.send_message(call.message.chat.id, "Введите название предложения")    
    
    # обработчик нажатия кнопки изменения названия предложения
    elif call.data == "input_offer_description":

        user = storage_worker.get_user_state(call.message.chat.id)
        user.state = State.ENTER_DESCRIPTION
        user.last_info_msg_id = call.message.message_id
        storage_worker.save_user_state(user)

        bot.send_message(call.message.chat.id, "Введите описание предложения")   

    # обработчик нажатия кнопки изменения координат маркера предложения
    elif call.data == "input_offer_coordinates":

        user = storage_worker.get_user_state(call.message.chat.id)
        user.state = State.ENTER_COORDINATES
        user.last_info_msg_id = call.message.message_id
        storage_worker.save_user_state(user)

        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.add(
            telebot.types.KeyboardButton("Отправить местоположение", request_location=True)
        )

        bot.send_message(call.message.chat.id, "Отправьте координаты места, где будет размещено ваше предложение", reply_markup=keyboard) 
     

    # обработчик нажатия кнопки "Назад" после ввода названия предложения
    elif call.data == "back_to_offer":

        user = storage_worker.get_user_state(call.message.chat.id)
        user.last_info_msg_id = call.message.message_id
        offer_id = user.cur_offer_id
        storage_worker.save_user_state(user)

        send_offer_info_message(call.message.chat.id, offer_id) 



    

# обработчик ввода названия предложения
@bot.message_handler(func=lambda message: storage_worker.get_user_state(message.from_user.id).state == State.ENTER_NAME)
def enter_offer_name(message):
    offer_name = message.text
    if offer_name:
        
        uid = message.from_user.id
        user = storage_worker.get_user_state(uid)
        
        with DBWorker(db_name) as db:
            db.update_offer_name(user.cur_offer_id, offer_name)
        
        user.state = State.START
        storage_worker.save_user_state(user)

        # Обновление информации в последнем информационном сообщении
        bot.edit_message_text(make_offer_info_string(user.cur_offer_id), message.chat.id, user.last_info_msg_id)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton("Вернуться к предложению", callback_data="back_to_offer")
        )
        bot.send_message(message.chat.id, "Принято!", reply_markup=keyboard)


# обработчик ввода описания предложения
@bot.message_handler(func=lambda message: storage_worker.get_user_state(message.from_user.id).state == State.ENTER_DESCRIPTION)
def enter_offer_description(message):
    offer_description = message.text
    if offer_description:
        
        uid = message.from_user.id
        user = storage_worker.get_user_state(uid)
        
        with DBWorker(db_name) as db:
            db.update_offer_description(user.cur_offer_id, offer_description)
        
        user.state = State.START
        storage_worker.save_user_state(user)

        # Обновление информации в последнем информационном сообщении
        bot.edit_message_text(make_offer_info_string(user.cur_offer_id), message.chat.id, user.last_info_msg_id)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton("Вернуться к предложению", callback_data="back_to_offer")
        )
        bot.send_message(message.chat.id, "Принято!", reply_markup=keyboard)

# обработчик ввода описания предложения
@bot.message_handler(func=lambda message: storage_worker.get_user_state(message.from_user.id).state == State.ENTER_COORDINATES, content_types=["location"])
def enter_offer_coordinates(message):
    offer_coordinates = message.location
    if offer_coordinates:
        
        uid = message.from_user.id
        user = storage_worker.get_user_state(uid)

        with DBWorker(db_name) as db:
            db.update_offer_coordinates(user.cur_offer_id, (offer_coordinates.latitude, offer_coordinates.longitude))
        
        user.state = State.START
        storage_worker.save_user_state(user)

        # Обновление информации в последнем информационном сообщении
        bot.edit_message_text(make_offer_info_string(user.cur_offer_id), message.chat.id, user.last_info_msg_id)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton("Вернуться к предложению", callback_data="back_to_offer")
        )
        bot.send_message(message.chat.id, "Принято!", reply_markup=keyboard)


# Обработчик всех сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    cid = message.chat.id
    uid = message.from_user.id

    if message.text == 'Поделиться':

        user = storage_worker.get_user_state(uid)

        # Создание нового предложения
        with DBWorker(db_name) as db:
            user.cur_offer_id = db.insert_offer(uid)

        storage_worker.save_user_state(user)

        send_offer_info_message(cid, user.cur_offer_id)
        
        
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
        
        offers = []
        with DBWorker(db_name) as db:
            offers = db.select_all_offers_of_user(uid)

        keyboard = telebot.types.InlineKeyboardMarkup()
        for offer in offers:
            keyboard.add(telebot.types.InlineKeyboardButton(f"{offer.id}, {offer.name}", callback_data=f"show_offer:{offer.id}"))

        bot.send_message(cid, "Ваши предложения:", reply_markup=keyboard)
 
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю :(')





############################ Служебные функции ############################ 

def make_offer_info_string(offer_id):
    with DBWorker(db_name) as db:
        offer = db.select_offer(offer_id)
        return f"Данные вашего предложения:\n{str(offer)}"

def make_offer_info_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        telebot.types.InlineKeyboardButton(text="Добавить название", callback_data="input_offer_name"),
        telebot.types.InlineKeyboardButton(text="Добавить описание", callback_data="input_offer_description"),
        telebot.types.InlineKeyboardButton(text="Разместить на карте", callback_data="input_offer_coordinates")
    )
    return keyboard

def send_offer_info_message(chat_id, offer_id):
    bot.send_message(
        chat_id, 
        make_offer_info_string(offer_id),
        reply_markup=make_offer_info_keyboard()
    )

def show_offer_from_callback(callback_data):
    pass


if __name__ == '__main__':
    bot.infinity_polling()