"""
Databricks Gemini & Genie Integration for AAF

Enables AAF to use:
1. Databricks Gemini - Google's Gemini models as LLM provider
2. Databricks Genie - Text-to-SQL conversational agent
"""

import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class DatabricksGeminiProvider:
    """
    LLM provider for Databricks-hosted Gemini models.
    
    Supports:
    - Gemini 2.5 Pro (advanced reasoning, 1M token context)
    - Gemini 2.5 Flash (fast, cost-efficient)
    - Gemini 3 Pro (latest frontier model)
    
    Example:
        from aaf.databricks_integration import DatabricksGeminiProvider
        
        # Configure provider
        provider = DatabricksGeminiProvider(
            workspace_url="https://myworkspace.databricks.com",
            token=os.environ["DATABRICKS_TOKEN"]
        )
        
        # Use with @llm decorator
        @llm(provider=provider, model="gemini-2.5-flash")
        def analyze_data(state):
            return {"analysis": "..."}
    """
    
    def __init__(
        self,
        workspace_url: str,
        token: Optional[str] = None,
        model: str = "gemini-2.5-flash"
    ):
        """
        Initialize Databricks Gemini provider.
        
        Args:
            workspace_url: Databricks workspace URL
                          (e.g., "https://myworkspace.databricks.com")
            token: Databricks personal access token
                  (defaults to DATABRICKS_TOKEN env var)
            model: Default model to use
                  ("gemini-2.5-pro", "gemini-2.5-flash", "gemini-3-pro")
        """
        self.workspace_url = workspace_url.rstrip('/')
        self.token = token or os.environ.get("DATABRICKS_TOKEN")
        self.model = model
        
        if not self.token:
            raise ValueError(
                "Databricks token required. Set DATABRICKS_TOKEN env var "
                "or pass token parameter."
            )
    
    def _get_endpoint_url(self, model: str) -> str:
        """Get serving endpoint URL for model."""
        return f"{self.workspace_url}/serving-endpoints/{model}/invocations"
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Generate completion using Databricks Gemini.
        
        Uses OpenAI-compatible endpoint format.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (overrides default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text completion
        """
        try:
            # Use OpenAI client for compatibility
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.token,
                base_url=f"{self.workspace_url}/serving-endpoints"
            )
            
            response = client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            logger.error("OpenAI package required: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Databricks Gemini API error: {e}")
            raise
    
    def complete_with_sql(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> str:
        """
        Generate completion using Databricks SQL `ai_query` function.
        
        This runs directly in SQL and can scale to millions of rows.
        
        Example SQL:
            SELECT ai_query('gemini-2.5-flash', 'Analyze this text...')
            FROM my_table;
        
        Args:
            prompt: Natural language prompt
            model: Model to use
            
        Returns:
            Generated completion
        """
        try:
            import requests
            
            # Use Databricks SQL API
            sql = f"""
            SELECT ai_query('{model or self.model}', '{prompt}') as result
            """
            
            url = f"{self.workspace_url}/api/2.0/sql/statements"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            data = {
                "statement": sql,
                "warehouse_id": os.environ.get("DATABRICKS_WAREHOUSE_ID")
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return result["result"]["data_array"][0][0]
            
        except Exception as e:
            logger.error(f"Databricks SQL error: {e}")
            raise


class DatabricksGenieAgent:
    """
    Databricks Genie as an AAF agent.
    
    Genie converts natural language to SQL queries and executes them
    against Unity Catalog data.
    
    This wraps the Genie API as an AAF autonomous agent.
    
    Example:
        from aaf import autonomous_agent
        from aaf.databricks_integration import DatabricksGenieAgent
        
        genie = DatabricksGenieAgent(
            workspace_url="https://myworkspace.databricks.com",
            space_id="abc123"
        )
        
        # Use as autonomous agent
        @autonomous_agent(backend=genie)
        def sql_assistant(state):
            return genie.ask(state["user_query"])
    """
    
    def __init__(
        self,
        workspace_url: str,
        space_id: str,
        token: Optional[str] = None
    ):
        """
        Initialize Databricks Genie agent.
        
        Args:
            workspace_url: Databricks workspace URL
            space_id: Genie space ID (from Genie space URL)
            token: Databricks access token
        """
        self.workspace_url = workspace_url.rstrip('/')
        self.space_id = space_id
        self.token = token or os.environ.get("DATABRICKS_TOKEN")
        
        if not self.token:
            raise ValueError("Databricks token required")
    
    def ask(
        self,
        question: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask Genie a natural language question about data.
        
        Args:
            question: Natural language query
                     (e.g., "What are total sales by region?")
            conversation_id: Optional conversation ID for follow-ups
            
        Returns:
            Dict with:
            - sql: Generated SQL query
            - result: Query results
            - summary: Natural language summary
            - conversation_id: ID for follow-up questions
        """
        try:
            import requests
            
            url = f"{self.workspace_url}/api/2.0/genie/spaces/{self.space_id}/start-conversation"
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            data = {"content": question}
            if conversation_id:
                data["conversation_id"] = conversation_id
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "sql": result.get("query", {}).get("query"),
                "result": result.get("result"),
                "summary": result.get("message", {}).get("content"),
                "conversation_id": result.get("conversation_id"),
                "thinking_steps": result.get("attachments", [])
            }
            
        except Exception as e:
            logger.error(f"Databricks Genie API error: {e}")
            raise
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute as AAF autonomous agent.
        
        Args:
            state: Workflow state with 'user_query' key
            
        Returns:
            Updated state with Genie response
        """
        question = state.get("user_query", "")
        conversation_id = state.get("genie_conversation_id")
        
        result = self.ask(question, conversation_id)
        
        return {
            **state,
            "genie_sql": result["sql"],
            "genie_result": result["result"],
            "genie_summary": result["summary"],
            "genie_conversation_id": result["conversation_id"]
        }


# Helper functions for easy integration
def create_databricks_gemini_llm(
    workspace_url: str,
    model: str = "gemini-2.5-flash",
    token: Optional[str] = None
):
    """
    Create Databricks Gemini LLM provider.
    
    Example:
        provider = create_databricks_gemini_llm(
            workspace_url="https://myworkspace.databricks.com",
            model="gemini-2.5-pro"
        )
    """
    return DatabricksGeminiProvider(
        workspace_url=workspace_url,
        token=token,
        model=model
    )


def create_databricks_genie_agent(
    workspace_url: str,
    space_id: str,
    token: Optional[str] = None
):
    """
    Create Databricks Genie agent.
    
    Example:
        genie = create_databricks_genie_agent(
            workspace_url="https://myworkspace.databricks.com",
            space_id="abc123"
        )
    """
    return DatabricksGenieAgent(
        workspace_url=workspace_url,
        space_id=space_id,
        token=token
    )
