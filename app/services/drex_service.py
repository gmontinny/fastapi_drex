import hashlib
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.models import Account, Transaction, Block, TransactionType


def _generate_address() -> str:
    return "0x" + uuid.uuid4().hex[:40]


def _generate_tx_hash(data: str) -> str:
    return "0x" + hashlib.sha256(data.encode()).hexdigest()


async def _get_latest_block(db: AsyncSession) -> Block | None:
    result = await db.execute(select(Block).order_by(Block.block_number.desc()).limit(1))
    return result.scalar_one_or_none()


async def _mine_block(db: AsyncSession, tx_id: str) -> int:
    latest = await _get_latest_block(db)
    prev_hash = latest.block_hash if latest else "0x" + "0" * 64
    block_number = (latest.block_number + 1) if latest else 1
    block_hash = _generate_tx_hash(f"{block_number}{prev_hash}{tx_id}{datetime.now(timezone.utc).isoformat()}")
    block = Block(block_number=block_number, block_hash=block_hash, previous_hash=prev_hash, tx_count=1)
    db.add(block)
    return block_number


async def create_account(db: AsyncSession, name: str, is_institution: bool) -> Account:
    account = Account(address=_generate_address(), name=name, is_institution=is_institution)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def get_account(db: AsyncSession, address: str) -> Account | None:
    result = await db.execute(select(Account).where(Account.address == address))
    return result.scalar_one_or_none()


async def list_accounts(db: AsyncSession) -> list[Account]:
    result = await db.execute(select(Account).order_by(Account.created_at))
    return list(result.scalars().all())


async def _get_bcb_address(db: AsyncSession) -> str | None:
    result = await db.execute(
        select(Account.address).where(Account.name == "Banco Central do Brasil").limit(1)
    )
    return result.scalar_one_or_none()


async def mint_drex(db: AsyncSession, to_address: str, amount: float, metadata_info: str | None) -> Transaction:
    account = await get_account(db, to_address)
    if not account:
        raise ValueError("Conta destinatária não encontrada")
    if account.frozen:
        raise ValueError("Conta congelada — operação negada")

    bcb_address = await _get_bcb_address(db)

    tx_id = str(uuid.uuid4())
    tx_hash = _generate_tx_hash(f"MINT{to_address}{amount}{tx_id}")
    block_number = await _mine_block(db, tx_id)

    account.balance = float(account.balance) + amount
    tx = Transaction(id=tx_id, tx_hash=tx_hash, type=TransactionType.MINT,
                     from_address=bcb_address, to_address=to_address, amount=amount,
                     block_number=block_number, metadata_info=metadata_info)
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


async def burn_drex(db: AsyncSession, from_address: str, amount: float) -> Transaction:
    account = await get_account(db, from_address)
    if not account:
        raise ValueError("Conta não encontrada")
    if account.frozen:
        raise ValueError("Conta congelada — operação negada")
    if float(account.balance) < amount:
        raise ValueError("Saldo insuficiente para queima")

    tx_id = str(uuid.uuid4())
    tx_hash = _generate_tx_hash(f"BURN{from_address}{amount}{tx_id}")
    block_number = await _mine_block(db, tx_id)

    account.balance = float(account.balance) - amount
    tx = Transaction(id=tx_id, tx_hash=tx_hash, type=TransactionType.BURN,
                     from_address=from_address, amount=amount, block_number=block_number)
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


async def transfer_drex(db: AsyncSession, from_address: str, to_address: str, amount: float, metadata_info: str | None) -> Transaction:
    sender = await get_account(db, from_address)
    receiver = await get_account(db, to_address)

    if not sender or not receiver:
        raise ValueError("Conta remetente ou destinatária não encontrada")
    if sender.frozen:
        raise ValueError("Remetente congelado — operação negada")
    if receiver.frozen:
        raise ValueError("Destinatário congelado — operação negada")
    if float(sender.balance) < amount:
        raise ValueError("Saldo insuficiente")

    tx_id = str(uuid.uuid4())
    tx_hash = _generate_tx_hash(f"TRANSFER{from_address}{to_address}{amount}{tx_id}")
    block_number = await _mine_block(db, tx_id)

    sender.balance = float(sender.balance) - amount
    receiver.balance = float(receiver.balance) + amount
    tx = Transaction(id=tx_id, tx_hash=tx_hash, type=TransactionType.TRANSFER,
                     from_address=from_address, to_address=to_address,
                     amount=amount, block_number=block_number, metadata_info=metadata_info)
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


async def freeze_account(db: AsyncSession, address: str, frozen: bool) -> Transaction:
    account = await get_account(db, address)
    if not account:
        raise ValueError("Conta não encontrada")

    tx_id = str(uuid.uuid4())
    tx_type = TransactionType.FREEZE if frozen else TransactionType.UNFREEZE
    tx_hash = _generate_tx_hash(f"{tx_type}{address}{tx_id}")
    block_number = await _mine_block(db, tx_id)

    account.frozen = frozen
    tx = Transaction(id=tx_id, tx_hash=tx_hash, type=tx_type,
                     to_address=address, amount=0, block_number=block_number)
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


async def list_transactions(db: AsyncSession, address: str | None = None) -> list[Transaction]:
    query = select(Transaction).order_by(Transaction.timestamp.desc())
    if address:
        query = query.where((Transaction.from_address == address) | (Transaction.to_address == address))
    result = await db.execute(query)
    return list(result.scalars().all())


async def list_blocks(db: AsyncSession) -> list[Block]:
    result = await db.execute(select(Block).order_by(Block.block_number.desc()).limit(20))
    return list(result.scalars().all())


async def get_supply_stats(db: AsyncSession) -> dict:
    minted = await db.execute(select(func.sum(Transaction.amount)).where(Transaction.type == TransactionType.MINT))
    burned = await db.execute(select(func.sum(Transaction.amount)).where(Transaction.type == TransactionType.BURN))
    total_minted = float(minted.scalar() or 0)
    total_burned = float(burned.scalar() or 0)
    return {
        "total_minted": total_minted,
        "total_burned": total_burned,
        "circulating_supply": total_minted - total_burned,
    }
