from flask import Flask, g
import sqlite3

class DataBase:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.DATABASE = 'database.db'
        self.init_db()

    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(self.DATABASE)
        return db

    def init_db(self):
        if not os.path.exists(self.DATABASE):
            with self.app.app_context():
                db = self.get_db()
                try:
                    with self.app.open_resource('database.sql', mode='r') as f:
                        db.cursor().executescript(f.read())
                    db.commit()
                    print(f"Database '{self.DATABASE}' created successfully.")
                except FileNotFoundError:
                    print("Error: 'database.sql' file not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")
        else:
            print(f"Database '{self.DATABASE}' already exists.")