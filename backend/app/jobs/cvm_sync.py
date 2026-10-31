"""Sincronização manual dos Dados Abertos CVM (OPEN-27, ADR-009): `python -m app.jobs.cvm_sync`.

Executa cadastro e índices DFP/ITR/IPE uma vez, sem novas tentativas, e imprime o resultado
por item; documentos inéditos geram aviso da watchlist.
"""

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.auth import AuthService
from app.application.cvm_sync import CvmSyncService
from app.config import get_settings
from app.infrastructure.official_sources import CvmSources
from app.infrastructure.security import Security


def main() -> dict[str, str]:
    settings = get_settings()
    engine = create_engine(settings.database_url.get_secret_value())
    clock = lambda: datetime.now(UTC)  # noqa: E731
    with sessionmaker(engine)() as db:
        auth = AuthService(
            db, settings, Security(settings.data_key.get_secret_value()), clock=clock
        )
        return CvmSyncService(db, clock, CvmSources(), auth.notify_watchlist_document).run()


if __name__ == "__main__":
    print(main())
