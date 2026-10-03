from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.models import TransactionType


class BcbUserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nome de usuário único para acesso ao painel do Banco Central. Use apenas letras, números e underscores.",
        examples=["analista_bcb"],
    )
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome completo do funcionário do Banco Central.",
        examples=["Ana Paula Ferreira"],
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Senha de acesso. Mínimo de 6 caracteres. Será armazenada com hash bcrypt.",
        examples=["senha_segura_123"],
    )


class BcbUserResponse(BaseModel):
    id: str = Field(description="Identificador interno do usuário (UUID).")
    username: str = Field(description="Nome de usuário.")
    full_name: str = Field(description="Nome completo.")
    active: bool = Field(description="Indica se o usuário está ativo.")
    created_at: datetime = Field(description="Data de criação do usuário.")

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str = Field(description="Token JWT para uso no cabeçalho `Authorization: Bearer <token>`.")
    token_type: str = Field(default="bearer", description="Tipo do token. Sempre `bearer`.")
    expires_in_minutes: int = Field(description="Tempo de expiração do token em minutos.")


class AccountCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome da pessoa física, jurídica ou instituição financeira.",
        examples=["João Silva", "Nubank"],
    )
    is_institution: bool = Field(
        False,
        description="Informe `true` para bancos e instituições financeiras; `false` para pessoas físicas ou empresas comuns.",
        examples=[False],
    )


class AccountResponse(BaseModel):
    id: str = Field(description="Identificador interno único da conta (UUID).")
    address: str = Field(description="Endereço blockchain da conta no formato `0x...`. Use este valor nas operações de transferência, mint e burn.")
    name: str = Field(description="Nome da conta.")
    balance: float = Field(description="Saldo atual em Drex.")
    frozen: bool = Field(description="Indica se a conta está congelada pelo Banco Central. Contas congeladas não podem enviar nem receber Drex.")
    is_institution: bool = Field(description="Indica se é uma instituição financeira (banco) ou uma pessoa.")
    created_at: datetime = Field(description="Data e hora de criação da conta.")

    model_config = {"from_attributes": True}


class MintRequest(BaseModel):
    to_address: str = Field(
        ...,
        description="Endereço da conta que vai receber os Drex emitidos. Use `GET /accounts/` para obter os endereços.",
        examples=["0xc2fbaf6f315b44a1999a1c442f0201fb"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Quantidade de Drex a emitir. Deve ser maior que zero.",
        examples=[50000.00],
    )
    metadata_info: Optional[str] = Field(
        None,
        description="Informação adicional opcional sobre a emissão (ex: motivo, referência).",
        examples=["Emissão trimestral Q1 2025"],
    )


class BurnRequest(BaseModel):
    from_address: str = Field(
        ...,
        description="Endereço da conta de onde os Drex serão destruídos.",
        examples=["0xc2fbaf6f315b44a1999a1c442f0201fb"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Quantidade de Drex a destruir. A conta deve ter saldo suficiente.",
        examples=[10000.00],
    )


class TransferRequest(BaseModel):
    from_address: str = Field(
        ...,
        description="Endereço da conta remetente (quem envia o Drex).",
        examples=["0xc2fbaf6f315b44a1999a1c442f0201fb"],
    )
    to_address: str = Field(
        ...,
        description="Endereço da conta destinatária (quem recebe o Drex).",
        examples=["0xc39a7db477514a368b39c40fcb251704"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Valor a transferir em Drex. O remetente deve ter saldo suficiente.",
        examples=[250.50],
    )
    metadata_info: Optional[str] = Field(
        None,
        description="Descrição opcional da transferência (ex: finalidade do pagamento).",
        examples=["Pagamento de salário"],
    )


class FreezeRequest(BaseModel):
    address: str = Field(
        ...,
        description="Endereço da conta a ser congelada ou descongelada.",
        examples=["0xc39a7db477514a368b39c40fcb251704"],
    )
    frozen: bool = Field(
        ...,
        description="`true` para congelar a conta; `false` para descongelar.",
        examples=[True],
    )


class TransactionResponse(BaseModel):
    id: str = Field(description="Identificador interno da transação (UUID).")
    tx_hash: str = Field(description="Hash SHA-256 único da transação no formato `0x...`. Funciona como comprovante digital imutável.")
    type: TransactionType = Field(description="Tipo da operação: MINT, BURN, TRANSFER, FREEZE ou UNFREEZE.")
    from_address: Optional[str] = Field(description="Endereço de quem enviou. Vazio em operações de emissão (MINT).")
    to_address: Optional[str] = Field(description="Endereço de quem recebeu. Vazio em operações de queima (BURN).")
    amount: float = Field(description="Valor movimentado em Drex.")
    block_number: int = Field(description="Número do bloco na blockchain onde esta transação foi registrada.")
    timestamp: datetime = Field(description="Data e hora exata em que a transação foi processada.")
    metadata_info: Optional[str] = Field(description="Informação adicional registrada na transação, se houver.")

    model_config = {"from_attributes": True}


class BlockResponse(BaseModel):
    block_number: int = Field(description="Número sequencial do bloco. O bloco 1 é o primeiro após o bloco gênesis.")
    block_hash: str = Field(description="Impressão digital única deste bloco, calculada com SHA-256. Qualquer alteração nos dados mudaria este hash.")
    previous_hash: str = Field(description="Hash do bloco anterior, formando a cadeia. O bloco gênesis possui `0x0000...000`.")
    tx_count: int = Field(description="Quantidade de transações registradas neste bloco.")
    timestamp: datetime = Field(description="Data e hora em que o bloco foi minerado.")

    model_config = {"from_attributes": True}
