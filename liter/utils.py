import json

def load_config():
    config = {}
    with open('literconfig.json', 'r') as f:
        config = json.load(f)
    return config

def save_config(config):
    with open('literconfig.json', 'w+') as f:
        json.dump(config, f)

def yn_input(msg):
    ans = input(f'{msg} (y/n)[y]:').lower()
    return ans == '' or ans == 'y'

class Style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    RESET = '\033[0m'