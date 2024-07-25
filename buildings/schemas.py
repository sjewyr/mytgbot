from pydantic import BaseModel


class Building(BaseModel):
    """
    Model for building entity.
    """

    id: int
    cost: int
    name: str
    income: int

    def get_info(self):
        """Get information for user"""
        return str(f"[{self.name} ({self.cost}$)]: {self.income}$\мин")


class BuildingInfo(BaseModel):
    """
    Model for building info entity.
    """

    cost: int
    name: str
    income: int
