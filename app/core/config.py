from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    BCB_ADMIN_KEY: str
    INITIAL_SUPPLY: int = 1_000_000

    model_config = {"env_file": ".env"}


settings = Settings()
