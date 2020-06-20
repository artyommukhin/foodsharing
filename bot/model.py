import config

import random
from enum import Enum

class State(Enum):
    START = 0
    ENTER_NAME = 1
    ENTER_DESCRIPTION = 2
    ENTER_COORDINATES = 3
    ENTER_PICKUP_DATE = 4
    

class UserState:
    'Класс, хранящий информацию о состоянии пользователя'
    def __init__(self, id, state=State.START, cur_offer_id=None, last_info_msg_id=None):
        self.id = id
        self.state = state
        self.cur_offer_id = cur_offer_id
        self.last_info_msg_id = last_info_msg_id
 
class User:
    'Класс для представления информации о пользователе из БД'
    def __init__(self, id, name, phone):
        self.id = id
        self.name = name
        self.phone = phone

class Offer:
    'Класс для представления информации о предложении из БД'
    def __init__(self, id, user_id, name: str, description, coordinates: tuple):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        # self.pickup_date = pickup_date
        self.coordinates = coordinates
        
    def __str__(self):
        return f"ID: {self.id}\nНазвание: {self.name}\nОписание: {self.description}\nКоординаты маркера: {self.coordinates}"
        