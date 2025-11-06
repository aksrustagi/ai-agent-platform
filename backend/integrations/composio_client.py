"""Composio client for tool integrations."""

from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import Settings
from backend.utils.errors import IntegrationError
from backend.utils.logger import get_logger
from backend.utils.security import mask_sensitive_data

logger = get_logger(__name__)


class ComposioClient:
    """
    Client for Composio API - provides access to 200+ app integrations.
    """
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize Composio client.
        
        Args:
            settings: Application settings
        """
        self.api_key = settings.composio_api_key
        self.base_url = "https://api.composio.dev/v1"
        self.timeout = settings.retry_timeout
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )
        
        logger.info(
            "Composio client initialized",
            api_key=mask_sensitive_data(self.api_key)
        )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Composio client closed")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a Composio action.
        
        Args:
            action: Action name (e.g., "gmail_send_email", "slack_send_message")
            params: Action parameters
            entity_id: Optional entity ID for user-specific actions
        
        Returns:
            Action execution result
        
        Raises:
            IntegrationError: If action execution fails
        """
        try:
            payload = {
                "action": action,
                "params": params
            }
            
            if entity_id:
                payload["entity_id"] = entity_id
            
            logger.debug(
                "Executing Composio action",
                action=action,
                entity_id=entity_id
            )
            
            response = await self.client.post("/actions/execute", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(
                "Composio action executed successfully",
                action=action,
                success=result.get("success", False)
            )
            
            return result
        
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to execute Composio action",
                action=action,
                status_code=e.response.status_code,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to execute action {action}: {e.response.status_code}",
                integration="composio",
                details={"action": action, "status_code": e.response.status_code}
            )
        except Exception as e:
            logger.error("Unexpected error executing Composio action", error=str(e))
            raise IntegrationError(
                f"Unexpected error executing action: {str(e)}",
                integration="composio"
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def list_actions(self, app: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available Composio actions.
        
        Args:
            app: Optional app filter (e.g., "gmail", "slack")
        
        Returns:
            List of available actions
        
        Raises:
            IntegrationError: If listing fails
        """
        try:
            params = {}
            if app:
                params["app"] = app
            
            logger.debug("Listing Composio actions", app=app)
            
            response = await self.client.get("/actions", params=params)
            response.raise_for_status()
            
            result = response.json()
            actions = result.get("actions", [])
            
            logger.info("Composio actions listed", count=len(actions))
            
            return actions
        
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to list Composio actions",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to list actions: {e.response.status_code}",
                integration="composio"
            )
        except Exception as e:
            logger.error("Unexpected error listing Composio actions", error=str(e))
            raise IntegrationError(
                f"Unexpected error listing actions: {str(e)}",
                integration="composio"
            )
    
    # Convenience methods for common actions
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email via Gmail or other email provider.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            from_email: Sender email (if applicable)
            entity_id: Entity ID for user-specific action
        
        Returns:
            Send result
        """
        params = {
            "to": to,
            "subject": subject,
            "body": body
        }
        
        if from_email:
            params["from"] = from_email
        
        return await self.execute_action("gmail_send_email", params, entity_id)
    
    async def send_sms(
        self,
        to: str,
        message: str,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS via Twilio or other SMS provider.
        
        Args:
            to: Recipient phone number
            message: SMS message
            entity_id: Entity ID for user-specific action
        
        Returns:
            Send result
        """
        params = {
            "to": to,
            "message": message
        }
        
        return await self.execute_action("twilio_send_sms", params, entity_id)
    
    async def create_calendar_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Google Calendar event.
        
        Args:
            title: Event title
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            description: Event description
            attendees: List of attendee emails
            entity_id: Entity ID for user-specific action
        
        Returns:
            Created event
        """
        params = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time
        }
        
        if description:
            params["description"] = description
        if attendees:
            params["attendees"] = attendees
        
        return await self.execute_action("google_calendar_create_event", params, entity_id)
    
    async def post_to_social_media(
        self,
        platform: str,
        content: str,
        media_urls: Optional[List[str]] = None,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post content to social media.
        
        Args:
            platform: Platform name (facebook, twitter, instagram, linkedin)
            content: Post content
            media_urls: Optional media URLs
            entity_id: Entity ID for user-specific action
        
        Returns:
            Post result
        """
        params = {
            "content": content
        }
        
        if media_urls:
            params["media_urls"] = media_urls
        
        action_map = {
            "facebook": "facebook_create_post",
            "twitter": "twitter_create_tweet",
            "instagram": "instagram_create_post",
            "linkedin": "linkedin_create_post"
        }
        
        action = action_map.get(platform.lower())
        if not action:
            raise IntegrationError(
                f"Unsupported social media platform: {platform}",
                integration="composio"
            )
        
        return await self.execute_action(action, params, entity_id)
    
    async def create_docusign_envelope(
        self,
        document_url: str,
        recipients: List[Dict[str, str]],
        email_subject: str,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a DocuSign envelope for signing.
        
        Args:
            document_url: URL of the document to sign
            recipients: List of recipients with email and name
            email_subject: Email subject
            entity_id: Entity ID for user-specific action
        
        Returns:
            Created envelope
        """
        params = {
            "document_url": document_url,
            "recipients": recipients,
            "email_subject": email_subject
        }
        
        return await self.execute_action("docusign_create_envelope", params, entity_id)
