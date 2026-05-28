"""Motor de análise financeira — cálculos puros sobre transações.

Sem dependência de pandas para manter o backend leve e previsível.
"""
from collections import defaultdict
from datetime import date
from statistics import mean

from app.models.transaction import Transaction

_WEEKDAYS_PT = [
    "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo",
]
_MONTHS_PT = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
]


def build_summary(txs: list[Transaction]) -> dict:
    if not txs:
        return {
            "total_spent": 0.0,
            "transaction_count": 0,
            "average_transaction": 0.0,
            "largest_transaction": 0.0,
            "smallest_transaction": 0.0,
            "period_start": None,
            "period_end": None,
            "daily_average": 0.0,
        }

    amounts = [t.amount for t in txs]
    dates = [t.date for t in txs]
    start, end = min(dates), max(dates)
    span_days = (end - start).days + 1
    total = sum(amounts)

    return {
        "total_spent": round(total, 2),
        "transaction_count": len(txs),
        "average_transaction": round(mean(amounts), 2),
        "largest_transaction": round(max(amounts), 2),
        "smallest_transaction": round(min(amounts), 2),
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "daily_average": round(total / span_days, 2) if span_days else round(total, 2),
    }


def by_category(txs: list[Transaction]) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for t in txs:
        totals[t.category] += t.amount
        counts[t.category] += 1
    grand_total = sum(totals.values()) or 1.0
    result = [
        {
            "category": cat,
            "total": round(total, 2),
            "count": counts[cat],
            "percentage": round(total / grand_total * 100, 1),
        }
        for cat, total in totals.items()
    ]
    return sorted(result, key=lambda x: x["total"], reverse=True)


def by_month(txs: list[Transaction]) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)
    for t in txs:
        key = f"{t.date.year}-{t.date.month:02d}"
        totals[key] += t.amount
    points = [
        {"period": _format_month(key), "total": round(total, 2)}
        for key, total in totals.items()
    ]
    return sorted(points, key=lambda x: x["period"])


def _format_month(key: str) -> str:
    year, month = key.split("-")
    return f"{_MONTHS_PT[int(month) - 1]}/{year}"


def by_weekday(txs: list[Transaction]) -> list[dict]:
    totals: dict[int, float] = defaultdict(float)
    for t in txs:
        totals[t.date.weekday()] += t.amount
    return [
        {"period": _WEEKDAYS_PT[i], "total": round(totals.get(i, 0.0), 2)}
        for i in range(7)
    ]


def top_merchants(txs: list[Transaction], limit: int = 10) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for t in txs:
        key = _normalize_merchant(t.description)
        totals[key] += t.amount
        counts[key] += 1
    merchants = [
        {"description": desc, "total": round(total, 2), "count": counts[desc]}
        for desc, total in totals.items()
    ]
    return sorted(merchants, key=lambda x: x["total"], reverse=True)[:limit]


def _normalize_merchant(description: str) -> str:
    # Agrupa parcelas e variações simples ("Loja 1/3" -> "Loja")
    text = description.strip()
    text = text.split(" - Parcela")[0]
    return text


def recurring_expenses(txs: list[Transaction]) -> list[dict]:
    """Detecta gastos recorrentes (assinaturas) por repetição de descrição."""
    groups: dict[str, list[float]] = defaultdict(list)
    months: dict[str, set] = defaultdict(set)
    for t in txs:
        key = _normalize_merchant(t.description).lower()
        groups[key].append(t.amount)
        months[key].add((t.date.year, t.date.month))

    recurring: list[dict] = []
    for key, amounts in groups.items():
        # Recorrente: aparece em pelo menos 2 meses distintos
        if len(months[key]) >= 2 and len(amounts) >= 2:
            avg = mean(amounts)
            recurring.append(
                {
                    "description": key.title(),
                    "average_amount": round(avg, 2),
                    "occurrences": len(amounts),
                    "estimated_monthly": round(avg, 2),
                }
            )
    return sorted(recurring, key=lambda x: x["estimated_monthly"], reverse=True)[:10]


def current_month_spending_by_category(txs: list[Transaction]) -> dict[str, float]:
    """Gasto do mês corrente por categoria (para acompanhamento de orçamento)."""
    today = date.today()
    totals: dict[str, float] = defaultdict(float)
    for t in txs:
        if t.date.year == today.year and t.date.month == today.month:
            totals[t.category] += t.amount
    return {k: round(v, 2) for k, v in totals.items()}
