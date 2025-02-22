from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from datetime import datetime
import json
import os
import bcrypt
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'NKYC!9t3t11Yz0@m*h2zIW_nhIN_CnQQ^'
MESSAGE_LIMIT = 10

USERS_FILE = "users.json"
CHATS_FILE = "chats.json"
MESSAGES_FILE = "db.json"
CHANNELS_FILE = "channels.json"  # Новый файл для хранения каналов
MEDIA_FOLDER = 'media'  # Папка для хранения медиафайлов
KEYS_FILE = "keys.json" # файл с ключами
os.makedirs(MEDIA_FOLDER, exist_ok=True)  # Создаем папку, если она не существует

# Функции для работы с пользователями
def load_users():
    if not os.path.exists(USERS_FILE) or not os.path.getsize(USERS_FILE) > 0:
        return {}
    with open(USERS_FILE, "r") as file:
        return json.load(file)

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

# функции для работы с ключами
def load_keys():
    if not os.path.exists(KEYS_FILE) or not os.path.getsize(KEYS_FILE) > 0:
        return {}
    with open(KEYS_FILE, "r") as file:
        return json.load(file)

def save_keys(keys):
    with open(KEYS_FILE, "w") as file:
        json.dump(keys, file)

# Функции для работы с чатами
def load_chats():
    if not os.path.exists(CHATS_FILE) or not os.path.getsize(CHATS_FILE) > 0:
        return []
    with open(CHATS_FILE, "r") as file:
        return json.load(file)

def save_chats(chats):
    with open(CHATS_FILE, "w") as file:
        json.dump(chats, file)

# Функции для работы с сообщениями
def load_messages(chat_id, last_time=None):
    if not os.path.exists(MESSAGES_FILE) or not os.path.getsize(MESSAGES_FILE) > 0:
        return []
    with open(MESSAGES_FILE, "r") as file:
        data = json.load(file)
    messages = data.get(str(chat_id), [])
    if last_time:
        messages = [msg for msg in messages if msg["time"] > last_time]
    return messages

def save_message(chat_id, message):
    all_messages = load_messages(chat_id)
    all_messages.append(message)

    # Загружаем существующие сообщения или инициализируем пустой словарь
    if not os.path.exists(MESSAGES_FILE) or os.path.getsize(MESSAGES_FILE) == 0:
        data = {}
    else:
        with open(MESSAGES_FILE, "r") as file:
            data = json.load(file)

    data[str(chat_id)] = all_messages

    # Сохраняем обратно в файл
    with open(MESSAGES_FILE, "w") as file:
        json.dump(data, file)

# Функции для работы с каналами
def load_channels():
    if not os.path.exists(CHANNELS_FILE) or not os.path.getsize(CHANNELS_FILE) > 0:
        return {"channels": []}
    with open(CHANNELS_FILE, "r") as file:
        return json.load(file)

def save_channels(channels):
    with open(CHANNELS_FILE, "w") as file:
        json.dump(channels, file)

# Главная страница
@app.route("/")
def main_page():
    if "username" in session:
        return render_template("main.html", username=session["username"])
    return render_template("main_no_user.html")

# Регистрация
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        age = request.form["age"]
        about_me = request.form.get("about_me", "")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        users = load_users()

        if username in users:
            return "Пользователь с этим именем уже существует.", 400

        profile_picture_filename = None

        users[username] = {
            "password": password_hash.decode(),
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "about_me": about_me,
            "profile_picture": profile_picture_filename
        }
        save_users(users)
        return redirect(url_for("login"))

    return render_template("register.html")

# Вход
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        key = request.form["key"]
        users = load_users()
        keys = load_keys()

        if username in users and bcrypt.checkpw(password.encode(), users[username]["password"].encode()):
            if username in keys and key == keys[username]:
                session["username"] = username
                return redirect(url_for("chat_page"))
        return "Неверное имя пользователя, пароль или ключ доступа.", 401

    return render_template("login.html")

# Выход
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main_page"))

# Страница чатов
@app.route("/chat")
def chat_page():
    if "username" not in session:
        return redirect(url_for("login"))

    chats = load_chats()
    return render_template("chat_list.html", chats=chats)

# Создание чата
@app.route("/create_chat", methods=["GET", "POST"])
def create_chat():
    if request.method == "POST":
        if "username" not in session:
            return redirect(url_for("login"))

        chat_name = request.form["chat_name"]
        participants = request.form.getlist("participants")
        chat_image = request.files.get("chat_image")  # Get the uploaded chat image

        chat_id = str(uuid.uuid4())
        chat = {
            "chat_id": chat_id,
            "name": chat_name,
            "participants": participants,
            "messages": [],
            "chat_image": None,
            "description": ""  # New field for chat description
        }

        # Save the chat image if uploaded
        if chat_image:
            chat_image_filename = secure_filename(chat_image.filename)
            chat_image_path = os.path.join(MEDIA_FOLDER, chat_image_filename)
            chat_image.save(chat_image_path)
            chat["chat_image"] = chat_image_filename  # Save the image filename in the chat data

        chats = load_chats()
        chats.append(chat)
        save_chats(chats)

        return redirect(url_for("chat_page"))

    users = load_users()
    return render_template("create_chat.html", users=users)

