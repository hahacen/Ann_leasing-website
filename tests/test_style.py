"""
Check Python style with pycodestyle, pydocstyle and pylint.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import subprocess
import utils


def test_pycodestyle():
    """Run pycodestyle."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    subprocess.run(["pycodestyle", "insta485"], check=True)


def test_pydocstyle():
    """Run pydocstyle."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    subprocess.run(["pydocstyle", "insta485"], check=True)


def test_pylint():
    """Run pylint."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    subprocess.run([
        "pylint",
        "--rcfile", "pyproject.toml",
        "insta485",
    ], check=True)


def test_eslint():
    """Run eslint."""
    assert_no_prohibited_terms("eslint-disable", "jQuery", "XMLHttpRequest")
    subprocess.run([
        "npx", "eslint",
        "--ext", "js,jsx,ts,tsx",
        "--no-inline-config",
        "--no-eslintrc",
        "--config", utils.TEST_DIR/"testdata/eslintrc.js",
        "insta485/js/",
    ], check=True)


def test_prettier():
    """Run Prettier."""
    assert_no_prohibited_terms("prettier-disable")
    subprocess.run([
        "npx", "prettier",
        "--check",
        "insta485/js",
    ], check=True)


def assert_no_prohibited_terms(*terms):
    """Check for prohibited terms before testing style."""
    for term in terms:
        completed_process = subprocess.run(
            [
                "grep",
                "-r",
                "-n",
                term,
                "--include=*.py",
                "--include=*.jsx",
                "--include=*.js",
                "--include=*.tsx",
                "--include=*.ts",
                "--exclude=__init__.py",
                "--exclude=bundle.js",
                "--exclude=*node_modules/*",
                "insta485",
            ],
            check=False,  # We'll check the return code manually
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        # Grep exit code should be non-zero, indicating that the prohibited
        # term was not found.  If the exit code is zero, crash and print a
        # helpful error message with a filename and line number.
        assert completed_process.returncode != 0, (
            f"The term \'{term}\' is prohibited.\n{completed_process.stdout}"
        )
