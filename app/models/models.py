import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
import enum


class TransactionType(str, enum.Enum):
    MINT = "MINT"
    BURN = "BURN"
    TRANSFER = "TRANSFER"
    FREEZE = "FREEZE"
    UNFREEZE = "UNFREEZE"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    address: Mapped[str] = mapped_column(String(42), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    balance: Mapped[float] = mapped_column(Numeric(20, 8), default=0)
    frozen: Mapped[bool] = mapped_column(Boolean, default=False)
    is_institution: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sent_transactions: Mapped[list["Transaction"]] = relationship("Transaction", foreign_keys="Transaction.from_address", back_populates="sender")
    received_transactions: Mapped[list["Transaction"]] = relationship("Transaction", foreign_keys="Transaction.to_address", back_populates="receiver")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tx_hash: Mapped[str] = mapped_column(String(66), unique=True, index=True)
    type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType))
    from_address: Mapped[str | None] = mapped_column(String(42), ForeignKey("accounts.address"), nullable=True)
    to_address: Mapped[str | None] = mapped_column(String(42), ForeignKey("accounts.address"), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(20, 8), default=0)
    block_number: Mapped[int] = mapped_column(default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    metadata_info: Mapped[str | None] = mapped_column(String(255), nullable=True)

    sender: Mapped["Account | None"] = relationship("Account", foreign_keys=[from_address], back_populates="sent_transactions")
    receiver: Mapped["Account | None"] = relationship("Account", foreign_keys=[to_address], back_populates="received_transactions")


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block_number: Mapped[int] = mapped_column(unique=True, index=True)
    block_hash: Mapped[str] = mapped_column(String(66), unique=True)
    previous_hash: Mapped[str] = mapped_column(String(66))
    tx_count: Mapped[int] = mapped_column(default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
