import random, string, json, hashlib, re
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone

def get_date():
  return re.sub(r"\.\d+.*$", " UTC", str(datetime.now(timezone.utc)))
  
def sha256(text):
  return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_user_data():
  file = open("user_data.json")
  data = json.loads(file.read())
  file.close()
  return data
  
def get_channel_data():
  file = open("channels.json")
  data = json.loads(file.read())
  file.close()
  return data

app = Flask(  # Create a flask app
	__name__,
	template_folder='templates',  # Name of html file folder
	static_folder='static'  # Name of directory for static files
)

ok_chars = string.ascii_letters + string.digits

@app.route('/', methods=['GET', 'POST'])  # What happens when the user visits the site
def base_page():
  return render_template('base.html')

@app.route('/signin')
def signinpage():
  return render_template('signin.html')

@app.route('/channels')
def channels_sorted():
  channels = get_channel_data()
  res = []
  for key, value in channels.items():
    last_post = value["messages"][-1] if len(value["messages"]) > 0 else None
    res.append({
      "name": value["name"],
      "id": key,
      "last_post": last_post
    })
  return jsonify(res)

@app.route('/messages/<id>', methods=['GET', 'POST'])
def messages(id):
  all_channel_data = get_channel_data()
  channel_data = all_channel_data[id]
  return jsonify(channel_data["messages"])

@app.route('/channel/<channel>')
def get_channel(channel):
  return render_template("channel.html", channel_id=channel,channel_name=get_channel_data()[channel]["name"])

@app.route('/chatcount/<channel>')
def chatcount(channel):
  return jsonify({
    "count": str(len(get_channel_data()[channel]["messages"]))
  })

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
  user_data = get_user_data()
  if not username in user_data:
    return jsonify({"status": "Error", "message": "Error: not signed in or user not found"})
  if sha256(pw) != user_data[username]["pwhash"]:
    return jsonify({"status": "Error", "message": "Error: Password incorrect, cannot verify user"})
  channel_data = get_channel_data()
  id = str(random.randint(0, 100000))
  while id in channel_data:
    id = str(random.randint(0, 100000))
  channel_data[id] = {
    "name": title, 
    "messages": [{"username": "Channel-Bot", "content": "Channel created by " + username, "date": get_date()}]
  }
  write_data = open("channels.json", "w")
  write_data.write(json.dumps(channel_data))
  write_data.close()
  return jsonify({"status": "Success", "message": id})

@app.route('/postmessage', methods=['POST'])
def postmessage():
  current_channels_data = get_channel_data()
  user_data = get_user_data()
  rq_json = request.get_json()
  usr = rq_json["username"]
  pw = rq_json["password"]
  if not usr in user_data:
    return "Error: Message failed: username not recognized"
  if user_data[usr]["pwhash"] != sha256(pw):
    return "Error: Message failed: wrong password for account"
  if not rq_json["channelId"] in current_channels_data:
    return "Error: Message failed: channel does not exist"
  current_channels_data[rq_json["channelId"]]["messages"].append({
    "username": usr,
    "content": rq_json["content"],
    "date": get_date()
  })
  write_file = open("channels.json", "w")
  write_file.write(json.dumps(current_channels_data))
  write_file.close()
  return "Success"

@app.route('/login', methods=['POST'])
def login():
  all_user_data = get_user_data()
  login_data = request.get_json()
  if not login_data["username"] in all_user_data:
    return "Error: Login failure: username not found"
  
  if sha256(login_data["password"]) != all_user_data[login_data["username"]]["pwhash"]:
    return "Error: Login failure: password incorrect"
  return "Success"

@app.route('/signup', methods=['POST'])
def signup():
  all_user_data = get_user_data()
  signup_data = request.get_json()
  username = signup_data["username"]
  password = signup_data["password"]
  if username in all_user_data:
    return "Error: Signup failure: username already exists"
  if not re.compile("^[\w-]{3,20}$").fullmatch(username):
    return "Error: Signup failure: username not valid (must consist of letters, numbers, - and _ and must be between 3 and 20 characters"
  write_file = open("user_data.json", "w")
  all_user_data[username] = {
    "pwhash": sha256(password),
    "bio": ""
  }
  write_file.write(json.dumps(all_user_data))
  write_file.close()
  return "Success"

@app.route('/settings')
def settingspage():
  return render_template('settings.html')

@app.route('/user_data', methods=['GET'])
def getbios():
  data = get_user_data()[request.args["user"]]
  return jsonify({
    "bio": data["bio"]
  })

@app.route('/profile', methods=['GET'])
def profile():
  user_data = get_user_data()
  name = request.args["user"]
  if not name in user_data:
    return "User not found"
  data = user_data[name]
  return render_template('profile.html', username=name, bio=data["bio"] if data["bio"] != "" else "None given.")

@app.route('/set_settings', methods=['POST'])
def set_settings():
  rq_json = request.get_json()
  username = rq_json["username"]
  pwhash = sha256(rq_json["password"])
  bio = rq_json["bio"]

  all_user_data = get_user_data()
  if not username in all_user_data:
    return "Error: username does not exist"
  if all_user_data[username]["pwhash"] != pwhash:
    return "Error: password incorrect (cannot verify profile)"
  all_user_data[username]["bio"] = bio
  write_file = open("user_data.json", "w")
  write_file.write(json.dumps(all_user_data))
  write_file.close()
  return "Success"
  
if __name__ == "__main__":  # Makes sure this is the main process
	app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
	)
