import json
import re
from pathlib import Path

DEFAULT_CONFIG = {
    "version" : "0.0.1",    
    "version_ignore" : [
        'git',
        'dist',
        'egg',
        'CHANGELOG',
        '.lock'        
     ],
    "changelog_sections" : {
        "Added" : [
            "add"
        ],
        "Fixed" : [
            "fix"
        ],    
        "Removed" : [
            "remove"
        ]
    },
    "changelog_include_others" : True,
    "changelog_ignore_commits" : [
        "merge"
    ],
    "changelog_only_path_pattern" : []
}

def _find_version(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            match = re.search('\d+\.\d+\.\d+', line)
            if match is not None:
                return match[0]
    return '0.0.0'

def load_config():
    config = {}
    config_path = Path('literconfig.json')

    if not config_path.exists():
        version = '0.0.1'
        if Path('pyproject.toml').exists():
            version = _find_version('pyproject.toml')
        elif Path('setup.py').exists():
            version = _find_version('setup.py')
        conf = DEFAULT_CONFIG.copy()
        conf['version'] = version
        with open('literconfig.json', 'w+') as f:
            json.dump(conf, f, indent=4)
        return conf

    loaded_config = {}
    with open('literconfig.json', 'r') as f:
        loaded_config = json.load(f)
        
    config = {}
    missing_key = False
    for key, item in DEFAULT_CONFIG.items():
        if key not in loaded_config.keys():
            config[key] = item
            missing_key = True
        else:
            config[key] = loaded_config[key] 

    if missing_key:
        with open('literconfig.json', 'w+') as f:
            json.dump(config, f, indent=4)        
    return config

def save_config(config):
    with open('literconfig.json', 'w+') as f:
        json.dump(config, f, indent=4)

def yn_input(msg):
    ans = input(f'{msg} (y/n)[y]:').lower()
    return ans == '' or ans == 'y'
