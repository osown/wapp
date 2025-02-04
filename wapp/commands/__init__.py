import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from wapp.files.pyproject import Pyproject
from wapp.files.requirements import Requirements
from wapp.files.wrapper import Wrapper

logger = logging.getLogger(__name__)


def wrap_project(
    dest_dir: Path,
    repo_dir: Path,
    requires: Optional[List[str]],
    package_name: str,
    version: str,
    scripts: Optional[Dict[str, str]],
):
    # Create pyproject
    pyproject = Pyproject()
    pyproject.set_name(package_name)
    pyproject.set_version(version)

    logger.info("Exposed scripts:")
    for script_target, link_name in scripts.items():
        wrapped_script_target = re.sub("[^0-9a-zA-Z.]+", "_", script_target)

        logger.info("  %s -> %s", link_name, wrapped_script_target)

        # Create wrappers
        wrapper = Wrapper(package_name, script_target)
        wrapper_path = dest_dir.joinpath(
            "src", f"wrapped_{package_name}", f"wrapped_{wrapped_script_target}"
        )
        wrapper_path.parent.mkdir(parents=True, exist_ok=True)
        wrapper.write(wrapper_path)

        # Create pyproject.toml
        pyproject.add_script(wrapped_script_target, link_name)

    pyproject.write(dest_dir.joinpath("pyproject.toml"))

    # Create requirements.txt
    requirements = Requirements()
    existing_requirements_path = repo_dir.joinpath("requirements.txt")
    if existing_requirements_path.is_file():
        requirements = requirements.from_config(existing_requirements_path)
    for dependency in requires:
        requirements.add_dependency(dependency)
    logger.debug("Merging requirements:")
    logger.debug("  Old requirements:")
    [
        logger.debug("    %s", item) for item in requirements.conf.values()
    ]  # pylint:disable=W0106
    logger.debug("  New requirements:")
    [
        logger.debug("    %s", item) for item in requirements.new_conf.values()
    ]  # pylint:disable=W0106
    merged_conf = requirements.write(dest_dir.joinpath("requirements.txt"))
    logger.debug("  Merged requirements:")
    [
        logger.debug("    %s", item) for item in merged_conf.values()
    ]  # pylint:disable=W0106

    # Create custom_requirements.txt
    if requires:
        custom_requirements = Requirements()
        for dependency in requires:
            custom_requirements.add_dependency(dependency)
        custom_requirements.write(dest_dir.joinpath("custom_requirements.txt"))

    wapp_identifier_path = dest_dir.joinpath(".wapp")
    wapp_identifier_path.touch(exist_ok=True)
