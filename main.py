"""
Agentic Application Framework (AAF) - Demonstration Script

This script demonstrates the AAF capabilities through two scenarios:
1. Scenario 1: Agent with security=True successfully using MCP Tool with token injection
2. Scenario 2: Agent with security=False failing A2A delegation due to missing token
"""

import logging
from aaf.framework import AgenticFrameworkX
from aaf.services import MCPToolService, A2AClientService


def setup_logging():
    """Configure logging for the demonstration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: dict, success: bool = True):
    """Print execution result."""
    status = "✓ SUCCESS" if success else "✗ FAILED"
    print(f"\n{status}")
    print("-" * 80)
    print(f"Agent ID: {result.get('agent_id')}")
    print(f"Response: {result.get('response')}")
    print(f"Metadata: {result.get('metadata')}")
    print("-" * 80)


def scenario_1_secure_mcp_tool():
    """
    Scenario 1: Create an agent with framework='langgraph' and security=True,
    successfully using an MCP Tool (via MCPToolService).
    
    Expected: The AuthMiddleware should inject the token from token_map,
    and the MCP tool should execute successfully with authentication.
    """
    print_section_header("SCENARIO 1: Secure MCP Tool Usage (security=True)")
    
    logger = logging.getLogger("scenario_1")
    framework = AgenticFrameworkX(logger)
    
    mcp_service = MCPToolService(tool_name="search", require_auth=True)
    
    agent = framework.create_agent(
        agent_id="secure_agent_1",
        framework="langgraph",
        services=[mcp_service],
        security=True,
        config={"description": "Agent with security enabled for MCP tool"}
    )
    
    input_data = {
        "context": {"user": "demo_user", "session": "session_123"},
        "token_map": {
            "mcp_tool_search": "mcp_secret_token_xyz789"
        },
        "request": {
            "params": {
                "query": "What is the weather today?",
                "max_results": 5
            }
        }
    }
    
    print("Input Configuration:")
    print(f"  - Framework: langgraph")
    print(f"  - Security: True (AuthMiddleware enabled)")
    print(f"  - Service: {mcp_service.service_name}")
    print(f"  - Token Provided: Yes (in token_map)")
    print(f"  - Request: {input_data['request']}")
    
    try:
        result = agent.execute(input_data)
        print_result(result, success=True)
        
        response = result.get('response', {})
        if response.get('status') == 'success' and response.get('authenticated') == True:
            print("\n✓ SCENARIO 1 PASSED: MCP tool executed successfully with authentication!")
            print(f"  Tool Result: {response.get('result')}")
            print(f"  Authenticated: {response.get('authenticated')}")
            print(f"  Token Used: {response.get('token_used')}")
        elif response.get('status') == 'success' and not response.get('authenticated'):
            print("\n✗ SCENARIO 1 FAILED: Service executed but was not authenticated!")
            print("  AuthMiddleware should have injected the token for authenticated execution.")
            return False
        else:
            print("\n✗ SCENARIO 1 FAILED: Unexpected response status")
            return False
        
        agent.shutdown()
        return True
    except Exception as e:
        print(f"\n✗ SCENARIO 1 FAILED with exception: {str(e)}")
        return False


def scenario_2_insecure_a2a_failure():
    """
    Scenario 2: Create an agent with framework='langgraph' and security=False,
    showing that A2A Delegation (via A2AClientService) fails due to missing token.
    
    Expected: Without AuthMiddleware (security=False), the token won't be injected,
    and the A2A service should raise PermissionError.
    """
    print_section_header("SCENARIO 2: A2A Delegation Failure (security=False)")
    
    logger = logging.getLogger("scenario_2")
    framework = AgenticFrameworkX(logger)
    
    a2a_service = A2AClientService(target_agent="assistant_agent")
    
    agent = framework.create_agent(
        agent_id="insecure_agent_2",
        framework="langgraph",
        services=[a2a_service],
        security=False,
        config={"description": "Agent with security disabled - should fail A2A"}
    )
    
    input_data = {
        "context": {"user": "demo_user", "session": "session_456"},
        "token_map": {
            "a2a_client_assistant_agent": "a2a_secret_token_abc123"
        },
        "request": {
            "task": {
                "action": "summarize",
                "data": "Please summarize this document"
            }
        }
    }
    
    print("Input Configuration:")
    print(f"  - Framework: langgraph")
    print(f"  - Security: False (AuthMiddleware NOT enabled)")
    print(f"  - Service: {a2a_service.service_name}")
    print(f"  - Token Available: Yes (in token_map, but won't be injected)")
    print(f"  - Request: {input_data['request']}")
    
    try:
        result = agent.execute(input_data)
        print_result(result, success=False)
        print("\n✗ SCENARIO 2 FAILED: A2A should have raised PermissionError but didn't!")
        agent.shutdown()
        return False
    except PermissionError as e:
        print(f"\n✓ SCENARIO 2 PASSED: A2A delegation correctly failed with PermissionError!")
        print(f"  Error Message: {str(e)}")
        print(f"  Reason: Token was not injected because security=False (no AuthMiddleware)")
        agent.shutdown()
        return True
    except Exception as e:
        print(f"\n✗ SCENARIO 2 FAILED with unexpected exception: {type(e).__name__}: {str(e)}")
        return False


def main():
    """Run all demonstration scenarios."""
    logger = setup_logging()
    
    print("\n" + "=" * 80)
    print("  AGENTIC APPLICATION FRAMEWORK (AAF) - DEMONSTRATION")
    print("=" * 80)
    print("\nThis demonstration shows the AAF's middleware architecture,")
    print("service abstraction, and token-based authentication flow.\n")
    
    results = []
    
    results.append(("Scenario 1: Secure MCP Tool", scenario_1_secure_mcp_tool()))
    
    results.append(("Scenario 2: Insecure A2A Failure", scenario_2_insecure_a2a_failure()))
    
    print_section_header("DEMONSTRATION SUMMARY")
    print("Results:")
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    print("\n" + "=" * 80)
    if all_passed:
        print("  ✓ ALL SCENARIOS PASSED - AAF DEMONSTRATION SUCCESSFUL!")
    else:
        print("  ✗ SOME SCENARIOS FAILED - REVIEW OUTPUT ABOVE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
