"""
commands.py: Command-line interface for PyGrits.
"""

import click
from pathlib import Path
from typing import Optional

from app.core.repository import Repository
from app.utils.logger import logger


@click.group()
def cli():
    """PyGrits - A simple version control system."""
    pass


@cli.command()
@click.option("--path", default=".", help="Path to initialize repository")
def init(path: str):
    """Initialize a new repository."""
    try:
        repo = Repository(path)
        repo.init()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def add(files):
    """Add file(s) to the staging area."""
    try:
        repo = Repository()
        for file_path in files:
            repo.add(file_path)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@cli.command()
@click.option("-m", "--message", required=True, help="Commit message")
def commit(message: str):
    """Create a new commit with staged changes."""
    try:
        repo = Repository()
        commit_hash = repo.create_commit(message)
        click.echo(f"Created commit: {commit_hash[:8]}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@cli.command()
@click.option("--max-entries", type=int, help="Maximum number of entries to display")
def log(max_entries: Optional[int]):
    """Show commit history."""
    try:
        repo = Repository()
        repo.log(max_entries)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@cli.command()
@click.argument("commit_hash")
def show(commit_hash: str):
    """Show changes in a specific commit."""
    try:
        repo = Repository()
        repo.show_commit_diff(commit_hash)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@cli.command()
@click.argument("commit_hash", required=False)
@click.argument("paths", nargs=-1, type=click.Path())
def restore(commit_hash: Optional[str], paths):
    """Restore files from a commit."""
    try:
        repo = Repository()
        repo.restore(commit_hash, paths if paths else None)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--source", "-s", help="Source commit to restore from")
@click.option("--staged", is_flag=True, help="Restore staged changes")
@click.option("--hard", is_flag=True, help="Discard all local changes")
def restore(paths, source, staged, hard):
    """Restore files or working tree state.
    Examples:
        pygrits restore file.txt              # Restore file from staging area
        pygrits restore --source HEAD file.txt # Restore file from HEAD
        pygrits restore --staged file.txt     # Restore staged changes
        pygrits restore --hard                # Discard all local changes
    """
    try:
        repo = Repository()
        if hard:
            if click.confirm("This will discard all local changes. Continue?"):
                repo.restore_hard()
                click.echo("Restored working tree to HEAD")
        elif paths:
            repo.restore(paths=paths, source=source, staged=staged)
            click.echo(f"Restored {len(paths)} file(s)")
        else:
            click.echo("Error: Either specify paths or use --hard", err=True)
            exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


if __name__ == "__main__":
    cli()
