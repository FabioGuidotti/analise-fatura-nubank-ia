from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    icon: str = Field(default="🏷️", max_length=16)
    color: str = Field(default="#6366f1", max_length=16)
    examples: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    icon: Optional[str] = Field(default=None, max_length=16)
    color: Optional[str] = Field(default=None, max_length=16)
    examples: Optional[str] = None


class CategoryPublic(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
