import config

import json
from enum import Enum

class UserState(Enum):
    START = 0
    ENTER_PRODUCT_NAME = 1
    

class User:
    'Класс, хранящий информацию о пользователе'
    def __init__(self, id, offers: list = []):
        # self.chat_id = chat_id
        self.id = id
        self.offers = offers

    def __str__(self):
        return f'user id:{self.id}\n{json.dumps(self.offers)}' 

class Offer:
    'Класс, хранящий информацию о предложении'
    def __init__(self, name: str, descr, date, coords: list):
        self.name = name
        self.date = date
        self.coords = coords

        self.id = random.getrandbits(16)
        self.status = "new"

        
    
    def __str__(self):
        return {
        'id': self.id,
        'name': 'Мясо',
        'desc': 'свежее',
        'time_to_pickup': str(datetime.now()),
        'marker': [1, 100], # lat, lon
        'address': 'Пушкина-колотушкина'
    }
    
# Нужно подумать...
# class UserStateInfo:

#     def __init__(self, user_id, offer_id, user_state):
#         self.user_id = user_id
#         self.offer_id = offer_id
#         self.user_state = user_state