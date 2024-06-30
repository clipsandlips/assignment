from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db_name: str
    postgres_domain: str
    postgres_port: str
    
    email_backend: str
    email_host: str
    email_port: int
    email_use_tls: bool
    email_host_user: str
    email_host_password: str


    class Config:
        env_file = ".env"

settings = Settings()


