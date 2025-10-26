from pydantic_settings import BaseSettings
from pydantic import Field
class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./local.db", alias="DATABASE_URL")
    secret_key: str = Field(default="change_me", alias="SECRET_KEY")
    jwt_exp_minutes: int = Field(default=4320, alias="JWT_EXP_MINUTES")
    class Config: env_file = ".env"; extra = "ignore"
settings = Settings()
