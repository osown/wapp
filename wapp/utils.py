import re
import subprocess
from pathlib import Path

import git
from build import ProjectBuilder


def get_git_version_string(repo: git.Repo) -> str:
    """
    Generate a version string based on the latest commit in the repository.

    Args:
        repo (git.Repo): The Git repository object.

    Returns:
        str: A version string in the format "0.0.0.dev0+YYYYMMDD.HHMMSS.short_commit_id".
    """
    latest_commit = repo.head.commit
    short_commit_id = repo.git.rev_parse(latest_commit.hexsha, short=7)
    formatted_date = latest_commit.committed_datetime.strftime("%Y%m%d.%H%M%S")
    version = f"0.0.0.dev0+{formatted_date}.{short_commit_id}"
    return version


def validate_package_name(repo_name: str) -> bool:
    """
    Check if a package name is valid (contains only alphanumeric characters and underscores).

    Args:
        repo_name (str): The package name to check.

    Returns:
        bool: True if the package name is valid, False otherwise.
    """
    result = re.match(r"^[a-zA-Z0-9_]*$", repo_name)
    return True if result else False


def normalize_package_name(repo_name: str) -> str:
    """
    Normalize a package name by replacing invalid characters with underscores and removing duplicates.

    Args:
        repo_name (str): The package name to normalize.

    Returns:
        str: The normalized package name.
    """
    normalized_repo_name = re.sub(
        r"[^0-9a-zA-Z]+",
        "_",
        repo_name,
    )
    normalized_repo_name = re.sub(
        "(_)\1+",
        r"\1 ",
        normalized_repo_name,
    )

    normalized_repo_name = normalized_repo_name.removeprefix("-").removesuffix("-")
    return normalized_repo_name


def update_via_pipx(package_name: str) -> None:
    """
    Update a package using pipx.

    Args:
        package_name (str): The name of the package to update.
    """
    result = subprocess.run(
        ["pipx", "update", package_name],
        encoding="utf-8",
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout


def install_via_pipx(path: Path) -> str:
    """
    Install a package using pipx.

    Args:
        path (Path): The path to the package to install.
    """
    result = subprocess.run(
        ["pipx", "install", path.absolute()],
        encoding="utf-8",
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout


def build_wheel(path: Path) -> Path:
    """
    Build a wheel for the package at the given path.

    Args:
        path (Path): The path to the package directory.

    Returns:
        Path: The path to the built wheel file.
    """
    builder = ProjectBuilder(path)
    out_dir = path / "dist"
    builder.build("wheel", output_directory=out_dir)
    wheel = list(out_dir.iterdir())[0]
    return wheel


def is_python_file(path: Path) -> bool:
    if path.is_file():
        if path.suffix == ".py":
            return True
        else:
            with open(str(path.resolve()), "r", errors='ignore') as file:
                if "#!/usr/bin/env python" in file.readline():
                    return True
    return False
        