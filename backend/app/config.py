from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    OPENAI_API_KEY: str

    MODEL_NAME: str = "gpt-5-mini"


    class Config:
        env_file = ".env"


settings = Settings()