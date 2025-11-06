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
