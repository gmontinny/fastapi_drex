from fastapi import Header, HTTPException, status
from app.core.config import settings


async def require_bcb_auth(x_bcb_key: str = Header(...)):
    if x_bcb_key != settings.BCB_ADMIN_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito ao Banco Central")
