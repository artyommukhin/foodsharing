import sqlite3
import sys
import random

from classes import User, Offer

class DBWorker:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self
    
    def __exit__(self, exit, value, exc):   
        self.close()


    def select_all_offers(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM offers').fetchall()

    def select_offer(self, offer_id):
        with self.connection:
            return self._row_to_offer(self.cursor.execute('SELECT * FROM offers WHERE id=?', (offer_id,)).fetchone())    

    def select_user_offers(self, user_id):
        with self.connection:
            return self.cursor.execute('SELECT * FROM offers WHERE user_id=?', (user_id,)).fetchall()

    def insert_user(self, user_id):
        try:
            with self.connection:
                self.cursor.execute('INSERT INTO users (id) VALUES (?)', (user_id,))
        except sqlite3.IntegrityError:
            print(sys.exc_info()[1])

    def insert_offer(self, user_id):
        offer_id = random.getrandbits(16)
        with self.connection:
            self.cursor.execute('INSERT INTO offers (id, user_id) VALUES (?, ?)', (offer_id, user_id))
            return offer_id

    def update_offer(self, offer_id):
        with self.connection:
            self.cursor.execute('UPDATE offers SET ...=? WHERE id=?', (data, offer_id))

    def update_user_phone(self, user_id, phone):
        with self.connection:
            self.cursor.execute('UPDATE users SET phone=? WHERE id=?', (phone, user_id))

    def close(self):
        self.connection.close()

    @staticmethod
    def _row_to_user(row):
        return User(row[0], row[1], row[2])
    
    @staticmethod
    def _row_to_offer(row):
        return Offer(row[0], row[1], )

