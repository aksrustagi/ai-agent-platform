# MCP Integration Guide

## Overview

The AI Agent Platform now supports full **Model Context Protocol (MCP)** integration, allowing AI agents to communicate with and control external services including:

- **MediaMagic API** - Media processing and management
- **Go Services** - Go-based microservices
- **Custom MCP Servers** - Any MCP-compliant service

## Architecture

The MCP integration follows a multi-layer architecture:

```
┌─────────────────────────────────────────────────────┐
│             AI Agents (7 Agents)                    │
├─────────────────────────────────────────────────────┤
│          Agent Coordinator                          │
├─────────────────────────────────────────────────────┤
│             MCP Client Layer                        │
│  (Unified interface for all MCP servers)            │
├─────────────────────────────────────────────────────┤
│         MCP Server Connections                      │
│  ┌─────────────┬──────────────┬──────────────┐     │
│  │   Default   │  MediaMagic  │ Go Services  │     │
│  │ MCP Server  │     API      │              │     │
│  └─────────────┴──────────────┴──────────────┘     │
└─────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8003
MCP_ENABLE_REMOTE=True

# MediaMagic API Configuration
MEDIAMAGIC_API_URL=http://localhost:8001
MEDIAMAGIC_API_KEY=your-mediamagic-api-key

# Go Services Configuration
GO_SERVICES_URL=http://localhost:8002
GO_SERVICES_API_KEY=your-go-services-api-key
```

## MCP Client Usage

### Initialize MCP Client

```python
from backend.dependencies import get_mcp_client

# Get MCP client instance
mcp_client = get_mcp_client()

# List all configured servers
servers = mcp_client.list_servers()
print(f"Available servers: {servers}")
```

### Register Local Tools

```python
# Register a local tool
def my_custom_tool(param1: str, param2: int) -> dict:
    return {"result": f"Processed {param1} with {param2}"}

mcp_client.register_tool(
    name="custom_tool",
    description="My custom processing tool",
    parameters={
        "param1": {"type": "string", "description": "First parameter"},
        "param2": {"type": "integer", "description": "Second parameter"}
    },
    function=my_custom_tool
)

# Execute local tool
result = await mcp_client.execute_tool(
    tool_name="custom_tool",
    parameters={"param1": "test", "param2": 42}
)
```

### Add Remote MCP Server

```python
# Add a new MCP server dynamically
mcp_client.add_server(
    name="my-custom-server",
    base_url="https://my-mcp-server.com",
    api_key="your-api-key",
    timeout=30,
    description="My custom MCP server"
)
```

### Execute Remote Tools

```python
# List tools from a remote server
tools = await mcp_client.list_remote_tools("mediamagic")

# Execute a remote tool
result = await mcp_client.execute_tool(
    tool_name="process_image",
    parameters={
        "image_url": "https://example.com/image.jpg",
        "operations": ["resize:800x600", "sharpen"]
    },
    server="mediamagic"
)
```

### Health Checks

```python
# Check health of an MCP server
health = await mcp_client.health_check("go-services")
print(f"Server healthy: {health['healthy']}")
```

## MediaMagic API Integration

### Process Images

```python
from backend.dependencies import get_mediamagic_client

mediamagic = get_mediamagic_client()

# Process an image
result = await mediamagic.process_image(
    image_url="https://example.com/property.jpg",
    operations=[
        "resize:1200x800",
        "enhance",
        "sharpen",
        "watermark:logo.png"
    ],
    output_format="jpg",
    quality=90
)

print(f"Processed image URL: {result['url']}")
```

### Create Videos

```python
# Create a video from property images
result = await mediamagic.create_video(
    images=[
        "https://example.com/property1.jpg",
        "https://example.com/property2.jpg",
        "https://example.com/property3.jpg",
        "https://example.com/property4.jpg"
    ],
    duration_per_image=3.0,
    transitions=["fade", "slide", "zoom"],
    audio_url="https://example.com/background-music.mp3",
    output_format="mp4"
)

print(f"Video URL: {result['video_url']}")
```

### Edit Media

```python
# Edit existing media
result = await mediamagic.edit_media(
    media_url="https://example.com/property-video.mp4",
    media_type="video",
    edits={
        "trim": {"start": 0, "end": 30},
        "add_text": {
            "text": "Beautiful 3BR Home",
            "position": "bottom",
            "font_size": 24
        },
        "add_logo": {
            "logo_url": "https://example.com/logo.png",
            "position": "top-right"
        }
    }
)
```

