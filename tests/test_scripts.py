"""
Test student-created utility scripts.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import subprocess
from pathlib import Path
import sqlite3


def test_executables():
    """Verify insta485run, insta485test, insta485db are executables."""
    assert_is_shell_script("bin/insta485run")
    assert_is_shell_script("bin/insta485test")
    assert_is_shell_script("bin/insta485db")
    assert_is_shell_script("bin/insta485install")


def test_insta485install():
    """Verify insta485test contains the right commands."""
    insta485test_content = Path("bin/insta485install")\
        .read_text(encoding='utf-8')
    assert "python3 -m venv" in insta485test_content
    assert "source env/bin/activate" in insta485test_content
    assert "pip install -r requirements.txt" in insta485test_content
    assert "pip install -e ." in insta485test_content
    assert "npm ci ." in insta485test_content


def test_insta485db_random():
    """Verify insta485db reset does a destroy and a create."""
    # Clean up
    db_path = Path("var/insta485.sqlite3")
    if db_path.exists():
        db_path.unlink()

    # Run "insta485db reset && insta485db random"
    subprocess.run(["bin/insta485db", "reset"], check=True)
    subprocess.run(["bin/insta485db", "random"], check=True)

    # Connect to the database
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")

    # Get the number of posts from the database
    cur = connection.execute("SELECT count(*) FROM posts")
    num_rows = cur.fetchone()[0]
    assert num_rows > 100


def assert_is_shell_script(path):
    """Assert path is an executable shell script."""
    path = Path(path)
    assert path.exists()
    output = subprocess.run(
        ["file", path],
        check=True, stdout=subprocess.PIPE, universal_newlines=True,
    ).stdout
    assert "shell script" in output
    assert "executable" in output
