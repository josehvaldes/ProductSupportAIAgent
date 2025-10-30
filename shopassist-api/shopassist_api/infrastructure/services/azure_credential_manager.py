from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from shopassist_api.logging_config import get_logger
from threading import RLock  # Changed from Lock


logger = get_logger(__name__)

class AzureCredentialManager:
    """Singleton manager for Azure credentials and token providers."""
    
    _instance = None
    _lock = RLock()
    _credential = None
    _openai_token_provider = None
    _cosmos_credential = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_credential(self) -> DefaultAzureCredential:
        """Get shared Azure credential (lazy initialization)."""
        if self._credential is None:
            with self._lock:
                if self._credential is None:
                    logger.info("Initializing shared Azure DefaultAzureCredential")
                    self._credential = DefaultAzureCredential()
        return self._credential
    
    def get_openai_token_provider(self):
        """Get token provider for Azure OpenAI."""
        if self._openai_token_provider is None:
            with self._lock:
                if self._openai_token_provider is None:
                    logger.info("Initializing OpenAI token provider")
                    credential = self.get_credential()
                    self._openai_token_provider = get_bearer_token_provider(
                        credential,
                        "https://cognitiveservices.azure.com/.default"
                    )
        return self._openai_token_provider
    
    def get_cosmos_credential(self) -> DefaultAzureCredential:
        """Get credential for Cosmos DB (uses same credential)."""
        return self.get_credential()


# Global instance
_credential_manager = AzureCredentialManager()

def get_credential_manager() -> AzureCredentialManager:
    """Get the shared credential manager instance."""
    return _credential_manager