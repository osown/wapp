import logging
from pathlib import Path

from wapp.config import Config

logger = logging.getLogger()

WRAPPER_SRC = """import runpy
import os
import sys

def main():  
    wapp_files_path = os.path.join(os.path.dirname(__file__), "{wrapped_repo}")
    script_path = os.path.join(wapp_files_path, "{script_target}")

    sys.path.insert(0, wapp_files_path)
    runpy.run_path(script_path, run_name="__main__")

if __name__ == "__main__":
    main()
"""


class Wrapper(Config):

    def __init__(self, package_name: str, script_target: str) -> None:
        self.package_name = package_name
        self.script_target = script_target

    def write(self, filename: Path):
        with open(str(filename), "w", encoding="utf-8") as f:
            f.write(
                WRAPPER_SRC.format(
                    script_target=self.script_target, wrapped_repo=self.package_name
                )
            )
            logger.debug("Created %s", filename)
