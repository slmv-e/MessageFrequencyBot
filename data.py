from dataclasses import dataclass


@dataclass
class User:
    id: int
    full_name: str
    last_time: int
    messages_difference: list[int]


@dataclass
class UsersInfo:
    users: list[User]
