from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Meta WhatsApp Cloud API
    WHATSAPP_TOKEN: str
    WHATSAPP_PHONE_ID: str
    WEBHOOK_VERIFY_TOKEN: str

    # Recipient (E.164 without the +, e.g. 5511999998888 for a Brazil number)
    GIRLFRIEND_PHONE: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
