from pydantic import BaseModel, ConfigDict, Field


class BudgetBase(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    monthly_limit: float = Field(gt=0)


class BudgetCreate(BudgetBase):
    pass


class BudgetPublic(BudgetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class BudgetStatus(BaseModel):
    category: str
    monthly_limit: float
    spent: float
    remaining: float
    percentage: float
    status: str  # ok | warning | exceeded
