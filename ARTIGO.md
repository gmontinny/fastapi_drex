# Drex Simulator: Uma Abordagem Acadêmica para Simulação de Moeda Digital de Banco Central com FastAPI, PostgreSQL e Princípios de Blockchain

**Área:** Sistemas Distribuídos, Engenharia de Software, Tecnologia Financeira  
**Nível:** Graduação (Ciência da Computação, Engenharia da Computação) e Pós-Graduação  
**Palavras-chave:** CBDC, Drex, Blockchain, FastAPI, Python, DLT, Smart Contracts, Moeda Digital

---

## Resumo

Este artigo apresenta o **Drex Simulator**, um sistema acadêmico desenvolvido em Python com FastAPI e PostgreSQL que simula o comportamento operacional do Drex — a Moeda Digital de Banco Central (CBDC) do Brasil. O projeto implementa os conceitos fundamentais de uma CBDC soberana: emissão monetária controlada (*mint*), destruição de oferta (*burn*), transferências rastreáveis e controle regulatório via congelamento de contas (*freeze*). A simulação da blockchain é realizada sem dependência de infraestrutura distribuída real, utilizando encadeamento de hashes SHA-256 persistido em PostgreSQL. O sistema expõe uma API REST documentada com OpenAPI/Swagger, containerizada com Docker Compose, e inclui um contrato inteligente em Solidity como referência conceitual. O objetivo é fornecer um ambiente reproduzível e didático para o estudo de CBDCs, arquiteturas de API assíncronas e princípios de ledger distribuído.

---

## 1. Introdução

O sistema financeiro global atravessa uma transformação estrutural impulsionada pela digitalização da moeda soberana. Bancos centrais de mais de 130 países estudam ou desenvolvem ativamente suas CBDCs (*Central Bank Digital Currencies*) [1]. No Brasil, o **Drex** — anteriormente denominado Real Digital — representa a resposta do Banco Central do Brasil (BCB) a esse movimento, com pilotos conduzidos entre 2023 e 2024 sobre a plataforma Hyperledger Besu, uma implementação da Ethereum Virtual Machine (EVM) compatível com contratos Solidity [2].

A complexidade técnica envolvida — DLT (*Distributed Ledger Technology*), contratos inteligentes, criptografia assimétrica, consenso distribuído — representa uma barreira significativa para estudantes que desejam compreender o funcionamento interno de uma CBDC. Ferramentas como Ganache e Hardhat reduzem parte dessa barreira, mas ainda exigem conhecimento prévio do ecossistema Ethereum.

Este trabalho propõe uma abordagem alternativa: um simulador funcional do Drex construído inteiramente em Python, que abstrai a infraestrutura blockchain real e expõe os conceitos essenciais — rastreabilidade, imutabilidade, controle regulatório e oferta monetária programável — por meio de uma API REST moderna, documentada e containerizada.

### 1.1 Motivação

A ausência de ferramentas pedagógicas acessíveis para o estudo de CBDCs em língua portuguesa motivou o desenvolvimento deste projeto. Enquanto a literatura internacional dispõe de simuladores para Bitcoin [3] e Ethereum [4], não há, até o momento, um simulador didático específico para o Drex que combine:

- API REST documentada em português
- Persistência relacional com rastreabilidade completa
- Simulação de blockchain sem dependência de nó externo
- Containerização para reprodutibilidade imediata
- Referência em Solidity para correlação com o contrato real

### 1.2 Contribuições

As principais contribuições deste trabalho são:

1. Um simulador funcional e reproduzível do Drex, de código aberto
2. Uma arquitetura de referência para sistemas financeiros assíncronos com FastAPI e SQLAlchemy 2.0
3. A implementação de encadeamento de blocos SHA-256 sobre banco relacional
4. Um contrato inteligente ERC-20 customizado em Solidity como referência conceitual
5. Documentação técnica e guias de uso em português brasileiro

---

## 2. Fundamentação Teórica

