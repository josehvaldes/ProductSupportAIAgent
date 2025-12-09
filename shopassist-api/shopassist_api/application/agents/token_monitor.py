
from shopassist_api.application.agents.base import Metadata
from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)

def token_monitor_dec(func):
    """Decorator to monitor token usage of agent methods."""
    async def wrapper(*args, **kwargs):
        
        print(" * Token monitoring active for function:", func.__name__)
        result = await func(*args, **kwargs)
        try:
            metadata:Metadata = result.metadata or {}
            #Send token usage info to monitoring system
            print(f" * Collected agent info: {result.agent_name}, Model: {result.model}, metadata: [{metadata}]")
            return result          
        except Exception as e:
            logger.error(f"Error in token monitoring decorator for function {func.__name__}: {e}")
            return result
        finally:
            logger.info("Token monitoring ended for function: {}".format(func.__name__))

    return wrapper