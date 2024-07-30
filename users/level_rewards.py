from abc import ABC, abstractmethod


class Reward(ABC):
    @abstractmethod
    def __init__(self, amount) -> None:
        self.amount = amount

    @abstractmethod
    def to_user(self):
        """Returns a string representation of the reward for the user"""
        pass

    @abstractmethod
    def to_sql(self):
        """Returns SQL script for the reward. Should be used with $1 user (telegram_id) parameter only"""
        pass


class Currency(Reward):
    def __init__(self, Amount) -> None:
        self.amount = Amount

    def to_user(self):
        return f"{self.amount}$"

    def to_sql(self):
        return f"UPDATE users SET currency = currency + {self.amount} WHERE telegram_id = $1"


REWARD_DICT: dict[int, Reward] = {i: Currency(i * 2000) for i in range(100)}
