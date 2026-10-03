from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.schemas import AccountCreate, AccountResponse
from app.services import drex_service

router = APIRouter(prefix="/accounts", tags=["🧑 Contas"])


@router.post(
    "/",
    response_model=AccountResponse,
    status_code=201,
    summary="Criar uma nova conta",
    description="""
Cria uma nova conta no sistema Drex.

Cada conta recebe automaticamente um **endereço único** no formato `0x...`, que funciona como uma identidade na blockchain.

**Campos:**
- `name`: Nome da pessoa ou instituição financeira.
- `is_institution`: Informe `true` se for um banco ou instituição financeira; `false` para pessoa física ou jurídica comum.

**Exemplo de uso:**
- Criar conta de pessoa física: `{"name": "João Silva", "is_institution": false}`
- Criar conta de banco: `{"name": "Nubank", "is_institution": true}`
    """,
)
async def create_account(payload: AccountCreate, db: AsyncSession = Depends(get_db)):
    return await drex_service.create_account(db, payload.name, payload.is_institution)


@router.get(
    "/",
    response_model=list[AccountResponse],
    summary="Listar todas as contas",
    description="""
Retorna a lista completa de contas cadastradas no sistema.

Use esta rota para descobrir os **endereços** (`address`) das contas e utilizá-los nas operações de transferência, mint e burn.

> 💡 Dica: copie o campo `address` de uma conta para usar nas outras operações.
    """,
)
async def list_accounts(db: AsyncSession = Depends(get_db)):
    return await drex_service.list_accounts(db)


@router.get(
    "/{address}",
    response_model=AccountResponse,
    summary="Consultar uma conta pelo endereço",
    description="""
Busca os detalhes de uma conta específica usando seu **endereço blockchain** (`0x...`).

Retorna:
- **Saldo atual** em Drex
- Se a conta está **congelada** (bloqueada pelo Banco Central)
- Se é uma **instituição financeira** ou pessoa

**Como obter o endereço?** Use `GET /accounts/` para listar todas as contas e copiar o campo `address`.
    """,
)
async def get_account(address: str, db: AsyncSession = Depends(get_db)):
    account = await drex_service.get_account(db, address)
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return account
