import random


from modules.loc_io import load_keys, save_keys


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
