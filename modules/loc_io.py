import json


from modules.constants import USERS_FILE, CHATS_FILE, CHANNELS_FILE, MESSAGES_FILE


def load_data(filename, default=None):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_users():
    return load_data(USERS_FILE)


def save_users(users):
    save_data(USERS_FILE, users)


def load_chats():
    return load_data(CHATS_FILE, [])


def save_chats(chats):
    save_data(CHATS_FILE, chats)


def load_channels():
    return load_data(CHANNELS_FILE, {"channels": []})


def save_channels(channels):
    save_data(CHANNELS_FILE, channels)


def load_messages(chat_id, last_time=None):
    all_messages = load_data(MESSAGES_FILE, {}).get(str(chat_id), [])
    if last_time:
        all_messages = [msg for msg in all_messages if msg["time"] > last_time]
    return all_messages


def save_message(chat_id, message):
    data = load_data(MESSAGES_FILE, {})
    chat_id_str = str(chat_id)
    if chat_id_str not in data:
        data[chat_id_str] = []
    data[chat_id_str].append(message)
    save_data(MESSAGES_FILE, data)