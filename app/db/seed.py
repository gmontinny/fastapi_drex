"""Script de seed para popular o banco com dados acadêmicos iniciais."""
import asyncio
from app.db.database import init_db, AsyncSessionLocal
from app.services import drex_service
from app.models.models import BcbUser
from app.core.security import hash_password
from sqlalchemy import select


INSTITUTIONS = [
    ("Banco Central do Brasil", True),
    ("Banco do Brasil", True),
    ("Caixa Econômica Federal", True),
    ("Itaú Unibanco", True),
    ("Bradesco", True),
]

INDIVIDUALS = [
    ("Alice Souza", False),
    ("Bruno Lima", False),
    ("Carla Mendes", False),
]


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:

        # Usuário BCB inicial
        existing = await db.execute(select(BcbUser).where(BcbUser.username == "admin_bcb"))
        if not existing.scalar_one_or_none():
            user = BcbUser(
                username="admin_bcb",
                full_name="Administrador Banco Central",
                hashed_password=hash_password("drex@2024"),
            )
            db.add(user)
            await db.commit()
            print("  Usuário BCB criado: admin_bcb / drex@2024")

        accounts = {}
        for name, is_inst in INSTITUTIONS + INDIVIDUALS:
            acc = await drex_service.create_account(db, name, is_inst)
            accounts[name] = acc
            print(f"  Conta criada: {name} → {acc.address}")

        bcb = accounts["Banco Central do Brasil"]
        bb = accounts["Banco do Brasil"]
        cef = accounts["Caixa Econômica Federal"]
        alice = accounts["Alice Souza"]
        bruno = accounts["Bruno Lima"]

        # BCB minta para instituições (atacado)
        await drex_service.mint_drex(db, bb.address, 500_000, "Emissão inicial atacado")
        await drex_service.mint_drex(db, cef.address, 300_000, "Emissão inicial atacado")
        print("  Mint para instituições concluído")

        # Instituições transferem para pessoas (varejo)
        await drex_service.transfer_drex(db, bb.address, alice.address, 1_000, "Depósito tokenizado varejo")
        await drex_service.transfer_drex(db, cef.address, bruno.address, 500, "Depósito tokenizado varejo")
        print("  Transferências varejo concluídas")

        # Simula queima
        await drex_service.burn_drex(db, bb.address, 10_000)
        print("  Queima simulada")

        print("\n✅ Seed concluído com sucesso!")


if __name__ == "__main__":
    asyncio.run(seed())
