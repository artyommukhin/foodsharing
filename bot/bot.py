# -*- coding: utf-8 -*-
from config import token, shelve_name, db_name 
import storage_worker
from db_worker import DBWorker
from model import  State, UserState, User, Offer

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


rules = '''\
Фудшеринг - это хорошо
Правила:
1. Если вы хотите поделиться продуктами, нажмите "Поделиться" 
2. Если вы хотите забрать продукты, нажмите "Забрать"
3. Если вы хотите просмотреть список своих предложений, нажмите "Мои предложения"
'''

# Инициализация объекта бота
bot = telebot.TeleBot(token)

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
    keyboard_main.row('Правила')
    keyboard_main.row('Мои предложения','Поделиться')
    keyboard_main.row('Забрать')
    # keyboard_main.resize_keyboard = True

    reply = ('Привет! Добро пожаловать в мир рационального использования ресурсов!\n'
            'Выберите действие\n'
            '(Если вы здесь впервые, то вы прочтите правила)'
    )
    
    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, reply, reply_markup=keyboard_main)


# Обработчик вызова помощи
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, rules)
    

# обработчик нажатия callback-кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    user_id = chat_id = call.message.chat.id

    # обработчик нажатия кнопки изменения названия предложения
    if call.data == "input_offer_name":

        user = storage_worker.get_user_state(chat_id)
        user.state = State.ENTER_NAME
        user.last_info_msg_id = call.message.message_id
        storage_worker.save_user_state(user)

        bot.send_message(chat_id, "Введите название предложения" )    
    
    # обработчик нажатия кнопки изменения названия предложения
    elif call.data == "input_offer_description":

        user = storage_worker.get_user_state(chat_id)
        user.state = State.ENTER_DESCRIPTION
        user.last_info_msg_id = call.message.message_id
        storage_worker.save_user_state(user)

        bot.send_message(chat_id, "Введите описание предложения")   

    # обработчик нажатия кнопки изменения координат маркера предложения
    elif call.data == "input_offer_coordinates":

        user = storage_worker.get_user_state(chat_id)
        user.state = State.ENTER_COORDINATES
        user.last_info_msg_id = call.message.message_id
        storage_worker.save_user_state(user)

        bot.send_message(chat_id, "Отправьте координаты места, где будет размещено ваше предложение\n(Координаты можно отправить, нажав на скрепочку)") 
     

    # обработчик нажатия кнопки "Назад" после ввода данных предложения
    elif call.data == "back_to_offer":

        user = storage_worker.get_user_state(chat_id)
        user.last_info_msg_id = call.message.message_id
        offer_id = user.cur_offer_id
        storage_worker.save_user_state(user)

        send_offer_info_message(chat_id, offer_id) 

    # обработчик нажатия на предложение из списка
    elif call.data.startswith("show_offer"):

        offer_id = int(call.data[11:])
        
        user = storage_worker.get_user_state(user_id)
        
        user.cur_offer_id = offer_id

        message_id = user.last_info_msg_id
        user.last_info_msg_id = None
        
        storage_worker.save_user_state(user)

        # удаление старого информационного сообщения
        if message_id:
            bot.delete_message(chat_id, message_id)

        send_offer_info_message(chat_id, offer_id)

    # обработчик нажатия на предложение из списка
    elif call.data == "create_new_offer":

        offer_id = create_new_offer(chat_id)

        send_offer_info_message(chat_id, offer_id)

    elif call.data.startswith("delete_offer:"):

        offer_id = int(call.data[13:])

        user = storage_worker.get_user_state(user_id)
        
        user.cur_offer_id = None

        with DBWorker(db_name) as db:
            db.delete_offer(offer_id)
        
        bot.send_message(chat_id, f"Предложение №{offer_id}  успешно удалено")
    

