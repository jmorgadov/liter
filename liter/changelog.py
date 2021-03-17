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

    sections = { name: [] for name in config['changelog_sections'].keys()}
    sections['Others'] = []

    for commit in commits:
        key_word = commit.split()[0].lower()
        on_section = False
        for section, filters in config['changelog_sections'].items():
            if key_word in filters:
                sections[section].append(commit)   
                on_section = True
        if not on_section:
            sections['Others'].append(commit)
    
    if not config['changelog_include_others']:
        sections.pop('Others')

    version_body = ""
    for name, cmmts in sections.items():
        if cmmts:
            version_body += _get_section(name, cmmts)

    return VERSION_MODEL.format(version, version_body)


def generate_changelogs():
    fmt = r'%d'
    subp = subprocess.Popen(f'git log --oneline --format="{fmt}"', stdout=subprocess.PIPE)
    tags = [str(s)[2:-3] for s in subp.stdout.readlines()]
    fmt = r'%s'
    subp = subprocess.Popen(f'git log --oneline --format="{fmt}"', stdout=subprocess.PIPE)
    commits = [str(s)[2:-3] + '\n' for s in subp.stdout.readlines()]

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

    with open('CHANGELOG.md', 'w+') as f:
        f.write(changelog)
    