### Generate Thumbnails

```python
# Generate thumbnail from video
result = await mediamagic.generate_thumbnail(
    video_url="https://example.com/property-tour.mp4",
    timestamp=5.0,  # 5 seconds in
    width=1280,
    height=720
)

print(f"Thumbnail URL: {result['thumbnail_url']}")
```

### Upload Media

```python
# Upload a media file
result = await mediamagic.upload_media(
    file_path="/path/to/property-photo.jpg",
    media_type="image",
    metadata={
        "property_id": "123",
        "title": "Front View",
        "tags": ["exterior", "front", "curb-appeal"]
    }
)

print(f"Uploaded to: {result['url']}")
```

## Go Services Integration

### Call Microservices

```python
from backend.dependencies import get_go_services_client

go_services = get_go_services_client()

# Call a specific service method
result = await go_services.call_service(
    service_name="property",
    method="get_details",
    payload={"property_id": "123"}
)
```

### Data Service

```python
# Query data service
result = await go_services.data_service_query(
    query="SELECT * FROM properties WHERE price < $1",
    parameters={"$1": 500000}
)

properties = result["data"]
```

### Cache Service

```python
# Get from cache
cached = await go_services.cache_service_get(key="user:123:preferences")

# Set in cache with TTL
await go_services.cache_service_set(
    key="user:123:preferences",
    value={"theme": "dark", "notifications": True},
    ttl=3600  # 1 hour
)
```

### Storage Service

```python
# Upload file to storage
result = await go_services.storage_service_upload(
    file_name="contract.pdf",
    content=file_bytes,
    content_type="application/pdf",
    metadata={"deal_id": "789", "type": "contract"}
)

file_url = result["url"]
```

### Notification Service

```python
# Send notification
result = await go_services.notification_service_send(
    recipient="user@example.com",
    channel="email",
    message="Your offer has been accepted!",
    metadata={"property_id": "123", "offer_id": "456"}
)
```

### Analytics Service

```python
# Track event
result = await go_services.analytics_service_track_event(
    event_name="property_viewed",
    user_id="user_123",
    properties={
        "property_id": "789",
        "source": "website",
        "time_spent": 45
    }
)
```

### Queue Service

```python
# Enqueue a task
result = await go_services.queue_service_enqueue(
    queue_name="email_queue",
    message={
        "to": "client@example.com",
        "template": "property_update",
        "data": {"property_id": "123"}
    },
    priority=5
)
```

## REST API Endpoints

### MCP Server Endpoints

#### List MCP Servers

```bash
GET /mcp/servers

Response:
{
  "success": true,
  "servers": [
    {
      "name": "default",
      "base_url": "http://localhost:8003",
      "description": "Default MCP server",
      "has_api_key": false
    },
    {
      "name": "mediamagic",
      "base_url": "http://localhost:8001",
      "description": "MediaMagic API",
      "has_api_key": true
    },
    {
      "name": "go-services",
      "base_url": "http://localhost:8002",
      "description": "Go microservices",
      "has_api_key": true
    }
  ],
  "total": 3
}
```

#### List Tools from Server

```bash
GET /mcp/tools/{server}

Example: GET /mcp/tools/mediamagic

Response:
{
  "success": true,
  "server": "mediamagic",
  "tools": [
    {
      "name": "process_image",
      "description": "Process images with various operations",
      "parameters": {...}
    },
    {
      "name": "create_video",
      "description": "Create videos from images",
      "parameters": {...}
    }
  ],
  "total": 2
}
```

#### Execute MCP Tool

```bash
POST /mcp/execute

Body:
{
  "tool_name": "process_image",
  "parameters": {
    "image_url": "https://example.com/image.jpg",
    "operations": ["resize:800x600", "sharpen"]
  },
  "server": "mediamagic"
}

Response:
{
  "success": true,
  "tool": "process_image",
  "server": "mediamagic",
  "result": {
    "url": "https://cdn.example.com/processed-image.jpg",
    "width": 800,
    "height": 600
  }
}
```

#### Check Server Health

```bash
GET /mcp/health/{server}

Example: GET /mcp/health/go-services

Response:
{
  "healthy": true,
  "status_code": 200,
  "server": "go-services"
}
```

### MediaMagic Endpoints

#### Process Image

