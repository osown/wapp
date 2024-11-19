from abc import ABC, abstractmethod
from pathlib import Path


class Config(ABC):
    @abstractmethod
    def write(self, filename: Path):
        pass
