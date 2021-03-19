import json
import os
import re
import sys
from liter.utils import load_config, yn_input
from pathlib import Path


def change_version(vtype: str = 'patch', force: bool = False):
    config = load_config()

    def match_ignore(s):
        for patt in config['version_ignore']:
            if re.search(patt, s) is not None:
                return True
        return False

    current_vers = config['version']
    new_vers = current_vers.split('.')

    if vtype == 'patch':
        new_vers[2] = str(int(new_vers[2]) + 1)
    elif vtype == 'minor':
        new_vers[1] = str(int(new_vers[1]) + 1)
        new_vers[2] = '0'
    elif vtype == 'major':
        new_vers[0] = str(int(new_vers[0]) + 1)
        new_vers[1] = '0'
        new_vers[2] = '0'
    
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
                            print('-' * 80)
                            new_line = re.sub(current_vers, new_vers, line)
                            if i > 0:
                                l0 = lines[i-1].strip('\n')
                                print(f'{i: >6} | {l0}')
                            s_new_line = new_line.strip('\n')
                            print(f'{i+1: >6} | {s_line}')
                            print(f'{"NEW --" : >6} | {s_new_line}')
                            if i + 1 < len(lines):
                                l2 = lines[i+1].strip('\n')
                                print(f'{i+2: >6} | {l2}')
                            if force or yn_input('\nReplace?'):
                                new_lines.append(new_line)
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                with open(full_path, 'w+') as f:
                    f.writelines(new_lines)
            except:
                pass