# обработчик ввода информации о предложении
@bot.message_handler(func=lambda message: storage_worker.get_user_state(message.from_user.id).state != State.START, content_types=['text','location'])
def enter_offer_info(message):
     
    user_id = chat_id = message.chat.id
    user = storage_worker.get_user_state(user_id)
    
    if user.state == State.ENTER_NAME and message.text:
        offer_name = message.text
        with DBWorker(db_name) as db:
            db.update_offer_name(user.cur_offer_id, offer_name)

    elif user.state == State.ENTER_DESCRIPTION and message.text:
        offer_description = message.text
        with DBWorker(db_name) as db:
            db.update_offer_description(user.cur_offer_id, offer_description)
    
    elif user.state == State.ENTER_COORDINATES and message.location:
        offer_coordinates = message.location
        with DBWorker(db_name) as db:
            db.update_offer_coordinates(user.cur_offer_id, (offer_coordinates.latitude, offer_coordinates.longitude))
    else:
        bot.send_message(chat_id, 'Введите корректные данные')
        return
    user.state = State.START
    storage_worker.save_user_state(user)

    # Обновление информации в последнем информационном сообщении
    refresh_offer_info_message(message.chat.id, user.cur_offer_id, user.last_info_msg_id)

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("Вернуться к предложению", callback_data="back_to_offer")
    )
    bot.send_message(message.chat.id, "Принято!", reply_markup=keyboard)


# Обработчик всех текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):

    user_id = chat_id = message.chat.id

    if message.text == 'Поделиться':

        offer_id = create_new_offer(user_id)

        send_offer_info_message(chat_id, offer_id)
        
        
    elif message.text == 'Забрать':
        markup_inline = telebot.types.InlineKeyboardMarkup()
        markup_inline.add(
            telebot.types.InlineKeyboardButton('Карта доноров (1)' ,  url = 'http://192.168.0.4/fsmap'), 
                # url='https://2gis.ru/krasnoyarsk/firm/986145966616730?m=92.797081%2C55.994433%2F16')
            telebot.types.InlineKeyboardButton('Карта доноров (2)' ,  url = 'http://192.168.0.3/fsmap') 
        )     
        bot.send_message(chat_id, 'Карта:', reply_markup=markup_inline)

    elif message.text == 'Правила':
        bot.send_message(message.chat.id, rules)

    elif message.text == 'Мои предложения':
        
        offers = []
        with DBWorker(db_name) as db:
            offers = db.select_all_offers_of_user(user_id)

        if offers:
            keyboard = telebot.types.InlineKeyboardMarkup()
            for offer in offers:
                keyboard.add(telebot.types.InlineKeyboardButton(f"{offer.id}, {offer.name}", callback_data=f"show_offer:{offer.id}"))
            bot.send_message(chat_id, "Ваши предложения:", reply_markup=keyboard)

        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(
                telebot.types.InlineKeyboardButton("Создать новое", callback_data='create_new_offer')
            )
            bot.send_message(chat_id, 'У вас нет предложений', reply_markup=keyboard)
 
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю :(')


############################ Служебные функции ############################ 

def make_offer_info_string(offer_id):
    with DBWorker(db_name) as db:
        offer = db.select_offer(offer_id)
        if offer:
            return f"Данные вашего предложения:\n{str(offer)}"
        return 'Нет информации'

def make_offer_info_keyboard(offer_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="Добавить название", callback_data="input_offer_name"),
        InlineKeyboardButton(text="Добавить описание", callback_data="input_offer_description"),
        InlineKeyboardButton(text="Разместить на карте", callback_data="input_offer_coordinates"),
        InlineKeyboardButton(text="Удалить", callback_data=f"delete_offer:{offer_id}")
    )
    return keyboard

def send_offer_info_message(chat_id, offer_id):
    bot.send_message(
        chat_id, 
        make_offer_info_string(offer_id),
        reply_markup=make_offer_info_keyboard(offer_id)
    )

def refresh_offer_info_message(chat_id, offer_id, message_id):
    bot.edit_message_text(
        make_offer_info_string(offer_id),
        chat_id,
        message_id,
        reply_markup=make_offer_info_keyboard(offer_id)
    )

def make_back_button_markup():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data="back")
    )

def make_back_button_keyboard():
    keyboard = ReplyKeyboardMarkup()
    keyboard.add(
        KeyboardButton("Отмена")
    )

def create_new_offer(user_id):

    user = storage_worker.get_user_state(user_id)
    # Создание нового предложения
    with DBWorker(db_name) as db:
        user.cur_offer_id = db.insert_offer(user_id)
    storage_worker.save_user_state(user)

    return user.cur_offer_id

if __name__ == '__main__':
    bot.infinity_polling()