"""Execução manual/agendada do resumo mensal (SPEC-040): `python -m app.jobs.monthly_summary`.

O agendamento em produção (cron, scheduler da plataforma) fica fora do recorte; o
servidor também executa o job diariamente às 06h de São Paulo.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.auth import AuthService
from app.application.monthly_summary import MonthlySummaryService
from app.config import get_settings
from app.infrastructure.channel_delivery import HttpsChannelDelivery, UnconfiguredChannelDelivery
from app.infrastructure.security import Security


def main() -> dict[str, int]:
    settings = get_settings()
    engine = create_engine(settings.database_url.get_secret_value())
    channels = {
        "email": HttpsChannelDelivery(settings.email_webhook_url.get_secret_value())
        if settings.email_webhook_url
        else UnconfiguredChannelDelivery(),
    }
    with sessionmaker(engine)() as db:
        auth = AuthService(
            db, settings, Security(settings.data_key.get_secret_value()), channel_delivery=channels
        )
        return MonthlySummaryService(db, auth).run()


if __name__ == "__main__":
    print(main())