```bash
POST /mediamagic/process-image

Query Parameters:
- image_url: string (required)
- operations: array of strings (required)
- output_format: string (default: "jpg")
- quality: integer (default: 90)

Response:
{
  "url": "https://cdn.example.com/processed.jpg",
  "width": 800,
  "height": 600,
  "format": "jpg",
  "size_bytes": 245678
}
```

#### Create Video

```bash
POST /mediamagic/create-video

Body:
{
  "images": [
    "https://example.com/img1.jpg",
    "https://example.com/img2.jpg"
  ],
  "duration_per_image": 3.0,
  "transitions": ["fade", "slide"],
  "audio_url": "https://example.com/music.mp3",
  "output_format": "mp4"
}

Response:
{
  "video_url": "https://cdn.example.com/video.mp4",
  "duration": 6.0,
  "resolution": "1920x1080",
  "size_bytes": 1234567
}
```

### Go Services Endpoints

#### List Services

```bash
GET /go-services/list

Response:
{
  "success": true,
  "services": [
    {
      "name": "data",
      "methods": ["query", "insert", "update", "delete"]
    },
    {
      "name": "cache",
      "methods": ["get", "set", "delete", "flush"]
    },
    {
      "name": "storage",
      "methods": ["upload", "download", "delete"]
    }
  ],
  "total": 3
}
```

#### Call Service

```bash
POST /go-services/call

Body:
{
  "service_name": "cache",
  "method": "get",
  "payload": {
    "key": "user:123:preferences"
  }
}

Response:
{
  "success": true,
  "data": {
    "theme": "dark",
    "notifications": true
  }
}
```

#### Health Check

```bash
GET /go-services/health

Response:
{
  "healthy": true,
  "services": {
    "data": "healthy",
    "cache": "healthy",
    "storage": "healthy",
    "notification": "healthy"
  }
}
```

## Agent Integration Examples

### Content Agent Using MediaMagic

```python
class ContentAgent(BaseAgent):
    async def create_social_media_post_with_video(
        self,
        property_id: str
    ) -> Dict[str, Any]:
        """Create a social media post with property video."""
        
        # Get property images
        images = await self.get_property_images(property_id)
        
        # Create video using MediaMagic via MCP
        video_result = await self.mcp_client.execute_tool(
            tool_name="create_video",
            parameters={
                "images": images,
                "duration_per_image": 2.5,
                "transitions": ["fade"],
                "audio_url": "https://cdn.example.com/upbeat-music.mp3"
            },
            server="mediamagic"
        )
        
        # Generate post caption
        caption = await self.generate_caption(property_id)
        
        # Post to social media via Composio
        result = await self.composio_client.execute_action(
            app="instagram",
            action="create_post",
            params={
                "video_url": video_result["video_url"],
                "caption": caption
            }
        )
        
        return {
            "video_url": video_result["video_url"],
            "post_url": result["post_url"]
        }
```

### Marketing Agent Using Go Services

```python
class MarketingAgent(BaseAgent):
    async def track_campaign_performance(
        self,
        campaign_id: str
    ) -> Dict[str, Any]:
        """Track and analyze campaign performance."""
        
        # Get campaign data from Go Services
        campaign_data = await self.mcp_client.execute_tool(
            tool_name="data_query",
            parameters={
                "query": "SELECT * FROM campaigns WHERE id = $1",
                "parameters": {"$1": campaign_id}
            },
            server="go-services"
        )
        
        # Track analytics event
        await self.mcp_client.execute_tool(
            tool_name="analytics_track",
            parameters={
                "event_name": "campaign_viewed",
                "user_id": self.user_id,
                "properties": {
                    "campaign_id": campaign_id,
                    "campaign_type": campaign_data["type"]
                }
            },
            server="go-services"
        )
        
        # Cache results
        await self.mcp_client.execute_tool(
            tool_name="cache_set",
            parameters={
                "key": f"campaign:{campaign_id}:performance",
                "value": campaign_data,
                "ttl": 300
            },
            server="go-services"
        )
        
        return campaign_data
```

## Docker Setup for MCP Services

### docker-compose.yml Addition

Add these services to your `docker-compose.yml`:

