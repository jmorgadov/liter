import subprocess
import datetime
import re

from liter.utils import load_config

COMMIT_MODEL = """* {0}"""

SECTION_MODEL = """
### {0}

{1}"""

VERSION_MODEL = """
## {0}
{1}"""

CHANGELOG_MODEL = """
# CHANGELOG
{0}"""

def _get_section(sec_name, commits):
    commits_md = ""
    for commit in commits:
        commits_md += COMMIT_MODEL.format(commit)
    return SECTION_MODEL.format(sec_name, commits_md)

def _get_version_model(version, commits, config):
    added, fixed, removed, others = [], [], [], []

    for commit in commits:
        key_word = commit.split()[0].lower()
        if key_word in config['added_words']:
            added.append(commit)
        elif key_word in config['fixed_words']:
            fixed.append(commit)
        elif key_word in config['removed_words']:
            removed.append(commit)
        else:
            others.append(commit)


    version_body = ""
    if added:
        version_body += _get_section('Added', added)
    if fixed:
        version_body += _get_section('Fixed', fixed)
    if removed:
        version_body += _get_section('Removed', removed)
    if others:
        version_body += _get_section('Others', others)

    return VERSION_MODEL.format(version, version_body)


def generate_changelogs():
    fmt = r'%d'
    subp = subprocess.Popen(f'git log --oneline --format="{fmt}"', stdout=subprocess.PIPE)
    tags = [str(s)[2:-3] for s in subp.stdout.readlines()]
    fmt = r'%s'
    subp = subprocess.Popen(f'git log --oneline --format="{fmt}"', stdout=subprocess.PIPE)
    commits = [str(s)[2:-3] + '\n' for s in subp.stdout.readlines()]

    print(commits)

    config = load_config()
    changelog_body = ""

    tags.reverse()
    commits.reverse()

    current_version_commits = []
    versions = []
    for i, commit in enumerate(commits):
        if tags[i] != '' and re.search('\d+\.\d+\.\d+', tags[i]) is not None:
            vers = 'v' + re.search('\d+\.\d+\.\d+', tags[i])[0]
            current_version_commits.append(commit)
            versions.append(_get_version_model(
                vers,
                current_version_commits,
                config
            ))
            current_version_commits = []
        else:
            current_version_commits.append(commit)
    if current_version_commits:
        versions.append(_get_version_model(
            'Not released', 
            current_version_commits,
            config
        ))

    versions.reverse()
    changelog = CHANGELOG_MODEL.format(''.join(versions))   

    print(changelog)
    with open('CHANGELOG.md', 'w+') as f:
        f.write(changelog)
    
