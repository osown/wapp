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

    script_dir = os.path.dirname("{script_target}")
    if script_dir:
        additional_dir = os.path.join(wapp_files_path, script_dir)
        sys.path.insert(0, additional_dir)
    
    runpy.run_path(script_path, run_name="__main__")

if __name__ == "__main__":
    main()
"""


class Wrapper(Config):
    """
    A wrapper class that creates a Python file containing the necessary
    code to execute the wrapped script. This class is responsible for writing
    the wrapper file to disk.

    Attributes:
        package_name (str): The name of the  package being wrapped.
        script_target (str): The path to the target script to be executed.
    """

    def __init__(self, package_name: str, script_target: str) -> None:
        """
        Initializes a new Wrapper instance.

        Args:
            package_name (str): The name of the package being wrapped.
            script_target (str): The path to the target script to be executed.
        """
        self.package_name = package_name
        self.script_target = script_target

    def write(self, filename: Path):
        """
        Writes the wrapper file to disk.

        Args:
            filename (Path): The path where the wrapper file will be written.
        """
        with open(str(filename), "w", encoding="utf-8") as f:
            f.write(
                WRAPPER_SRC.format(
                    script_target=self.script_target, wrapped_repo=self.package_name
                )
            )
            logger.debug("Created %s", filename)
