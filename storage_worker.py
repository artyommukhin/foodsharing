from config import shelve_name
from classes import State, UserState

import shelve

def save_user(user: UserState):
    with shelve.open(shelve_name, flag='c') as storage:
        storage[str(user.id)] = user


def get_user(user_id):
    with shelve.open(shelve_name, flag='r') as storage:
        if str(user_id) in storage:
            return storage[str(user_id)]
    return UserState(user_id)
