import logging
import re
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Optional

from giturlparse import parse as parse_giturl

from wapp.config import Config

logger = logging.getLogger()


class Requirements(Config):

    @staticmethod
    def _extract_package_name(string: str):
        result = re.match(r"^([a-zA-Z0-9_]*).*$", string)
        if result:
            return result.group(1)

    def __init__(self, conf: Optional[Dict] = None) -> None:
        self.new_conf = OrderedDict()
        if conf:
            self.conf = conf.copy()
        else:
            self.conf = OrderedDict()

    @staticmethod
    def from_config(filename: Path) -> "Requirements":
        old_conf = OrderedDict()
        with open(str(filename), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                package_name = Requirements._extract_package_name(line)
                old_conf[package_name] = line
        logger.debug("Loaded %s", filename)
        return Requirements(conf=old_conf)

    def add_dependency(self, dependency: str):
        parsed = parse_giturl(dependency, check_domain=False)
        if parsed.valid:
            dependency = f"{parsed.name} @ {dependency}"

        package_name = Requirements._extract_package_name(dependency)
        self.new_conf[package_name] = dependency

    def write(self, filename: Path) -> OrderedDict:
        # Merge old requirements with new requirements
        merged_conf = self.conf.copy()
        merged_conf.update(self.new_conf)

        with open(str(filename), "w", encoding="utf-8") as f:
            for item in merged_conf.values():
                f.write(item)
                f.write("\n")
        logger.debug("Created %s", filename)
        return merged_conf
