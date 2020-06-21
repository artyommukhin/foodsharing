# -*- coding: utf-8 -*-
from config import token, shelve_name, db_name 
import storage_worker
from db_worker import DBWorker
from model import  State, UserState, User, Offer

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import sys


rules = '''\
Фудшеринг - это хорошо
Правила:
1. Если вы хотите поделиться продуктами, нажмите "Поделиться" 
2. Если вы хотите забрать продукты, нажмите "Забрать"
3. Если вы хотите просмотреть список своих предложений, нажмите "Мои предложения"
'''

# Инициализация объекта бота
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(message.chat.id, "[Настя](tg://user?id=379247899)", parse_mode="Markdown")

# Обработчик стартовой команды
@bot.message_handler(commands=['start'])
def start_message(message):
    
    uid = message.from_user.id
    username = message.from_user.username

    # Сохранение пользователя в БД
    with DBWorker(db_name) as db:
        db.insert_user(uid)
        if username:
            db.update_user_name(uid, username)

    # Сохранение пользователя в хранилище
    storage_worker.save_user_state(UserState(uid))

    reply = ('Привет! Добро пожаловать в мир рационального использования ресурсов!\n'
            'Выберите действие\n'
            '(Если вы здесь впервые, то вы прочтите правила)'
    )
    
    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, reply, reply_markup=make_main_keyboard())


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

        bot.send_message(chat_id, "Введите название предложения", reply_markup=make_cancel_button_keyboard())    
    
    # обработчик нажатия кнопки изменения названия предложения
    elif call.data == "input_offer_description":

        user = storage_worker.get_user_state(chat_id)
        user.state = State.ENTER_DESCRIPTION
        user.last_info_msg_id = call.message.message_id
        storage_worker.save_user_state(user)

        bot.send_message(chat_id, "Введите описание предложения", reply_markup=make_cancel_button_keyboard())   
        
    # обработчик нажатия кнопки изменения координат маркера предложения
    elif call.data == "input_offer_coordinates":

        user = storage_worker.get_user_state(chat_id)
        
        if not is_offer_ready(user.cur_offer_id):
            bot.send_message(chat_id, "Невозможно разместить предложение на карте\nНедостаточно информации о предложении") 
            return

        with DBWorker(db_name) as db:
            username = db.select_user_name(user_id)
            phone = db.select_user_phone(user_id)
            if not (username or phone):
                user.state = State.ENTER_CONTACT
                storage_worker.save_user_state(user)
                keyboard = ReplyKeyboardMarkup()
                keyboard.add(KeyboardButton('Отправить телефон',request_contact=True))
                keyboard.resize_keyboard = True
                bot.send_message(chat_id, 'Для связи с вами необходим телефон', reply_markup=keyboard)
                return               
        
        user.state = State.ENTER_COORDINATES
        user.last_info_msg_id = call.message.message_id
        storage_worker.save_user_state(user)
   
        bot.send_message(chat_id, "Отправьте координаты места, где будет размещено ваше предложение\n(Координаты можно отправить, нажав на скрепочку и выбрав местоположение)",
            reply_markup=make_cancel_button_keyboard()) 


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

        # удаление старого информационного сообщения
        message_id = user.last_info_msg_id
        if message_id:
            bot.delete_message(chat_id, message_id)

        # отправка нового информационного сообщения
        reply = send_offer_info_message(chat_id, offer_id)

        # сохранение нового информационного сообщения
        user.last_info_msg_id = reply.message_id
        storage_worker.save_user_state(user)

    # обработчик нажатия на предложение из списка
    elif call.data == "create_new_offer":

        offer_id = create_new_offer(chat_id)

        user = storage_worker.get_user_state(user_id)
        user.cur_offer_id = offer_id
        storage_worker.save_user_state(user)

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
    
    if message.text == 'Отмена':
        user.state = State.START
        storage_worker.save_user_state(user)
        bot.send_message(chat_id, 'Ввод отменён', reply_markup=make_main_keyboard())
        return

    elif user.state == State.ENTER_NAME and message.text:
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
            
   
    elif user.state == State.ENTER_CONTACT and message.contact:
        
        user_phone = message.contact.phone_number
        with DBWorker(db_name) as db:
            db.update_user_phone(user_id, user_phone)
        user.state = State.ENTER_COORDINATES
        storage_worker.save_user_state(user)

        bot.send_message(chat_id, "Отправьте координаты места, где будет размещено ваше предложение\n(Координаты можно отправить, нажав на скрепочку и выбрав местоположение)",
            reply_markup=make_cancel_button_keyboard()) 

    else:

        bot.send_message(chat_id, 'Введите корректные данные')
        return
    
    user.state = State.START
    storage_worker.save_user_state(user)

    # Обновление информации в последнем информационном сообщении
    refresh_offer_info_message(message.chat.id, user.cur_offer_id, user.last_info_msg_id)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Вернуться к предложению", callback_data="back_to_offer")
    )
    bot.send_message(message.chat.id, "Принято!", reply_markup=keyboard)


# Обработчик всех остальных сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):

    user_id = chat_id = message.chat.id

    if message.text == 'Поделиться':
        
        offer_id = create_new_offer(user_id)

        user = storage_worker.get_user_state(user_id)
        user.cur_offer_id = offer_id
        storage_worker.save_user_state(user)

        send_offer_info_message(chat_id, offer_id)
        
        
    elif message.text == 'Забрать':

        markup_inline = InlineKeyboardMarkup()
        markup_inline.add(
            InlineKeyboardButton('Открыть карту' ,  url = 'http://192.168.0.4') 
        )     
        bot.send_message(chat_id, 'Ссылка на карту:', reply_markup=markup_inline)

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
def make_main_keyboard():
    keyboard_main = ReplyKeyboardMarkup()
    keyboard_main.row('Правила')
    keyboard_main.row('Мои предложения','Поделиться')
    keyboard_main.row('Забрать')
    return keyboard_main

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
    reply = bot.send_message(
        chat_id, 
        make_offer_info_string(offer_id),
        reply_markup=make_offer_info_keyboard(offer_id)
    )
    return reply

def refresh_offer_info_message(chat_id, offer_id, message_id):
    try:
        bot.edit_message_text(
            make_offer_info_string(offer_id),
            chat_id,
            message_id,
            reply_markup=make_offer_info_keyboard(offer_id)
        )
    except telebot.apihelper.ApiException:
        print(sys.exc_info()[1]) 

def make_back_button_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data="back")
    )

def make_cancel_button_keyboard():
    keyboard = ReplyKeyboardMarkup()
    keyboard.row("Отмена")    
    keyboard.resize_keyboard = True
    return keyboard

def create_new_offer(user_id):

    with DBWorker(db_name) as db: 
        offer_id = db.insert_offer(user_id)

    return offer_id 

def is_offer_ready(offer_id):
    with DBWorker(db_name) as db:
        return db.select_offer_is_ready(offer_id)

if __name__ == '__main__':
    bot.infinity_polling()