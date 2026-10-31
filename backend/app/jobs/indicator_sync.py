"""Sincronização manual das fontes oficiais (ADR-009): `python -m app.jobs.indicator_sync`.

Executa SGS (SELIC, CDI, IPCA), PTAX (USD, EUR) e Tesouro Direto uma vez, sem novas
tentativas, e imprime o resultado por item (`updated`, `kept` ou `failed`).
"""

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.indicator_sync import IndicatorSyncService
from app.config import get_settings
from app.infrastructure.official_sources import OfficialSources


def main() -> dict[str, str]:
    engine = create_engine(get_settings().database_url.get_secret_value())
    with sessionmaker(engine)() as db:
        return IndicatorSyncService(db, lambda: datetime.now(UTC), OfficialSources()).run()


if __name__ == "__main__":
    print(main())
