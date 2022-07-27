import random, string, json, hashlib, re
from flask import Flask, render_template, request

def sha256(text):
  return hashlib.sha256(text.encode("utf-8")).hexdigest()

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

@app.route('/chats', methods=['GET', 'POST'])
def page():
  chat_file = open("chats.json", "r")
  
  chats = chat_file.read()
  if request.method == 'POST':
    new_msg = request.get_json()
    username = new_msg["username"]
    password = new_msg["password"]
    del new_msg["username"]
    del new_msg["password"]
    user_data_file = open("user_data.json")
    user_data = json.loads(user_data_file.read())
    user_data_file.close()
    if not username in user_data:
      return "Error: Message failed: username not recognized"
    if user_data[username] != sha256(password):
      return "Error: Message failed: wrong password for account"
    
    write_file = open("chats.json", "w")
    chats = json.loads(chats)
    chats.append({
      "username": username,
      "date": new_msg["date"],
      "content": new_msg["content"]
    })
    write_file.write(json.dumps(chats))
    write_file.close()
    chat_file.close()
    return "Success"
  chat_file.close()
  return chats

@app.route('/chatcount', methods=['GET'])
def chatcount():
  chat_file = open("chats.json", "r")
  count = str(len(json.loads(chat_file.read())))
  chat_file.close()
  return count

@app.route('/login', methods=['POST'])
def login():
  data_file = open("user_data.json", "r")
  all_user_data = json.loads(data_file.read())
  login_data = request.get_json()
  data_file.close()
  if not login_data["username"] in all_user_data:
    return "Error: Login failure: username not found"
  
  if sha256(login_data["password"]) != all_user_data[login_data["username"]]:
    return "Error: Login failure: password incorrect"
  return "Success"

@app.route('/signup', methods=['POST'])
def signup():
  read_data = open("user_data.json", "r")
  all_user_data = json.loads(read_data.read())
  read_data.close()
  signup_data = request.get_json()
  username = signup_data["username"]
  password = signup_data["password"]
  if username in all_user_data:
    return "Error: Signup failure: username already exists"
  if not re.compile("^[\w-]{3,20}$").fullmatch(username):
    return "Error: Signup failure: username not valid (must consist of letters, numbers, - and _ and must be between 3 and 20 characters"
  write_file = open("user_data.json", "w")
  print(all_user_data, signup_data["username"])
  all_user_data[username] =  sha256(password)
  write_file.write(json.dumps(all_user_data))
  write_file.close()
  return "Success"

if __name__ == "__main__":  # Makes sure this is the main process
	app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
	)
