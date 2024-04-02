from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr
    payment_token: str
    api_key : str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8' ,extra="ignore")


config = Settings()
print(config.payment_token)
print(config.api_key)