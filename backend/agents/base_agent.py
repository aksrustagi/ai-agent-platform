"""Base agent class for all specialized agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.config import Settings
from backend.integrations.tool_registry import get_tool_registry
from backend.memory.memory_manager import MemoryManager
from backend.services.llm_service import LLMProvider, LLMService
from backend.utils.logger import get_logger, log_agent_action

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    """
    
    def __init__(
        self,
        settings: Settings,
        llm_service: LLMService,
        memory_manager: MemoryManager
    ) -> None:
        """
        Initialize base agent.
        
        Args:
            settings: Application settings
            llm_service: LLM service instance
            memory_manager: Memory manager instance
        """
        self.settings = settings
        self.llm_service = llm_service
        self.memory_manager = memory_manager
        
        logger.info(f"Initialized {self.agent_name}")
    
    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique agent identifier (e.g., 'growth', 'outreach')."""
        pass
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Human-readable agent name."""
        pass
    
    @property
    @abstractmethod
    def agent_description(self) -> str:
        """Description of agent's purpose and capabilities."""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt defining agent's behavior and personality."""
        pass
    
    @property
    @abstractmethod
    def llm_provider(self) -> LLMProvider:
        """LLM provider this agent uses."""
        pass
    
    @property
    def capabilities(self) -> List[str]:
        """List of agent capabilities."""
        return []
    
    @property
    def available_tools(self) -> List[Dict[str, Any]]:
        """List of tools available to this agent from the tool registry."""
        tool_registry = get_tool_registry()
        return tool_registry.get_tools_for_agent(self.agent_id)
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        include_memory: bool = True,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Process a user message with agentic loop for tool calling.
        
        Args:
            user_id: User identifier
            message: User message
            conversation_id: Optional conversation ID for context
            include_memory: Whether to include memory context
            max_iterations: Maximum tool calling iterations
        
        Returns:
            Agent response with content and metadata
        """
        log_agent_action(
            logger,
            self.agent_name,
            "process_message",
            user_id,
            message_preview=message[:50]
        )
        
        # Build messages list
        messages = []
        
        # Add memory context if requested
        if include_memory:
            memory_context = await self.memory_manager.get_context_for_agent(
                user_id=user_id,
                agent_id=self.agent_id,
                query=message,
                max_memories=10
            )
            
            if memory_context and memory_context != "No relevant memories found.":
                messages.append({
                    "role": "user",
                    "content": f"[Context from your memory]\n{memory_context}\n\n[End of context]"
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Agentic loop: iterate until agent returns final answer or max iterations reached
        all_tool_calls = []
        all_tool_results = []
        iteration = 0
        final_response = None
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agentic loop iteration {iteration}/{max_iterations}")
            
            # Generate response from LLM
            response = await self.llm_service.generate(
                provider=self.llm_provider,
                messages=messages,
                system_prompt=self.system_prompt,
                temperature=self.get_temperature(),
                max_tokens=self.get_max_tokens(),
                tools=self.available_tools if self.available_tools else None
            )
            
            # Accumulate token usage
            if response.get("usage"):
                for key in total_usage:
                    total_usage[key] += response["usage"].get(key, 0)
            
            # Check if agent made tool calls
            tool_calls = response.get("tool_calls")
            
            if not tool_calls:
                # No tool calls - this is the final response
                final_response = response
                break
            
            # Execute tools
            logger.info(f"Executing {len(tool_calls)} tool(s)")
            tool_results = await self.execute_tools(tool_calls)
            
            # Store tool calls and results
            all_tool_calls.extend(tool_calls)
            all_tool_results.extend(tool_results)
            
            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": response.get("content") or "",
                "tool_calls": tool_calls
            })
            
            # Add tool results to conversation
            for tool_result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_result.get("tool_call_id"),
                    "name": tool_result.get("tool_name"),
                    "content": str(tool_result.get("result") if tool_result.get("success") else tool_result.get("error"))
                })
        
        # If we hit max iterations without final response, use last response
        if final_response is None:
            logger.warning(f"Max iterations ({max_iterations}) reached without final response")
            final_response = response
        
        # Store important information in memory
        await self.store_conversation_memory(
            user_id=user_id,
            user_message=message,
            agent_response=final_response.get("content", "")
        )
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "content": final_response.get("content", ""),
            "tool_calls": all_tool_calls if all_tool_calls else None,
            "tool_results": all_tool_results if all_tool_results else None,
            "iterations": iteration,
            "usage": total_usage,
            "provider": final_response.get("provider"),
            "model": final_response.get("model")
        }
    
    async def execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute tool calls made by the agent.
        
        Args:
            tool_calls: List of tool calls from LLM
        
        Returns:
            List of tool execution results
        """
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]
            
            try:
                logger.info(f"Executing tool: {tool_name}", tool=tool_name)
                
                # Call the tool execution method
                result = await self.execute_tool(tool_name, tool_args)
                
                results.append({
                    "tool_call_id": tool_call["id"],
                    "tool_name": tool_name,
                    "success": True,
                    "result": result
                })
            
            except Exception as e:
                logger.error(f"Tool execution failed: {tool_name}", error=str(e))
                results.append({
                    "tool_call_id": tool_call["id"],
                    "tool_name": tool_name,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a specific tool using the tool registry.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
        
        Returns:
            Tool execution result
        """
        tool_registry = get_tool_registry()
        result = await tool_registry.execute_tool(
            tool_name=tool_name,
            parameters=arguments,
            agent_id=self.agent_id
        )
        
        if result.get("success"):
            return result.get("result")
        else:
            raise Exception(result.get("error", "Tool execution failed"))
    
    async def store_conversation_memory(
        self,
        user_id: str,
        user_message: str,
        agent_response: str
    ) -> None:
        """
        Store conversation in memory.
        
        Args:
            user_id: User identifier
            user_message: User's message
            agent_response: Agent's response
        """
        try:
            # Extract key facts from the conversation
            key_facts = await self.extract_key_facts(user_message, agent_response)
            
            if key_facts:
                await self.memory_manager.store_conversation_context(
                    user_id=user_id,
                    agent_id=self.agent_id,
                    conversation_summary=f"User asked: {user_message[:100]}...",
                    key_facts=key_facts
                )
        except Exception as e:
            logger.error("Failed to store conversation memory", error=str(e))
    
    async def extract_key_facts(self, user_message: str, agent_response: str) -> List[str]:
        """
        Extract key facts to store in memory. Override in subclasses for custom logic.
        
        Args:
            user_message: User's message
            agent_response: Agent's response
        
        Returns:
            List of key facts
        """
        return []
    
    def get_temperature(self) -> float:
        """Get temperature for LLM generation. Override in subclasses."""
        return 0.7
    
    def get_max_tokens(self) -> int:
        """Get max tokens for LLM generation. Override in subclasses."""
        return 4000
