# AAF Product Team Skills

This directory contains YAML configuration files defining the "skills" (personas, goals, and system prompts) for the specialized AI agents required to manage and develop the Agentic Application Framework (AAF) as a full product.

## The AAF Product Team Roles

1. **`competitive_analyst.yaml`**: Monitors frameworks like LangGraph, Pydantic AI, and CrewAI to ensure AAF's competitive edge.
2. **`product_manager.yaml`**: Owns the roadmap (Type Safety, Streaming) and prioritizes engineering work without compromising simplicity.
3. **`chief_architect.yaml`**: Enforces the "Everything is a Decorator" philosophy and designs cross-framework integrations.
4. **`core_engineer.yaml`**: Writes robust, type-safe Python code to implement decorators, memory, and planning.
5. **`qa_engineer.yaml`**: Validates the codebase with 100% test coverage and handles edge-case bug hunting.
6. **`devrel_engineer.yaml`**: Creates beautiful `examples/` and reduces the "Time-to-Hello-World" metric.
7. **`technical_writer.yaml`**: Maintains pristine Markdown documentation (e.g., `USER_GUIDE.md`).
8. **`release_manager.yaml`**: Automates CI/CD pipelines, dependency checks (`uv.lock`), and PyPI releases.
9. **`product_marketing_manager.yaml`**: Crafts compelling messaging around the "Lambda for AI Agents" value proposition.

## How to Use These Files

These YAML files are designed to be read by **any modern LLM IDE** (Cursor, Copilot, Jules) or loaded programmatically into an **agentic framework** (like AAF itself, CrewAI, AutoGen, or LangChain).

### Method 1: IDE Context (Cursor, Copilot, Jules)

If you are using an AI coding assistant, you can simply @-mention these files to assume the persona.
For example, in Cursor:
> "@skills/technical_writer.yaml Read `aaf/decorators.py` and write documentation for the new `@stack` feature."

The LLM will automatically adopt the goals, constraints, and system prompt defined in the YAML file.

### Method 2: Programmatic Usage (with AAF)

You can load these YAML files in Python to dynamically configure your AAF agents:

```python
import yaml
from aaf import agent

# Load the skill configuration
with open("skills/devrel_engineer.yaml", "r") as f:
    skill_config = yaml.safe_load(f)

# Define the agent using the loaded system prompt
@agent
def devrel_agent(context: dict) -> dict:
    prompt = skill_config["system_prompt"]
    # ... call LLM API using the prompt and context ...
    return result
```

By structuring these as YAML, the AAF product team can scale from a set of human-driven AI instructions into a fully automated, multi-agent product development lifecycle.
