from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AntiProxy"
    DATABASE_URL: str = "sqlite:///./antiproxy.db"
    ADSPOWER_API_URL: str = "http://localhost:50325"
    SECRET_KEY: str = "super-secret-antiproxy-key"
    ADMIN_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"

settings = Settings()