```yaml
services:
  # ... existing services ...

  mediamagic-api:
    image: mediamagic-api:latest
    container_name: mediamagic-api
    ports:
      - "8001:8000"
    environment:
      - API_KEY=${MEDIAMAGIC_API_KEY}
      - STORAGE_URL=http://storage:8080
    networks:
      - ai-agent-network

  go-services:
    image: go-services:latest
    container_name: go-services
    ports:
      - "8002:8000"
    environment:
      - API_KEY=${GO_SERVICES_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
    networks:
      - ai-agent-network

  mcp-server:
    image: mcp-server:latest
    container_name: mcp-server
    ports:
      - "8003:8000"
    environment:
      - MEDIAMAGIC_URL=http://mediamagic-api:8000
      - GO_SERVICES_URL=http://go-services:8000
    networks:
      - ai-agent-network

networks:
  ai-agent-network:
    driver: bridge
```

## Testing MCP Integration

### Test MCP Client

```python
import pytest
from backend.integrations.mcp_client import MCPClient

@pytest.mark.asyncio
async def test_mcp_client():
    # Initialize client
    mcp_client = MCPClient()
    
    # Add test server
    mcp_client.add_server(
        name="test",
        base_url="http://localhost:8003",
        description="Test server"
    )
    
    # List servers
    servers = mcp_client.list_servers()
    assert len(servers) == 1
    assert servers[0]["name"] == "test"
    
    # Register local tool
    def test_tool(x: int, y: int) -> int:
        return x + y
    
    mcp_client.register_tool(
        name="add",
        description="Add two numbers",
        parameters={},
        function=test_tool
    )
    
    # Execute local tool
    result = await mcp_client.execute_tool(
        tool_name="add",
        parameters={"x": 5, "y": 3}
    )
    assert result == 8
```

### Test MediaMagic Client

```python
@pytest.mark.asyncio
async def test_mediamagic_process_image():
    client = MediaMagicClient(
        base_url="http://localhost:8001",
        api_key="test-key"
    )
    
    result = await client.process_image(
        image_url="https://example.com/test.jpg",
        operations=["resize:800x600"],
        output_format="jpg",
        quality=90
    )
    
    assert "url" in result
    assert result["width"] == 800
    assert result["height"] == 600
```

### Test Go Services Client

```python
@pytest.mark.asyncio
async def test_go_services_cache():
    client = GoServicesClient(
        base_url="http://localhost:8002",
        api_key="test-key"
    )
    
    # Set value
    await client.cache_service_set(
        key="test_key",
        value={"data": "test"},
        ttl=60
    )
    
    # Get value
    result = await client.cache_service_get(key="test_key")
    assert result["data"] == "test"
```

## Security Considerations

1. **API Key Management**
   - Store API keys in environment variables
   - Never commit keys to version control
   - Rotate keys regularly

2. **Authentication**
   - Use Bearer token authentication
   - Implement request signing for sensitive operations
   - Validate all incoming requests

3. **Rate Limiting**
   - Implement rate limiting on MCP endpoints
   - Monitor usage patterns
   - Set appropriate timeouts

4. **Input Validation**
   - Validate all parameters before sending to MCP servers
   - Sanitize file uploads
   - Check URL formats and domains

5. **Network Security**
   - Use HTTPS for production
   - Implement SSL/TLS for all communications
   - Restrict access with firewalls

## Troubleshooting

### MCP Server Not Responding

```python
# Check health
health = await mcp_client.health_check("mediamagic")
if not health["healthy"]:
    print(f"Server unhealthy: {health['error']}")
```

### Tool Execution Timeout

```python
# Increase timeout for specific server
mcp_client.add_server(
    name="slow-server",
    base_url="http://localhost:8004",
    timeout=60  # 60 seconds
)
```

### Authentication Errors

```bash
# Verify API keys
curl -H "Authorization: Bearer $MEDIAMAGIC_API_KEY" \
  http://localhost:8001/health
```

## Best Practices

1. **Error Handling**
   - Always wrap MCP calls in try-except blocks
   - Log errors with context
   - Implement retry logic for transient failures

2. **Performance**
   - Cache frequently accessed data
   - Use connection pooling
   - Implement request batching where possible

3. **Monitoring**
   - Track MCP server health
   - Monitor response times
   - Set up alerts for failures

4. **Testing**
   - Mock MCP responses in unit tests
   - Test with real servers in integration tests
   - Implement contract testing

## Additional Resources

- [MCP Specification](https://github.com/modelcontextprotocol/specification)
- [MediaMagic API Documentation](#) (link when available)
- [Go Services Documentation](#) (link when available)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for detailed error messages
