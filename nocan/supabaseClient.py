import os
from supabase import create_client, Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        self.client = None
        self.initializeClient()
    
    def initializeClient(self):
        """Initialize the Supabase client with environment variables or settings"""
        try:
            # Get Supabase URL and key from environment variables or Django settings
            supabaseUrl = os.getenv('SUPABASE_URL') or getattr(settings, 'SUPABASE_URL', None)
            supabaseKey = os.getenv('SUPABASE_ANON_KEY') or getattr(settings, 'SUPABASE_ANON_KEY', None)
            
            if not supabaseUrl or not supabaseKey:
                logger.error("Supabase URL or Key not found in environment variables or settings")
                raise ValueError("Supabase configuration missing")
            
            self.client = create_client(supabaseUrl, supabaseKey)
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    def getClient(self) -> Client:
        """Get the Supabase client instance"""
        if not self.client:
            self.initializeClient()
        return self.client
    
    def testConnection(self):
        """Test the connection to Supabase"""
        try:
            client = self.getClient()
            # Try a simple query to test connection
            response = client.table('_dummy_table_').select('*').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False

# Global instance
supabaseManager = SupabaseManager() 