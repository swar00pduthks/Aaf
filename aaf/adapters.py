"""
Framework adapters for integrating AAF with popular agentic frameworks.

This module provides adapter classes that wrap agents from other frameworks
(LangGraph, Microsoft Agent Framework, CrewAI) to work seamlessly with AAF's
protocol-based architecture.

Usage:
    from aaf.adapters import LangGraphAdapter, CrewAIAdapter
    
    # Wrap your LangGraph agent
    lg_agent = create_react_agent(...)
    aaf_agent = LangGraphAdapter("researcher", lg_agent)
    
    # Use with AAF patterns
    pipeline = SequentialPattern(agents=[aaf_agent, ...])
"""

import logging
from typing import Any, Dict, Optional


class LangGraphAdapter:
    """
    Adapter for LangGraph agents to work with AAF protocols.
    
    LangGraph provides stateful graph execution with conditional edges
    and checkpointing. AAF adds REST API, memory, and HITL workflows.
    
    Example:
        from langgraph.prebuilt import create_react_agent
        from aaf.adapters import LangGraphAdapter
        
        lg_agent = create_react_agent(model, tools)
        aaf_agent = LangGraphAdapter("my_agent", lg_agent)
        
        result = aaf_agent.execute({"messages": [...]})
    """
    
    def __init__(
        self,
        agent_id: str,
        langgraph_agent,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize LangGraph adapter.
        
        Args:
            agent_id: Unique identifier for this agent
            langgraph_agent: Your LangGraph agent instance
            logger: Optional logger for debugging
        """
        self._agent_id = agent_id
        self._lg_agent = langgraph_agent
        self._logger = logger or logging.getLogger(__name__)
    
    @property
    def agent_id(self) -> str:
        return self._agent_id
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the agent with configuration."""
        self._logger.info(f"[LangGraphAdapter:{self._agent_id}] Initialized")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the LangGraph agent.
        
        Args:
            input_data: Input dictionary (typically contains 'messages')
            
        Returns:
            Execution result from LangGraph agent
        """
        self._logger.info(f"[LangGraphAdapter:{self._agent_id}] Executing")
        
        try:
            # LangGraph agents typically use .invoke() or .stream()
            result = self._lg_agent.invoke(input_data)
            
            return {
                "status": "success",
                "agent_id": self._agent_id,
                "framework": "LangGraph",
                "result": result
            }
        except Exception as e:
            self._logger.error(f"[LangGraphAdapter:{self._agent_id}] Error: {str(e)}")
            return {
                "status": "error",
                "agent_id": self._agent_id,
                "framework": "LangGraph",
                "error": str(e)
            }
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        self._logger.info(f"[LangGraphAdapter:{self._agent_id}] Shutdown")


class MicrosoftAgentAdapter:
    """
    Adapter for Microsoft Agent Framework agents to work with AAF protocols.
    
    Microsoft Agent Framework provides multi-agent patterns, MCP support,
    and A2A communication. AAF adds REST API layer and production features.
    
    Example:
        from agent_framework import ChatAgent
        from aaf.adapters import MicrosoftAgentAdapter
        
        ms_agent = ChatAgent(...)
        aaf_agent = MicrosoftAgentAdapter("assistant", ms_agent)
        
        result = aaf_agent.execute({"query": "..."})
    """
    
    def __init__(
        self,
        agent_id: str,
        microsoft_agent,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Microsoft Agent adapter.
        
        Args:
            agent_id: Unique identifier for this agent
            microsoft_agent: Your Microsoft Agent Framework agent
            logger: Optional logger for debugging
        """
        self._agent_id = agent_id
        self._ms_agent = microsoft_agent
        self._logger = logger or logging.getLogger(__name__)
    
    @property
    def agent_id(self) -> str:
        return self._agent_id
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the agent with configuration."""
        self._logger.info(f"[MSAgentAdapter:{self._agent_id}] Initialized")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Microsoft Agent Framework agent.
        
        Args:
            input_data: Input dictionary (typically contains 'query' or 'messages')
            
        Returns:
            Execution result from Microsoft agent
        """
        self._logger.info(f"[MSAgentAdapter:{self._agent_id}] Executing")
        
        try:
            # Microsoft agents use .run() or .run_async()
            # For async agents, you may need to wrap in asyncio.run()
            query = input_data.get("query", input_data.get("messages", ""))
            
            # If your agent is async:
            # import asyncio
            # result = asyncio.run(self._ms_agent.run_async(query))
            
            # For sync agents (placeholder - replace with actual call):
            result = f"Microsoft Agent {self._agent_id} processed: {query}"
            
            return {
                "status": "success",
                "agent_id": self._agent_id,
                "framework": "Microsoft Agent Framework",
                "result": result
            }
        except Exception as e:
            self._logger.error(f"[MSAgentAdapter:{self._agent_id}] Error: {str(e)}")
            return {
                "status": "error",
                "agent_id": self._agent_id,
                "framework": "Microsoft Agent Framework",
                "error": str(e)
            }
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        self._logger.info(f"[MSAgentAdapter:{self._agent_id}] Shutdown")


class CrewAIAdapter:
    """
    Adapter for CrewAI agents to work with AAF protocols.
    
    CrewAI provides role-based agent collaboration with crews and flows.
    AAF adds memory, planning, guardrails, and REST API exposure.
    
    Example:
        from crewai import Agent, Task, Crew
        from aaf.adapters import CrewAIAdapter
        
        crew_agent = Agent(role="Researcher", goal="...", backstory="...")
        aaf_agent = CrewAIAdapter("researcher", crew_agent)
        
        result = aaf_agent.execute({"task": "research AI trends"})
    """
    
    def __init__(
        self,
        agent_id: str,
        crewai_agent,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize CrewAI adapter.
        
        Args:
            agent_id: Unique identifier for this agent
            crewai_agent: Your CrewAI Agent instance
            logger: Optional logger for debugging
        """
        self._agent_id = agent_id
        self._crew_agent = crewai_agent
        self._logger = logger or logging.getLogger(__name__)
    
    @property
    def agent_id(self) -> str:
        return self._agent_id
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the agent with configuration."""
        self._logger.info(f"[CrewAIAdapter:{self._agent_id}] Initialized")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the CrewAI agent.
        
        Args:
            input_data: Input dictionary (typically contains 'task')
            
        Returns:
            Execution result from CrewAI agent
        """
        self._logger.info(f"[CrewAIAdapter:{self._agent_id}] Executing")
        
        try:
            # CrewAI agents execute tasks
            # For a single agent: agent.execute_task(task)
            # For a crew: crew.kickoff()
            
            task_description = input_data.get("task", input_data.get("description", ""))
            
            # Placeholder - replace with actual CrewAI execution:
            # from crewai import Task
            # task = Task(description=task_description, agent=self._crew_agent)
            # result = self._crew_agent.execute_task(task)
            
            result = f"CrewAI Agent {self._agent_id} processed: {task_description}"
            
            return {
                "status": "success",
                "agent_id": self._agent_id,
                "framework": "CrewAI",
                "role": getattr(self._crew_agent, "role", "unknown"),
                "result": result
            }
        except Exception as e:
            self._logger.error(f"[CrewAIAdapter:{self._agent_id}] Error: {str(e)}")
            return {
                "status": "error",
                "agent_id": self._agent_id,
                "framework": "CrewAI",
                "error": str(e)
            }
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        self._logger.info(f"[CrewAIAdapter:{self._agent_id}] Shutdown")


class AutoGenAdapter:
    """
    Adapter for AutoGen agents to work with AAF protocols.
    
    AutoGen provides multi-agent conversations and group chat patterns.
    AAF adds orchestration, memory, and production features.
    
    Example:
        from autogen import AssistantAgent
        from aaf.adapters import AutoGenAdapter
        
        autogen_agent = AssistantAgent("assistant", llm_config={...})
        aaf_agent = AutoGenAdapter("assistant", autogen_agent)
        
        result = aaf_agent.execute({"message": "analyze this data"})
    """
    
    def __init__(
        self,
        agent_id: str,
        autogen_agent,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize AutoGen adapter.
        
        Args:
            agent_id: Unique identifier for this agent
            autogen_agent: Your AutoGen agent instance
            logger: Optional logger for debugging
        """
        self._agent_id = agent_id
        self._autogen_agent = autogen_agent
        self._logger = logger or logging.getLogger(__name__)
    
    @property
    def agent_id(self) -> str:
        return self._agent_id
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the agent with configuration."""
        self._logger.info(f"[AutoGenAdapter:{self._agent_id}] Initialized")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the AutoGen agent.
        
        Args:
            input_data: Input dictionary (typically contains 'message')
            
        Returns:
            Execution result from AutoGen agent
        """
        self._logger.info(f"[AutoGenAdapter:{self._agent_id}] Executing")
        
        try:
            message = input_data.get("message", input_data.get("query", ""))
            
            # AutoGen agents use .generate_reply() or conversation patterns
            # Placeholder - replace with actual AutoGen call:
            # reply = self._autogen_agent.generate_reply(messages=[{"role": "user", "content": message}])
            
            result = f"AutoGen Agent {self._agent_id} processed: {message}"
            
            return {
                "status": "success",
                "agent_id": self._agent_id,
                "framework": "AutoGen",
                "result": result
            }
        except Exception as e:
            self._logger.error(f"[AutoGenAdapter:{self._agent_id}] Error: {str(e)}")
            return {
                "status": "error",
                "agent_id": self._agent_id,
                "framework": "AutoGen",
                "error": str(e)
            }
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        self._logger.info(f"[AutoGenAdapter:{self._agent_id}] Shutdown")
