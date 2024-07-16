from pydantic import BaseModel


class Building(BaseModel):
    id: int
    cost: int
    name: str
    income: int

    def get_info(self):
        return str(f"[{self.name} ({self.cost}$)]: {self.income}$\мин")


class BuildingInfo(BaseModel):
    cost: int
    name: str
    income: int
