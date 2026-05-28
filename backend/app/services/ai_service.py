"""Serviço de IA: extração de transações e chat financeiro.

Usa a API da OpenAI com saída JSON estruturada (eliminando parsing frágil).
Quando nenhuma chave de API está configurada, recai sobre um extrator
heurístico baseado em regex, de forma que a aplicação continua utilizável.
"""
import json
import re
from datetime import date, datetime
from typing import Optional

from app.core.config import settings

_MONTHS_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}


def _client():
    """Cria o cliente OpenAI sob demanda (evita falha no import sem a lib)."""
    from openai import OpenAI

    return OpenAI(api_key=settings.OPENAI_API_KEY)


# --------------------------------------------------------------------------- #
# Extração de transações
# --------------------------------------------------------------------------- #
def extract_transactions(text: str, categories: list[dict]) -> list[dict]:
    """Extrai transações do texto da fatura.

    `categories` é uma lista de dicts com chaves `name` e `examples`.
    Retorna lista de dicts: {date, description, amount, category}.
    """
    if settings.ai_enabled:
        try:
            return _extract_with_ai(text, categories)
        except Exception as exc:  # noqa: BLE001 - degrada para heurística
            print(f"[ai_service] Falha na extração via IA: {exc}. Usando heurística.")
    return _extract_heuristic(text, categories)


def _category_names(categories: list[dict]) -> list[str]:
    names = [c["name"] for c in categories] or ["Outros"]
    if "Outros" not in names:
        names.append("Outros")
    return names


def _extract_with_ai(text: str, categories: list[dict]) -> list[dict]:
    catalog = "\n".join(
        f"- {c['name']}" + (f" (exemplos: {c['examples']})" if c.get("examples") else "")
        for c in categories
    )
    names = _category_names(categories)

    system = (
        "Você é um especialista em extrair transações de faturas de cartão de "
        "crédito brasileiras (Nubank). Responda SOMENTE com JSON válido."
    )
    user = f"""
Extraia TODAS as transações de compra do texto da fatura abaixo.

Regras:
1. IGNORE linhas de "Pagamento recebido", totais, saldos e cabeçalhos.
2. Extraia apenas compras/gastos individuais.
3. Datas no formato ISO "YYYY-MM-DD".
4. Valores como número decimal com ponto (ex.: 25.90), sempre positivo.
5. Classifique cada transação em UMA das categorias disponíveis. Se não houver
   correspondência clara, use "Outros".

Categorias disponíveis:
{catalog}

Responda EXATAMENTE neste formato JSON:
{{"transactions": [{{"date": "YYYY-MM-DD", "description": "...", "amount": 0.00, "category": "..."}}]}}

TEXTO DA FATURA:
{text}
"""

    response = _client().chat.completions.create(
        model=settings.OPENAI_MODEL_EXTRACTION,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    payload = json.loads(response.choices[0].message.content)
    raw = payload.get("transactions", []) if isinstance(payload, dict) else []
    return _normalize(raw, names)


def _normalize(raw: list[dict], valid_categories: list[str]) -> list[dict]:
    """Valida e normaliza transações vindas da IA."""
    result: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            parsed_date = _parse_date(str(item.get("date", "")))
            amount = _parse_amount(item.get("amount"))
            description = str(item.get("description", "")).strip()
            if not description or amount <= 0 or parsed_date is None:
                continue
            category = str(item.get("category", "Outros")).strip()
            if category not in valid_categories:
                category = "Outros"
            result.append(
                {
                    "date": parsed_date,
                    "description": description[:255],
                    "amount": round(amount, 2),
                    "category": category,
                }
            )
        except Exception:  # noqa: BLE001
            continue
    return result


def _parse_date(value: str) -> Optional[date]:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_amount(value) -> float:
    if isinstance(value, (int, float)):
        return abs(float(value))
    text = str(value).replace("R$", "").replace("$", "").strip()
    # Formato brasileiro 1.250,90 -> 1250.90
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return abs(float(text))
    except ValueError:
        nums = re.findall(r"[\d.]+", text)
        return abs(float(nums[0])) if nums else 0.0


# --------------------------------------------------------------------------- #
# Extrator heurístico (sem IA)
# --------------------------------------------------------------------------- #
def _extract_heuristic(text: str, categories: list[dict]) -> list[dict]:
    """Extrai transações por regex quando a IA não está disponível.

    Reconhece linhas típicas do Nubank como "15 SET Padaria 25,90".
    """
    names = _category_names(categories)
    keyword_map = _build_keyword_map(categories)
    results: list[dict] = []
    current_year = datetime.now().year

    line_re = re.compile(
        r"^\s*(\d{1,2})\s+([A-Za-zçÇ]{3})\.?\s+(.+?)\s+"
        r"(-?\d{1,3}(?:\.\d{3})*,\d{2}|-?\d+,\d{2})\s*$"
    )
    iso_re = re.compile(
        r"^\s*(\d{4}-\d{2}-\d{2})\s+(.+?)\s+"
        r"(-?\d{1,3}(?:\.\d{3})*,\d{2}|-?\d+,\d{2})\s*$"
    )

    for line in text.split("\n"):
        low = line.lower()
        if any(skip in low for skip in ("pagamento", "saldo", "total", "fatura anterior")):
            continue

        m = line_re.match(line)
        parsed = None
        if m:
            day, mon, desc, val = m.groups()
            month = _MONTHS_PT.get(mon.lower()[:3])
            if month:
                try:
                    parsed = (date(current_year, month, int(day)), desc, val)
                except ValueError:
                    parsed = None
        else:
            m2 = iso_re.match(line)
            if m2:
                iso, desc, val = m2.groups()
                d = _parse_date(iso)
                if d:
                    parsed = (d, desc, val)

        if not parsed:
            continue

        d, desc, val = parsed
        amount = _parse_amount(val)
        if amount <= 0:
            continue
        desc = desc.strip()
        results.append(
            {
                "date": d,
                "description": desc[:255],
                "amount": round(amount, 2),
                "category": _guess_category(desc, keyword_map),
            }
        )
    return results


def _build_keyword_map(categories: list[dict]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for cat in categories:
        if not cat.get("examples"):
            continue
        for token in re.split(r"[,\n;]", cat["examples"]):
            token = token.strip().lower()
            if token:
                mapping[token] = cat["name"]
    return mapping


def _guess_category(description: str, keyword_map: dict[str, str]) -> str:
    low = description.lower()
    for keyword, category in keyword_map.items():
        if keyword in low:
            return category
    return "Outros"


# --------------------------------------------------------------------------- #
# Chat financeiro
# --------------------------------------------------------------------------- #
def chat(question: str, context: str) -> str:
    """Responde a uma pergunta do usuário sobre seus dados financeiros."""
    if not settings.ai_enabled:
        return (
            "O assistente de IA não está configurado. Defina a variável de "
            "ambiente OPENAI_API_KEY para conversar com a IA. Enquanto isso, "
            "você pode explorar os gráficos e recomendações no painel de Análise."
        )

    system = (
        "Você é um consultor financeiro pessoal, claro, prático e amigável. "
        "Responda em português do Brasil, use valores em R$ e dê sugestões "
        "acionáveis. Baseie-se apenas nos dados fornecidos."
    )
    user = f"Dados financeiros do usuário:\n{context}\n\nPergunta: {question}"

    response = _client().chat.completions.create(
        model=settings.OPENAI_MODEL_CHAT,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
        max_tokens=900,
    )
    return response.choices[0].message.content.strip()
