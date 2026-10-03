# 🪙 Simulador do Drex com Python, FastAPI, Blockchain e Smart Contracts

> Guia completo para construir uma mini-CBDC (Central Bank Digital Currency) funcional inspirada no Drex (moeda digital brasileira).

---

## 📑 Índice

1. [Entendendo o Drex](#-entendendo-o-drex-para-simulação)
2. [Arquitetura da Simulação](#️-arquitetura-da-simulação)
3. [Smart Contract DrexToken.sol](#-smart-contract-drextokensol)
4. [API FastAPI com Web3.py](#-api-fastapi-com-web3py)
5. [Passo a Passo para Executar](#️-passo-a-passo-para-executar)
6. [Considerações sobre Privacidade e Regulação](#-considerações-sobre-privacidade-e-regulação)
7. [Recursos Adicionais](#-recursos-adicionais)
8. [Resumo](#-resumo)

---

## 🧠 Entendendo o Drex para Simulação

O Drex foi originalmente concebido como uma **plataforma DLT (Distributed Ledger Technology) multi-ativos programável**. A arquitetura tinha duas camadas principais:

- **Atacado (wholesale)**: instituições financeiras liquidavam transações usando dinheiro do Banco Central.
- **Varejo (retail)**: agentes mantinham depósitos bancários tokenizados, e as transferências no atacado refletiam a execução de smart contracts no varejo.

O BC chegou a usar o **Hyperledger Besu** (uma implementação da Ethereum Virtual Machine) com contratos em **Solidity**, mas abandonou essa tecnologia por limitações de privacidade e escalabilidade. Para a sua simulação, você pode usar a **EVM** (Ethereum Virtual Machine) local (Ganache ou Hardhat) para representar essa arquitetura de forma simplificada.

---

## 🏗️ Arquitetura da Simulação

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Postman / Frontend)              │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────────┐
│              API FASTAPI (Python)                            │
│  • Endpoints REST para consultar saldo, transferir, mintar   │
│  • Usa Web3.py para interagir com a blockchain              │
└──────────────────────────┬──────────────────────────────────┘
                           │ JSON-RPC
┌──────────────────────────▼──────────────────────────────────┐
│         BLOCKCHAIN LOCAL (Ganache / Hardhat)                 │
│  • Smart Contract DrexToken.sol (ERC-20 customizado)        │
│  • Funções: mint, transfer, burn, freeze, balanceOf         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📜 Smart Contract DrexToken.sol

O contrato abaixo é inspirado na implementação open-source de referência do Drex, que inclui funcionalidades de **mint, transfer, burn, freeze e balanceOf**.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract DrexToken is ERC20, Ownable {
    // Mapeamento de contas congeladas (exigência do BCB)
    mapping(address => bool) public frozen;

    event Mint(address indexed to, uint256 amount);
    event Burn(address indexed from, uint256 amount);
    event Freeze(address indexed account, bool status);

    constructor() ERC20("Drex", "DREX") Ownable(msg.sender) {}

    // Apenas o BCB (owner) pode mintar
    function mint(address to, uint256 amount) external onlyOwner {
        require(!frozen[to], "Conta congelada");
        _mint(to, amount);
        emit Mint(to, amount);
    }

    // Queima tokens (reduz oferta)
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
        emit Burn(msg.sender, amount);
    }

    // Congelar/descongelar conta (controle regulatorio)
    function freeze(address account, bool status) external onlyOwner {
        frozen[account] = status;
        emit Freeze(account, status);
    }

    // Sobrescreve transfer para respeitar congelamento
    function transfer(address to, uint256 amount) public override returns (bool) {
        require(!frozen[msg.sender], "Remetente congelado");
        require(!frozen[to], "Destinatario congelado");
        return super.transfer(to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        require(!frozen[from], "Remetente congelado");
        require(!frozen[to], "Destinatario congelado");
        return super.transferFrom(from, to, amount);
    }
}
```

> **Nota**: O contrato real do Drex é mais complexo e inclui governança, permissões e privacidade. Este é um ponto de partida funcional para simulação.

---

## 🐍 API FastAPI com Web3.py

### 📦 Dependências

```bash
pip install fastapi uvicorn web3 py-solc-x python-dotenv
```

### 📁 Estrutura do Projeto

```
drex-simulator/
├── contracts/
│   └── DrexToken.sol
├── app/
│   ├── main.py
│   ├── blockchain.py
│   └── schemas.py
├── .env
└── requirements.txt
```

### 🔌 `blockchain.py` – Conexão com a Blockchain

```python
from web3 import Web3
from web3.contract import Contract
import os
from dotenv import load_dotenv

load_dotenv()

# Conexão com Ganache local (ou Hardhat)
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL", "http://127.0.0.1:8545")))

# Endereço do contrato deployado
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# ABI do contrato (obtido após compilação)
CONTRACT_ABI = [...]  # Cole aqui o ABI gerado pelo solc

def get_contract() -> Contract:
    return w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def get_balance(address: str) -> int:
    contract = get_contract()
    return contract.functions.balanceOf(address).call()

def transfer(from_addr: str, to_addr: str, amount: int, private_key: str) -> str:
    contract = get_contract()
    nonce = w3.eth.get_transaction_count(from_addr)
    tx = contract.functions.transfer(to_addr, amount).build_transaction({
        'chainId': w3.eth.chain_id,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()

def mint(to_addr: str, amount: int, private_key: str) -> str:
    contract = get_contract()
    nonce = w3.eth.get_transaction_count(w3.eth.accounts[0])
    tx = contract.functions.mint(to_addr, amount).build_transaction({
        'chainId': w3.eth.chain_id,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()
```

### 🚀 `main.py` – Endpoints FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.blockchain import get_balance, transfer, mint

app = FastAPI(title="Drex Simulator API", version="1.0.0")

class TransferRequest(BaseModel):
    from_address: str
    to_address: str
    amount: int
    private_key: str

class MintRequest(BaseModel):
    to_address: str
    amount: int
    private_key: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/balance/{address}")
def balance(address: str):
    try:
        bal = get_balance(address)
        return {"address": address, "balance": bal}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transfer")
def transfer_endpoint(req: TransferRequest):
    try:
        tx_hash = transfer(req.from_address, req.to_address, req.amount, req.private_key)
        return {"tx_hash": tx_hash, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/mint")
def mint_endpoint(req: MintRequest):
    try:
        tx_hash = mint(req.to_address, req.amount, req.private_key)
        return {"tx_hash": tx_hash, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### ⚙️ `.env` – Configurações

```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x...
PRIVATE_KEY_BCB=0x...
```

---

## 🛠️ Passo a Passo para Executar

1. **Inicie uma blockchain local** (Ganache ou Hardhat):
   ```bash
   npx hardhat node
   ```
2. **Compile e deploy o contrato** usando `solcx` ou Hardhat:
   ```python
   # deploy.py (simplificado)
   from web3 import Web3
   from solcx import compile_source, install_solc
   # ... compilar e deployar
   ```
3. **Configure o `.env`** com o endereço do contrato e a chave privada do BCB (owner).
4. **Execute a API**:
   ```bash
   uvicorn app.main:app --reload
   ```
5. **Teste os endpoints**:
   - `GET /balance/{address}`
   - `POST /transfer`
   - `POST /mint`

---

## 🔐 Considerações sobre Privacidade e Regulação

O Drex real exige **privacidade** e **controle regulatório**. Na sua simulação, você pode adicionar:

- **Zero-Knowledge Proofs** (via `zk-SNARKs` ou `Anonymous Zether`) para transações privadas.
- **Controle de acesso** com roles (ex.: `onlyOwner` para mint e freeze).
- **KYC/AML** simulado com uma whitelist de endereços autorizados.

---

## 📚 Recursos Adicionais

- **Repositório de referência**: [pedrosgmagalhaes/drex_smartcontracts](https://github.com/pedrosgmagalhaes/drex_smartcontracts) – implementação em Solidity com funcionalidades de mint, transfer, burn, freeze.
- **Tutorial DeFi com FastAPI + Web3.py**: [DEV Community – Building a DeFi Application](https://dev.to/rishisharma/building-a-decentralized-finance-defi-application-using-python-ecosystem-o6j) – cobre desde a configuração até a integração completa.
- **Simulador de blockchain em Python**: [Syedz68/Blockchain-Simulator](https://github.com/Syedz68/Blockchain-Simulator) – exemplo de blockchain educacional com FastAPI.

---

## ✅ Resumo

| Componente | Tecnologia |
|------------|------------|
| API REST | FastAPI + Uvicorn |
| Blockchain | Ganache / Hardhat (EVM local) |
| Smart Contract | Solidity (ERC-20 customizado) |
| Integração | Web3.py |
| Segurança | Ownable, freeze, mint controlado |

Com essa estrutura, você tem uma **simulação funcional do Drex** que pode ser expandida para incluir múltiplos ativos tokenizados, privacidade avançada e integração com sistemas externos.