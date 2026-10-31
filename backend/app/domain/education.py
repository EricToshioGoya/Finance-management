"""SPEC-035 — versioned, reviewed-in-code educational glossary.

One immutable catalog drives search, suggestions and contextual explanations.
Editorial approval for expansion/translations remains OPEN-30.
"""

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Article:
    key: str
    title_pt: str
    title_en: str
    body_pt: str
    body_en: str
    level: int
    tags: tuple[str, ...]


CATALOG_VERSION = "education-v1"
ARTICLES: tuple[Article, ...] = (
    Article(
        "cdi",
        "CDI",
        "CDI",
        (
            "O CDI é uma taxa de referência do mercado interbancário brasileiro. "
            "Produtos atrelados ao CDI podem render um percentual dessa taxa; "
            "rendimento e risco dependem do produto."
        ),
        (
            "CDI is a Brazilian interbank benchmark rate. Investments linked to it "
            "may yield a percentage of that rate; returns and risks depend on the "
            "specific product."
        ),
        0,
        ("cdi", "taxa", "renda fixa", "fixed income", "interest"),
    ),
    Article(
        "interest-rate",
        "Taxa de juros",
        "Interest rate",
        (
            "A taxa de juros indica o custo de um empréstimo ou a remuneração de um "
            "capital ao longo do tempo. Taxas anuais e mensais precisam ser "
            "convertidas de forma equivalente em juros compostos."
        ),
        (
            "An interest rate describes borrowing costs or capital growth over time. "
            "Annual and monthly rates require equivalent compounding conversions."
        ),
        0,
        ("juros", "taxa", "rate", "calculator", "simulador"),
    ),
    Article(
        "compound-interest",
        "Juros compostos",
        "Compound interest",
        (
            "Em juros compostos, os rendimentos acumulados também passam a render. O "
            "resultado depende da taxa, do prazo e do momento dos aportes."
        ),
        (
            "With compound interest, accumulated returns also earn returns. The "
            "outcome depends on the rate, duration and timing of contributions."
        ),
        0,
        ("juros", "compostos", "compound", "simulação"),
    ),
    Article(
        "diversification",
        "Diversificação",
        "Diversification",
        (
            "Diversificar é distribuir recursos entre diferentes investimentos e "
            "riscos. Pode reduzir a concentração, mas não elimina o risco de perda."
        ),
        (
            "Diversification spreads investments across different assets and risks. "
            "It can reduce concentration, but does not eliminate the possibility of "
            "losses."
        ),
        0,
        ("carteira", "alocação", "allocation", "risco", "risk"),
    ),
    Article(
        "liquidity",
        "Liquidez",
        "Liquidity",
        (
            "Liquidez é a facilidade de converter um ativo em dinheiro sem perda "
            "relevante. Uma aplicação pode ter valor elevado e ainda assim não estar "
            "disponível para emergências."
        ),
        (
            "Liquidity measures how easily an asset can be turned into cash without a "
            "substantial loss. An investment may be valuable yet unavailable for "
            "emergencies."
        ),
        0,
        ("reserva", "emergência", "emergency", "cash"),
    ),
    Article(
        "volatility",
        "Volatilidade",
        "Volatility",
        (
            "Volatilidade mede a variação dos retornos ao longo do tempo. É uma "
            "medida de oscilação histórica, não uma previsão exata de perdas futuras."
        ),
        (
            "Volatility measures variation in returns over time. It reflects "
            "historical fluctuations, not an exact prediction of future losses."
        ),
        2,
        ("volatilidade", "risk", "risco", "mercado", "market"),
    ),
    Article(
        "sharpe",
        "Índice de Sharpe",
        "Sharpe ratio",
        (
            "O índice de Sharpe compara o retorno excedente a uma referência livre de "
            "risco com a volatilidade dos retornos. Depende do período, da referência "
            "e da qualidade dos dados históricos."
        ),
        (
            "The Sharpe ratio compares returns in excess of a risk-free benchmark "
            "with return volatility. It depends on the observation period, benchmark, "
            "and quality of historical data."
        ),
        2,
        ("sharpe", "volatilidade", "volatility", "benchmark", "risk"),
    ),
    Article(
        "net-worth",
        "Patrimônio líquido",
        "Net worth",
        (
            "Patrimônio líquido é a diferença entre os ativos e os passivos. Uma "
            "simulação de investimento não representa, por si só, patrimônio real."
        ),
        (
            "Net worth is assets minus liabilities. A hypothetical investment "
            "projection is not, by itself, part of real net worth."
        ),
        1,
        ("patrimônio", "asset", "passivo", "ativos", "liabilities"),
    ),
)


def _fold(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(char)
    )


def get_article(key: str, language: str) -> dict[str, str | bool] | None:
    entry = next((article for article in ARTICLES if article.key == key), None)
    if entry is None:
        return None
    use_english = language == "en"
    return {
        "key": entry.key,
        "title": entry.title_en if use_english else entry.title_pt,
        "body": entry.body_en if use_english else entry.body_pt,
        "language": "en" if use_english else "pt",
        "fallback": False,
        "version": CATALOG_VERSION,
    }


def search_articles(query: str, language: str, profile: str | None) -> list[dict[str, str | bool]]:
    normalized = _fold(query.strip())
    if len(normalized) > 100:
        raise ValueError("search_term_too_long")
    preferred = 2 if profile == "arrojado" else 1 if profile == "moderado" else 0

    def relevance(entry: Article) -> int:
        title = _fold(entry.title_en if language == "en" else entry.title_pt)
        if normalized == _fold(entry.key) or normalized == title:
            return 3
        if normalized in title or normalized in _fold(entry.key):
            return 2
        if any(normalized in _fold(tag) for tag in entry.tags):
            return 1
        return 0

    ranked = [
        article
        for article in ARTICLES
        if not normalized
        or relevance(article) > 0
        or normalized in _fold(article.body_en if language == "en" else article.body_pt)
    ]
    ranked.sort(
        key=lambda entry: (
            -relevance(entry) if normalized else 0,
            abs(entry.level - preferred),
            entry.key,
        )
    )
    return [get_article(article.key, language) for article in ranked[:20]]
