"""Teste de carga do RNF-04: P95 < 3 s em simulações e dashboards.

Uso (com a API local em execução, ver scripts/start-local.sh):
    cd backend && uv run --frozen python ../scripts/carga.py [--requests 90] [--concurrency 10]

O script cria um usuário sintético, marca o e-mail como verificado direto no banco local
(nunca use banco de produção), popula lançamentos e mede a latência de:
- POST /api/v1/auth/financial/calculator      (simulação)
- POST /api/v1/auth/financial/simulations/fixed-income (simulação persistida)
- GET  /api/v1/auth/financial/dashboard        (dashboard de 12 meses)
As escritas em /financial compartilham o limite do RNF-13 (100/min por cliente); por isso cada
endpoint de escrita é medido em uma janela de 1 minuto própria, com no máximo 90 requisições.
"""

import argparse
import asyncio
import statistics
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx
from sqlalchemy import create_engine, update

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.config import get_settings  # noqa: E402
from app.infrastructure.models import UserRecord  # noqa: E402

ORIGIN = "https://localhost:8443"
CERT = Path(__file__).resolve().parents[1] / ".local/localhost.crt"
LIMIT_SECONDS = 3.0


async def next_window() -> None:
    """Aguarda o início da próxima janela de 1 minuto do rate limit (RNF-13)."""
    await asyncio.sleep(60 - time.time() % 60 + 0.5)


def p95(values: list[float]) -> float:
    return statistics.quantiles(values, n=100)[94] if len(values) >= 2 else values[0]


async def measure(client, method, path, body, total, concurrency):
    latencies, errors = [], 0
    semaphore = asyncio.Semaphore(concurrency)

    async def one():
        nonlocal errors
        async with semaphore:
            start = time.perf_counter()
            response = await client.request(method, path, json=body)
            latencies.append(time.perf_counter() - start)
            errors += response.status_code >= 400

    await asyncio.gather(*(one() for _ in range(total)))
    return latencies, errors


async def main(total: int, concurrency: int) -> int:
    email = f"carga-{uuid.uuid4()}@example.com"
    password = uuid.uuid4().hex
    async with httpx.AsyncClient(base_url=ORIGIN, verify=str(CERT), timeout=30) as client:
        created = await client.post(
            "/api/v1/auth/register", json={"name": "Carga", "email": email, "password": password}
        )
        created.raise_for_status()
        engine = create_engine(get_settings().database_url.get_secret_value())
        with engine.begin() as db:
            db.execute(
                update(UserRecord)
                .where(UserRecord.id == uuid.UUID(created.json()["id"]))
                .values(email_verified_at=datetime.now(UTC))
            )
        login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        await next_window()  # preparação também usa o limite de escritas
        account = (
            await client.post(
                "/api/v1/auth/financial/accounts",
                json={"name": "Carga", "account_type": "checking", "initial_balance": "0"},
            )
        ).json()["id"]
        for month in range(1, 13):
            await client.post(
                "/api/v1/auth/financial/expenses",
                headers={"Idempotency-Key": str(uuid.uuid4())},
                json={
                    "description": "Despesa sintética",
                    "amount": "100.00",
                    "category_key": "standard:alimentacao",
                    "occurred_on": f"2026-{month:02d}-10",
                    "account_id": account,
                },
            )
        simulation = {
            "initial_amount": "10000",
            "monthly_contribution": "500",
            "annual_rate": "10",
            "term_months": 360,
        }
        cases = [
            ("POST", "/api/v1/auth/financial/calculator", simulation),
            (
                "POST",
                "/api/v1/auth/financial/simulations/fixed-income",
                {**simulation, "label": "Carga", "product": "cdb"},
            ),
            ("GET", "/api/v1/auth/financial/dashboard?start=2026-01&end=2026-12", None),
        ]
        failed = False
        print(f"RNF-04: {total} requisições por endpoint, concorrência {concurrency}")
        for method, path, body in cases:
            if method == "POST":
                await next_window()
            latencies, errors = await measure(client, method, path, body, total, concurrency)
            value = p95(latencies)
            ok = value < LIMIT_SECONDS and errors == 0
            failed |= not ok
            print(
                f"{'OK ' if ok else 'FALHA'} {method} {path.split('?')[0]}: "
                f"P95={value * 1000:.0f} ms, mediana={statistics.median(latencies) * 1000:.0f} ms, "
                f"erros={errors}"
            )
        return 1 if failed else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--requests", type=int, default=90)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()
    sys.exit(asyncio.run(main(min(args.requests, 90), args.concurrency)))
