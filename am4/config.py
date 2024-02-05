import json
import os


class ConfigBase:
    def __init__(self, cfg: dict):
        for k, v in cfg.items():
            print(k, hasattr(self, k), v)
            if hasattr(self, k):
                setattr(self, k, v)

    @classmethod
    def from_json(cls, fn: str):
        with open(fn) as f:
            return cls(json.load(f))


production = os.environ.get("PRODUCTION") == "1"
