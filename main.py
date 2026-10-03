from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db
from app.api.routes import accounts, drex, blockchain


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


DESCRICAO = """
## 🪙 Simulador do Drex — Moeda Digital Brasileira

Este sistema simula o funcionamento do **Drex**, a moeda digital oficial do **Banco Central do Brasil (BCB)**.

---

### 🏦 O que é o Drex?

O Drex é uma **CBDC** (*Central Bank Digital Currency*), ou seja, uma moeda digital emitida e controlada pelo governo brasileiro.
Ao contrário do Pix (que movimenta reais tradicionais), o Drex é uma representação digital do real em uma **blockchain**.

---

### ⚙️ Como funciona este simulador?

O sistema possui **três grupos de funcionalidades**:

| Grupo | O que faz |
|---|---|
| 🧑 **Contas** | Cria e consulta contas de bancos e pessoas |
| 💸 **Operações Drex** | Emite, queima, transfere e congela saldo |
| 🔗 **Blockchain** | Consulta o histórico de blocos e transações |

---

### 🔒 Operações restritas ao Banco Central

Algumas operações só podem ser feitas pelo **Banco Central**.
Para isso, envie o seguinte cabeçalho HTTP em sua requisição:

```
X-Bcb-Key: bcb-master-key-simulacao
```

Sem esse cabeçalho, a API retorna **403 Forbidden**.

---

### 📍 Endereços de conta

Cada conta possui um **endereço único** no formato `0x...` (igual ao usado em blockchains como Ethereum).
Esse endereço é gerado automaticamente ao criar uma conta e é usado em todas as operações.

---

### 🌱 Dados de exemplo já disponíveis

Ao iniciar o sistema, as seguintes contas são criadas automaticamente:

- **Banco Central do Brasil** — emissor do Drex
- **Banco do Brasil** — saldo de R$ 489.000
- **Caixa Econômica Federal** — saldo de R$ 299.500
- **Itaú Unibanco** e **Bradesco** — sem saldo inicial
- **Alice Souza** — saldo de R$ 1.000
- **Bruno Lima** — saldo de R$ 500
- **Carla Mendes** — sem saldo inicial

Use `GET /accounts/` para ver os endereços de cada conta.
"""

app = FastAPI(
    title="🪙 Drex Simulator — Moeda Digital Brasileira",
    description=DESCRICAO,
    version="1.0.0",
    contact={
        "name": "Projeto Acadêmico — Drex Simulator",
    },
    license_info={
        "name": "Uso Acadêmico",
    },
    lifespan=lifespan,
)

app.include_router(accounts.router)
app.include_router(drex.router)
app.include_router(blockchain.router)


@app.get(
    "/",
    tags=["Status"],
    summary="Verifica se a API está no ar",
    description="Retorna informações básicas sobre o sistema. Use para confirmar que a API está funcionando corretamente.",
)
async def root():
    return {
        "projeto": "Drex Simulator",
        "descricao": "Simulador acadêmico da CBDC brasileira",
        "status": "online",
        "documentacao": "/docs",
    }
