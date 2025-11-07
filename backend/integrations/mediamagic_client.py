"""MediaMagic API client for media processing and management."""

from typing import Any, Dict, List, Optional

import httpx

from backend.utils.errors import IntegrationError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MediaMagicClient:
    """
    Client for MediaMagic API integration.
    Handles media processing, editing, and management operations.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize MediaMagic client.
        
        Args:
            base_url: MediaMagic API base URL
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self._http_client: Optional[httpx.AsyncClient] = None
        logger.info(f"MediaMagic client initialized: {self.base_url}")
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def process_image(
        self,
        image_url: str,
        operations: List[str],
        output_format: str = "jpg",
        quality: int = 90
    ) -> Dict[str, Any]:
        """
        Process an image with various operations.
        
        Args:
            image_url: URL of the image to process
            operations: List of operations (e.g., ["resize:800x600", "blur:5", "sharpen"])
            output_format: Output format (jpg, png, webp)
            quality: Output quality (1-100)
        
        Returns:
            Processing result with processed image URL
        """
        try:
            client = await self._get_http_client()
            
            payload = {
                "image_url": image_url,
                "operations": operations,
                "output_format": output_format,
                "quality": quality
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/image/process",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Image processed successfully: {image_url}")
            
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Image processing failed: {e}")
            raise IntegrationError(
                message="Failed to process image",
                details={"error": str(e), "image_url": image_url}
            )
    
    async def create_video(
        self,
        images: List[str],
        duration_per_image: float = 3.0,
        transitions: Optional[List[str]] = None,
        audio_url: Optional[str] = None,
        output_format: str = "mp4"
    ) -> Dict[str, Any]:
        """
        Create a video from images.
        
        Args:
            images: List of image URLs
            duration_per_image: Duration each image is shown (seconds)
            transitions: Optional list of transition effects
            audio_url: Optional background audio URL
            output_format: Output format (mp4, webm)
        
        Returns:
            Video creation result with video URL
        """
        try:
            client = await self._get_http_client()
            
            payload = {
                "images": images,
                "duration_per_image": duration_per_image,
                "transitions": transitions or ["fade"],
                "output_format": output_format
            }
            
            if audio_url:
                payload["audio_url"] = audio_url
            
            response = await client.post(
                f"{self.base_url}/api/v1/video/create",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Video created successfully from {len(images)} images")
            
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Video creation failed: {e}")
            raise IntegrationError(
                message="Failed to create video",
                details={"error": str(e), "image_count": len(images)}
            )
    
    async def edit_media(
        self,
        media_url: str,
        media_type: str,
        edits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Edit media (image or video) with specified edits.
        
        Args:
            media_url: URL of media to edit
            media_type: Type of media ("image" or "video")
            edits: Dictionary of edit operations and parameters
        
        Returns:
            Edit result with edited media URL
        """
        try:
            client = await self._get_http_client()
            
            payload = {
                "media_url": media_url,
                "media_type": media_type,
                "edits": edits
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/media/edit",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Media edited successfully: {media_url}")
            
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Media editing failed: {e}")
            raise IntegrationError(
                message="Failed to edit media",
                details={"error": str(e), "media_url": media_url}
            )
    
    async def generate_thumbnail(
        self,
        video_url: str,
        timestamp: float = 0.0,
        width: int = 1280,
        height: int = 720
    ) -> Dict[str, Any]:
        """
        Generate a thumbnail from a video.
        
        Args:
            video_url: URL of the video
            timestamp: Timestamp in seconds to capture
            width: Thumbnail width
            height: Thumbnail height
        
        Returns:
            Thumbnail result with thumbnail URL
        """
        try:
            client = await self._get_http_client()
            
            payload = {
                "video_url": video_url,
                "timestamp": timestamp,
                "width": width,
                "height": height
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/video/thumbnail",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Thumbnail generated: {video_url}")
            
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Thumbnail generation failed: {e}")
            raise IntegrationError(
                message="Failed to generate thumbnail",
                details={"error": str(e), "video_url": video_url}
            )
    
    async def upload_media(
        self,
        file_path: str,
        media_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload media file.
        
        Args:
            file_path: Path to the file to upload
            media_type: Type of media ("image", "video", "audio")
            metadata: Optional metadata
        
        Returns:
            Upload result with media URL
        """
        try:
            client = await self._get_http_client()
            
            with open(file_path, "rb") as f:
                files = {"file": f}
                data = {
                    "media_type": media_type,
                    "metadata": metadata or {}
                }
                
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.post(
                    f"{self.base_url}/api/v1/media/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
            
            result = response.json()
            logger.info(f"Media uploaded successfully: {file_path}")
            
            return result
        
        except Exception as e:
            logger.error(f"Media upload failed: {e}")
            raise IntegrationError(
                message="Failed to upload media",
                details={"error": str(e), "file_path": file_path}
            )
    
    async def get_media_info(self, media_url: str) -> Dict[str, Any]:
        """
        Get information about a media file.
        
        Args:
            media_url: URL of the media
        
        Returns:
            Media information (dimensions, duration, format, etc.)
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(
                f"{self.base_url}/api/v1/media/info",
                params={"media_url": media_url},
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Retrieved media info: {media_url}")
            
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to get media info: {e}")
            raise IntegrationError(
                message="Failed to get media information",
                details={"error": str(e), "media_url": media_url}
            )
