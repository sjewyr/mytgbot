import pydantic


class Building(pydantic.BaseModel):
    id: int
    cost: int
    income: int