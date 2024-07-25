from pydantic import BaseModel


class UserTask(BaseModel):
    """
    Represents a user's task.
    """

    id: int
    name: str
    reward: int
    exp_reward: int
    lvl_required: int
    cost: int
    length: int

    def get_info(self):
        """Returns a formatted string containing the task's details for user."""
        return f"{self.name} [{self.cost}$]: {self.reward}$ + {self.exp_reward}exp, {self.length}m"
