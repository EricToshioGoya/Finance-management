"""Adaptadores das fontes oficiais do ADR-009: buscam e convertem, sem regra de negócio.

Somente HTTPS para a lista fechada de hosts; o transporte é injetável para que os testes
usem dublês e nunca chamem a fonte real (C-17).
"""

import csv
import io
import json
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ALLOWED_HOSTS = frozenset(
    {"api.bcb.gov.br", "olinda.bcb.gov.br", "www.tesourotransparente.gov.br", "dados.cvm.gov.br"}
)
TIMEOUT_SECONDS = 20
SAO_PAULO = ZoneInfo("America/Sao_Paulo")

# OPEN-10 (2026-10-31): séries SGS em % a.a.
SGS_SERIES = {"selic": 432, "cdi": 4389, "ipca": 13522}
SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series}/dados/ultimos/1?formato=json"
PTAX_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)"
    "?@moeda='{currency}'&@dataCotacao='{day}'&$format=json"
)
TREASURY_URL = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/"
    "resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
)

Transport = Callable[[str], bytes]


class SourceError(Exception):
    """Falha de transporte ou formato inesperado; o chamador mantém o último valor (C-08)."""


def https_get(url: str) -> bytes:
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise SourceError("host_not_allowed")
    request = Request(
        url, headers={"Accept": "application/json, text/csv", "User-Agent": "FinNova"}
    )
    try:
        # HTTPS e host da lista fechada validados acima.
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310  # nosec B310
            return response.read()
    except OSError as exc:
        raise SourceError("transport_failure") from exc


def _decimal(raw: str) -> Decimal:
    try:
        value = Decimal(raw.strip().replace(".", "").replace(",", ".") if "," in raw else raw)
    except (InvalidOperation, AttributeError) as exc:
        raise SourceError("invalid_number") from exc
    if not value.is_finite():
        raise SourceError("invalid_number")
    return value


def _br_date(raw: str) -> date:
    try:
        return datetime.strptime(raw.strip(), "%d/%m/%Y").date()
    except (ValueError, AttributeError) as exc:
        raise SourceError("invalid_date") from exc


@dataclass(frozen=True)
class Observation:
    value: Decimal
    reference_date: date


@dataclass(frozen=True)
class PtaxQuote:
    sell_rate: Decimal
    reference_date: date
    quoted_at: datetime


@dataclass(frozen=True)
class TreasuryRate:
    bond_type: str
    maturity: date
    buy_rate: Decimal
    reference_date: date


class OfficialSources:
    def __init__(self, transport: Transport = https_get):
        self.transport = transport

    def sgs_latest(self, code: str) -> Observation:
        """Último valor publicado da série SGS (JSON `[{"data": "dd/mm/aaaa", "valor": "..."}]`)."""
        try:
            rows = json.loads(self.transport(SGS_URL.format(series=SGS_SERIES[code])))
            row = rows[-1]
            return Observation(_decimal(str(row["valor"])), _br_date(row["data"]))
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise SourceError("unexpected_format") from exc

    def ptax_sell(self, currency: str, day: date) -> PtaxQuote | None:
        """PTAX de venda do boletim de fechamento do dia; None quando não há boletim (feriado)."""
        url = PTAX_URL.format(currency=quote(currency), day=day.strftime("%m-%d-%Y"))
        try:
            rows = json.loads(self.transport(url))["value"]
            closing = [row for row in rows if "Fechamento" in str(row.get("tipoBoletim", ""))]
            if not closing:
                return None
            row = closing[-1]
            quoted_at = datetime.fromisoformat(str(row["dataHoraCotacao"])[:19]).replace(
                tzinfo=SAO_PAULO
            )
            rate = _decimal(str(row["cotacaoVenda"]))
        except (ValueError, KeyError, TypeError) as exc:
            raise SourceError("unexpected_format") from exc
        if rate <= 0:
            raise SourceError("invalid_number")
        return PtaxQuote(rate, quoted_at.date(), quoted_at)

    def treasury_rates(self) -> list[TreasuryRate]:
        """Taxas de compra da data-base mais recente do CSV `PrecoTaxaTesouroDireto`."""
        raw = self.transport(TREASURY_URL)
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        try:
            rows = [
                TreasuryRate(
                    bond_type=row["Tipo Titulo"].strip(),
                    maturity=_br_date(row["Data Vencimento"]),
                    buy_rate=_decimal(row["Taxa Compra Manha"]),
                    reference_date=_br_date(row["Data Base"]),
                )
                for row in csv.DictReader(io.StringIO(text), delimiter=";")
            ]
        except (KeyError, AttributeError) as exc:
            raise SourceError("unexpected_format") from exc
        if not rows:
            raise SourceError("empty_source")
        latest = max(row.reference_date for row in rows)
        # Taxa zero indica título fora de venda; nunca é publicada como taxa (C-08).
        return [row for row in rows if row.reference_date == latest and row.buy_rate > 0]


