from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IELTS Writing Task 2 Evaluator"
    env: str = "dev"
    default_token_limit: int = 200000
    upload_dir: str = "./uploads"
    ocr_self_host: bool = False
    database_url: str = "sqlite:///./app.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
