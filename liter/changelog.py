import subprocess
import datetime
import re
from typing import List

from liter.utils import load_config

COMMIT_MODEL = """- {0}"""

SECTION_MODEL = """
### {0}

{1}"""

VERSION_MODEL = """
## {0}
{1}"""

CHANGELOG_MODEL = """# CHANGELOG
{0}"""

VERSION_RE = r'\d+\.\d+\.\d+'
VERSION_MODEL_RE = r'## \[(?:Not released|\d+\.\d+\.\d+)\] ' \
                   r'(?:\d+\-\d+\-\d+)*\n\n(?:###\s(?:{0})\n\n(?:\-\s.*\n)*\n)*'

def _get_section(sec_name, commits: List[str]):
    commits_md = ""
    for commit in commits:
        commit = commit.capitalize()
        commits_md += COMMIT_MODEL.format(commit)
    return SECTION_MODEL.format(sec_name, commits_md)

def match_pattern(pattern, text):
    if pattern.startswith('m:') and \
        re.match(pattern[2:], text) is not None:
        return True
    elif pattern.startswith('s:') and \
            re.search(pattern[2:], text) is not None:
        return True
    elif text.lower().startswith(pattern):
        return True
    return False

def _get_version_model(version, commits, config, date=''):

    version = f'[{version}]'
    sections = { name: [] for name in config['changelog_sections'].keys()}
    sections['Others'] = []

    for commit in commits:
        # Checking ignore pattern
        for ignore_patt in config['changelog_ignore_commits']:
            if match_pattern(ignore_patt, commit):
                continue

        on_section = False
        for section, filters in config['changelog_sections'].items():
            for patt in filters:
                if match_pattern(patt, commit):
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

def subprocess_output(command, new_line_end=True, min=3, max=-4):
    subp = subprocess.Popen(command, stdout=subprocess.PIPE)
    end = '\n' if new_line_end else ''
    return [str(s)[min:max] + end for s in subp.stdout.readlines()]

def match(s, patterns):
    for patt in patterns:
        match_p = re.search(patt, s)
        if match_p:
            return match_p

def only_file_changes_valid_commits(path_filter_patterns):
    command = ['git', 'log', '--name-only', '--oneline', r'--format="%H"']
    history = subprocess_output(command, False, 2, -3)
    commits_file_changes = {}

    i = 0
    current_hash = ''
    while i < len(history):
        is_hash = i + 1 < len(history) and history[i + 1] == ''
        if is_hash:
            current_hash = history[i][1:-1]
            i += 2
            continue

        file_path = history[i]

        if file_path not in commits_file_changes.keys():
            commits_file_changes[file_path] = []

        commits_file_changes[file_path].append(current_hash)
        i += 1

    path_keys = list(commits_file_changes.keys())
    valid_commits = []
    for path in path_keys:
        if match(path, path_filter_patterns):
            valid_commits += commits_file_changes[path]

    return set(valid_commits)

def basic_git_logs():
    tags = subprocess_output(['git', 'log', '--oneline', r'--format="%d"'])
    commits = subprocess_output(['git', 'log', '--oneline', r'--format="%s"'])
    dates = subprocess_output(['git', 'log', '--oneline', r'--format="%as"'], False)
    full_hash = subprocess_output(['git', 'log', '--oneline', r'--format="%H"'], False)
    return tags, commits, dates, full_hash

def append_last(current_version, version_model, config):
    version_model += '\n'
    changelog_txt = ''
    with open('CHANGELOG.md', 'r') as f:
        changelog_txt = f.read()

    sections = '|'.join(config['changelog_sections'].keys())
    patt = VERSION_MODEL_RE.format(sections)

    versions = re.findall(patt, changelog_txt)
    last = versions[0]
    title_re = r'## \[(Not released|\d+\.\d+\.\d+)\].*'
    last_version_value = re.match(title_re, last).groups(0)[0]

    if last_version_value == current_version:
        versions[0] = version_model
    else:
        versions.insert(0, version_model)

    with open('CHANGELOG.md', 'w+') as f:
        f.write('# CHANGELOG\n' + ''.join(versions))


def generate_changelogs(start_in: str = None, last: bool = False):
    tags, commits, dates, full_hash = basic_git_logs()
    config = load_config()

    tags.reverse()
    commits.reverse()
    dates.reverse()
    full_hash.reverse()

    path_filter_patterns = config['changelog_only_path_pattern']
    use_path_filter = len(path_filter_patterns)
    valid_commits = only_file_changes_valid_commits(path_filter_patterns)

    current_version_commits = []
    versions = []
    saving = start_in is None
    current_version = 'Not released'
    for i, commit in enumerate(commits):
        valid_commit = True

        if use_path_filter:
            valid_commit = full_hash[i] in valid_commits

        if re.search(VERSION_RE, tags[i]) is not None:
            vers = re.search(VERSION_RE, tags[i])[0]
            if vers == start_in:
                saving = True

            if not saving:
                current_version_commits = []
                continue

            if valid_commit:
                current_version_commits.append(commit)

            versions.append(_get_version_model(
                vers,
                current_version_commits,
                config,
                dates[i]
            ))
            current_version = vers
            current_version_commits = []
        elif valid_commit:
            current_version_commits.append(commit)

    if current_version_commits:
        versions.append(_get_version_model(
            'Not released',
            current_version_commits,
            config
        ))
        current_version = 'Not released'

    versions.reverse()

    if last:
        append_last(current_version, versions[0], config)
    else:
        changelog = CHANGELOG_MODEL.format(''.join(versions))
        with open('CHANGELOG.md', 'w+') as f:
            f.write(changelog)
