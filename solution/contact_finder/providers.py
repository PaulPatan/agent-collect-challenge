from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

class Provider(ABC):
    @abstractmethod
    def lookup(self, company_name: str) -> Dict[str, dict]:
        raise NotImplementedError

class MockProvider(Provider):

    def __init__(self, data: Dict[str, dict]):
        self._data = data

    @classmethod
    def from_file(cls, json_path) -> "MockProvider":
        raw = Path(json_path).read_text(encoding="utf-8")
        return cls(json.loads(raw))

    def lookup(self, company_name: str) -> Dict[str, dict]:
        entry = self._data.get(company_name)
        return dict(entry) if isinstance(entry, dict) else {}
