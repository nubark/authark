import json
from typing import Dict
from abc import ABC, abstractmethod


class HashService(ABC):
    @abstractmethod
    def generate_hash(self, value: str) -> str:
        "Generate method to be implemented."


class MemoryHashService(HashService):
    def generate_hash(self, value: str) -> str:
        return "HASHED: {}".format(value)
