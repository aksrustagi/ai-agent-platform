"""FastAPI application with REST API and WebSocket support."""

import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import Settings
from backend.coordinator.agent_coordinator import AgentCoordinator
from backend.dependencies import (
    get_agent_coordinator,
    get_cached_settings,
    get_go_services_client,
    get_mcp_client,
    get_mediamagic_client,
    get_memory_manager,
)
from backend.memory.memory_manager import MemoryManager
from backend.models.requests import (
    AgentType,
    ChatRequest,
    MemoryAddRequest,
    MemorySearchRequest,
)
from backend.models.responses import (
    AgentInfo,
    AgentListResponse,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
    MemoryResponse,
    MessageResponse,
    MessageRole,
    SuccessResponse,
)
from backend.services.websocket_service import connection_manager
from backend.utils.errors import AgentPlatformError
from backend.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    settings = get_cached_settings()
    configure_logging(settings.log_level, json_logs=settings.is_production)
    logger.info("🚀 AI Agent Platform starting up")
    
    yield
    
    # Shutdown
    logger.info("👋 AI Agent Platform shutting down")
    await connection_manager.close_all()


# Create FastAPI app
app = FastAPI(
    title="AI Agent Platform",
    description="Multi-agent AI system for real estate professionals",
    version="1.0.0",
    lifespan=lifespan
)


# Add CORS middleware
@app.on_event("startup")
async def configure_cors():
    """Configure CORS settings."""
    settings = get_cached_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Exception handler
