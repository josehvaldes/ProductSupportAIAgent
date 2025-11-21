from datetime import datetime, timezone
import re
from typing import List
import uuid
from langsmith import traceable
from shopassist_api.application.interfaces.service_interfaces import CacheServiceInterface, RepositoryServiceInterface
from shopassist_api.domain.models.session_context import SessionContext
from shopassist_api.domain.models.message import Message
from shopassist_api.domain.models.user_preferences import UserPreferences

class SessionManager:
    def __init__(
        self, 
        repository_service: RepositoryServiceInterface,
        cache_service: CacheServiceInterface = None
    ):
        """
        Manages conversation context and session state
        
        Args:
            repository: Cosmos DB client for persistence
            cache_client: Optional Redis for hot session cache
        """
        self.repository = repository_service
        self.cache = cache_service
        self.cache_ttl = 1800  # 1 hour TTL for cached sessions
        
    async def create_session(self, user_id:str, metadata: dict = None) -> str:
        """Create new session, return session_id"""
        session_id = str(uuid.uuid4())
        session_context = SessionContext(
            id=session_id,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            messages=[],
            user_preferences=None,
            current_intent=None,
            metadata=metadata or {}
        )
        
        session_id = await self.repository.create_session(data=session_context)

        return session_id

    @traceable(name="session.get_session", tags=["session", "cache"], metadata={"version": "1.0"})
    async def get_session(self, session_id: str) -> SessionContext:
        """Load full session context"""
        if self.cache:
            cached = await self.cache.get(f"session:{session_id}")
            if cached:
                return SessionContext.model_validate_json(cached)
            
        session = await self.repository.get_session(session_id)
        if self.cache and session:
            await self.cache.set(
                key=session_id, 
                value=session.model_dump_json(), 
                ttl=self.cache_ttl
            )

        return session
    
    async def delete_session(self, user_id:str, session_id: str) -> None:
        """Delete session from repository and cache"""
        await self.repository.delete_session( user_id, session_id)
        if self.cache:
            await self.cache.delete(f"session:{session_id}")

    async def add_message(
        self, 
        user_id: str,
        session_id: str, 
        role: str, 
        content: str,
        metadata: dict = None
    ) -> None:
        """Append message to conversation history"""
        timestamp = datetime.now(timezone.utc)
        await self.repository.save_message(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            timestamp=timestamp,
            metadata=metadata
        )
        if self.cache:
            # Invalidate cache
            await self.cache.delete(f"session:{session_id}")
        
    async def get_conversation_history(
        self, 
        session_id: str, 
        max_turns: int = 5
    ) -> List[Message]:
        """Get last N turns for LLM context"""
        raw = await self.repository.get_conversation_history(session_id)
        messages = [ Message.model_validate(msg) for msg in raw ]
        return messages[-max_turns:]
        
    async def update_preferences(
        self, 
        session_id: str, 
        preferences: dict
    ) -> None:
        """Update user preferences based on conversation"""
        existing_preferences = await self.get_preferences(session_id)
        new_preferences = UserPreferences(**preferences)
        merged_preferences = await self._merge_preferences(existing_preferences, new_preferences)
        
        await self.repository.update_preferences(
            session_id=session_id,
            preferences=merged_preferences.model_dump()
        )
        
    async def get_preferences(
        self, 
        session_id: str
    ) -> UserPreferences:
        """Retrieve current user preferences"""
        preferences = await self.repository.get_preferences(session_id)
        if preferences:
            return preferences
        return None

    
    async def _extract_preferences_from_messages(
        self, 
        messages: List[Message]
    ) -> UserPreferences:
        """
        Parse messages to extract:
        - Price mentions ("under $1000", "between $500-$800")
        - Category mentions ("laptop", "headphones")
        - Brand mentions ("Apple", "Dell", "Sony")
        - Product IDs from AI responses
        """
        preferences = UserPreferences()
        
        for msg in messages:
            # Extract price range with regex
            if price_match := re.search(r'under \$(\d+)', msg.content):
                preferences.price_range = (0, float(price_match.group(1)))
            
            # TODO:
            # Extract categories (use NER or keyword matching)
            # Extract brands
            # Extract product IDs from metadata
            
        return preferences
    
    async def _merge_preferences(
        self, 
        existing: UserPreferences, 
        new: UserPreferences
    ) -> UserPreferences:
        """Merge new preferences with existing, prioritize recent"""
        merged = existing.model_copy()
        
        # Merge price range
        if new.price_range:
            merged.price_range = new.price_range
        
        # Merge preferred categories
        merged.preferred_categories = list(set(merged.preferred_categories + new.preferred_categories))
        
        # Merge preferred brands
        merged.preferred_brands = list(set(merged.preferred_brands + new.preferred_brands))
        
        # Merge mentioned products
        merged.mentioned_products = list(set(merged.mentioned_products + new.mentioned_products))
        
        return merged