import typer
import json
import os
import re
from pathlib import Path

app = typer.Typer()

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

@app.command()
def version():
    config = load_config()

    def match_ignore(s):
        for patt in config['ignore']:
            if re.search(patt, s) is not None:
                return True
        return False

    current_vers = config['version']
    new_vers = current_vers.split('.')
    new_vers[2] = str(int(new_vers[2]) + 1)
    new_vers = '.'.join(new_vers)

    for root, dirs, files in os.walk('.'):
        for file in files:
            full_path = str(Path(root) / Path(file))
            if match_ignore(full_path):
                continue
            new_lines = []
            try:
                with open(full_path, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        s_line = line.strip('\n')
                        if re.search(current_vers, line) is not None:
                            print(f'\nFile: {full_path}')
                            print('-' * 40)
                            new_line = re.sub(current_vers, new_vers, line)
                            if i > 0:
                                l0 = lines[i-1].strip('\n')
                                print(f'{i: >6} | {l0}')
                            s_new_line = new_line.strip('\n')
                            print(f'{i+1: >6} | {Style.RED}{s_line}{Style.RESET}')
                            print(f'{"" : >6} | {Style.GREEN}{s_new_line}{Style.RESET}')
                            if i + 1 < len(lines):
                                l2 = lines[i+1].strip('\n')
                                print(f'{i+2: >6} | {l2}')
                            if yn_input('Replace?'):
                                new_lines.append(new_line)
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                with open(full_path, 'w+') as f:
                    f.writelines(new_lines)
            except:
                pass
