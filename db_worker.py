import sqlite3

class DBWorker:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_all(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM offers').fetchall()

    def save_user(self, user_id):
        with self.connection:
            self.cursor.execute('INSERT INTO users (id, ) VALUES ()')