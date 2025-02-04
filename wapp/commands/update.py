import logging
from pathlib import Path

import git
import git.exc

from wapp.commands import wrap_project
from wapp.files.pyproject import Pyproject
from wapp.files.requirements import Requirements
from wapp.utils import build_wheel, get_git_version_string, update_via_pipx

logger = logging.getLogger(__name__)


def update(args):
    dest_dir = args.wrapped_dir  # type: Path
    install = args.pipx  # type: bool

    requires = []
    custom_requirements_path = dest_dir.joinpath("custom_requirements.txt")
    if custom_requirements_path.exists():
        custom_requirements = Requirements.from_config(custom_requirements_path)
        requires = custom_requirements.conf.values()

    wapp_identifier_path = dest_dir.joinpath(".wapp")
    if not wapp_identifier_path.exists():
        raise RuntimeError("Seems to be not a wapp-wrapped project, are you sure?")

    pyproject_path = dest_dir.joinpath("pyproject.toml")
    if not pyproject_path.exists():
        raise RuntimeError(
            "Seems to be not a wapp-wrapped project, missing pyproject.toml"
        )

    pyproject = Pyproject.from_config(pyproject_path)
    package_name = pyproject.name
    scripts = pyproject.scripts
    version = pyproject.version

    logger.debug("Old package version %s", version)
    logger.info("Updating Repo")
    repo_dir = dest_dir.joinpath("src", f"wrapped_{pyproject.name}", pyproject.name)
    try:
        repo = git.Repo(repo_dir)
        version = get_git_version_string(repo)

        repo.remotes.origin.pull()
    except git.exc.NoSuchPathError as e:
        raise RuntimeError(
            f'Seems to be not a wapp-wrapped projection, reason: "{repo_dir}" not a git repo'
        ) from e

    if pyproject.version != version:
        logger.info("Updated package from %s to %s", pyproject.version, version)

        wrap_project(dest_dir, repo_dir, requires, package_name, version, scripts)
        wheel_path = build_wheel(dest_dir)

        logger.info("Successfully updated wrapped package %s", package_name)

        if install:
            logger.info('Running "pipx upgrade %s":', wheel_path)
            retval, output = update_via_pipx(wheel_path.absolute())
            [logger.info("  %s", line) for line in output.splitlines()]
            logger.info("pipx exited with: %d", retval)
        else:
            logger.info('Run "pipx upgrade %s" to update package', wheel_path)
    else:
        logger.info("Already latest revision %s", version)
