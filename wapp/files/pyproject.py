import logging
from pathlib import Path
from typing import Dict, Optional

from tomlkit import dump as dump_toml
from tomlkit import load as load_toml

from wapp.config import Config

logger = logging.getLogger()


class Pyproject(Config):

    PYPROJECT_SRC = {
        "build-system": {
            "requires": ["setuptools", "wheel"],
            "build-backend": "setuptools.build_meta",
        },
        "project": {
            "dynamic": ["dependencies"],
            "name": "__NAME__",
            "version": "__VERSION__",
            "scripts": {},
        },
        "tool": {
            "setuptools": {
                "include-package-data": True,
                "package-data": {"*": ["*", "*/**"]},
                "dynamic": {"dependencies": {"file": ["requirements.txt"]}},
                "py-modules": ["__NAME__"],
                "packages": {"find": {"where": ["src"]}},
            }
        },
    }

    def __init__(self, conf: Optional[Dict] = None) -> None:
        self.scripts = {}
        self.name = ""
        self.version = ""
        if conf:
            self.conf = dict(conf)
            self.name = conf["project"]["name"]
            for target, link in conf["project"]["scripts"].items():
                link = link.removeprefix("wrapped_")
                link = "".join([link.split(":")[0], ".py"])
                self.scripts[link] = target
            self.version = conf["project"]["version"]
        else:
            self.conf = Pyproject.PYPROJECT_SRC.copy()

    @staticmethod
    def from_config(filename: Path) -> "Pyproject":
        conf = {}
        with open(str(filename), "r", encoding="utf-8") as f:
            conf = load_toml(f).unwrap()

        logger.debug("Loaded %s", filename)
        return Pyproject(conf)

    def add_script(self, script_target: str, link_name: str):
        self.scripts[link_name] = script_target

    def set_name(self, name: str):
        self.name = name

    def set_version(self, version: str):
        self.version = version

    def write(self, filename: Path):
        name = self.name
        if not name:
            logger.warning('No package name set, defaulting to name "package"')
            name = "package"

        version = self.version
        if not version:
            logger.warning('No package version set, defaulting to name "0.0.0"')
            version = "0.0.0"

        self.conf["project"]["name"] = self.name
        self.conf["project"]["version"] = self.version
        self.conf["tool"]["setuptools"]["py-modules"] = []
        for link_name, script_target in self.scripts.items():
            script_target = script_target.removesuffix(".py")

            self.conf["tool"]["setuptools"]["py-modules"].append(
                f"wrapped_{script_target}"
            )
            self.conf["project"]["scripts"][
                link_name
            ] = f"wrapped_{self.name}.wrapped_{script_target}:main"

        with open(str(filename), "w", encoding="utf-8") as f:
            dump_toml(self.conf, f)

        logger.debug("Created %s", filename)
