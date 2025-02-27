import json
import random
import os


from modules.constants import KEYS_FILE, USERS_FILE
from modules.loc_io import load_data, save_data


def load_keys():
    return load_data(KEYS_FILE)


def save_keys(keys):
    save_data(KEYS_FILE, keys)


def load_users():
    if (not os.path.exists(USERS_FILE) or not os.path.getsize(USERS_FILE)) > 0:
        return {}
    with open(USERS_FILE, "r") as file:
        return json.load(file)


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)


def generate_key(name):
    keys = load_keys()
    if name in keys:
        print(keys[name])
    else:
        key = random.randint(0, 
            9999999999999999)
        key = str(key).zfill(16)
        keys[name] = key
        save_keys(keys)
