from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import BcbUser
from app.schemas.schemas import BcbUserCreate, BcbUserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["🔐 Autenticação BCB"])


@router.post(
    "/registrar",
    response_model=BcbUserResponse,
    status_code=201,
    summary="Registrar novo usuário do Banco Central",
    description="""
Cria um novo usuário com acesso às operações restritas do Banco Central (mint, burn, freeze).

---

## 📋 Passo a passo para começar a usar o sistema

### Passo 1 — Registre um usuário do BCB

Este é o **primeiro passo obrigatório** antes de usar qualquer operação restrita.
Informe um `username`, `full_name` e `password`.

```json
{
  "username": "analista_bcb",
  "full_name": "Ana Paula Ferreira",
  "password": "senha_segura_123"
}
```

### Passo 2 — Faça login para obter o token JWT

Use `POST /auth/login` com o `username` e `password` cadastrados.
Você receberá um `access_token` com validade de **60 minutos**.

### Passo 3 — Use o token nas operações restritas

No Swagger UI, clique no botão **🔓 Authorize** (canto superior direito),
cole o token no campo **Value** e clique em **Authorize**.

A partir daí, todas as operações de mint, burn e freeze funcionarão automaticamente.

---

> ⚠️ **Regras:**
> - O `username` deve ser único no sistema.
> - A senha é armazenada com hash **bcrypt** — nunca em texto puro.
> - Apenas usuários registrados aqui podem operar como Banco Central.
    """,
)
async def registrar(payload: BcbUserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(BcbUser).where(BcbUser.username == payload.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Nome de usuário já cadastrado")
    user = BcbUser(
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login — obter token JWT",
    description="""
Autentica um usuário do Banco Central e retorna um **token JWT** para uso nas operações restritas.

---

## 📋 Como usar

### Passo 1 — Preencha as credenciais

Informe o `username` e `password` cadastrados em `POST /auth/registrar`.

> 💡 No Swagger UI, este endpoint usa o formulário padrão OAuth2
> com os campos `username` e `password`.

### Passo 2 — Copie o `access_token` retornado

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in_minutes": 60
}
```

### Passo 3 — Autorize no Swagger UI

Clique no botão **🔓 Authorize** no topo da página,
cole o token no campo **Value** e clique em **Authorize**.

### Passo 4 — Execute as operações restritas

Com o token ativo, você pode usar:
- `POST /drex/mint` — emitir Drex
- `POST /drex/burn` — queimar Drex
- `POST /drex/freeze` — congelar ou descongelar contas

> ⏱️ O token expira em **60 minutos**. Após isso, faça login novamente.
    """,
)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BcbUser).where(BcbUser.username == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.active:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    return TokenResponse(
        access_token=create_access_token(user.username),
        token_type="bearer",
        expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
