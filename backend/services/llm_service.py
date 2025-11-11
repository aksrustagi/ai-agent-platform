"""Multi-LLM service supporting Claude, GPT-4, and Groq."""

import time
from enum import Enum
from typing import Any, Dict, List, Optional

import anthropic
import groq
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import Settings
from backend.utils.errors import LLMProviderError
from backend.utils.helpers import CircuitBreaker, measure_time
from backend.utils.logger import get_logger, log_llm_request, log_llm_response

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    GPT4 = "gpt4"
    GROQ = "groq"


class LLMService:
    """
    Multi-provider LLM service with retry logic and circuit breakers.
    """
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize LLM service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        
        # Initialize clients
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.groq_client = groq.AsyncGroq(api_key=settings.groq_api_key)
        
        # Circuit breakers for each provider
        self.circuit_breakers = {
            LLMProvider.CLAUDE: CircuitBreaker(
                failure_threshold=settings.circuit_breaker_failure_threshold,
                recovery_timeout=settings.circuit_breaker_recovery_timeout,
                name="claude"
            ),
            LLMProvider.GPT4: CircuitBreaker(
                failure_threshold=settings.circuit_breaker_failure_threshold,
                recovery_timeout=settings.circuit_breaker_recovery_timeout,
                name="gpt4"
            ),
            LLMProvider.GROQ: CircuitBreaker(
                failure_threshold=settings.circuit_breaker_failure_threshold,
                recovery_timeout=settings.circuit_breaker_recovery_timeout,
                name="groq"
            ),
        }
        
        logger.info("LLM service initialized with all providers")
    
    @measure_time
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate(
        self,
        provider: LLMProvider,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate completion from specified LLM provider.
        
        Args:
            provider: LLM provider to use
            messages: List of messages
            system_prompt: Optional system prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            tools: Optional tools for function calling
        
        Returns:
            Response dictionary with content, usage, and metadata
        
        Raises:
            LLMProviderError: If generation fails
        """
        circuit_breaker = self.circuit_breakers[provider]
        
        try:
            if provider == LLMProvider.CLAUDE:
                return await circuit_breaker.call(
                    self._generate_claude,
                    messages,
                    system_prompt,
                    temperature,
                    max_tokens,
                    tools
                )
            elif provider == LLMProvider.GPT4:
                return await circuit_breaker.call(
                    self._generate_gpt4,
                    messages,
                    system_prompt,
                    temperature,
                    max_tokens,
                    tools
                )
            elif provider == LLMProvider.GROQ:
                return await circuit_breaker.call(
                    self._generate_groq,
                    messages,
                    system_prompt,
                    temperature,
                    max_tokens
                )
            else:
                raise LLMProviderError(f"Unsupported provider: {provider}", provider=provider.value)
        
        except Exception as e:
            logger.error(f"LLM generation failed for {provider}", error=str(e))
            raise LLMProviderError(f"Generation failed: {str(e)}", provider=provider.value)
    
    async def _generate_claude(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Generate completion using Claude."""
        start_time = time.time()
        
        # Log request
        prompt_tokens = sum(len(m["content"]) // 4 for m in messages)  # Rough estimate
        log_llm_request(logger, "anthropic", self.settings.claude_model, prompt_tokens)
        
        try:
            kwargs = {
                "model": self.settings.claude_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            if tools:
                kwargs["tools"] = tools
            
            response = await self.anthropic_client.messages.create(**kwargs)
            
            # Extract response - Claude uses content blocks
            content = ""
            tool_calls = None
            
            if response.content:
                # Extract text content and tool use
                text_blocks = []
                tool_use_blocks = []
                
                for block in response.content:
                    if block.type == "text":
                        text_blocks.append(block.text)
                    elif block.type == "tool_use":
                        tool_use_blocks.append(block)
                
                content = "\n".join(text_blocks)
                
                # Convert Claude tool use to standard format
                if tool_use_blocks:
                    tool_calls = [
                        {
                            "id": tc.id,
                            "name": tc.name,
                            "arguments": tc.input
                        }
                        for tc in tool_use_blocks
                    ]
            
            # Log response
            latency_ms = (time.time() - start_time) * 1000
            completion_tokens = response.usage.output_tokens if hasattr(response, 'usage') else 0
            log_llm_response(
                logger,
                "anthropic",
                self.settings.claude_model,
                completion_tokens,
                latency_ms
            )
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens if hasattr(response, 'usage') else 0,
                    "completion_tokens": completion_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens if hasattr(response, 'usage') else 0
                },
                "model": self.settings.claude_model,
                "provider": "claude"
            }
        
        except Exception as e:
            logger.error("Claude generation failed", error=str(e))
            raise
    
    async def _generate_gpt4(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Generate completion using GPT-4."""
        start_time = time.time()
        
        # Prepare messages with system prompt
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        # Log request
        prompt_tokens = sum(len(m["content"]) // 4 for m in full_messages)
        log_llm_request(logger, "openai", self.settings.gpt4_model, prompt_tokens)
        
        try:
            kwargs = {
                "model": self.settings.gpt4_model,
                "messages": full_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            response = await self.openai_client.chat.completions.create(**kwargs)
            
            # Extract response
            message = response.choices[0].message
            content = message.content or ""
            tool_calls = None
            
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                    for tc in message.tool_calls
                ]
            
            # Log response
            latency_ms = (time.time() - start_time) * 1000
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            log_llm_response(
                logger,
                "openai",
                self.settings.gpt4_model,
                completion_tokens,
                latency_ms
            )
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": completion_tokens,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "model": self.settings.gpt4_model,
                "provider": "gpt4"
            }
        
        except Exception as e:
            logger.error("GPT-4 generation failed", error=str(e))
            raise
    
    async def _generate_groq(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Generate completion using Groq."""
        start_time = time.time()
        
        # Prepare messages with system prompt
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        # Log request
        prompt_tokens = sum(len(m["content"]) // 4 for m in full_messages)
        log_llm_request(logger, "groq", self.settings.groq_model, prompt_tokens)
        
        try:
            response = await self.groq_client.chat.completions.create(
                model=self.settings.groq_model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response
            content = response.choices[0].message.content or ""
            
            # Log response
            latency_ms = (time.time() - start_time) * 1000
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            log_llm_response(
                logger,
                "groq",
                self.settings.groq_model,
                completion_tokens,
                latency_ms
            )
            
            return {
                "content": content,
                "tool_calls": None,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": completion_tokens,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "model": self.settings.groq_model,
                "provider": "groq"
            }
        
        except Exception as e:
            logger.error("Groq generation failed", error=str(e))
            raise
