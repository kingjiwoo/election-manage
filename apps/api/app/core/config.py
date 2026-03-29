from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/election"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # External APIs
    kakao_rest_api_key: str = ""
    skt_tmap_app_key: str = ""
    public_data_api_key: str = ""

    # AI
    anthropic_api_key: str = ""

    # App
    app_env: str = "development"
    debug: bool = True


settings = Settings()
