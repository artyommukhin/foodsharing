from model import User, Offer

import sqlite3
import sys
import random

class DBWorker:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self
    
    def __exit__(self, exit, value, exc):   
        self.close()

    def close(self):
        self.connection.close()

    ############################## users ##############################
    def select_user_name(self, user_id):
        with self.connection:
            username = self.cursor.execute('SELECT name FROM users WHERE id=?', (user_id,)).fetchone()
            if username == (None,):
                return None
            return username

    def select_user_phone(self, user_id):
        with self.connection:
            phone = self.cursor.execute('SELECT phone FROM users WHERE id=?', (user_id,)).fetchone()
            if phone == (None,):
                return None
            return phone

    def select_offer_is_ready(self, offer_id):
        with self.connection:
            return bool(self.cursor.execute('SELECT is_ready FROM offers WHERE id=?', (offer_id,)).fetchone())

    def insert_user(self, user_id):
        try:
            with self.connection:
                self.cursor.execute('INSERT INTO users (id) VALUES (?)', (user_id,))
        except sqlite3.IntegrityError:
            print(sys.exc_info()[1])

    def update_user_name(self, user_id, name):
        with self.connection:
            self.cursor.execute('UPDATE users SET name=? WHERE id=?', (name, user_id))

    def update_user_phone(self, user_id, phone):
        with self.connection:
            self.cursor.execute('UPDATE users SET phone=? WHERE id=?', (phone, user_id))

    ############################## offers ##############################
    def select_all_offers_of_user(self, user_id):
        with self.connection:
            rows = self.cursor.execute('SELECT * FROM offers WHERE user_id=?',(user_id,)).fetchall()
            offers = []
            for row in rows:
                offers.append(self._row_to_offer(row))
            return offers

    def select_offer(self, offer_id):
        with self.connection:
            return self._row_to_offer(self.cursor.execute('SELECT * FROM offers WHERE id=?', (offer_id,)).fetchone())  

    def insert_offer(self, user_id):
        offer_id = random.getrandbits(16)
        with self.connection:
            self.cursor.execute('INSERT INTO offers (id, user_id) VALUES (?, ?)', (offer_id, user_id))
            return offer_id

    def update_offer_name(self, offer_id, name):
        with self.connection:
            self.cursor.execute('UPDATE offers SET name=? WHERE id=?', (name, offer_id))
            
    def update_offer_description(self, offer_id, description):
        with self.connection:
            self.cursor.execute('UPDATE offers SET description=? WHERE id=?', (description, offer_id))

    def update_offer_coordinates(self, offer_id, coordinates: tuple):
        "coordinates (lat, long)"
        (lat, long) = coordinates
        with self.connection:
            self.cursor.execute('UPDATE offers SET marker_latitude=?, marker_longitude=? WHERE id=?', (lat, long, offer_id))

    def delete_offer(self, offer_id):
        with self.connection:
            self.cursor.execute('DELETE FROM offers WhERE id=?', (offer_id,))


    @staticmethod
    def _row_to_user(row):
        if row:
            return User(row[0], row[1], row[2])
    
    @staticmethod
    def _row_to_offer(row):
        if row:
            return Offer(row[0], row[1], row[2], row[3], (row[4],row[5]))