import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # FastAPI Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    def validate_settings(self):
        """Validate that required settings are present"""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY environment variable is required")

# Create settings instance
settings = Settings()
