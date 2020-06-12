from config import shelve_name
from classes import UserState, User, Offer

import shelve


def save_user(user_id):
    with shelve.open(shelve_name, flag='c') as db:
        if not str(user_id) in db:
            db[str(user_id)] = User(user_id)
        


def get_state(user_id):
    with shelve.open(shelve_name, flag='r') as db:
        if str(user_id) in db:
            return db[str(user_id)].state

        return UserState.START