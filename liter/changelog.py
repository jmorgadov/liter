import subprocess

def generate_changelogs():
    subp = subprocess.Popen('git log --oneline', stdout=subprocess.PIPE)
    commits = [str(s)[2:-3] for s in subp.stdout.readlines()]
    print(commits)