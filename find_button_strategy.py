from abc import ABC, abstractmethod

from pyscreeze import Box

class FindButtonStrategy(ABC):
    @abstractmethod
    def find_button(button) -> Box | None: