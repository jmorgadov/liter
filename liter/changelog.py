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

def _get_version_model(version, commits, config, date=''):

    sections = { name: [] for name in config['changelog_sections'].keys()}
    sections['Others'] = []

    for commit in commits:
        key_word = commit.split()[0].lower()
        if key_word in config['changelog_ignore_commits']:
            continue
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


    return VERSION_MODEL.format(f'{version} {date}', version_body)

def get_subprocess_output(command, new_line_end=True, min=3, max=-4):
    subp = subprocess.Popen(command, stdout=subprocess.PIPE)
    end = '\n' if new_line_end else ''
    return [str(s)[min:max] + end for s in subp.stdout.readlines()]

def match(s, patterns):
    for patt in patterns:
        match_p = re.search(patt, s)
        if match_p:
            return match_p    

def generate_changelogs(start_in: str = None):
    # Getting tags
    tags = get_subprocess_output(['git', 'log', '--oneline', r'--format="%d"'])
    # Getting subjects
    commits = get_subprocess_output(['git', 'log', '--oneline', r'--format="%s"'])
    # Getting dates
    dates = get_subprocess_output(['git', 'log', '--oneline', r'--format="%as"'])

    config = load_config()
    changelog_body = ""

    tags.reverse()
    commits.reverse()
    dates.reverse()

    current_version_commits = []
    versions = []
    saving = start_in is None
    for i, commit in enumerate(commits):
        if tags[i] != '' and re.search('\d+\.\d+\.\d+', tags[i]) is not None:            
            vers = re.search('\d+\.\d+\.\d+', tags[i])[0]
            if vers == start_in:
                saving = True

            if not saving:
                current_version_commits = []
                continue

            current_version_commits.append(commit)
                
            versions.append(_get_version_model(
                f'[{vers}]',
                current_version_commits,
                config,
                dates[i]
            ))
            current_version_commits = []
        else:
            current_version_commits.append(commit)
    if current_version_commits:
        versions.append(_get_version_model(
            '[Not released]',
            current_version_commits,
            config
        ))

    versions.reverse()
    changelog = CHANGELOG_MODEL.format(''.join(versions))   

    with open('CHANGELOG.md', 'w+') as f:
        f.write(changelog)
    
