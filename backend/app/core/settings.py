from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # app
    app_name: str = "SLEEP API"
    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # database
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    # redis
    redis_url: str

    # jwt
    jwt_secret: str
    jwt_alg: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7

    # aws
    aws_region: str | None = None
    aws_ses_sender: str | None = None
    s3_bucket: str | None = None

    # load from .env in backend/
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def db_dsn_async(self) -> str:
        """postgresql DSN for SQLAlchemy async engine"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

# single settings instance to import elsewhere
settings = Settings()
