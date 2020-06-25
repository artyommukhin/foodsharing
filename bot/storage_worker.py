from config import shelve_name
from model import State, UserState

import shelve

def save_user_state(user: UserState):
    'Функция для сохранения состояния пользователя'
    with shelve.open(shelve_name, flag='c') as storage:
        storage[str(user.id)] = user
    


def get_user_state(user_id):
    'Функция для получения текущего состояния пользователя'
    with shelve.open(shelve_name, flag='r') as storage:
        if str(user_id) in storage:
            return storage[str(user_id)]
    return UserState(user_id)
