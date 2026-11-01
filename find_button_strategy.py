from abc import ABC, abstractmethod

from pyscreeze import Box

from button import Button


class FindButtonStrategy(ABC):
    @abstractmethod
    def find_button(self, button: Button) -> Box | None:
        ...
