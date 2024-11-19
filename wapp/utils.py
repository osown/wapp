import re
import subprocess
from pathlib import Path

import git


def get_git_version_string(repo: git.Repo) -> str:
    latest_commit = repo.head.commit
    short_commit_id = repo.git.rev_parse(latest_commit.hexsha, short=7)
    formatted_date = latest_commit.committed_datetime.strftime("%Y%m%d.%H%M%S")
    version = f"0.0.0.dev0+{formatted_date}.{short_commit_id}"
    return version


def validate_package_name(repo_name: str) -> bool:
    result = re.match(r"^[a-zA-Z0-9_]*$", repo_name)
    return True if result else False


def normalize_package_name(repo_name: str) -> str:
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
    result = subprocess.run(
        ["pipx", "update", package_name],
        encoding="utf-8",
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout


def install_via_pipx(path: Path) -> str:
    result = subprocess.run(
        ["pipx", "install", path.absolute()],
        encoding="utf-8",
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout
