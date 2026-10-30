from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: SecretStr
    
    model_config = SettingsConfigDict(
        env_file = Path(__file__).with_name(".env"),
        env_file_encoding = "utf-8",
    )
    
settings = Settings()