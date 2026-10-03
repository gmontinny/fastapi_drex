# 🪙 Drex Simulator

> Simulador acadêmico do **Drex** — a Moeda Digital Brasileira (CBDC) do Banco Central do Brasil.  
> Construído com **Python**, **FastAPI**, **PostgreSQL** e princípios de **blockchain** para fins educacionais.

---

## 📑 Índice

1. [O que é o Drex?](#-o-que-é-o-drex)
2. [Objetivo do Projeto](#-objetivo-do-projeto)
3. [Tecnologias](#-tecnologias)
4. [Arquitetura](#️-arquitetura)
5. [Estrutura do Projeto](#-estrutura-do-projeto)
6. [Modelo de Dados](#-modelo-de-dados)
7. [Endpoints da API](#-endpoints-da-api)
8. [Segurança e Controle Regulatório](#-segurança-e-controle-regulatório)
9. [Smart Contract de Referência](#-smart-contract-de-referência)
10. [Como Executar](#-como-executar)
11. [Guia de Uso Passo a Passo](#-guia-de-uso-passo-a-passo)
12. [Exemplos de Uso](#-exemplos-de-uso)
13. [Dados Iniciais (Seed)](#-dados-iniciais-seed)
14. [Artigo Científico](#-artigo-científico)

---

## 🧠 O que é o Drex?

O **Drex** é o projeto de moeda digital oficial do **Banco Central do Brasil (BCB)**, classificado como uma **CBDC** (*Central Bank Digital Currency* — Moeda Digital de Banco Central). Diferente das criptomoedas descentralizadas, o Drex é emitido, controlado e garantido pelo Estado brasileiro.

### Características principais

| Característica | Descrição |
|---|---|
| Emissor | Banco Central do Brasil |
| Tecnologia base | DLT — *Distributed Ledger Technology* |
| Plataforma original | Hyperledger Besu (EVM-compatible) |
| Contratos | Solidity (ERC-20 customizado) |
| Camadas | Atacado (wholesale) + Varejo (retail) |
| Controle | Mint, Burn, Freeze regulatório |

### As duas camadas do Drex

```
┌─────────────────────────────────────────────────────────────┐
│  CAMADA ATACADO (Wholesale)                                  │
│  BCB ──mint──► Banco do Brasil, Caixa, Itaú, Bradesco...    │
│  Liquidação interbancária com dinheiro do Banco Central      │
└─────────────────────────────────────────────────────────────┘
                          │ tokenização
┌─────────────────────────▼───────────────────────────────────┐
│  CAMADA VAREJO (Retail)                                      │
│  Bancos ──transfer──► Pessoas físicas e jurídicas            │
│  Depósitos bancários tokenizados em smart contracts          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Objetivo do Projeto

Este projeto foi desenvolvido para **fins acadêmicos**, com o objetivo de demonstrar:

- O comportamento de uma **CBDC** em ambiente simulado
- A integração entre **API REST moderna** e **lógica de blockchain**
- O papel do **controle regulatório** em moedas digitais soberanas
- A **rastreabilidade imutável** de transações financeiras via encadeamento de blocos
- Boas práticas de desenvolvimento com **Python assíncrono** e **containerização**

---

## 🛠️ Tecnologias

### Backend

| Tecnologia | Versão | Papel no Projeto |
|---|---|---|
| **Python** | 3.12 | Linguagem principal |
| **FastAPI** | 0.111.0 | Framework web assíncrono para a API REST |
| **Uvicorn** | 0.30.1 | Servidor ASGI de alta performance |
| **Pydantic v2** | 2.7.1 | Validação de dados e schemas |
| **Pydantic Settings** | 2.3.0 | Gerenciamento de configurações via `.env` |

### Banco de Dados

| Tecnologia | Versão | Papel no Projeto |
|---|---|---|
| **PostgreSQL** | 16 | Banco de dados relacional principal |
| **SQLAlchemy** | 2.0.30 | ORM assíncrono com *Mapped Types* |
| **asyncpg** | 0.29.0 | Driver async nativo para PostgreSQL |
| **Alembic** | 1.13.1 | Gerenciamento de migrações de schema |

### Segurança

| Tecnologia | Versão | Papel no Projeto |
|---|---|---|
| **passlib[bcrypt]** | 1.7.4 | Hash seguro de senhas |
| **python-jose** | 3.3.0 | Geração e validação de tokens JWT |
| **python-dotenv** | 1.0.1 | Isolamento de variáveis sensíveis |

### Infraestrutura

| Tecnologia | Versão | Papel no Projeto |
|---|---|---|
| **Docker** | — | Containerização da aplicação |
| **Docker Compose** | — | Orquestração dos serviços |
| **httpx** | 0.27.0 | Cliente HTTP assíncrono para testes |

### Blockchain Simulada

| Conceito | Implementação |
|---|---|
| Endereços | UUID v4 → formato `0x` hexadecimal |
| Hash de transação | SHA-256 sobre dados da operação |
| Encadeamento de blocos | `block_hash` referencia `previous_hash` do bloco anterior |
| Bloco gênese | `previous_hash = 0x000...000` |

---

## 🏗️ Arquitetura

### Visão Geral

```
┌──────────────────────────────────────────────────────────────────┐
│                    CLIENTE                                        │
│            (Postman / curl / Frontend / Swagger UI)              │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTP / REST
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    FASTAPI  (porta 8000)                          │
│                                                                   │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │  /accounts  │  │     /drex        │  │   /blockchain      │  │
│  │             │  │                  │  │                    │  │
│  │ POST /      │  │ POST /mint  🔒   │  │ GET /transactions  │  │
│  │ GET  /      │  │ POST /burn  🔒   │  │ GET /blocks        │  │
│  │ GET  /{addr}│  │ POST /transfer   │  │ GET /supply        │  │
│  └─────────────┘  │ POST /freeze 🔒  │  └────────────────────┘  │
│                   └──────────────────┘                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                  drex_service.py                           │  │
│  │  mint_drex │ burn_drex │ transfer_drex │ freeze_account    │  │
│  │  _mine_block (SHA-256 encadeado) │ get_supply_stats        │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              SQLAlchemy Async ORM                          │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │ asyncpg (SQL async)
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                 POSTGRESQL 16  (porta 5432)                       │
│                                                                   │
│   ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│   │   accounts   │  │  transactions   │  │     blocks       │   │
│   │              │  │                 │  │                  │   │
│   │ id           │  │ id              │  │ id               │   │
│   │ address (PK) │  │ tx_hash         │  │ block_number     │   │
│   │ name         │  │ type            │  │ block_hash       │   │
│   │ balance      │  │ from_address FK │  │ previous_hash    │   │
│   │ frozen       │  │ to_address   FK │  │ tx_count         │   │
│   │ is_institution│ │ amount          │  │ timestamp        │   │
│   │ created_at   │  │ block_number    │  └──────────────────┘   │
│   └──────────────┘  │ timestamp       │                          │
│                     │ metadata_info   │                          │
│                     └─────────────────┘                          │
└──────────────────────────────────────────────────────────────────┘
```

### Fluxo de uma Transação

```
Cliente                  FastAPI               PostgreSQL
   │                        │                       │
   │── POST /drex/transfer ─►│                       │
   │                        │── valida schema ──────►│
   │                        │── busca sender ────────►│
   │                        │◄── Account ────────────│
   │                        │── busca receiver ──────►│
   │                        │◄── Account ────────────│
   │                        │                       │
   │                        │── verifica frozen      │
   │                        │── verifica saldo       │
   │                        │                       │
   │                        │── _mine_block()        │
   │                        │   SHA-256(n+prev+id+ts)│
   │                        │── INSERT Block ────────►│
   │                        │── UPDATE balances ─────►│
   │                        │── INSERT Transaction ──►│
   │                        │── COMMIT ──────────────►│
   │                        │◄── tx_hash ────────────│
   │◄── TransactionResponse ─│                       │
```

### Encadeamento de Blocos

```
  Bloco Gênese              Bloco 1                  Bloco 2
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ block_number: 0  │    │ block_number: 1  │    │ block_number: 2  │
│ prev: 0x0000...  │◄───│ prev: 0xABCD...  │◄───│ prev: 0x1234...  │
│ hash: 0xABCD...  │    │ hash: 0x1234...  │    │ hash: 0x5678...  │
│ tx_count: 1      │    │ tx_count: 1      │    │ tx_count: 1      │
└──────────────────┘    └──────────────────┘    └──────────────────┘
       MINT                   TRANSFER                  BURN
```

---

## 📁 Estrutura do Projeto

```
fastapi_drex/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── accounts.py       # CRUD de contas
│   │       ├── drex.py           # Operações mint/burn/transfer/freeze
│   │       └── blockchain.py     # Consulta de blocos, txs e supply
│   │
│   ├── core/
│   │   ├── config.py             # Settings via pydantic-settings
│   │   └── security.py           # Autenticação BCB via header
│   │
│   ├── db/
│   │   ├── database.py           # Engine async + sessão + init_db
│   │   └── seed.py               # Dados iniciais para simulação
│   │
│   ├── models/
│   │   └── models.py             # ORM: Account, Transaction, Block
│   │
│   ├── schemas/
│   │   └── schemas.py            # Pydantic: request/response models
│   │
│   └── services/
│       └── drex_service.py       # Lógica de negócio + blockchain sim
│
├── contracts/
│   └── DrexToken.sol             # Smart contract Solidity (referência)
│
├── .env                          # Variáveis de ambiente
├── .gitignore
├── Dockerfile                    # Imagem Python 3.12-slim
├── docker-compose.yml            # db + api + seed
├── main.py                       # Entrypoint FastAPI
├── requirements.txt
├── DOC.md                        # Documentação técnica de referência
└── README.md
```

---

## 🗄️ Modelo de Dados

### `accounts` — Contas

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | UUID | Identificador interno |
| `address` | VARCHAR(42) | Endereço blockchain `0x...` (único) |
| `name` | VARCHAR(100) | Nome da instituição ou pessoa |
| `balance` | NUMERIC(20,8) | Saldo em Drex |
| `frozen` | BOOLEAN | Conta bloqueada pelo BCB |
| `is_institution` | BOOLEAN | Distingue atacado de varejo |
| `created_at` | TIMESTAMPTZ | Data de criação |

### `transactions` — Transações

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | UUID | Identificador interno |
| `tx_hash` | VARCHAR(66) | Hash SHA-256 da transação `0x...` |
| `type` | ENUM | `MINT`, `BURN`, `TRANSFER`, `FREEZE`, `UNFREEZE` |
| `from_address` | VARCHAR(42) FK | Endereço remetente (nullable) |
| `to_address` | VARCHAR(42) FK | Endereço destinatário (nullable) |
| `amount` | NUMERIC(20,8) | Valor da operação |
| `block_number` | INTEGER | Bloco onde foi registrada |
| `timestamp` | TIMESTAMPTZ | Data/hora da operação |
| `metadata_info` | VARCHAR(255) | Informação adicional opcional |

### `blocks` — Blocos

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER | Chave primária auto-incremental |
| `block_number` | INTEGER | Número sequencial do bloco (único) |
| `block_hash` | VARCHAR(66) | Hash SHA-256 do bloco `0x...` |
| `previous_hash` | VARCHAR(66) | Hash do bloco anterior (encadeamento) |
| `tx_count` | INTEGER | Quantidade de transações no bloco |
| `timestamp` | TIMESTAMPTZ | Data/hora de mineração |

---

## 🔌 Endpoints da API

A documentação interativa completa está disponível em **`http://localhost:8000/docs`** (Swagger UI).

### Contas — `/accounts`

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/accounts/` | Cria uma nova conta |
| `GET` | `/accounts/` | Lista todas as contas |
| `GET` | `/accounts/{address}` | Consulta saldo e status de uma conta |

### Operações Drex — `/drex`

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/drex/mint` | 🔒 BCB | Emite novos Drex para uma conta |
| `POST` | `/drex/burn` | 🔒 BCB | Queima Drex, reduzindo a oferta |
| `POST` | `/drex/transfer` | — | Transfere Drex entre contas |
| `POST` | `/drex/freeze` | 🔒 BCB | Congela ou descongela uma conta |

### Blockchain — `/blockchain`

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/blockchain/transactions` | Lista transações (filtro por `?address=`) |
| `GET` | `/blockchain/blocks` | Lista os últimos 20 blocos minerados |
| `GET` | `/blockchain/supply` | Retorna oferta total, queimada e circulante |

---

## 🔐 Segurança e Controle Regulatório

As operações exclusivas do **Banco Central** são protegidas por autenticação via **HTTP Header**:

```
X-Bcb-Key: bcb-master-key-simulacao
```

Qualquer requisição a `/drex/mint`, `/drex/burn` ou `/drex/freeze` sem esse header retorna `403 Forbidden`.

### Regras de negócio implementadas

- Conta **congelada** não pode enviar nem receber Drex
- Saldo **insuficiente** bloqueia transferências e queimas
- Apenas o BCB (via header) pode **emitir**, **queimar** e **congelar**
- Cada operação gera um **bloco imutável** com hash encadeado

---

## 📜 Smart Contract de Referência

O arquivo `contracts/DrexToken.sol` contém a implementação em **Solidity** que inspirou a lógica deste simulador. Ele representa o contrato ERC-20 customizado que o Banco Central utilizaria em uma blockchain EVM real (como o Hyperledger Besu).

```
Funcionalidades do contrato:
  ✅ mint(address, amount)         — apenas owner (BCB)
  ✅ burn(amount)                  — qualquer conta não congelada
  ✅ transfer(to, amount)          — respeita congelamento
  ✅ freeze(address, status)       — apenas owner (BCB)
  ✅ balanceOf(address)            — consulta pública
```

> O contrato Solidity é fornecido como **referência acadêmica**. A lógica equivalente é executada em Python pelo `drex_service.py`.

---

## 🗺️ Guia de Uso Passo a Passo

Esta seção mostra o fluxo completo de uso do sistema, do zero até consultar o histórico de transações na blockchain.

---

### 🔵 Cenário 1 — Consultar transações de uma conta existente

> Use este fluxo para explorar os dados já criados pelo seed automático.

**Passo 1 — Liste todas as contas para obter os endereços**

```bash
curl http://localhost:8000/accounts/
```

No resultado, localize a conta desejada e copie o campo `address`. Exemplo de resposta:

```json
[
  {
    "address": "0xc2fbaf6f315b44a1999a1c442f0201fb",
    "name": "Banco do Brasil",
    "balance": 489000.0,
    "frozen": false
  }
]
```

**Passo 2 — Consulte as transações daquela conta**

```bash
curl "http://localhost:8000/blockchain/transactions?address=0xc2fbaf6f315b44a1999a1c442f0201fb"
```

Retorna todas as transações enviadas **e** recebidas por essa conta.

**Passo 3 — Consulte o saldo e status da conta**

```bash
curl http://localhost:8000/accounts/0xc2fbaf6f315b44a1999a1c442f0201fb
```

---

### 🟢 Cenário 2 — Criar conta e receber Drex do Banco Central

> Use este fluxo para simular a entrada de uma nova instituição no sistema.

**Passo 1 — Crie a nova conta**

```bash
curl -X POST http://localhost:8000/accounts/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Nubank", "is_institution": true}'
```

Guarde o `address` retornado. Exemplo: `0xabcdef1234567890abcdef1234567890abcdef12`

**Passo 2 — O BCB emite Drex para a nova conta** *(requer autenticação)*

```bash
curl -X POST http://localhost:8000/drex/mint \
  -H "Content-Type: application/json" \
  -H "X-Bcb-Key: bcb-master-key-simulacao" \
  -d '{
    "to_address": "0xabcdef1234567890abcdef1234567890abcdef12",
    "amount": 100000,
    "metadata_info": "Emissão inicial Nubank"
  }'
```

**Passo 3 — Confirme o saldo da nova conta**

```bash
curl http://localhost:8000/accounts/0xabcdef1234567890abcdef1234567890abcdef12
```

**Passo 4 — Veja a transação registrada na blockchain**

```bash
curl "http://localhost:8000/blockchain/transactions?address=0xabcdef1234567890abcdef1234567890abcdef12"
```

---

### 🟡 Cenário 3 — Transferência entre banco e pessoa física

> Simula o fluxo de varejo: banco distribui Drex para um cliente.

**Passo 1 — Crie a conta do cliente**

```bash
curl -X POST http://localhost:8000/accounts/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Maria Oliveira", "is_institution": false}'
```

Guarde o `address` retornado. Exemplo: `0x1111222233334444555566667777888899990000`

**Passo 2 — Transfira Drex do banco para o cliente**

```bash
curl -X POST http://localhost:8000/drex/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "0xabcdef1234567890abcdef1234567890abcdef12",
    "to_address": "0x1111222233334444555566667777888899990000",
    "amount": 500.00,
    "metadata_info": "Crédito de salário"
  }'
```

**Passo 3 — Verifique os saldos atualizados**

```bash
# Saldo do banco (debitado)
curl http://localhost:8000/accounts/0xabcdef1234567890abcdef1234567890abcdef12

# Saldo do cliente (creditado)
curl http://localhost:8000/accounts/0x1111222233334444555566667777888899990000
```

**Passo 4 — Consulte o bloco gerado pela transferência**

```bash
curl http://localhost:8000/blockchain/blocks
```

---

### 🔴 Cenário 4 — Congelar e descongelar uma conta

> Simula o controle regulatório do Banco Central.

**Passo 1 — Congele a conta** *(requer autenticação)*

```bash
curl -X POST http://localhost:8000/drex/freeze \
  -H "Content-Type: application/json" \
  -H "X-Bcb-Key: bcb-master-key-simulacao" \
  -d '{
    "address": "0x1111222233334444555566667777888899990000",
    "frozen": true
  }'
```

**Passo 2 — Tente transferir para a conta congelada (deve falhar)**

```bash
curl -X POST http://localhost:8000/drex/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "0xabcdef1234567890abcdef1234567890abcdef12",
    "to_address": "0x1111222233334444555566667777888899990000",
    "amount": 100
  }'
```

Resposta esperada: `400 Bad Request — Destinatário congelado — operação negada`

**Passo 3 — Descongele a conta** *(requer autenticação)*

```bash
curl -X POST http://localhost:8000/drex/freeze \
  -H "Content-Type: application/json" \
  -H "X-Bcb-Key: bcb-master-key-simulacao" \
  -d '{
    "address": "0x1111222233334444555566667777888899990000",
    "frozen": false
  }'
```

---

### ⚠️ Observação sobre o Banco Central e transações antigas

O endereço do **Banco Central do Brasil** só aparece como remetente (`from_address`) em operações de MINT realizadas **após a inicialização do sistema**. As emissões do seed inicial (blocos 1 a 5) foram gravadas sem o endereço do BCB por limitação da versão original.

Para gerar novas transações rastreáveis do BCB, use `POST /drex/mint` com o header de autenticação.

---

## 🚀 Como Executar

### Pré-requisitos

- [Docker](https://www.docker.com/) instalado
- [Docker Compose](https://docs.docker.com/compose/) instalado

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd fastapi_drex
```

### 2. Configure as variáveis de ambiente

O arquivo `.env` já está configurado para uso local com Docker:

```env
DATABASE_URL=postgresql+asyncpg://drex:drex123@db:5432/drexdb
SECRET_KEY=drex-simulator-secret-key-academico-2024
BCB_ADMIN_KEY=bcb-master-key-simulacao
INITIAL_SUPPLY=1000000
```

### 3. Suba os containers

```bash
docker-compose up --build -d
```

Isso irá iniciar três serviços:

| Serviço | Descrição |
|---|---|
| `db` | PostgreSQL 16 com healthcheck |
| `api` | FastAPI na porta `8000` |
| `seed` | Script que popula o banco com dados iniciais |

### 4. Acesse a aplicação

| Recurso | URL |
|---|---|
| API Root | http://localhost:8000 |
| Swagger UI (docs) | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### 5. Comandos úteis

```bash
# Ver logs da API
docker-compose logs -f api

# Ver logs do seed
docker-compose logs seed

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (limpa o banco)
docker-compose down -v

# Recriar apenas a API após mudanças no código
docker-compose up --build api
```

---

## 💡 Exemplos de Uso

### Criar uma nova conta

```bash
curl -X POST http://localhost:8000/accounts/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Nubank", "is_institution": true}'
```

### Emitir Drex (BCB)

```bash
curl -X POST http://localhost:8000/drex/mint \
  -H "Content-Type: application/json" \
  -H "X-Bcb-Key: bcb-master-key-simulacao" \
  -d '{"to_address": "0x<address>", "amount": 50000, "metadata_info": "Emissão Q1 2025"}'
```

### Transferir Drex

```bash
curl -X POST http://localhost:8000/drex/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "0x<address_banco>",
    "to_address": "0x<address_pessoa>",
    "amount": 250.50,
    "metadata_info": "Pagamento de salário"
  }'
```

### Congelar uma conta (BCB)

```bash
curl -X POST http://localhost:8000/drex/freeze \
  -H "Content-Type: application/json" \
  -H "X-Bcb-Key: bcb-master-key-simulacao" \
  -d '{"address": "0x<address>", "frozen": true}'
```

### Consultar oferta monetária

```bash
curl http://localhost:8000/blockchain/supply
```

```json
{
  "total_minted": 800000.0,
  "total_burned": 10000.0,
  "circulating_supply": 790000.0
}
```

### Consultar histórico de transações de uma conta

```bash
# 1. Liste as contas para obter o endereço
curl http://localhost:8000/accounts/

# 2. Use o endereço no filtro
curl "http://localhost:8000/blockchain/transactions?address=0x<address>"
```

---

## 🌱 Dados Iniciais (Seed)

Ao subir com `docker-compose`, o serviço `seed` popula automaticamente o banco com um cenário realista:

### Contas criadas

| Nome | Tipo | Saldo inicial |
|---|---|---|
| Banco Central do Brasil | Instituição | R$ 0 (emissor) |
| Banco do Brasil | Instituição | R$ 489.000 |
| Caixa Econômica Federal | Instituição | R$ 299.500 |
| Itaú Unibanco | Instituição | R$ 0 |
| Bradesco | Instituição | R$ 0 |
| Alice Souza | Pessoa física | R$ 1.000 |
| Bruno Lima | Pessoa física | R$ 500 |
| Carla Mendes | Pessoa física | R$ 0 |

### Operações simuladas

```
BCB  ──mint 500.000──►  Banco do Brasil        (Bloco #1 — atacado)
BCB  ──mint 300.000──►  Caixa Econômica        (Bloco #2 — atacado)
BB   ──transfer 1.000──► Alice Souza           (Bloco #3 — varejo)
CEF  ──transfer 500──►  Bruno Lima             (Bloco #4 — varejo)
BB   ──burn 10.000──►   [destruído]            (Bloco #5 — contração)
```

---

## 📄 Artigo Científico

Este projeto é acompanhado de um artigo científico completo voltado para estudantes de **Ciência da Computação**, **Engenharia da Computação** e **pós-graduação**:

📖 **[ARTIGO.md](./ARTIGO.md)** — *Drex Simulator: Uma Abordagem Acadêmica para Simulação de Moeda Digital de Banco Central com FastAPI, PostgreSQL e Princípios de Blockchain*

O artigo cobre:
- Fundamentação teórica sobre CBDCs, DLT e Smart Contracts
- Decisões de arquitetura e modelagem de dados
- Análise da implementação da blockchain simulada
- Correlação entre o contrato Solidity e a lógica Python
- Experimentos sugeridos para uso em sala de aula
- Limitações do simulador e trabalhos futuros
- 13 referências bibliográficas

---

## 📚 Referências

- [Banco Central do Brasil — Drex](https://www.bcb.gov.br/estabilidadefinanceira/drex)
- [Repositório de referência — DrexToken.sol](https://github.com/pedrosgmagalhaes/drex_smartcontracts)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Hyperledger Besu — EVM para CBDC](https://besu.hyperledger.org/)

---

> Projeto desenvolvido para fins **acadêmicos e educacionais**.  
> Não representa a implementação real do Drex pelo Banco Central do Brasil.
