import json
from typing import NamedTuple


class JSONConfig(NamedTuple):
    admin_ids: list[str]
    chat_ids: list[str]


def read_from_json() -> JSONConfig:
    with open("config.json", 'r') as f:
        data = json.load(f)
    res = JSONConfig(admin_ids=data.get("ADMIN_IDS"), chat_ids=data.get("CHAT_IDS"))
    return res


def dump_to_json(key: str, value):
    with open("config.json", 'r') as f:
        data = json.load(f)
    data[key] = value
    with open("config.json", 'w') as f:
        json.dump(data, f, indent=4)
