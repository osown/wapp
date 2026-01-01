import logging
from pathlib import Path
from typing import List

from git import Repo as GitRepo
from giturlparse import parse as parse_giturl

from wapp.commands import wrap_project
from wapp.utils import (
    build_wheel,
    get_git_version_string,
    install_via_pipx,
    normalize_package_name,
    validate_package_name,
    is_python_file
)

logger = logging.getLogger(__name__)


def create(args):
    script_args = args.scripts  # type: List[str]
    requires = args.requires  # type: List[str]
    repo_url = args.repo_url  # type: str
    install = args.pipx  # type: bool

    # Script validation
    scripts = {}
    for script_arg in script_args:
        splitted_script = script_arg.split(":")
        if len(splitted_script) == 1:
            script_target, link_name = splitted_script, splitted_script
        if len(splitted_script) == 2:
            script_target, link_name = splitted_script
            if not script_target or not link_name:
                raise RuntimeError("Target or link name cannot be empty")
        else:
            raise RuntimeError("Too many : in the specification of scripts")
        scripts[script_target] = link_name

    # Repo URL validation
    parsed_repo_url = parse_giturl(repo_url, check_domain=False)
    if not parsed_repo_url.valid:
        raise RuntimeError(f'Git repo "{repo_url}" invalid, specify another repo')

    # Package name validation
    package_name = args.package_name  # type: str
    if package_name:
        if not validate_package_name(package_name):
            raise RuntimeError(
                f'Specified invalid repo name  "{package_name}", only alphanumeric values and underscores are allowed'
            )
    else:
        package_name = normalize_package_name(parsed_repo_url.name)

    # Destination validation
    dest_dir = (
        args.dest_dir if args.dest_dir else Path().cwd() / package_name
    )  # type: Path

    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created %s", dest_dir)

    if dest_dir.exists() and list(dest_dir.iterdir()):
        raise RuntimeError(
            f'Destination "{dest_dir}" not empty, change directory or #specify another destination'
        )

    repo_dir = dest_dir / "src" / f"wrapped_{package_name}" / package_name
    repo_dir.mkdir(exist_ok=True, parents=True)

    # Clone repo
    name_components = parsed_repo_url.name.rsplit("@")
    branch = ""
    if len(name_components) == 2:
        branch = name_components[1]

    repo_url = repo_url.removesuffix(f"@{branch}")

    logger.info("Cloning %s into %s", repo_url, repo_dir)
    repo = GitRepo.clone_from(url=repo_url, to_path=repo_dir)
    if branch:
        logger.info("Switching branch to %s", branch)
        repo.git.checkout(branch)
    version = get_git_version_string(repo)

    # Enumerate python scripts to be exposed as executable
    # If scripts is not define, auto-discover them
    logger.info("Enumerating exposed scripts:")
    path_list = [
        path.name
        for path in repo_dir.iterdir()
        if is_python_file(path)
    ]
    if not scripts:
        scripts.update({path: path for path in path_list})
    else:
        path_list_complete = [
            str(path.relative_to(repo_dir))
            for path in repo_dir.glob("**/*")
            if is_python_file(path)
        ]
        for script_target in scripts.keys():
            if script_target not in path_list_complete:
                raise RuntimeError(f'Target script "{script_target}" not found')

    wrap_project(dest_dir, repo_dir, requires, package_name, version, scripts)
    wheel_path = build_wheel(dest_dir)

    logger.info("Successfully created wrapped package %s", package_name)
    logger.info("Package revision: %s", version)

    if install:
        logger.info('Running "pipx install %s":', wheel_path)
        retval, output = install_via_pipx(wheel_path.absolute())
        [logger.info("  %s", line) for line in output.splitlines()]
        logger.info("pipx exited with: %d", retval)
    else:
        logger.info('Run "pipx install %s" to install package', wheel_path)