@app.exception_handler(AgentPlatformError)
async def platform_error_handler(request, exc: AgentPlatformError):
    """Handle platform-specific errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            details=exc.details,
            timestamp=datetime.utcnow()
        ).model_dump()
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_cached_settings)):
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services={
            "database": True,  # TODO: Add real health checks
            "redis": True,
            "llm": True
        }
    )


# List available agents
@app.get("/agents", response_model=AgentListResponse)
async def list_agents(coordinator: AgentCoordinator = Depends(get_agent_coordinator)):
    """List all available agents."""
    agents = coordinator.list_agents()
    
    agent_info_list = [
        AgentInfo(
            agent_type=AgentType(agent.agent_id),
            name=agent.agent_name,
            description=agent.agent_description,
            llm_provider=agent.llm_provider.value,
            capabilities=agent.capabilities,
            available_tools=[tool["name"] for tool in agent.available_tools]
        )
        for agent in agents.values()
    ]
    
    return AgentListResponse(
        agents=agent_info_list,
        total=len(agent_info_list)
    )


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Process a chat message and return agent response."""
    start_time = time.time()
    
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:12]}"
        
        # Route message to appropriate agent
        response = await coordinator.route_message(
            user_id=request.user_id,
            message=request.message,
            agent_type=request.agent_type.value if request.agent_type != AgentType.AUTO else None,
            conversation_id=conversation_id,
            include_memory=request.include_memory
        )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Build response
        return ChatResponse(
            conversation_id=conversation_id,
            agent_type=AgentType(response["agent_id"]),
            agent_name=response["agent_name"],
            message=MessageResponse(
                role=MessageRole.ASSISTANT,
                content=response["content"],
                timestamp=datetime.utcnow(),
                metadata={"provider": response.get("provider"), "model": response.get("model")}
            ),
            suggested_actions=None,  # TODO: Extract from response
            tool_calls=response.get("tool_calls"),
            processing_time_ms=processing_time_ms,
            tokens_used=response.get("usage")
        )
    
    except Exception as e:
        logger.error("Chat processing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Memory endpoints
@app.post("/memory/add", response_model=SuccessResponse)
async def add_memory(
    request: MemoryAddRequest,
    memory_manager: MemoryManager = Depends(get_memory_manager)
):
    """Add a memory."""
    try:
        memory = await memory_manager.add_memory(
            user_id=request.user_id,
            agent_id=request.agent_id,
            content=request.content,
            metadata=request.metadata,
            category=request.category
        )
        
        return SuccessResponse(
            success=True,
            message="Memory added successfully",
            data={"memory_id": memory.id}
        )
    
    except Exception as e:
        logger.error("Failed to add memory", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/memory/search", response_model=MemoryResponse)
async def search_memories(
    request: MemorySearchRequest,
    memory_manager: MemoryManager = Depends(get_memory_manager)
):
    """Search memories."""
    try:
        memories = await memory_manager.search_memories(
            user_id=request.user_id,
            query=request.query,
            agent_id=request.agent_id,
            category=request.category,
            limit=request.limit
        )
        
        return MemoryResponse(
            memories=memories,
            total=len(memories)
        )
    
    except Exception as e:
        logger.error("Failed to search memories", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# MCP Server Management Endpoints
@app.get("/mcp/servers")
async def list_mcp_servers(
    mcp_client = Depends(get_mcp_client)
):
    """List all configured MCP servers."""
    try:
        servers = mcp_client.list_servers()
        return {
            "success": True,
            "servers": servers,
            "total": len(servers)
        }
    except Exception as e:
        logger.error("Failed to list MCP servers", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/mcp/tools/{server}")
async def list_mcp_tools(
    server: str,
    mcp_client = Depends(get_mcp_client)
):
    """List available tools from an MCP server."""
    try:
        tools = await mcp_client.list_remote_tools(server)
        return {
            "success": True,
            "server": server,
            "tools": tools,
            "total": len(tools)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to list tools from {server}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/execute")
async def execute_mcp_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    server: str = "default",
    mcp_client = Depends(get_mcp_client)
):
    """Execute a tool via MCP."""
    try:
        result = await mcp_client.execute_tool(
            tool_name=tool_name,
            parameters=parameters,
            server=server
        )
        return {
            "success": True,
            "tool": tool_name,
            "server": server,
            "result": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to execute tool {tool_name}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/mcp/health/{server}")
async def check_mcp_server_health(
    server: str,
    mcp_client = Depends(get_mcp_client)
):
    """Check health of an MCP server."""
    try:
        health = await mcp_client.health_check(server)
        return health
    except Exception as e:
        logger.error(f"Health check failed for {server}", error=str(e))
        return {
            "healthy": False,
            "error": str(e),
            "server": server
        }


# MediaMagic API Endpoints
@app.post("/mediamagic/process-image")
async def process_image(
    image_url: str,
    operations: list[str],
    output_format: str = "jpg",
    quality: int = 90,
    mediamagic_client = Depends(get_mediamagic_client)
):
    """Process an image using MediaMagic API."""
    if not mediamagic_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MediaMagic API is not configured"
        )
    
    try:
        result = await mediamagic_client.process_image(
            image_url=image_url,
            operations=operations,
            output_format=output_format,
            quality=quality
        )
        return result
    except Exception as e:
        logger.error("Failed to process image", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mediamagic/create-video")
async def create_video(
    images: list[str],
    duration_per_image: float = 3.0,
    transitions: list[str] | None = None,
    audio_url: str | None = None,
    output_format: str = "mp4",
    mediamagic_client = Depends(get_mediamagic_client)
):
    """Create a video from images using MediaMagic API."""
    if not mediamagic_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MediaMagic API is not configured"
        )
    
    try:
        result = await mediamagic_client.create_video(
            images=images,
            duration_per_image=duration_per_image,
            transitions=transitions,
            audio_url=audio_url,
            output_format=output_format
        )
        return result
    except Exception as e:
        logger.error("Failed to create video", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Go Services Endpoints
@app.get("/go-services/list")
async def list_go_services(
    go_services_client = Depends(get_go_services_client)
):
    """List all available Go services."""
    if not go_services_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Go Services are not configured"
        )
    
    try:
        services = await go_services_client.list_services()
        return {
            "success": True,
            "services": services,
            "total": len(services)
        }
    except Exception as e:
        logger.error("Failed to list Go services", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/go-services/call")
async def call_go_service(
    service_name: str,
    method: str,
    payload: Dict[str, Any],
    go_services_client = Depends(get_go_services_client)
):
    """Call a Go microservice."""
    if not go_services_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Go Services are not configured"
        )
    
    try:
        result = await go_services_client.call_service(
            service_name=service_name,
            method=method,
            payload=payload
        )
        return result
    except Exception as e:
        logger.error(f"Failed to call service {service_name}.{method}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/go-services/health")
async def check_go_services_health(
    go_services_client = Depends(get_go_services_client)
):
    """Check health of Go services."""
    if not go_services_client:
        return {
            "healthy": False,
            "error": "Go Services are not configured"
        }
    
    try:
        health = await go_services_client.health_check()
        return health
    except Exception as e:
        logger.error("Go Services health check failed", error=str(e))
        return {
            "healthy": False,
            "error": str(e)
        }


# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """WebSocket endpoint for real-time communication."""
    connection_id = f"conn_{uuid.uuid4().hex[:12]}"
    
    try:
        # Accept connection
        await connection_manager.connect(websocket, connection_id, user_id)
        
        # Message loop
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "ping":
                await connection_manager.handle_ping(connection_id)
            
            elif message_type == "chat":
                # Process chat message
                user_message = data.get("message")
                agent_type = data.get("agent_type", "auto")
                
                if not user_message:
                    await connection_manager.send_message(connection_id, {
                        "type": "error",
                        "error": "Message is required"
                    })
                    continue
                
                # Send typing indicator
                await connection_manager.send_message(connection_id, {
                    "type": "typing",
                    "agent": "processing"
                })
                
                try:
                    # Route message
                    response = await coordinator.route_message(
                        user_id=user_id,
                        message=user_message,
                        agent_type=agent_type if agent_type != "auto" else None,
                        include_memory=True
                    )
                    
                    # Send response
                    await connection_manager.send_message(connection_id, {
                        "type": "chat_response",
                        "agent_id": response["agent_id"],
                        "agent_name": response["agent_name"],
                        "content": response["content"],
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                except Exception as e:
                    logger.error(f"Chat processing failed: {e}")
                    await connection_manager.send_message(connection_id, {
                        "type": "error",
                        "error": str(e)
                    })
            
            else:
                await connection_manager.send_message(connection_id, {
                    "type": "error",
                    "error": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
        connection_manager.disconnect(connection_id, user_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connection_manager.disconnect(connection_id, user_id)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Agent Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_cached_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