### 2.1 Moedas Digitais de Banco Central (CBDCs)

Uma CBDC é uma forma digital de moeda fiduciária emitida e garantida por um banco central [5]. Diferencia-se das criptomoedas descentralizadas (Bitcoin, Ethereum) por três características fundamentais:

| Característica | Criptomoeda Descentralizada | CBDC |
|---|---|---|
| Emissor | Protocolo distribuído | Banco Central (Estado) |
| Lastro | Algoritmo de consenso | Reservas soberanas |
| Controle | Imutável por design | Programável pelo emissor |
| Privacidade | Pseudônima | Regulada por lei |

O modelo do Drex segue a arquitetura de **duas camadas** proposta pelo BIS (*Bank for International Settlements*) [6]:

- **Camada Atacado (Wholesale):** O BCB emite Drex diretamente para instituições financeiras autorizadas. As liquidações interbancárias ocorrem nesta camada com finalidade imediata.
- **Camada Varejo (Retail):** Instituições financeiras distribuem Drex tokenizado para pessoas físicas e jurídicas, representando depósitos bancários em formato digital.

### 2.2 Distributed Ledger Technology (DLT)

DLT é uma categoria de sistemas de banco de dados distribuídos onde múltiplos participantes mantêm cópias sincronizadas de um registro compartilhado [7]. A blockchain é a implementação mais conhecida de DLT, caracterizada pelo encadeamento criptográfico de blocos de transações.

O princípio de imutabilidade de uma blockchain deriva da função de hash criptográfico: cada bloco contém o hash do bloco anterior, formando uma cadeia onde qualquer alteração retroativa invalida todos os blocos subsequentes. Formalmente:

```
H(n) = SHA-256( block_number || H(n-1) || tx_id || timestamp )
```

Onde `H(n)` é o hash do bloco `n` e `H(n-1)` é o hash do bloco anterior. O bloco gênese possui `H(0) = 0x000...000` por convenção.

### 2.3 Smart Contracts e o Padrão ERC-20

Contratos inteligentes são programas armazenados em blockchain que executam automaticamente quando condições predefinidas são satisfeitas [8]. O padrão ERC-20 define uma interface comum para tokens fungíveis na EVM, incluindo operações de transferência, aprovação e consulta de saldo.

O Drex real utiliza um contrato ERC-20 customizado com extensões regulatórias: a função `freeze(address, bool)` permite ao BCB bloquear contas suspeitas, e a função `mint(address, uint256)` é restrita ao *owner* do contrato (o BCB), impedindo emissão não autorizada.

### 2.4 Programação Assíncrona em Python

O modelo de I/O assíncrono (*async/await*) em Python, baseado no protocolo ASGI (*Asynchronous Server Gateway Interface*), permite que um único processo gerencie milhares de conexões concorrentes sem bloqueio de thread [9]. Em sistemas financeiros, onde operações de banco de dados são o principal gargalo, o uso de drivers assíncronos como `asyncpg` reduz significativamente a latência de resposta.

---

## 3. Arquitetura do Sistema

### 3.1 Visão Geral

O Drex Simulator adota uma arquitetura em três camadas, containerizada com Docker Compose:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE                                   │
│          (Swagger UI / curl / Postman / Frontend)                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST (porta 8000)
┌──────────────────────────▼──────────────────────────────────────┐
│                    FASTAPI + UVICORN                             │
│                                                                  │
│  Camada de Rotas          Camada de Serviço                      │
│  ┌────────────────┐       ┌──────────────────────────────────┐  │
│  │ /accounts      │──────►│ drex_service.py                  │  │
│  │ /drex          │       │  mint_drex()   burn_drex()        │  │
│  │ /blockchain    │       │  transfer_drex() freeze_account() │  │
│  └────────────────┘       │  _mine_block() — SHA-256          │  │
│                           └──────────────────────────────────┘  │
│  Camada de Schemas                                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Pydantic v2 — validação de entrada e serialização          │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │ asyncpg (SQL assíncrono)
┌──────────────────────────▼──────────────────────────────────────┐
│                   POSTGRESQL 16                                  │
│   accounts │ transactions │ blocks                               │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Modelo de Dados