# Просмотр чата
@app.route("/chat/<chat_id>")
def view_chat(chat_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    chats = load_chats()
    chat = next((c for c in chats if c["chat_id"] == chat_id), None)

    if not chat:
        return "Чат не найден", 404

    if username not in chat["participants"]:
        return "У вас нет доступа к этому чату", 403

    users = load_users()  # Load all users
    return render_template("chat.html", chat=chat, users=users)

# Отправка сообщения
@app.route("/send_message/<chat_id>", methods=["POST"])
def send_message(chat_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    text = request.form.get("text")
    media = request.files.get("media")

    chats = load_chats()
    chat = next((c for c in chats if c["chat_id"] == chat_id), None)

    if not chat:
        return "Чат не найден", 404

    if username not in chat["participants"]:
        return "У вас нет доступа к этому чату", 403

    # Ограничение на количество сообщений
    user_messages = [msg for msg in load_messages(chat_id) if msg["author"] == username]
    if len(user_messages) >= MESSAGE_LIMIT:
        return f"Вы достигли лимита в {MESSAGE_LIMIT} сообщений в этом чате.", 403

    message = {
        "author": username,
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S"),
        "media": None,  # Поле для медиафайла
    }

    # Обработка медиафайла
    if media:
        filename = secure_filename(media.filename)
        media_path = os.path.join(MEDIA_FOLDER, filename)
        media.save(media_path)  # Сохранение файла
        message["media"] = filename  # Сохраняем имя файла в сообщении

    save_message(chat_id, message)
    return redirect(url_for("view_chat", chat_id=chat_id))

# Загрузка сообщений
@app.route("/load_messages/<chat_id>")
def load_messages_route(chat_id):
    last_time = request.args.get("last_time")
    messages = load_messages(chat_id, last_time)
    return jsonify(messages)

# Настройки чатов
@app.route("/chat/<chat_id>/settings", methods=["GET", "POST"])
def chat_settings(chat_id):
    if "username" not in session:
        return redirect(url_for("login"))

    chats = load_chats()
    chat = next((c for c in chats if c["chat_id"] == chat_id), None)

    if not chat:
        return "Чат не найден", 404

    if session["username"] not in chat["participants"]:
        return "У вас нет доступа к настройкам этого чата", 403

    if request.method == "POST":
        chat["name"] = request.form["chat_name"]
        chat["description"] = request.form.get("chat_description", "")
        chat["participants"] = request.form.getlist("participants")

        chat_image = request.files.get("chat_image")
        if chat_image:
            chat_image_filename = secure_filename(chat_image.filename)
            chat_image_path = os.path.join(MEDIA_FOLDER, chat_image_filename)
            chat_image.save(chat_image_path)
            chat["chat_image"] = chat_image_filename

        save_chats(chats)
        return redirect(url_for("view_chat", chat_id=chat_id))

    all_users = load_users().keys()
    return render_template("chat_settings.html", chat=chat, all_users=all_users)

# Страница пользователей
@app.route("/users", methods=["GET"])
def users_page():
    users = load_users()
    return render_template("users.html", users=users)

# Профиль пользователя
@app.route("/user/<username>")
def user_profile(username):
    users = load_users()
    user_info = users.get(username)

    if not user_info:
        return "Пользователь не найден", 404

    return render_template("user_profile.html", username=username, user_info=user_info)

# Редактирование профиля
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    users = load_users()

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        age = request.form["age"]
        about_me = request.form.get("about_me", "")
        profile_picture = request.files.get("profile_picture")

        users[username]["first_name"] = first_name
        users[username]["last_name"] = last_name
        users[username]["age"] = age
        users[username]["about_me"] = about_me

        if profile_picture:
            profile_picture_filename = secure_filename(profile_picture.filename)
            profile_picture_path = os.path.join(MEDIA_FOLDER, profile_picture_filename)
            profile_picture.save(profile_picture_path)
            users[username]["profile_picture"] = profile_picture_filename

        save_users(users)
        return redirect(url_for("user_profile", username=username))

    user_info = users[username]
    return render_template("edit_profile.html", user_info=user_info)

# Личные сообщения
@app.route("/start_dm/<recipient_username>", methods=["GET", "POST"])
def start_dm(recipient_username):
    if "username" not in session:
        return redirect(url_for("login"))

    current_user = session["username"]
    users = load_users()

    if recipient_username not in users:
        return "Пользователь не найден", 404

    chats = load_chats()

    dm_chat = next((c for c in chats if c["name"] == f"{recipient_username} и {current_user}" or c["name"] == f"{current_user} и {recipient_username}"), None)

    if dm_chat:
        return redirect(url_for("view_chat", chat_id=dm_chat["chat_id"]))

    else:
        chat_id = str(uuid.uuid4())
        chat = {
            "chat_id": chat_id,
            "name": f"{recipient_username} и {current_user}",
            "participants": [current_user, recipient_username],
            "messages": []
        }

        chats.append(chat)
        save_chats(chats)

        return redirect(url_for("view_chat", chat_id=chat_id))

# Создание канала
@app.route("/create_channel", methods=["GET", "POST"])
def create_channel():
    if request.method == "POST":
        if "username" not in session:
            return redirect(url_for("login"))

        channel_name = request.form["channel_name"]
        admins = request.form.getlist("admins")
        channel_image = request.files.get("channel_image")  # Get the uploaded channel image

        channel_id = str(uuid.uuid4())
        channel = {
            "channel_id": channel_id,
            "name": channel_name,
            "admins": admins,
            "subscribers": [],
            "messages": [],
            "channel_image": None,
            "description": ""  # New field for channel description
        }

        # Save the channel image if uploaded
        if channel_image:
            channel_image_filename = secure_filename(channel_image.filename)
            channel_image_path = os.path.join(MEDIA_FOLDER, channel_image_filename)
            channel_image.save(channel_image_path)
            channel["channel_image"] = channel_image_filename  # Save the image filename in the channel data

        channels = load_channels()
        channels["channels"].append(channel)
        save_channels(channels)

        return redirect(url_for("channel_list"))

    users = load_users()
    return render_template("create_channel.html", users=users)

# Просмотр канала
@app.route("/channel/<channel_id>")
def view_channel(channel_id):
    if "username" not in session:
        return redirect(url_for("login"))

    channels = load_channels()
    channel = next((c for c in channels["channels"] if c["channel_id"] == channel_id), None)

    if not channel:
        return "Канал не найден", 404

    users = load_users()  # Load all users
    return render_template("channel.html", channel=channel, users=users)

# Отправка сообщения в канал
@app.route("/send_message_channel/<channel_id>", methods=["POST"])
def send_message_channel(channel_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    text = request.form["text"]
    media = request.files.get("media")  # Получаем загруженный файл

    channels = load_channels()
    channel = next((c for c in channels["channels"] if c["channel_id"] == channel_id), None)

    if not channel:
        return "Канал не найден", 404

    if username not in channel["admins"]:
        return "У вас нет прав для отправки сообщений в этот канал", 403

    message = {
        "author": username,
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S"),
        "media": None,  # Поле для медиафайла
    }

    # Обработка медиафайла
    if media:
        filename = secure_filename(media.filename)
        media_path = os.path.join(MEDIA_FOLDER, filename)
        media.save(media_path)  # Сохранение файла
        message["media"] = filename  # Сохраняем имя файла в сообщении

    channel["messages"].append(message)
    save_channels(channels)

    return redirect(url_for("view_channel", channel_id=channel_id))

# Настройки каналов
@app.route("/channel/<channel_id>/settings", methods=["GET", "POST"])
def channel_settings(channel_id):
    if "username" not in session:
        return redirect(url_for("login"))

    channels = load_channels()
    channel = next((c for c in channels["channels"] if c["channel_id"] == channel_id), None)

    if not channel:
        return "Канал не найден", 404

    if session["username"] not in channel["admins"]:
        return "У вас нет прав для изменения настроек этого канала", 403

    if request.method == "POST":
        channel["name"] = request.form["channel_name"]
        channel["description"] = request.form.get("channel_description", "")
        channel["admins"] = request.form.getlist("admins")
        channel["subscribers"] = request.form.getlist("subscribers")

        channel_image = request.files.get("channel_image")
        if channel_image:
            channel_image_filename = secure_filename(channel_image.filename)
            channel_image_path = os.path.join(MEDIA_FOLDER, channel_image_filename)
            channel_image.save(channel_image_path)
            channel["channel_image"] = channel_image_filename

        save_channels(channels)
        return redirect(url_for("view_channel", channel_id=channel_id))

    all_users = load_users().keys()
    return render_template("channel_settings.html", channel=channel, all_users=all_users)

# Страница со списком каналов
@app.route("/channels")
def channel_list():
    if "username" not in session:
        return redirect(url_for("login"))

    channels = load_channels()
    return render_template("channel_list.html", channels=channels["channels"])

# Маршрут для доступа к медиафайлам
@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)