from typing import Optional

from pydantic import BaseModel


class Summary(BaseModel):
    total_spent: float
    transaction_count: int
    average_transaction: float
    largest_transaction: float
    smallest_transaction: float
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    daily_average: float = 0.0


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int
    percentage: float


class TimeSeriesPoint(BaseModel):
    period: str
    total: float


class MerchantStat(BaseModel):
    description: str
    total: float
    count: int


class RecurringExpense(BaseModel):
    description: str
    average_amount: float
    occurrences: int
    estimated_monthly: float


class Recommendation(BaseModel):
    severity: str  # info | warning | critical | success
    title: str
    message: str
    icon: str = "💡"


class AnalysisResponse(BaseModel):
    summary: Summary
    by_category: list[CategoryBreakdown]
    by_month: list[TimeSeriesPoint]
    by_weekday: list[TimeSeriesPoint]
    top_merchants: list[MerchantStat]
    recurring: list[RecurringExpense]
    recommendations: list[Recommendation]


class ChatRequest(BaseModel):
    question: str
    category: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
