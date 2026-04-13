from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Invoice Automation"
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "invoice_automation"
    
    GROQ_API_KEY_1: str = ""
    GROQ_API_KEY_2: str = ""
    GROQ_API_KEY_3: str = ""
    
    @property
    def groq_keys(self):
        return [k for k in [self.GROQ_API_KEY_1, self.GROQ_API_KEY_2, self.GROQ_API_KEY_3] if k]
    
    FINANCE_EMAIL: str = ""
    EMAIL_PASSWORD: str = ""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    IMAP_SERVER: str = "imap.gmail.com"
    
    class Config:
        env_file = ".env"
        extra = "ignore" # This prevents crashes if you have extra variables in .env

settings = Settings()
