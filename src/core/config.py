from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str
    APP_VERSION: str
    ENV: str
    LOG_LEVEL: str
    ORIGINS: str
    ROOT_PATH: str

    DATABASE_URL: str

    @property
    def origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ORIGINS.split(",") if origin.strip()]


settings = Settings()

