import sqlite3

connection = sqlite3.connect("user_data.db")
connection.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR, pwhash VARCHAR, bio VARCHAR);")
connection.commit()
connection.close()

connection = sqlite3.connect("channel_data.db")
connection.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY, name TEXT, founder TEXT);")
connection.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, channel INTEGER, content TEXT, author TEXT, date TEXT);")
connection.commit()
connection.close()

"""SCHEMA
  users:
username pwhash bio

  channels:
id name founder

  comments:
id channel content author date
"""