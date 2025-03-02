import random


def generate_key():
    key = random.randint(0, 
        9999999999999999)
    key = str(key).zfill(16)
    return key

