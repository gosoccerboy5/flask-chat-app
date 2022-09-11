import sqlite3

connection = sqlite3.connect("user_data.db")
connection.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR, pwhash VARCHAR, bio VARCHAR);")
connection.commit()
connection.close()