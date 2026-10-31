"""C-02: SPEC-027-R05 e SPEC-054-R03/R06 com a sincronização semanal CVM (OPEN-27, ADR-009).

Dublês no formato público dos Dados Abertos CVM; nenhuma chamada real (C-17).
"""

import io
import uuid
import zipfile
from datetime import UTC, date, datetime

import pytest
from sqlalchemy import delete, select

from app.application.auth import AuthService
from app.application.cvm_sync import CvmSyncService, reference_label
from app.infrastructure.cvm_catalogue import PETR4, VALE3
from app.infrastructure.models import OfficialDocumentRecord, PublicCompanyRecord
from app.infrastructure.official_sources import (
    CVM_INDEX_URL,
    CVM_REGISTER_URL,
    CvmDocument,
    CvmSources,
    SourceError,
)
from tests.clause_support import verified_user

NOW = datetime(2026, 11, 1, 6, 0, tzinfo=UTC)  # domingo, 03h em São Paulo
PETR4_CNPJ = "33.000.167/0001-01"
DFP_HEADER = "CNPJ_CIA;DT_REFER;VERSAO;DENOM_CIA;CD_CVM;CATEG_DOC;ID_DOC;DT_RECEB;LINK_DOC"
IPE_HEADER = (
    "CNPJ_Companhia;Nome_Companhia;Codigo_CVM;Data_Referencia;Categoria;Tipo;Especie;"
    "Assunto;Data_Entrega;Tipo_Apresentacao;Protocolo_Entrega;Versao;Link_Download"
)
LINK = "https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&numSequencia={}"


