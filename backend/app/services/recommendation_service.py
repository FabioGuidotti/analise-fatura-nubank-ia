"""Motor de recomendações financeiras baseado em regras.

Gera insights acionáveis a partir dos dados analisados, sem depender de IA
(funciona 100% offline). As recomendações alimentam a aba "Recomendações".
"""
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.services import analysis_service


def generate(txs: list[Transaction], budgets: list[Budget]) -> list[dict]:
    recommendations: list[dict] = []
    if not txs:
        return [
            {
                "severity": "info",
                "icon": "📥",
                "title": "Comece importando uma fatura",
                "message": "Importe seu PDF do Nubank para receber análises e "
                "recomendações personalizadas dos seus gastos.",
            }
        ]

    summary = analysis_service.build_summary(txs)
    categories = analysis_service.by_category(txs)
    months = analysis_service.by_month(txs)
    recurring = analysis_service.recurring_expenses(txs)

    _check_top_category(recommendations, categories, summary)
    _check_month_trend(recommendations, months)
    _check_budgets(recommendations, txs, budgets)
    _check_recurring(recommendations, recurring)
    _check_savings_opportunity(recommendations, categories, summary)

    if not recommendations:
        recommendations.append(
            {
                "severity": "success",
                "icon": "✅",
                "title": "Seus gastos estão equilibrados",
                "message": "Nenhum alerta relevante encontrado. Continue "
                "acompanhando seus gastos regularmente.",
            }
        )
    return recommendations


def _check_top_category(recs, categories, summary):
    if not categories:
        return
    top = categories[0]
    if top["percentage"] >= 40:
        recs.append(
            {
                "severity": "warning",
                "icon": "🎯",
                "title": f"Concentração em {top['category']}",
                "message": f"{top['percentage']:.0f}% dos seus gastos "
                f"(R$ {top['total']:,.2f}) estão em {top['category']}. "
                "Avalie se há espaço para reduzir nessa categoria.",
            }
        )


def _check_month_trend(recs, months):
    if len(months) < 2:
        return
    last, previous = months[-1], months[-2]
    if previous["total"] <= 0:
        return
    change = (last["total"] - previous["total"]) / previous["total"] * 100
    if change >= 20:
        recs.append(
            {
                "severity": "critical",
                "icon": "📈",
                "title": "Gastos em alta",
                "message": f"Seus gastos subiram {change:.0f}% de "
                f"{previous['period']} para {last['period']} "
                f"(R$ {previous['total']:,.2f} → R$ {last['total']:,.2f}).",
            }
        )
    elif change <= -15:
        recs.append(
            {
                "severity": "success",
                "icon": "📉",
                "title": "Você economizou!",
                "message": f"Seus gastos caíram {abs(change):.0f}% de "
                f"{previous['period']} para {last['period']}. Continue assim!",
            }
        )


def _check_budgets(recs, txs, budgets):
    if not budgets:
        return
    spent = analysis_service.current_month_spending_by_category(txs)
    for budget in budgets:
        used = spent.get(budget.category, 0.0)
        if budget.monthly_limit <= 0:
            continue
        pct = used / budget.monthly_limit * 100
        if pct >= 100:
            recs.append(
                {
                    "severity": "critical",
                    "icon": "🚨",
                    "title": f"Orçamento estourado: {budget.category}",
                    "message": f"Você já gastou R$ {used:,.2f} de R$ "
                    f"{budget.monthly_limit:,.2f} ({pct:.0f}%) em "
                    f"{budget.category} neste mês.",
                }
            )
        elif pct >= 80:
            recs.append(
                {
                    "severity": "warning",
                    "icon": "⚠️",
                    "title": f"Orçamento quase no limite: {budget.category}",
                    "message": f"Você já usou {pct:.0f}% do orçamento de "
                    f"{budget.category} (R$ {used:,.2f} de "
                    f"R$ {budget.monthly_limit:,.2f}).",
                }
            )


def _check_recurring(recs, recurring):
    if not recurring:
        return
    total_monthly = sum(r["estimated_monthly"] for r in recurring)
    top_names = ", ".join(r["description"] for r in recurring[:3])
    recs.append(
        {
            "severity": "info",
            "icon": "🔁",
            "title": "Gastos recorrentes detectados",
            "message": f"Identificamos ~R$ {total_monthly:,.2f}/mês em gastos "
            f"recorrentes (ex.: {top_names}). Revise assinaturas que não usa.",
        }
    )


def _check_savings_opportunity(recs, categories, summary):
    targets = {"Alimentação", "Lazer", "Restaurantes", "Delivery", "Compras"}
    candidates = [c for c in categories if c["category"] in targets]
    if not candidates:
        return
    top = max(candidates, key=lambda c: c["total"])
    potential = top["total"] * 0.15
    if potential >= 30:
        recs.append(
            {
                "severity": "info",
                "icon": "💰",
                "title": "Oportunidade de economia",
                "message": f"Reduzindo 15% em {top['category']} você "
                f"economizaria cerca de R$ {potential:,.2f} no período.",
            }
        )