O modelo relacional é composto por três entidades principais:

**Tabela `accounts`** — representa participantes do sistema (BCB, bancos, pessoas):

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | UUID | Identificador interno |
| `address` | VARCHAR(42) | Endereço blockchain `0x...` gerado via UUID v4 |
| `name` | VARCHAR(100) | Nome do participante |
| `balance` | NUMERIC(20,8) | Saldo em Drex com precisão de 8 casas decimais |
| `frozen` | BOOLEAN | Estado de congelamento regulatório |
| `is_institution` | BOOLEAN | Distingue camada atacado (true) de varejo (false) |
| `created_at` | TIMESTAMPTZ | Timestamp com fuso horário |

**Tabela `transactions`** — registro imutável de todas as operações:

| Coluna | Tipo | Descrição |
|---|---|---|
| `tx_hash` | VARCHAR(66) | Hash SHA-256 único da transação |
| `type` | ENUM | `MINT`, `BURN`, `TRANSFER`, `FREEZE`, `UNFREEZE` |
| `from_address` | VARCHAR(42) FK | Remetente (nullable para MINT/FREEZE) |
| `to_address` | VARCHAR(42) FK | Destinatário (nullable para BURN) |
| `amount` | NUMERIC(20,8) | Valor movimentado |
| `block_number` | INTEGER | Referência ao bloco minerado |

**Tabela `blocks`** — cadeia de blocos simulada:

| Coluna | Tipo | Descrição |
|---|---|---|
| `block_number` | INTEGER | Número sequencial único |
| `block_hash` | VARCHAR(66) | Hash SHA-256 deste bloco |
| `previous_hash` | VARCHAR(66) | Hash do bloco anterior (encadeamento) |
| `tx_count` | INTEGER | Transações neste bloco |

### 3.3 Estrutura de Módulos

O projeto segue o padrão de arquitetura em camadas com separação clara de responsabilidades:

```
app/
├── api/routes/       # Camada de apresentação (HTTP handlers)
│   ├── accounts.py   # CRUD de contas
│   ├── drex.py       # Operações monetárias
│   └── blockchain.py # Consultas à cadeia
├── core/
│   ├── config.py     # Configurações via pydantic-settings
│   └── security.py   # Autenticação BCB por header HTTP
├── db/
│   ├── database.py   # Engine assíncrona + sessão
│   └── seed.py       # Dados iniciais para simulação
├── models/
│   └── models.py     # ORM SQLAlchemy com Mapped Types
├── schemas/
│   └── schemas.py    # Contratos Pydantic v2
└── services/
    └── drex_service.py  # Lógica de negócio + blockchain
```

---

## 4. Implementação

### 4.1 Simulação da Blockchain

O núcleo da simulação está na função `_mine_block`, que implementa o encadeamento criptográfico de blocos:

```python
async def _mine_block(db: AsyncSession, tx_id: str) -> int:
    latest = await _get_latest_block(db)
    prev_hash = latest.block_hash if latest else "0x" + "0" * 64
    block_number = (latest.block_number + 1) if latest else 1
    block_hash = _generate_tx_hash(
        f"{block_number}{prev_hash}{tx_id}{datetime.now(timezone.utc).isoformat()}"
    )
    block = Block(
        block_number=block_number,
        block_hash=block_hash,
        previous_hash=prev_hash,
        tx_count=1
    )
    db.add(block)
    return block_number
```

A função de hash utiliza SHA-256 sobre a concatenação de quatro elementos: número do bloco, hash anterior, identificador da transação e timestamp UTC. Essa composição garante que dois blocos com a mesma transação em momentos diferentes produzam hashes distintos, prevenindo colisões determinísticas.

