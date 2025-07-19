from supabase import create_client, Client
from .settings import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            try:
                # Validate settings before creating client
                settings.validate_settings()
                
                # Create Supabase client
                self._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
    
    @property
    def client(self) -> Client:
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client
    
    def test_connection(self) -> bool:
        """Test the Supabase connection"""
        try:
            # Try to fetch from a system table to test connection
            result = self._client.table('users').select('*').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False

# Create singleton instance
supabase_client = SupabaseClient()

def get_supabase() -> Client:
    """Dependency to get Supabase client"""
    return supabase_client.client
