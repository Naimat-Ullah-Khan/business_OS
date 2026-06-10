from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    SECRET_KEY: str = "super secret key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()