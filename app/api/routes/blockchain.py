from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.database import get_db
from app.schemas.schemas import TransactionResponse, BlockResponse
from app.services import drex_service

router = APIRouter(prefix="/blockchain", tags=["🔗 Blockchain"])


@router.get(
    "/transactions",
    response_model=list[TransactionResponse],
    summary="Listar histórico de transações",
    description="""
Retorna o histórico completo de transações registradas na blockchain, em ordem da mais recente para a mais antiga.

---

## 📋 Passo a passo para usar este endpoint

### Passo 1 — Descubra os endereços das contas

Antes de filtrar transações, você precisa saber o **endereço** (`address`) da conta que deseja consultar.

Faça uma requisição para listar todas as contas:
```
GET /accounts/
```
No resultado, localize a conta desejada e copie o valor do campo `address` (ex: `0xc2fbaf6f315b44a1999a1c442f0201fb`).

---

### Passo 2 — Consulte todas as transações (sem filtro)

Para ver **todas** as transações do sistema, execute sem parâmetros:
```
GET /blockchain/transactions
```

---

### Passo 3 — Filtre por uma conta específica

Para ver apenas as transações de uma conta, informe o endereço no parâmetro `address`:
```
GET /blockchain/transactions?address=0xc2fbaf6f315b44a1999a1c442f0201fb
```
O filtro retorna tanto as transações **enviadas** quanto as **recebidas** por aquela conta.

---

### ⚠️ Por que o Banco Central pode não ter transações antigas?

O endereço do **Banco Central do Brasil** (`0x1fe7...`) só aparece como remetente (`from_address`) em operações de **MINT realizadas após a correção do sistema**.
As emissões do seed inicial (blocos 1 a 5) foram gravadas sem o endereço do BCB e por isso não aparecem no filtro.
Para gerar novas transações rastreáveis do BCB, use `POST /drex/mint`.

---

## 📊 Tipos de transação e seus campos

| Tipo | `from_address` | `to_address` | Descrição |
|---|---|---|---|
| `MINT` | Endereço do BCB | Banco ou conta destino | Emissão de Drex pelo Banco Central |
| `BURN` | Conta que teve Drex destruído | `null` | Queima de Drex, reduz oferta |
| `TRANSFER` | Conta remetente | Conta destinatária | Transferência entre contas |
| `FREEZE` | `null` | Conta congelada | Congelamento de conta pelo BCB |
| `UNFREEZE` | `null` | Conta descongelada | Descongelamento de conta pelo BCB |

> 💡 Cada transação possui um `tx_hash` único (funciona como um comprovante digital imutável) e está vinculada a um `block_number`.
    """,
)
async def list_transactions(address: Optional[str] = Query(None, description="Endereço da conta para filtrar transações (ex: 0xabc123...)"), db: AsyncSession = Depends(get_db)):
    return await drex_service.list_transactions(db, address)


@router.get(
    "/blocks",
    response_model=list[BlockResponse],
    summary="Listar blocos da blockchain",
    description="""
Retorna os últimos 20 blocos minerados na blockchain simulada, do mais recente ao mais antigo.

**O que é um bloco?**
Cada operação (mint, transfer, burn, freeze) gera um **bloco** contendo:
- Um **número sequencial** (`block_number`)
- Um **hash único** calculado com SHA-256 (`block_hash`)
- O **hash do bloco anterior** (`previous_hash`), formando a cadeia

**Por que isso importa?**
O encadeamento de hashes garante que nenhum registro possa ser alterado sem invalidar todos os blocos seguintes — esse é o princípio fundamental de imutabilidade de uma blockchain.

> O primeiro bloco da cadeia (bloco gênese) possui `previous_hash` igual a `0x0000...000`.
    """,
)
async def list_blocks(db: AsyncSession = Depends(get_db)):
    return await drex_service.list_blocks(db)


@router.get(
    "/supply",
    summary="Consultar oferta monetária",
    description="""
Retorna um resumo da oferta monetária do Drex em circulação.

**Campos retornados:**

| Campo | Descrição |
|---|---|
| `total_minted` | Total de Drex emitido pelo Banco Central desde o início |
| `total_burned` | Total de Drex destruído (queimado) pelo Banco Central |
| `circulating_supply` | Drex efetivamente em circulação (`total_minted - total_burned`) |

> Analogia: é como consultar quantas cédulas de real foram impressas, quantas foram destruídas e quantas estão em uso no país.
    """,
)
async def supply_stats(db: AsyncSession = Depends(get_db)):
    return await drex_service.get_supply_stats(db)