O bloco gênese é identificado pelo `previous_hash = 0x` seguido de 64 zeros, convenção adotada pelo protocolo Bitcoin e mantida neste simulador para fidelidade conceitual.

### 4.2 Geração de Endereços

Os endereços de conta seguem o formato hexadecimal `0x` utilizado pela EVM, gerados a partir de UUID v4:

```python
def _generate_address() -> str:
    return "0x" + uuid.uuid4().hex[:40]
```

UUID v4 fornece 122 bits de aleatoriedade, resultando em probabilidade de colisão desprezível para fins acadêmicos. Em produção, endereços Ethereum são derivados da chave pública via algoritmo Keccak-256 [10].

### 4.3 Operação de Emissão (Mint)

A emissão monetária registra o BCB como remetente rastreável, garantindo auditabilidade completa da cadeia de custódia:

```python
async def mint_drex(db, to_address, amount, metadata_info):
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
    tx = Transaction(
        from_address=bcb_address,   # BCB como emissor rastreável
        to_address=to_address,
        type=TransactionType.MINT,
        ...
    )
```

A atomicidade da operação é garantida pela sessão assíncrona do SQLAlchemy: o bloco, a atualização de saldo e a transação são persistidos em um único `COMMIT`.

### 4.4 Controle Regulatório

A autenticação do BCB é implementada como dependência FastAPI injetada nas rotas protegidas:

```python
async def require_bcb_auth(x_bcb_key: str = Header(...)):
    if x_bcb_key != settings.BCB_ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao Banco Central"
        )
```

