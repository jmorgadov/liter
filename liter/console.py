import typer
from pathlib import Path
import subprocess
from liter.changelog import generate_changelogs
from liter.version import change_version
app = typer.Typer()

@app.command()
def changelog():
    generate_changelogs()

@app.command()
def version(vtype: str = typer.Argument(default='patch'),
            force: bool = typer.Option(default=False)):
    change_version(vtype, force)
