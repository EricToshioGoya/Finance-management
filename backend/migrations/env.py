from alembic import context
from sqlalchemy import create_engine, pool

from app.config import get_settings
from app.infrastructure.models import Base

engine = create_engine(get_settings().database_url.get_secret_value(), poolclass=pool.NullPool)
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