O padrão de injeção de dependência do FastAPI permite que a verificação seja declarada uma única vez e reutilizada em múltiplas rotas via `dependencies=[Depends(require_bcb_auth)]`, seguindo o princípio DRY (*Don't Repeat Yourself*).

### 4.5 Smart Contract de Referência

O contrato `DrexToken.sol` implementa o padrão ERC-20 com extensões regulatórias, servindo como referência conceitual para correlação com a lógica Python:

```solidity
contract DrexToken is IERC20 {
    address public owner; // Banco Central do Brasil
    mapping(address => bool) public frozen;

    modifier onlyOwner() {
        require(msg.sender == owner, "Apenas o BCB pode executar");
        _;
    }

    function mint(address to, uint256 amount)
        external onlyOwner notFrozen(to) {
        _totalSupply += amount;
        _balances[to] += amount;
        emit Mint(to, amount);
    }

    function freeze(address account, bool status)
        external onlyOwner {
        frozen[account] = status;
        emit Freeze(account, status);
    }
}
```

A tabela a seguir correlaciona as funções do contrato Solidity com os endpoints da API Python:

| Solidity | Endpoint REST | Restrição |
|---|---|---|
| `mint(address, uint256)` | `POST /drex/mint` | Apenas BCB |
| `burn(uint256)` | `POST /drex/burn` | Apenas BCB |
| `transfer(address, uint256)` | `POST /drex/transfer` | Conta não congelada |
| `freeze(address, bool)` | `POST /drex/freeze` | Apenas BCB |
| `balanceOf(address)` | `GET /accounts/{address}` | Pública |

---

## 5. Infraestrutura e Reprodutibilidade

### 5.1 Containerização com Docker Compose

O ambiente é definido em três serviços orquestrados:

```yaml
services:
  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U drex -d drexdb"]

  api:
    build: .
    depends_on:
      db:
        condition: service_healthy

  seed:
    command: python -m app.db.seed
    depends_on:
      db:
        condition: service_healthy
    restart: "no"
```

O uso de `healthcheck` com `condition: service_healthy` garante que a API só inicie após o PostgreSQL estar pronto para aceitar conexões, eliminando condições de corrida comuns em ambientes containerizados.

### 5.2 Dados Iniciais (Seed)

O serviço `seed` popula o banco com um cenário realista que simula as duas camadas do Drex:

```
BCB  ──mint 500.000──►  Banco do Brasil        (Bloco #1 — atacado)
BCB  ──mint 300.000──►  Caixa Econômica        (Bloco #2 — atacado)
BB   ──transfer 1.000──► Alice Souza           (Bloco #3 — varejo)
CEF  ──transfer 500──►  Bruno Lima             (Bloco #4 — varejo)
BB   ──burn 10.000──►   [destruído]            (Bloco #5 — contração)
```

Este cenário permite que estudantes explorem imediatamente os dados sem necessidade de configuração manual, reduzindo a fricção de entrada.

### 5.3 Documentação Interativa

A API expõe documentação OpenAPI 3.0 via Swagger UI em `/docs`, com descrições em português, exemplos de valores e explicações contextuais para cada campo. Isso permite que estudantes sem experiência prévia com APIs REST interajam com o sistema diretamente pelo navegador.

---

## 6. Cenários de Uso Acadêmico

### 6.1 Disciplinas Aplicáveis

| Disciplina | Conceitos Demonstrados |
|---|---|
| Sistemas Distribuídos | DLT, consenso, imutabilidade, encadeamento de hashes |
| Engenharia de Software | Arquitetura em camadas, DRY, injeção de dependência, ORM |
| Banco de Dados | Modelagem relacional, transações ACID, índices, chaves estrangeiras |
| Segurança da Informação | Autenticação por header, hash criptográfico, controle de acesso |
| Tecnologia Financeira | CBDC, oferta monetária, controle regulatório, rastreabilidade |
| Programação Web | API REST, OpenAPI, serialização JSON, validação de dados |

### 6.2 Experimentos Sugeridos

**Experimento 1 — Verificação de imutabilidade:**
Consulte `GET /blockchain/blocks` e observe o encadeamento de `previous_hash`. Modifique manualmente um registro na tabela `blocks` via SQL e verifique que o hash do bloco seguinte não corresponde mais ao hash alterado, demonstrando a propriedade de imutabilidade.

**Experimento 2 — Controle de oferta monetária:**
Execute sequências de `mint` e `burn` e acompanhe `GET /blockchain/supply`. Observe como `circulating_supply = total_minted - total_burned` reflete a política monetária simulada.

**Experimento 3 — Controle regulatório:**
Congele uma conta via `POST /drex/freeze` e tente realizar uma transferência para ela. Observe o erro `400 Bad Request` e consulte `GET /blockchain/transactions` para verificar que o congelamento foi registrado como transação imutável na blockchain.

**Experimento 4 — Rastreabilidade do BCB:**
Obtenha o endereço do BCB via `GET /accounts/` e filtre suas transações em `GET /blockchain/transactions?address=0x...`. Observe que o BCB aparece como `from_address` em todas as emissões, demonstrando rastreabilidade completa da origem monetária.

---

## 7. Limitações e Trabalhos Futuros

### 7.1 Limitações do Simulador

Este simulador é uma abstração pedagógica e não replica todos os aspectos de uma blockchain real:

- **Consenso distribuído:** Não há múltiplos nós validadores. A "mineração" é centralizada no serviço Python, sem mecanismo de consenso (PoW, PoS, PBFT).
- **Criptografia assimétrica:** Endereços são gerados via UUID, não por par de chaves pública/privada. Não há assinatura digital de transações.
- **Privacidade:** O Drex real utiliza técnicas de privacidade seletiva (como *Anonymous Zether* ou *Nightfall*) para ocultar valores de transações de terceiros. Este simulador não implementa privacidade.
- **Escalabilidade:** O banco de dados relacional centralizado não replica o comportamento de um ledger distribuído com múltiplos participantes.
- **Finalidade:** Não há mecanismo de confirmação de blocos. Toda transação é imediatamente final.

### 7.2 Trabalhos Futuros

- Implementação de assinatura digital com `cryptography` (Ed25519 ou ECDSA secp256k1)
- Adição de múltiplos nós com sincronização via WebSocket para simular consenso
- Integração com Hardhat para execução real do contrato `DrexToken.sol`
- Implementação de privacidade seletiva com Pedersen Commitments
- Painel de visualização da cadeia de blocos em tempo real (React + WebSocket)
- Testes de carga para análise de throughput (TPS — transações por segundo)

---

## 8. Conclusão

O Drex Simulator demonstra que é possível construir um ambiente didático funcional para o estudo de CBDCs sem a complexidade operacional de uma blockchain real. A combinação de FastAPI assíncrono, SQLAlchemy 2.0 com *Mapped Types*, PostgreSQL e Docker Compose resulta em um sistema reproduzível, documentado e acessível a estudantes de diferentes níveis.

Os conceitos fundamentais de uma CBDC — emissão controlada, rastreabilidade, imutabilidade e controle regulatório — são demonstrados de forma concreta e interativa, com dados de exemplo pré-carregados e documentação em português. O contrato Solidity incluído como referência permite a correlação direta entre a lógica Python e a implementação real do Drex sobre Hyperledger Besu.

O projeto está disponível como código aberto e pode ser executado com um único comando (`docker-compose up --build -d`), tornando-o adequado para uso em laboratórios de informática, disciplinas de graduação e pós-graduação, e como ponto de partida para pesquisas sobre sistemas financeiros digitais soberanos.

---

## Referências

[1] ATLANTIC COUNCIL. **Central Bank Digital Currency Tracker**. Disponível em: https://www.atlanticcouncil.org/cbdctracker/. Acesso em: 2024.

[2] BANCO CENTRAL DO BRASIL. **Drex — Real Digital**. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/drex. Acesso em: 2024.

[3] NAKAMOTO, S. **Bitcoin: A Peer-to-Peer Electronic Cash System**. 2008. Disponível em: https://bitcoin.org/bitcoin.pdf.

[4] BUTERIN, V. **Ethereum: A Next-Generation Smart Contract and Decentralized Application Platform**. 2014. Disponível em: https://ethereum.org/en/whitepaper/.

[5] BANK FOR INTERNATIONAL SETTLEMENTS. **Central bank digital currencies: foundational principles and core features**. BIS Papers, n. 1, 2020.

[6] BANK FOR INTERNATIONAL SETTLEMENTS. **CBDCs: an opportunity for the monetary system**. BIS Annual Economic Report, 2021.

[7] HYPERLEDGER FOUNDATION. **Hyperledger Besu Documentation**. Disponível em: https://besu.hyperledger.org/. Acesso em: 2024.

[8] SZABO, N. **Smart Contracts: Building Blocks for Digital Markets**. 1996. Disponível em: http://www.fon.hum.uva.nl/rob/Courses/InformationInSpeech/CDROM/Literature/LOTwinterschool2006/szabo.best.vwh.net/smart_contracts_2.html.

[9] PYTHON SOFTWARE FOUNDATION. **asyncio — Asynchronous I/O**. Python 3.12 Documentation. Disponível em: https://docs.python.org/3/library/asyncio.html.

[10] WOOD, G. **Ethereum: A Secure Decentralised Generalised Transaction Ledger**. Ethereum Yellow Paper, 2014. Disponível em: https://ethereum.github.io/yellowpaper/paper.pdf.

[11] RAMÍREZ, S. **FastAPI Documentation**. Disponível em: https://fastapi.tiangolo.com/. Acesso em: 2024.

[12] SQLALCHEMY AUTHORS. **SQLAlchemy 2.0 Documentation — Asyncio Extension**. Disponível em: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html. Acesso em: 2024.

[13] MAGALHÃES, P. S. **DrexToken Smart Contract Reference Implementation**. GitHub, 2023. Disponível em: https://github.com/pedrosgmagalhaes/drex_smartcontracts.

---

> **Nota:** Este artigo e o projeto associado foram desenvolvidos para fins **acadêmicos e educacionais**.  
> O Drex Simulator não representa a implementação oficial do Drex pelo Banco Central do Brasil,  
> nem deve ser utilizado em ambientes de produção ou para fins financeiros reais.
