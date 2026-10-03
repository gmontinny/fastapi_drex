from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.security import require_bcb_auth
from app.schemas.schemas import MintRequest, BurnRequest, TransferRequest, FreezeRequest, TransactionResponse
from app.services import drex_service

router = APIRouter(prefix="/drex", tags=["💸 Operações Drex"])


@router.post(
    "/mint",
    response_model=TransactionResponse,
    dependencies=[Depends(require_bcb_auth)],
    summary="Emitir Drex (somente Banco Central)",
    description="""
Emite (cria) uma quantidade de Drex e deposita na conta indicada.

> 🔒 **Operação restrita ao Banco Central.** Você precisa estar autenticado com um token JWT válido.
> Caso ainda não tenha um token: registre um usuário em `POST /auth/registrar`, faça login em `POST /auth/login` e clique em **🔓 Authorize** no topo desta página.: o BCB cria Drex do zero e distribui para instituições financeiras (camada atacado).

**Regras:**
- A conta destinatária deve existir.
- A conta destinatária não pode estar congelada.
- O valor deve ser maior que zero.

**Cada emissão gera um novo bloco** na blockchain simulada com hash único encadeado ao bloco anterior.
    """,
)
async def mint(payload: MintRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await drex_service.mint_drex(db, payload.to_address, payload.amount, payload.metadata_info)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/burn",
    response_model=TransactionResponse,
    dependencies=[Depends(require_bcb_auth)],
    summary="Queimar Drex (somente Banco Central)",
    description="""
Destrói uma quantidade de Drex de uma conta, reduzindo a oferta monetária total em circulação.

> 🔒 **Operação restrita ao Banco Central.** Você precisa estar autenticado com um token JWT válido.
> Caso ainda não tenha um token: registre um usuário em `POST /auth/registrar`, faça login em `POST /auth/login` e clique em **🔓 Authorize** no topo desta página.

A **queima** é o oposto da emissão: o BCB remove Drex de circulação para controlar a oferta monetária, similar ao que bancos centrais fazem com cédulas físicas.

**Regras:**
- A conta deve existir e não estar congelada.
- A conta deve ter saldo suficiente para a queima.
- O valor deve ser maior que zero.
    """,
)
async def burn(payload: BurnRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await drex_service.burn_drex(db, payload.from_address, payload.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/transfer",
    response_model=TransactionResponse,
    summary="Transferir Drex entre contas",
    description="""
Realiza uma transferência de Drex de uma conta para outra.

Esta é a operação mais comum do sistema, equivalente a um **Pix em moeda digital**.

**Regras:**
- Remetente e destinatário devem existir.
- Nenhum dos dois pode estar com a conta congelada.
- O remetente deve ter saldo suficiente.
- O valor deve ser maior que zero.

**A transferência é atômica:** o saldo é debitado e creditado na mesma operação, garantindo consistência.
    """,
)
async def transfer(payload: TransferRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await drex_service.transfer_drex(db, payload.from_address, payload.to_address, payload.amount, payload.metadata_info)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/freeze",
    response_model=TransactionResponse,
    dependencies=[Depends(require_bcb_auth)],
    summary="Congelar ou descongelar uma conta (somente Banco Central)",
    description="""
Bloqueia ou desbloqueia uma conta, impedindo que ela envie ou receba Drex.

> 🔒 **Operação restrita ao Banco Central.** Você precisa estar autenticado com um token JWT válido.
> Caso ainda não tenha um token: registre um usuário em `POST /auth/registrar`, faça login em `POST /auth/login` e clique em **🔓 Authorize** no topo desta página.

O **congelamento** é um mecanismo de **controle regulatório**: o BCB pode bloquear contas suspeitas de fraude, lavagem de dinheiro ou outras irregularidades.

**Como usar:**
- Para congelar: `{"address": "0x...", "frozen": true}`
- Para descongelar: `{"address": "0x...", "frozen": false}`

**Efeito do congelamento:**
- A conta não pode enviar Drex.
- A conta não pode receber Drex.
- O congelamento fica registrado na blockchain.
    """,
)
async def freeze(payload: FreezeRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await drex_service.freeze_account(db, payload.address, payload.frozen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