# OPEN-27 (2026-10-31): CVM Dados Abertos — cadastro e índices DFP/ITR/IPE.
CVM_REGISTER_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
CVM_INDEX_URL = {
    "DFP": "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year}.zip",
    "ITR": "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_{year}.zip",
    "IPE": "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/ipe_cia_aberta_{year}.zip",
}


@dataclass(frozen=True)
class CvmCompany:
    cnpj: str
    legal_name: str
    sector: str
    active: bool


@dataclass(frozen=True)
class CvmDocument:
    cnpj: str
    document_type: str
    reference_date: date
    version: int
    delivered_on: date
    link: str
    subject: str


def digits(value: str) -> str:
    return "".join(char for char in value if char.isdigit())


def _iso_date(raw: str) -> date:
    try:
        return date.fromisoformat(raw.strip()[:10])
    except (ValueError, AttributeError) as exc:
        raise SourceError("invalid_date") from exc


def _csv_rows(raw: bytes) -> list[dict[str, str]]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return list(csv.DictReader(io.StringIO(text), delimiter=";"))


def cvm_document_from_row(document_type: str, row: dict[str, str]) -> CvmDocument:
    """Converte uma linha do índice DFP/ITR (`CNPJ_CIA`...) ou IPE (`CNPJ_Companhia`...)."""
    if document_type == "IPE":
        return CvmDocument(
            cnpj=digits(row["CNPJ_Companhia"]),
            document_type="IPE",
            reference_date=_iso_date(row["Data_Referencia"]),
            version=int(row["Versao"]),
            delivered_on=_iso_date(row["Data_Entrega"]),
            link=row["Link_Download"].strip(),
            subject=(row.get("Assunto") or row.get("Categoria") or "Documento IPE").strip(),
        )
    return CvmDocument(
        cnpj=digits(row["CNPJ_CIA"]),
        document_type=document_type,
        reference_date=_iso_date(row["DT_REFER"]),
        version=int(row["VERSAO"]),
        delivered_on=_iso_date(row["DT_RECEB"]),
        link=row["LINK_DOC"].strip(),
        subject="Demonstrações Financeiras Padronizadas"
        if document_type == "DFP"
        else "Informações Trimestrais",
    )


class CvmSources:
    def __init__(self, transport: Transport = https_get):
        self.transport = transport

    def company_register(self) -> list[CvmCompany]:
        try:
            return [
                CvmCompany(
                    cnpj=digits(row["CNPJ_CIA"]),
                    legal_name=row["DENOM_SOCIAL"].strip(),
                    sector=(row.get("SETOR_ATIV") or "").strip(),
                    active=row["SIT"].strip().upper() == "ATIVO",
                )
                for row in _csv_rows(self.transport(CVM_REGISTER_URL))
            ]
        except (KeyError, AttributeError) as exc:
            raise SourceError("unexpected_format") from exc

    def document_index(self, document_type: str, year: int) -> list[CvmDocument]:
        """Lê só o CSV de índice dentro do ZIP anual; demonstrações e PDFs não são lidos (C-09)."""
        raw = self.transport(CVM_INDEX_URL[document_type].format(year=year))
        expected = f"{document_type.lower()}_cia_aberta_{year}.csv"
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                index = archive.read(expected)
            return [cvm_document_from_row(document_type, row) for row in _csv_rows(index)]
        except (zipfile.BadZipFile, KeyError, ValueError, AttributeError) as exc:
            raise SourceError("unexpected_format") from exc
