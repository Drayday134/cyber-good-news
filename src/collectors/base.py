"""Base collector interface."""

from abc import ABC, abstractmethod
from typing import List
from ..models import CyberGoodNews


class BaseCollector(ABC):
    """Abstract base class for news collectors."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def collect(self) -> List[CyberGoodNews]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"
