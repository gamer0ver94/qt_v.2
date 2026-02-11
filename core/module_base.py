from abc import ABC, abstractmethod


class BaseModule(ABC):

    def __init__(self, app):
        self.app = app

    @abstractmethod
    def name(self) -> str:
        """Display name of the module"""
        pass

    @abstractmethod
    def build(self, parent):
        """Build module UI inside given parent frame"""
        pass
