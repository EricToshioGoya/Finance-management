"""SPEC-044 (vínculo entre dois usuários) e SPEC-045 (divisão de despesas e acertos).

Regras do recorte aprovado em 2026-10-31:
- convite por e-mail com resposta genérica (não revela se o e-mail existe);
- no máximo um vínculo ativo por usuário; convite expira em 7 dias;
- após desfazer, o histórico compartilhado continua visível aos dois, somente leitura;
- divisão 50/50 ou percentual com 2 casas somando 100%; o centavo restante fica com quem pagou;
- acerto limitado ao saldo pendente, idempotente e permitido mesmo após o fim do vínculo.
"""

import uuid
from datetime import timedelta
from decimal import ROUND_DOWN, Decimal

from sqlalchemy import or_, select

from app.application.auth import AuthError, AuthService
from app.domain.identity import normalize_email
from app.infrastructure.models import (
    ExpenseRecord,
    SettlementRecord,
    SharedExpenseRecord,
    SharedLinkRecord,
    UserRecord,
)

INVITATION_TTL = timedelta(days=7)
CENT = Decimal("0.01")
HUNDRED = Decimal("100")


def split_amount(amount: Decimal, payer_percent: Decimal) -> tuple[Decimal, Decimal]:
    """Retorna (parte do pagador, parte do outro membro); o centavo restante fica com o pagador."""
    partner = (amount * (HUNDRED - payer_percent) / HUNDRED).quantize(CENT, ROUND_DOWN)
    return amount - partner, partner