def zipped(name: str, header: str, rows: list[str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, "\n".join([header, *rows]).encode("latin-1"))
    return buffer.getvalue()


def dfp_row(version: int, received: str = "2026-02-26", cnpj: str = PETR4_CNPJ) -> str:
    return (
        f"{cnpj};2025-12-31;{version};PETROBRAS;9512;DFP;{100 + version};{received};"
        f"{LINK.format(100 + version)}"
    )


def ipe_row(subject: str, delivered: str = "2026-10-29") -> str:
    return (
        f"{PETR4_CNPJ};PETROBRAS;9512;2026-10-29;Fato Relevante;;;{subject};{delivered};AP;"
        f"777;1;{LINK.format(777)}"
    )


def responses(dfp_rows=(), ipe_rows=(), itr_rows=()) -> dict[str, bytes]:
    data = {
        CVM_REGISTER_URL: (
            "CNPJ_CIA;DENOM_SOCIAL;SIT;SETOR_ATIV\n"
            f"{PETR4_CNPJ};PETROLEO BRASILEIRO S.A. - PETROBRAS (CVM);ATIVO;Petróleo e Gás\n"
            "00.000.000/0001-91;EMPRESA FORA DO CATALOGO;ATIVO;Bancos\n"
        ).encode("latin-1")
    }
    for kind, header, rows in (
        ("DFP", DFP_HEADER, dfp_rows),
        ("ITR", DFP_HEADER, itr_rows),
        ("IPE", IPE_HEADER, ipe_rows),
    ):
        for year in (2025, 2026):
            data[CVM_INDEX_URL[kind].format(year=year)] = zipped(
                f"{kind.lower()}_cia_aberta_{year}.csv", header, list(rows) if year == 2026 else []
            )
    return data


class FakeTransport:
    def __init__(self, data: dict[str, bytes]):
        self.data = data

    def __call__(self, url: str) -> bytes:
        if url not in self.data:
            raise SourceError("transport_failure")
        return self.data[url]


@pytest.fixture
def catalogue(app):
    """Restaura cadastro e remove documentos sincronizados ao final (tabelas compartilhadas)."""
    with app.state.sessions() as db:
        original = {c.id: (c.legal_name, c.sector) for c in db.scalars(select(PublicCompanyRecord))}
    yield
    with app.state.sessions() as db:
        db.execute(
            delete(OfficialDocumentRecord).where(OfficialDocumentRecord.cvm_version.is_not(None))
        )
        for company in db.scalars(select(PublicCompanyRecord)):
            company.legal_name, company.sector = original[company.id]
        db.commit()


def run(app, data, items=("register", "DFP", "ITR", "IPE")):
    with app.state.sessions() as db:
        auth = AuthService(db, None, app.state.security, clock=lambda: NOW)
        service = CvmSyncService(
            db, lambda: NOW, CvmSources(FakeTransport(data)), auth.notify_watchlist_document
        )
        return service.run(items)


def synced(app, kind="DFP"):
    with app.state.sessions() as db:
        return [
            (r.cvm_version, r.status, r.reference_period, r.official_url)
            for r in db.scalars(
                select(OfficialDocumentRecord)
                .where(
                    OfficialDocumentRecord.company_id == PETR4,
                    OfficialDocumentRecord.document_type == kind,
                    OfficialDocumentRecord.cvm_version.is_not(None),
                )
                .order_by(OfficialDocumentRecord.cvm_version)
            )
        ]


def notifications(client, headers):
    return [
        n
        for n in client.get("/api/v1/notifications", headers=headers).json()
        if n["kind"] == "watchlist_document"
    ]


def test_SPEC_012_register_updates_only_catalogued_active_companies(app, catalogue):
    assert run(app, responses(), ("register",)) == {"register": "updated"}
    with app.state.sessions() as db:
        petr4 = db.get(PublicCompanyRecord, PETR4)
        assert petr4.legal_name.endswith("(CVM)") and petr4.sector == "Petróleo e Gás"
        # Cadastro CVM não traz ticker: companhia fora do catálogo não é criada.
        assert (
            db.scalar(select(PublicCompanyRecord).where(PublicCompanyRecord.cnpj.like("00%")))
            is None
        )
        assert db.get(PublicCompanyRecord, VALE3).legal_name.startswith("VALE")
    assert run(app, responses(), ("register",)) == {"register": "kept"}


def test_SPEC_027_R05_new_document_alerts_watchlist_once(app, client, catalogue):
    headers = verified_user(client, app)
    assert client.post(f"/api/v1/companies/{PETR4}/watchlist", headers=headers).status_code == 200
    data = responses(dfp_rows=[dfp_row(1)], ipe_rows=[ipe_row("Descoberta de petróleo")])
    assert run(app, data) == {
        "register": "updated",
        "DFP": "updated",
        "ITR": "kept",
        "IPE": "updated",
    }
    assert len(notifications(client, headers)) == 2
    run(app, data)  # nova execução semanal com os mesmos documentos
    assert len(notifications(client, headers)) == 2
    assert synced(app, "IPE")[0][:3] == (1, "active", "29/10/2026")


def test_SPEC_027_R05_restatement_replaces_effective_without_new_alert(app, client, catalogue):
    headers = verified_user(client, app)
    client.post(f"/api/v1/companies/{PETR4}/watchlist", headers=headers)
    run(app, responses(dfp_rows=[dfp_row(1)]), ("DFP",))
    run(app, responses(dfp_rows=[dfp_row(1), dfp_row(2, "2026-03-15")]), ("DFP",))
    assert [(v, s) for v, s, *_ in synced(app)] == [(1, "replaced"), (2, "restated")]
    assert len(notifications(client, headers)) == 1


def test_SPEC_027_late_old_version_never_becomes_effective(app, catalogue):
    run(app, responses(dfp_rows=[dfp_row(2)]), ("DFP",))
    run(app, responses(dfp_rows=[dfp_row(1), dfp_row(2)]), ("DFP",))
    assert [(v, s) for v, s, *_ in synced(app)] == [(1, "replaced"), (2, "active")]


def test_SPEC_054_R03_only_last_12_calendar_months_enter_cache(app, catalogue):
    old = dfp_row(1, received="2025-10-31")
    run(app, responses(dfp_rows=[old]), ("DFP",))
    assert synced(app) == []
    run(app, responses(dfp_rows=[dfp_row(1, received="2025-11-01")]), ("DFP",))
    assert len(synced(app)) == 1


def test_SPEC_054_R06_only_metadata_and_official_link_are_stored(app, catalogue):
    foreign = dfp_row(1).replace(LINK.format(101), "https://example.com/doc.pdf")
    run(app, responses(dfp_rows=[foreign]), ("DFP",))
    (_version, _status, period, url) = synced(app)[0]
    assert period == "Exercício 2025"
    assert url.startswith("https://www.rad.cvm.gov.br/") and "example.com" not in url
    assert not hasattr(OfficialDocumentRecord, "content")


def test_SPEC_054_R02_source_failure_keeps_cache_and_reports_failure(app, catalogue):
    run(app, responses(dfp_rows=[dfp_row(1)]), ("DFP",))
    assert run(app, {}, ("register", "DFP")) == {"register": "failed", "DFP": "failed"}
    assert len(synced(app)) == 1
    broken = responses()
    broken[CVM_INDEX_URL["DFP"].format(year=2026)] = b"not a zip"
    assert run(app, broken, ("DFP",)) == {"DFP": "failed"}


@pytest.mark.parametrize(
    ("kind", "reference", "label"),
    [
        ("DFP", date(2025, 12, 31), "Exercício 2025"),
        ("ITR", date(2026, 6, 30), "2º trimestre de 2026"),
    ],
)
def test_reference_labels_follow_catalogue_convention(kind, reference, label):
    document = CvmDocument("1", kind, reference, 1, reference, "", "")
    assert reference_label(document) == label


def test_identity_is_unique_per_company_type_reference_and_version(app, catalogue):
    run(app, responses(dfp_rows=[dfp_row(1)]), ("DFP",))
    with app.state.sessions() as db:
        db.add(
            OfficialDocumentRecord(
                id=uuid.uuid4(),
                company_id=PETR4,
                document_type="DFP",
                subject="dup",
                reference_period="x",
                delivered_at=date(2026, 2, 26),
                status="active",
                official_url=LINK.format(1),
                link_status="unchecked",
                synced_at=NOW,
                cvm_reference_date=date(2025, 12, 31),
                cvm_version=1,
            )
        )
        with pytest.raises(Exception, match="uq_official_document_identity"):
            db.commit()
