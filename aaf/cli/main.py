import argparse
import sys
import importlib
import inspect
import ast

def parse_args():
    parser = argparse.ArgumentParser(description="Agentic Application Framework (AAF) CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    eject_parser = subparsers.add_parser("eject", help="Eject an AAF decorated workflow/agent into standard Python code.")
    eject_parser.add_argument("module", help="The module containing the workflow (e.g., my_app.workflows)")
    eject_parser.add_argument("name", help="The name of the decorated function to eject")

    return parser.parse_args()

def unwrap_function(func):
    """Unwraps a decorated function to get the original function object."""
    # AAF agents often store original func in `_func` or `func`
    if hasattr(func, "_func"):
        return func._func
    if hasattr(func, "func"):
        return func.func
    # Handle standard python wrappers
    if hasattr(func, "__wrapped__"):
        return unwrap_function(func.__wrapped__)
    return func

def eject_code(module_name: str, target_name: str):
    """
    Attempts to 'eject' a decorated function by providing a rough translation
    into standard un-decorated code by parsing AST.
    """
    print(f"Ejecting {target_name} from {module_name}...\n")
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        print(f"Error importing module {module_name}: {e}")
        sys.exit(1)

    func = getattr(module, target_name, None)
    if not func:
        print(f"Function {target_name} not found in {module_name}")
        sys.exit(1)

    original_func = unwrap_function(func)

    try:
        source_file = inspect.getsourcefile(original_func)
        if not source_file:
             raise ValueError("Source file could not be found.")
        with open(source_file, "r") as f:
            source = f.read()
    except Exception as e:
        print(f"Could not retrieve source for {target_name}: {e}")
        sys.exit(1)

    parsed_ast = ast.parse(source)
    target_node = None
    for node in parsed_ast.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == target_name:
            target_node = node
            break

    if not target_node:
         print(f"Function {target_name} not found in AST.")
         sys.exit(1)

    decorators = []
    for dec in target_node.decorator_list:
        if isinstance(dec, ast.Call):
            if hasattr(dec.func, 'id'):
                 decorators.append(dec.func.id)
            elif hasattr(dec.func, 'attr'):
                 decorators.append(f"{dec.func.value.id}.{dec.func.attr}")
        elif isinstance(dec, ast.Name):
            decorators.append(dec.id)

    print("# NOTE: This is a generated 'ejected' version of your AAF decorated code.")
    print("# It provides a starting point for moving away from AAF decorators to raw framework code.")
    print(f"# Original decorators detected: {', '.join(decorators) if decorators else 'None'}\n")

    print("# Raw Framework Code:")
    is_async = "async " if isinstance(target_node, ast.AsyncFunctionDef) else ""
    print(f"{is_async}def raw_{target_name}(*args, **kwargs):")

    # Simple heuristic-based mapping.
    if 'langgraph_agent' in decorators:
         print("    # LangGraph mapping:")
         print("    # from langgraph.prebuilt import create_react_agent")
         print("    # agent = create_react_agent(...)")
         print("    # return agent.invoke(*args, **kwargs)")
    elif 'crewai_agent' in decorators:
         print("    # CrewAI mapping:")
         print("    # from crewai import Agent")
         print("    # agent = Agent(...)")
         print("    # return agent.execute_task(*args, **kwargs)")
    elif 'pydantic_agent' in decorators:
         print("    # Pydantic AI mapping:")
         print("    # from pydantic_ai import Agent")
         print("    # agent = Agent(...)")
         print("    # return agent.run_sync(*args, **kwargs)")
    else:
         print("    # Generic agent fallback:")
         print("    # agent = YourUnderlyingAgent(...)")
         print("    # return agent.execute(*args, **kwargs)")
    print("    pass\n")

def main():
    args = parse_args()
    if args.command == "eject":
        eject_code(args.module, args.name)

if __name__ == "__main__":
    main()
