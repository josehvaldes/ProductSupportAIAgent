
from typing import Any

from shopassist_api.application.agents.base import EscalationResponse, Metadata
from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)

class EscalationAgent:
    """No tools needed - just returns escalation message"""
    
    async def ainvoke(self, state: dict) -> EscalationResponse:
        """Escalate the issue to human support"""
        
        #execute escalation logic here (e.g., create support ticket, notify human agent, etc.)

        logger.info("EscalationAgent: Escalating issue to human support.")
        return EscalationResponse(
            agent_name="escalation",
            message="Your issue has been escalated to a human agent. A support ticket has been created with ticket ID: TICKET12345. Our support team will contact you shortly at your registered email address.",
            ticket_id="TICKET12345",
            contact_info="shopassist@test.com",
            confidence=0.95,
            metadata= Metadata(input_token=0, output_token=0, total_token=0)
            )

