import random, string, json, hashlib, re, os, sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
from flask_sock import Sock
import tables

def get_date():
  return re.sub(r"\.\d+.*$", " UTC", str(datetime.now(timezone.utc)))

def sha256(text):
  return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_user_data(username=None):
  connection = sqlite3.connect("user_data.db")
  user_data = None
  if username is not None:
    user_data = connection.execute("SELECT * FROM users WHERE username = ?;", (username, )).fetchone()
  else:
    user_data = connection.execute("SELECT * FROM users;").fetchall()
  connection.close()
  return user_data
  
def get_channel_data(id):
  id = str(id)
  connection = sqlite3.connect("channel_data.db")
  channel_data = connection.execute("SELECT ch.id, ch.name, co.content, co.date, co.author, co.id AS commentid FROM channels ch JOIN comments co ON ch.id = co.channel WHERE ch.id = ?;", (id, )).fetchall()
  connection.close()
  return channel_data

def verify_user(username, hash):
  data = get_user_data(username)
  return data is not None and data[1] == hash

app = Flask(  # Create a flask app
	__name__,
	template_folder='templates',  # Name of html file folder
	static_folder='static'  # Name of directory for static files
)

socket = Sock(app)
sockets = []

@socket.route("/channelws")
def channelws(sock):
  do_run = True
  
  md = json.loads(sock.receive()) #metadata
  mypair = (sock, {"channel": md["channel"]})
  sockets.append(mypair)

  if not verify_user(md["username"] or "", sha256(md["password"] or "")):
    do_run = False
  
  while True:
    try:
      data = json.loads(sock.receive())
      if not do_run:
        continue
      data["date"] = get_date()
      post_message(data, md["channel"])
      data = json.dumps(data)
      for pair in sockets:
        if pair[1]["channel"] == md["channel"]:
          pair[0].send(data)
    except Exception as e:
      print(e)
      sockets.remove(mypair)
      return
      
def post_message(msg, channel):
  connection = sqlite3.connect("channel_data.db")
  count = int(connection.execute("SELECT COUNT(*) FROM comments;").fetchone()[0])
  connection.execute("INSERT INTO comments VALUES (?, ?, ?, ?, ?);", (str(count+1), str(channel), msg["content"], msg["username"], get_date()))
  connection.commit()
  connection.close()

ok_chars = string.ascii_letters + string.digits

@app.get('/')  # What happens when the user visits the site
def base_page():
  return render_template('base.html')

@app.get('/signin')
def signinpage():
  return render_template('signin.html')

@app.get('/channels')
def channels_sorted():
  connection = sqlite3.connect("channel_data.db")
  data = connection.execute("SELECT * FROM channels").fetchall()
  data = [{"id": row[0], "name": row[1], "founder": row[2]} for row in data]
  connection.close()
  return jsonify(data)

@app.get('/messages/<id>')
def messages(id):
  data = get_channel_data(id)
  c = sqlite3.connect("channel_data.db")
  title = c.execute("SELECT name FROM channels WHERE id = ?", (id, )).fetchone()[0]
  c.close()
  return {"title": title, "messages": [{"username": row[4], "content": row[2], "date": row[3]} for row in data]}

@app.get('/channel/<channel>')
def get_channel(channel):
  return render_template("channel.html")

@app.route('/createchannel', methods=['GET', 'POST'])
def createchannel():
  if request.method == 'GET':
    return render_template('create_channel.html')
  rq_json = request.get_json()
  title = rq_json["title"].strip()
  if len(title) == 0:
    return jsonify({"status": "Error", "message": "Error: must have a title"})
  username = rq_json["username"]
  pw = rq_json["password"]
  user_data = get_user_data(username)
  if user_data == None:
    return jsonify({"status": "Error", "message": "Error: not signed in or user not found"})
  if sha256(pw) != user_data[1]:
    return jsonify({"status": "Error", "message": "Error: Password incorrect, cannot verify user"})

  connection = sqlite3.connect("channel_data.db")
  ids = [row[0] for row in connection.execute("SELECT id FROM channels;").fetchall()]
  id = str(random.randint(0, 100000))
  while id in ids:
    id = str(random.randint(0, 100000))
  connection.execute("INSERT INTO channels VALUES (?, ?, ?);", (id, title, username))
  connection.commit()
  connection.close()
  
  return jsonify({"status": "Success", "message": id})

@app.post('/login')
def login():
  rq_json = request.get_json()
  login_data = get_user_data(rq_json["username"])
  if login_data == None:
    return "Error: Login failure: username not found"
  if sha256(rq_json["password"]) != login_data[1]:
    return "Error: Login failure: password incorrect"
  return "Success"

@app.post('/signup')
def signup():
  signup_data = request.get_json()
  username = signup_data["username"]
  password = signup_data["password"]
  if get_user_data(username) is not None:
    return "Error: Signup failure: username already exists"
  if not re.compile("^[\w-]{3,20}$").fullmatch(username):
    return "Error: Signup failure: username not valid (must consist of letters, numbers, - and _ and must be between 3 and 20 characters"
  connection = sqlite3.connect("user_data.db")
  connection.execute("INSERT INTO users VALUES (?, ?, '');", (username, sha256(password)))
  connection.commit()
  connection.close()
  return "Success"

@app.get('/settings')
def settingspage():
  return render_template('settings.html')

@app.get('/user_data')
def get_individual_data():
  data = get_user_data(request.args["user"])
  if data == None:
    return jsonify({})
  return jsonify({
    "bio": data[2]
  })

@app.get('/profile')
def profile():
  name = request.args["user"]
  data = get_user_data(name)
  if data == None:
    return "User not found"
  return render_template('profile.html', username=name, bio=data[2] if data[2] != "" else "None given.")

@app.post('/set_settings')
def set_settings():
  rq_json = request.get_json()
  username = rq_json["username"]
  pwhash = sha256(rq_json["password"])
  bio = rq_json["bio"]

  if get_user_data(username) == None:
    return "Error: username does not exist"
  if get_user_data(username)[1] != pwhash:
    return "Error: password incorrect (cannot verify profile)"
  connection = sqlite3.connect("user_data.db")
  connection.execute("UPDATE users SET bio = ? WHERE username = ?", (bio, username))
  connection.commit()
  connection.close()
  return "Success"
  
if __name__ == "__main__":  # Makes sure this is the main process
	app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
	)