class SharingService:
    def __init__(self, db, auth: AuthService):
        self.db, self.auth, self.security = db, auth, auth.security

    # ---------- auxiliares ----------
    def _member(self, user_id: uuid.UUID) -> UserRecord:
        return self.auth.require_category_owner(user_id)

    def _now(self):
        return self.auth.clock()

    def _expire_pending(self) -> None:
        for link in self.db.scalars(
            select(SharedLinkRecord).where(
                SharedLinkRecord.status == "pending", SharedLinkRecord.expires_at <= self._now()
            )
        ):
            link.status = "expired"

    def _active_link(self, user_id: uuid.UUID, lock: bool = False) -> SharedLinkRecord | None:
        query = select(SharedLinkRecord).where(
            SharedLinkRecord.status == "active",
            or_(SharedLinkRecord.inviter_id == user_id, SharedLinkRecord.invitee_id == user_id),
        )
        if lock:
            query = query.with_for_update()
        return self.db.scalar(query)

    def _partner_id(self, link: SharedLinkRecord, user_id: uuid.UUID) -> uuid.UUID:
        return link.invitee_id if link.inviter_id == user_id else link.inviter_id

    def _name(self, user_id: uuid.UUID) -> str:
        record = self.db.get(UserRecord, user_id)
        return self.security.decrypt(record.name_encrypted) if record else ""

    def _membership(self, user_id: uuid.UUID, link_id: uuid.UUID | None, lock=False):
        if link_id is None:
            link = self._active_link(user_id, lock)
            if link is None:
                raise AuthError("no_active_link", 409)
            return link
        query = select(SharedLinkRecord).where(SharedLinkRecord.id == link_id)
        if lock:
            query = query.with_for_update()
        link = self.db.scalar(query)
        # INV-002: não membro recebe 404, sem confirmar a existência do vínculo.
        if link is None or user_id not in (link.inviter_id, link.invitee_id):
            raise AuthError("link_not_found", 404)
        if link.status not in ("active", "ended"):
            raise AuthError("link_not_found", 404)
        return link

    # ---------- SPEC-044 ----------
    def invite(self, user_id: uuid.UUID, email: str) -> dict[str, str]:
        me = self._member(user_id)
        normalized = normalize_email(email)
        if self.security.decrypt(me.email_encrypted) == normalized:
            raise AuthError("self_invitation", 422)
        self._expire_pending()
        if self._active_link(user_id) is not None:
            raise AuthError("already_linked", 409)
        target = self.db.scalar(
            select(UserRecord).where(UserRecord.email_lookup == self.security.lookup(normalized))
        )
        # Convite só é criado para titular cadastrado e verificado, sem vínculo ativo e sem
        # convite pendente do mesmo par. A resposta é sempre a mesma (sem enumeração).
        if (
            target is not None
            and target.email_verified_at is not None
            and self._active_link(target.id) is None
        ):
            duplicate = self.db.scalar(
                select(SharedLinkRecord.id).where(
                    SharedLinkRecord.status == "pending",
                    SharedLinkRecord.inviter_id == user_id,
                    SharedLinkRecord.invitee_id == target.id,
                )
            )
            if duplicate is None:
                now = self._now()
                self.db.add(
                    SharedLinkRecord(
                        inviter_id=user_id,
                        invitee_id=target.id,
                        status="pending",
                        created_at=now,
                        expires_at=now + INVITATION_TTL,
                    )
                )
        self.db.commit()
        return {"status": "sent"}

    def overview(self, user_id: uuid.UUID) -> dict[str, object]:
        self._member(user_id)
        self._expire_pending()
        self.db.commit()
        links = self.db.scalars(
            select(SharedLinkRecord)
            .where(
                or_(SharedLinkRecord.inviter_id == user_id, SharedLinkRecord.invitee_id == user_id)
            )
            .order_by(SharedLinkRecord.created_at.desc())
        ).all()
        active, received, sent, history = None, [], [], []
        for link in links:
            partner = self._partner_id(link, user_id)
            if link.status == "active":
                active = {
                    "id": link.id,
                    "partner_name": self._name(partner),
                    "since": link.responded_at,
                }
            elif link.status == "pending" and link.invitee_id == user_id:
                received.append(
                    {"id": link.id, "from_name": self._name(partner), "expires_at": link.expires_at}
                )
            elif link.status == "pending":
                # O convidante não vê nome/e-mail do convidado antes do aceite.
                sent.append({"id": link.id, "expires_at": link.expires_at})
            elif link.status == "ended":
                history.append(
                    {"id": link.id, "partner_name": self._name(partner), "ended_at": link.ended_at}
                )
        return {"active": active, "received": received, "sent": sent, "history": history}

    def _pending_for(self, link_id: uuid.UUID, user_id: uuid.UUID, role: str):
        self._member(user_id)
        link = self.db.scalar(
            select(SharedLinkRecord).where(SharedLinkRecord.id == link_id).with_for_update()
        )
        owner = (
            None if link is None else (link.invitee_id if role == "invitee" else link.inviter_id)
        )
        if link is None or owner != user_id or link.status not in ("pending", "expired"):
            raise AuthError("invitation_not_found", 404)
        if link.status == "expired" or link.expires_at <= self._now():
            link.status = "expired"
            self.db.commit()
            raise AuthError("invitation_expired", 409)
        return link

    def accept(self, user_id: uuid.UUID, link_id: uuid.UUID) -> dict[str, object]:
        link = self._pending_for(link_id, user_id, "invitee")
        # Bloqueia os dois usuários para impedir dois vínculos ativos concorrentes.
        self.db.scalars(
            select(UserRecord)
            .where(UserRecord.id.in_([link.inviter_id, link.invitee_id]))
            .order_by(UserRecord.id)
            .with_for_update()
        ).all()
        if self._active_link(link.inviter_id) or self._active_link(link.invitee_id):
            raise AuthError("already_linked", 409)
        link.status, link.responded_at = "active", self._now()
        self.db.commit()
        return self.overview(user_id)

    def decline(self, user_id: uuid.UUID, link_id: uuid.UUID) -> None:
        link = self._pending_for(link_id, user_id, "invitee")
        link.status, link.responded_at = "declined", self._now()
        self.db.commit()

    def cancel(self, user_id: uuid.UUID, link_id: uuid.UUID) -> None:
        link = self._pending_for(link_id, user_id, "inviter")
        link.status, link.responded_at = "cancelled", self._now()
        self.db.commit()

    def end(self, user_id: uuid.UUID, link_id: uuid.UUID) -> None:
        self._member(user_id)
        link = self._membership(user_id, link_id, lock=True)
        if link.status != "active":
            raise AuthError("link_not_active", 409)
        link.status, link.ended_at = "ended", self._now()
        self.db.commit()

    # ---------- SPEC-045 ----------
    def share_expense(
        self, user_id: uuid.UUID, expense_id: uuid.UUID, payer_percent: Decimal
    ) -> dict[str, object]:
        self._member(user_id)
        link = self._membership(user_id, None, lock=True)
        expense = self.db.get(ExpenseRecord, expense_id)
        if expense is None or expense.user_id != user_id:
            raise AuthError("expense_not_found", 404)
        exists = self.db.scalar(
            select(SharedExpenseRecord.id).where(SharedExpenseRecord.expense_id == expense_id)
        )
        if exists is not None:
            raise AuthError("expense_already_shared", 409)
        self.db.add(
            SharedExpenseRecord(
                link_id=link.id,
                expense_id=expense_id,
                payer_id=user_id,
                payer_percent=payer_percent,
                created_at=self._now(),
            )
        )
        self.db.commit()
        return self.balance(user_id, link.id)

    def _own_share(self, user_id: uuid.UUID, share_id: uuid.UUID) -> SharedExpenseRecord:
        self._member(user_id)
        share = self.db.get(SharedExpenseRecord, share_id)
        if share is None or share.payer_id != user_id:
            raise AuthError("shared_expense_not_found", 404)
        link = self.db.get(SharedLinkRecord, share.link_id)
        if link.status != "active":
            raise AuthError("link_not_active", 409)
        return share

    def update_share(
        self, user_id: uuid.UUID, share_id: uuid.UUID, payer_percent: Decimal
    ) -> dict[str, object]:
        share = self._own_share(user_id, share_id)
        share.payer_percent = payer_percent
        self.db.commit()
        return self.balance(user_id, share.link_id)

    def unshare(self, user_id: uuid.UUID, share_id: uuid.UUID) -> None:
        share = self._own_share(user_id, share_id)
        self.db.delete(share)
        self.db.commit()

    def _net(self, link: SharedLinkRecord, user_id: uuid.UUID):
        rows = self.db.execute(
            select(SharedExpenseRecord, ExpenseRecord)
            .join(ExpenseRecord, ExpenseRecord.id == SharedExpenseRecord.expense_id)
            .where(SharedExpenseRecord.link_id == link.id)
            .order_by(ExpenseRecord.occurred_on.desc())
        ).all()
        items, owed_to_me, i_owe = [], Decimal("0"), Decimal("0")
        for share, expense in rows:
            payer_part, partner_part = split_amount(expense.amount, share.payer_percent)
            mine = share.payer_id == user_id
            if mine:
                owed_to_me += partner_part
            else:
                i_owe += partner_part
            items.append(
                {
                    "id": share.id,
                    "expense_id": expense.id,
                    "description": self.security.decrypt(expense.description_encrypted),
                    "amount": expense.amount,
                    "occurred_on": expense.occurred_on,
                    "paid_by": "me" if mine else "partner",
                    "payer_percent": share.payer_percent,
                    "my_share": payer_part if mine else partner_part,
                    "partner_share": partner_part if mine else payer_part,
                }
            )
        settlements = self.db.scalars(
            select(SettlementRecord)
            .where(SettlementRecord.link_id == link.id)
            .order_by(SettlementRecord.created_at)
        ).all()
        paid = sum((s.amount for s in settlements if s.payer_id == user_id), Decimal("0"))
        received = sum((s.amount for s in settlements if s.receiver_id == user_id), Decimal("0"))
        net = (owed_to_me - received) - (i_owe - paid)
        return items, settlements, net

    def balance(self, user_id: uuid.UUID, link_id: uuid.UUID | None = None) -> dict[str, object]:
        self._member(user_id)
        link = self._membership(user_id, link_id)
        items, settlements, net = self._net(link, user_id)
        direction = "settled" if net == 0 else ("partner_owes_me" if net > 0 else "i_owe_partner")
        return {
            "link_id": link.id,
            "status": link.status,
            "partner_name": self._name(self._partner_id(link, user_id)),
            "items": items,
            "settlements": [
                {
                    "id": s.id,
                    "amount": s.amount,
                    "paid_by": "me" if s.payer_id == user_id else "partner",
                    "created_at": s.created_at,
                }
                for s in settlements
            ],
            "direction": direction,
            "amount": abs(net),
        }

    def settle(
        self, user_id: uuid.UUID, amount: Decimal, key: str, link_id: uuid.UUID | None
    ) -> dict[str, object]:
        self._member(user_id)
        link = self._membership(user_id, link_id, lock=True)
        repeated = self.db.scalar(
            select(SettlementRecord.id).where(
                SettlementRecord.link_id == link.id,
                SettlementRecord.payer_id == user_id,
                SettlementRecord.idempotency_key == key,
            )
        )
        if repeated is None:
            _, _, net = self._net(link, user_id)
            if net >= 0:
                raise AuthError("nothing_to_settle", 409)
            if amount > -net:
                raise AuthError("settlement_exceeds_balance", 422)
            self.db.add(
                SettlementRecord(
                    link_id=link.id,
                    payer_id=user_id,
                    receiver_id=self._partner_id(link, user_id),
                    amount=amount,
                    idempotency_key=key,
                    created_at=self._now(),
                )
            )
            self.db.commit()
        return self.balance(user_id, link.id)
