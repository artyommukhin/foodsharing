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
    def __init__(self, id, state=State.START, cur_offer_id=None):
        self.id = id
        self.state = state
        self.cur_offer_id = cur_offer_id
 
class User:
    'Класс для представления информации о пользователе из БД'
    def __init__(self, id, name, phone):
        self.id = id
        self.name = name
        self.phone = phone

class Offer:
    'Класс для представления информации о предложении из БД'
    def __init__(self, id, user_id, name: str, descr, pickup_date, coords: tuple):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.pickup_date = pickup_date
        self.coords = coords

        self.id = random.getrandbits(16)

        
    
    # def __str__(self):
    #     return {
    #     'id': self.id,
    #     'name': 'Мясо',
    #     'desc': 'свежее',
    #     'time_to_pickup': str(datetime.now()),
    #     'marker': [1, 100], # lat, lon
    #     'address': 'Пушкина-колотушкина'
    # }
    
# Нужно подумать...
# class UserStorageInfo:

#      def __init__(self, offer_id, state):
#         #  self.user_id = user_id
#          self.offer_id = offer_id
#          self.state = state